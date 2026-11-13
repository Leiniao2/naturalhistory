using System;
using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Climate
{
    public enum ClimateZone
    {
        TropicalRainforest, TropicalSavanna, HotDesert, ColdDesert, Steppe,
        HumidSubtropical, Mediterranean, Oceanic, Continental, Boreal, Tundra, IceCap,
        TropicalOcean, TemperateOcean, PolarOcean, SeaIce
    }

    // World-wide averages for the current date
    public struct GlobalClimate
    {
        public float TemperatureC;
        public float Humidity;      // area-weighted mean relative humidity of all tiles, %
        public float O2Percent;
        public float Co2Ppm;
        public float SeaLevelM;     // relative to today
        public string Note;         // nearest dated climate event, e.g. "Hirnantian glaciation"
    }

    public struct TileClimate
    {
        public float TemperatureC;  // annual mean surface air temperature
        public float Humidity;      // relative humidity, %
        public float O2Percent;
        public float Co2Ppm;
        public ClimateZone Zone;
    }

    // Computes every tile's climate from the global averages for the current date (interpolated from
    // climate_history.json) plus the tile's geography: latitude, altitude, distance to water, terrain
    // and vegetation. Tiles are re-centred so their area-weighted average equals the global value, and the
    // whole thing is a pure function of (map, date), so values change smoothly turn to turn and
    // nothing extra needs saving.
    public class ClimateSystem : MonoBehaviour
    {
        public static ClimateSystem Instance { get; private set; }

        public event Action Updated;

        public GlobalClimate Global { get; private set; }
        public bool HasData => tiles != null;

        // --- Model constants ---
        const float LapseRatePerKm     = 6.5f;  // °C cooler per km of altitude
        const float KmPerElevation     = 0.35f; // terrace level → km (level 10 ≈ 3.5 km)
        const float ModernGradient     = 45f;   // equator-to-pole temperature difference today (°C)
        const float GradientPerDegree  = 1.6f;  // warmer worlds have flatter gradients
        const float MinGradient        = 18f;
        const float MaxGradient        = 52f;
        const float OceanDamping       = 0.85f; // seas swing less than land

        private HexGrid grid;
        private TileClimate[,] tiles;

        // Static per-tile geography, rebuilt when the map is (re)generated
        private float[,] latitudeProfile; // cos²(latitude): 1 at the equator, 0 at the poles
        private float[,] latitudeRad;
        private float[,] areaWeight;       // cos(latitude): the map is a flat projection, so polar rows
                                           // stand for much less of the globe than equatorial ones
        private float[,] altitudeKm;
        private float[,] baseHumidity;     // before the global aridity nudge
        private float[,] o2Factor, co2Factor; // local sources/sinks, mean-zero
        private float[,] noise;            // small fixed per-tile variety, °C
        private bool[,] isWater;

        // Like PlayerBall: spawn in any scene with a map, so Game.unity doesn't need editing.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<ClimateSystem>() != null) return;
            new GameObject("ClimateSystem").AddComponent<ClimateSystem>();
        }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            grid = HexGrid.Instance;
            if (grid != null)
            {
                grid.Generated += OnMapGenerated;
                if (grid.IsGenerated) BuildGeography();
            }
            if (AgeManager.Instance != null) AgeManager.Instance.TimeChanged += Recompute;
            Recompute();
        }

        private void OnDestroy()
        {
            if (grid != null) grid.Generated -= OnMapGenerated;
            if (AgeManager.Instance != null) AgeManager.Instance.TimeChanged -= Recompute;
            if (Instance == this) Instance = null;
        }

        public TileClimate Get(HexCell cell)
        {
            if (tiles == null || cell == null) return default;
            var (col, row) = cell.Coordinates.ToOffsetCoordinates();
            if (col < 0 || row < 0 || col >= tiles.GetLength(0) || row >= tiles.GetLength(1)) return default;
            return tiles[col, row];
        }

        private void OnMapGenerated()
        {
            BuildGeography();
            Recompute();
        }

        // ---------- Global averages ----------

        // Linear interpolation between dated keyframes (sorted oldest → newest)
        public static GlobalClimate SampleHistory(float ma)
        {
            if (GameDataLoader.ClimateHistory == null) GameDataLoader.Initialize();
            var keys = GameDataLoader.ClimateHistory;
            if (keys == null || keys.Count == 0) return new GlobalClimate { TemperatureC = 14f, O2Percent = 20.95f, Co2Ppm = 280f };

            if (ma >= keys[0].ma) return FromKey(keys[0], keys[0], 0f);
            for (int i = 1; i < keys.Count; i++)
            {
                if (ma < keys[i].ma) continue;
                var older = keys[i - 1];
                var newer = keys[i];
                float t = Mathf.InverseLerp(older.ma, newer.ma, ma);
                return FromKey(older, newer, t);
            }
            var last = keys[keys.Count - 1];
            return FromKey(last, last, 0f);
        }

        private static GlobalClimate FromKey(ClimateKeyframe a, ClimateKeyframe b, float t) => new()
        {
            TemperatureC = Mathf.Lerp(a.temperatureC, b.temperatureC, t),
            Co2Ppm       = Mathf.Lerp(a.co2ppm,       b.co2ppm,       t),
            O2Percent    = Mathf.Lerp(a.o2Percent,    b.o2Percent,    t),
            SeaLevelM    = Mathf.Lerp(a.seaLevelM,    b.seaLevelM,    t),
            Humidity     = Mathf.Lerp(a.humidityOffset, b.humidityOffset, t), // offset here; replaced by the tile mean
            Note         = t < 0.5f ? a.note : b.note,
        };

        // ---------- Per-tile model ----------

        private void BuildGeography()
        {
            int w = grid.Width, h = grid.Height;
            latitudeProfile = new float[w, h];
            latitudeRad     = new float[w, h];
            areaWeight      = new float[w, h];
            altitudeKm      = new float[w, h];
            baseHumidity    = new float[w, h];
            o2Factor        = new float[w, h];
            co2Factor       = new float[w, h];
            noise           = new float[w, h];
            isWater         = new bool[w, h];
            tiles           = new TileClimate[w, h];

            var waterDistance = WaterDistances(w, h);

            for (int r = 0; r < h; r++)
            for (int q = 0; q < w; q++)
            {
                var cell = grid.GetCell(q, r);
                var kind = cell.Terrain != null ? cell.Terrain.kind : TerrainKind.Plain;
                bool water = cell.Terrain != null && cell.Terrain.IsWater;
                isWater[q, r] = water;

                // Rows run pole to pole
                float lat = (r / (float)Mathf.Max(1, h - 1) - 0.5f) * Mathf.PI;
                latitudeRad[q, r]     = lat;
                areaWeight[q, r]      = Mathf.Max(0.02f, Mathf.Cos(lat));
                latitudeProfile[q, r] = Mathf.Cos(lat) * Mathf.Cos(lat);
                altitudeKm[q, r]      = water ? 0f : cell.Elevation * KmPerElevation;
                noise[q, r]           = (Hash01(q, r, 17) - 0.5f) * 2f; // ±1 °C

                // Relative humidity: Hadley/Ferrel circulation (wet equator & ~60°, dry ~30° & poles),
                // drier deep inside continents, plus terrain and vegetation.
                float hum = 70f + 12f * Mathf.Cos(6f * lat);
                if (water) hum = 82f;
                else
                {
                    hum -= Mathf.Min(waterDistance[q, r], 12) * 2.5f;
                    hum += kind switch
                    {
                        TerrainKind.Wetland  => 12f,
                        TerrainKind.Desert   => -25f,
                        TerrainKind.Mountain => -6f,
                        TerrainKind.IceSheet => -5f,
                        _                    => 0f,
                    };
                    if (cell.IsForest) hum += 6f;
                }
                baseHumidity[q, r] = hum;

                // Local gas sources/sinks (fractions of the global value), small by design: both
                // gases are well mixed in the real atmosphere.
                float o2 = 0f, co2 = 0f;
                if (cell.IsForest)                   { o2 += 0.010f; co2 -= 0.030f; }
                if (kind == TerrainKind.Wetland)     { o2 += 0.004f; co2 += 0.010f; }
                if (kind == TerrainKind.Desert)      { o2 -= 0.004f; co2 += 0.008f; }
                if (kind == TerrainKind.IceSheet)    { o2 -= 0.002f; }
                if (kind == TerrainKind.SaltWater)   { co2 -= 0.010f; }  // ocean uptake
                if (kind == TerrainKind.Mountain)    { co2 += 0.006f; }  // volcanic / weathering stand-in
                o2Factor[q, r]  = o2;
                co2Factor[q, r] = co2;
            }

            CenterOnZero(o2Factor, areaWeight);
            CenterOnZero(co2Factor, areaWeight);
        }

        // Combines geography with the global averages for the current date.
        private void Recompute()
        {
            float ma = AgeManager.Instance != null ? AgeManager.Instance.MillionYearsAgo : 538.8f;
            var global = SampleHistory(ma);
            float aridity = global.Humidity;

            if (tiles == null)
            {
                global.Humidity = 0f;
                Global = global;
                Updated?.Invoke();
                return;
            }

            int w = tiles.GetLength(0), h = tiles.GetLength(1);
            float gradient = Mathf.Clamp(ModernGradient - GradientPerDegree * (global.TemperatureC - 14f), MinGradient, MaxGradient);

            float meanProfile = Mean(latitudeProfile, areaWeight);
            double sumT = 0, sumH = 0, sumW = 0;
            for (int r = 0; r < h; r++)
            for (int q = 0; q < w; q++)
            {
                float anomaly = gradient * (latitudeProfile[q, r] - meanProfile);
                if (isWater[q, r]) anomaly *= OceanDamping;
                float temp = global.TemperatureC + anomaly - altitudeKm[q, r] * LapseRatePerKm + noise[q, r];

                // Air holds more moisture when warm; cold air is relatively dry in polar deserts
                float hum = baseHumidity[q, r] + aridity;
                if (temp < -10f && !isWater[q, r]) hum -= 8f;
                hum = Mathf.Clamp(hum, 5f, 100f);

                tiles[q, r] = new TileClimate
                {
                    TemperatureC = temp,
                    Humidity     = hum,
                    O2Percent    = global.O2Percent * (1f + o2Factor[q, r]),
                    Co2Ppm       = global.Co2Ppm    * (1f + co2Factor[q, r]),
                };
                float wgt = areaWeight[q, r];
                sumT += temp * wgt;
                sumH += hum * wgt;
                sumW += wgt;
            }

            // Re-centre temperature so the area-weighted tile average equals the global mean exactly
            float shift = global.TemperatureC - (float)(sumT / sumW);
            for (int r = 0; r < h; r++)
            for (int q = 0; q < w; q++)
            {
                var t = tiles[q, r];
                t.TemperatureC += shift;
                t.Zone = Classify(t.TemperatureC, t.Humidity, isWater[q, r]);
                tiles[q, r] = t;
            }

            global.Humidity = (float)(sumH / sumW);
            Global = global;
            Updated?.Invoke();
        }

        // Simplified Köppen-style zone from annual mean temperature and relative humidity
        public static ClimateZone Classify(float tempC, float humidity, bool water)
        {
            if (water)
            {
                if (tempC < -1.8f) return ClimateZone.SeaIce;
                if (tempC < 5f)    return ClimateZone.PolarOcean;
                if (tempC < 20f)   return ClimateZone.TemperateOcean;
                return ClimateZone.TropicalOcean;
            }
            if (tempC < -10f) return ClimateZone.IceCap;
            if (tempC < -2f)  return ClimateZone.Tundra;
            if (humidity < 35f) return tempC >= 18f ? ClimateZone.HotDesert : ClimateZone.ColdDesert;
            if (humidity < 45f) return ClimateZone.Steppe;
            if (tempC >= 22f) return humidity >= 70f ? ClimateZone.TropicalRainforest : ClimateZone.TropicalSavanna;
            if (tempC >= 14f) return humidity >= 60f ? ClimateZone.HumidSubtropical : ClimateZone.Mediterranean;
            if (tempC >= 6f)  return humidity >= 70f ? ClimateZone.Oceanic : ClimateZone.Continental;
            return ClimateZone.Boreal;
        }

        public static string ZoneName(ClimateZone zone) => zone switch
        {
            ClimateZone.TropicalRainforest => "Tropical rainforest",
            ClimateZone.TropicalSavanna    => "Tropical savanna",
            ClimateZone.HotDesert          => "Hot desert",
            ClimateZone.ColdDesert         => "Cold desert",
            ClimateZone.Steppe             => "Steppe",
            ClimateZone.HumidSubtropical   => "Humid subtropical",
            ClimateZone.Mediterranean      => "Mediterranean",
            ClimateZone.Oceanic            => "Temperate oceanic",
            ClimateZone.Continental        => "Temperate continental",
            ClimateZone.Boreal             => "Boreal (subarctic)",
            ClimateZone.Tundra             => "Tundra",
            ClimateZone.IceCap             => "Ice cap",
            ClimateZone.TropicalOcean      => "Tropical ocean",
            ClimateZone.TemperateOcean     => "Temperate ocean",
            ClimateZone.PolarOcean         => "Polar ocean",
            ClimateZone.SeaIce             => "Sea ice",
            _                              => zone.ToString(),
        };

        // ---------- Helpers ----------

        // Hex steps from each cell to the nearest water cell (multi-source BFS)
        private int[,] WaterDistances(int w, int h)
        {
            var dist  = new int[w, h];
            var queue = new Queue<HexCell>();
            for (int r = 0; r < h; r++)
            for (int q = 0; q < w; q++)
            {
                var cell = grid.GetCell(q, r);
                bool water = cell.Terrain != null && cell.Terrain.IsWater;
                dist[q, r] = water ? 0 : int.MaxValue;
                if (water) queue.Enqueue(cell);
            }
            while (queue.Count > 0)
            {
                var cell = queue.Dequeue();
                var (cq, cr) = cell.Coordinates.ToOffsetCoordinates();
                foreach (var nb in grid.GetNeighbors(cell))
                {
                    var (nq, nr) = nb.Coordinates.ToOffsetCoordinates();
                    if (dist[nq, nr] <= dist[cq, cr] + 1) continue;
                    dist[nq, nr] = dist[cq, cr] + 1;
                    queue.Enqueue(nb);
                }
            }
            for (int r = 0; r < h; r++)
            for (int q = 0; q < w; q++)
                if (dist[q, r] == int.MaxValue) dist[q, r] = 12; // no water on the map at all
            return dist;
        }

        private static float Mean(float[,] values, float[,] weights)
        {
            double sum = 0, total = 0;
            for (int i = 0; i < values.GetLength(0); i++)
            for (int j = 0; j < values.GetLength(1); j++)
            {
                sum   += values[i, j] * weights[i, j];
                total += weights[i, j];
            }
            return (float)(sum / total);
        }

        private static void CenterOnZero(float[,] values, float[,] weights)
        {
            float mean = Mean(values, weights);
            for (int i = 0; i < values.GetLength(0); i++)
            for (int j = 0; j < values.GetLength(1); j++)
                values[i, j] -= mean;
        }

        private static float Hash01(int x, int y, int salt)
        {
            unchecked
            {
                uint hsh = (uint)(x * 73856093) ^ (uint)(y * 19349663) ^ (uint)(salt * 83492791);
                hsh ^= hsh >> 13; hsh *= 0x5bd1e995; hsh ^= hsh >> 15;
                return (hsh & 0xFFFFFF) / (float)0xFFFFFF;
            }
        }
    }
}
