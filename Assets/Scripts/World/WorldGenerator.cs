using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    public static class WorldGenerator
    {
        public static void Generate(HexCell[,] cells, int width, int height, int seed)
        {
            var terrains = new Dictionary<TerrainKind, TerrainType>();
            foreach (var t in Resources.LoadAll<TerrainType>("Terrains"))
                terrains[t.kind] = t;

            if (terrains.Count == 0)
            {
                Debug.LogWarning("[WorldGenerator] No terrain assets found in Resources/Terrains.");
                return;
            }

            var rng   = new System.Random(seed);
            Vector3 RandomOffset() => new((float)rng.NextDouble() * 1000f, (float)rng.NextDouble() * 1000f, (float)rng.NextDouble() * 1000f);
            var eOff = RandomOffset();
            var mOff = RandomOffset();
            var fOff = RandomOffset();
            var rOff = RandomOffset();
            const float scale       = 0.16f; // continent-sized elevation/moisture blobs
            const float ridgeScale  = 0.16f; // mountain ranges
            const float forestScale = 0.35f; // finer than climate noise → patchy woods, not one huge forest

            // Pass 1: raw noise per cell (index = r * width + q)
            int n = width * height;
            var rawE = new float[n];
            var rawM = new float[n];
            var rawF = new float[n];
            var rawR = new float[n];
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                int i = r * width + q;
                // Position around the map's east–west loop (odd rows sit half a column right)
                float around = (q + 0.5f * (r & 1)) / width;
                // fBm elevation (5 octaves), sinking toward the poles so the top/bottom rows are sea
                float cy = (r / (float)(height - 1) - 0.5f) * 2f;
                rawE[i] = FBm(OnCylinder(around, r, width, scale) + eOff, 5) - Mathf.Pow(Mathf.Abs(cy), 3f) * 0.3f;
                rawM[i] = FBm(OnCylinder(around, r, width, scale) + mOff, 4);
                rawF[i] = FBm(OnCylinder(around, r, width, forestScale) + fOff, 3);
                rawR[i] = RidgedFBm(OnCylinder(around, r, width, ridgeScale) + rOff, 4);
            }

            // Pass 2: replace raw noise with ranks (0..1), so every threshold below is a share of
            // the map rather than a noise value. Land/mountain proportions then hold for any map
            // size and don't depend on Perlin noise's narrow, octave-averaged range.
            var all  = new List<int>(n);
            for (int i = 0; i < n; i++) all.Add(i);
            var e = Rank(rawE, all);
            var m = Rank(rawM, all);
            var f = Rank(rawF, all);

            var land = all.FindAll(i => e[i] >= WaterThreshold);
            // Ruggedness: ridged noise, nudged toward high ground so ranges favour the interior
            var ridge = new float[n];
            foreach (int i in land) ridge[i] = rawR[i] + 0.3f * e[i];
            var rugged = Rank(ridge, land);
            var landE  = Rank(rawE, land);

            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                int i = r * width + q;
                bool isLand = e[i] >= WaterThreshold;
                int level   = isLand ? ToElevationLevel(landE[i], rugged[i]) : 0;

                // Temperature: hot at equator (center row), cold at poles and altitude
                float lat  = Mathf.Abs(r / (float)(height - 1) - 0.5f) * 2f;
                float temp = Mathf.Clamp01(1f - lat * 0.9f - level / (float)MaxElevation * 0.3f);

                var kind = ClassifyTerrain(e[i], rugged[i], m[i], temp);
                if (terrains.TryGetValue(kind, out var terrain))
                    cells[q, r].SetTerrain(terrain);
                cells[q, r].SetElevation(level);
                cells[q, r].SetFeature(ChooseFeature(kind, m[i], temp, f[i]));
            }

            Debug.Log($"[WorldGenerator] Generated world (seed={seed}).");
        }

        public const int MaxElevation = 10;

        // Shares of the map (elevation rank) and of the land (ruggedness rank)
        const float SaltWaterThreshold = 0.37f; // lowest 37% of cells: open sea
        const float WaterThreshold     = 0.45f; // next 8%: shallow/fresh water; the rest is land
        const float HillThreshold      = 0.62f; // most rugged 38% of land is hills or mountains…
        const float MountainThreshold  = 0.80f; // …and the top 20% of land is mountains

        const float TropicalTemp = 0.68f; // warmer than this is the tropical belt

        // Terrace bands: lowland 1–4 (by elevation), hills 5–7 and mountains 8–10 (by ruggedness)
        public const int MountainElevation = 8;

        static int ToElevationLevel(float landElevation, float rugged)
        {
            if (rugged > MountainThreshold) return Band(MountainElevation, 3, Mathf.InverseLerp(MountainThreshold, 1f, rugged));
            if (rugged > HillThreshold)     return Band(5, 3, Mathf.InverseLerp(HillThreshold, MountainThreshold, rugged));
            return Band(1, 4, landElevation);
        }

        static int Band(int lowest, int levels, float t) => lowest + Mathf.Min(levels - 1, Mathf.FloorToInt(t * levels));

        // Rank of values[i] among `indices`, scaled to 0..1 (other entries stay 0). Ties break by index.
        static float[] Rank(float[] values, List<int> indices)
        {
            var result = new float[values.Length];
            var sorted = new List<int>(indices);
            sorted.Sort((a, b) => values[a] != values[b] ? values[a].CompareTo(values[b]) : a.CompareTo(b));
            float denom = Mathf.Max(1, sorted.Count - 1);
            for (int k = 0; k < sorted.Count; k++) result[sorted[k]] = k / denom;
            return result;
        }

        // Forests grow on moist, not-too-cold land; f is patchiness noise (both ranks).
        // Conifers take the cold end (tundra edge, high latitudes, altitude).
        static TerrainFeature ChooseFeature(TerrainKind kind, float m, float temp, float f)
        {
            switch (kind)
            {
                case TerrainKind.Rainforest when f > 0.2f:                           return TerrainFeature.Jungle;
                case TerrainKind.Wetland    when temp > TropicalTemp && f > 0.55f:    return TerrainFeature.Jungle;
                case TerrainKind.FreshWater when temp > 0.6f && f > 0.55f:           return TerrainFeature.Reef;
                case TerrainKind.Desert     when f > 0.93f:                          return TerrainFeature.Oasis;
                case TerrainKind.Mountain   when f > 0.94f:                          return TerrainFeature.Volcano;
            }

            bool forested = kind switch
            {
                TerrainKind.Plain   => m > 0.50f && f > 0.45f,
                TerrainKind.Hill    => m > 0.40f && f > 0.50f,
                TerrainKind.Wetland => f > 0.55f,
                TerrainKind.Tundra  => m > 0.50f && f > 0.50f,
                _                   => false,
            };
            if (!forested) return TerrainFeature.None;
            return kind == TerrainKind.Tundra || temp < 0.45f ? TerrainFeature.ConiferForest : TerrainFeature.BroadleafForest;
        }

        // Noise sample point for a cell: the map is rolled into a cylinder whose circumference
        // is `width` cells, so noise matches up where the east and west edges meet.
        // `scale` keeps the same feature size as sampling a flat grid at (col, row) * scale.
        static Vector3 OnCylinder(float around, int row, int width, float scale)
        {
            float angle  = around * Mathf.PI * 2f;
            float radius = width * scale / (Mathf.PI * 2f);
            return new Vector3(Mathf.Cos(angle) * radius, row * scale, Mathf.Sin(angle) * radius);
        }

        // Fractal Brownian Motion: sum octaves at doubling frequency, halving amplitude (0..1)
        static float FBm(Vector3 p, int octaves)
        {
            float val = 0f, amp = 0.5f, freq = 1f, max = 0f;
            for (int o = 0; o < octaves; o++)
            {
                val  += (PerlinNoise3D.Sample(p.x * freq, p.y * freq, p.z * freq) * 0.5f + 0.5f) * amp;
                max  += amp;
                amp  *= 0.5f;
                freq *= 2f;
            }
            return val / max;
        }

        // Ridged multifractal: 1 - |noise| folds each octave into sharp crests, which read as
        // mountain chains instead of round blobs.
        static float RidgedFBm(Vector3 p, int octaves)
        {
            float val = 0f, amp = 0.5f, freq = 1f, max = 0f;
            for (int o = 0; o < octaves; o++)
            {
                float ridge = 1f - Mathf.Abs(PerlinNoise3D.Sample(p.x * freq, p.y * freq, p.z * freq));
                val  += ridge * ridge * amp;
                max  += amp;
                amp  *= 0.5f;
                freq *= 2f;
            }
            return val / max;
        }

        // Whittaker biome classification: elevation rank drives water, ruggedness drives
        // mountain/hill, then temperature × moisture drive lowland biomes. All inputs are ranks.
        static TerrainKind ClassifyTerrain(float e, float rugged, float m, float temp)
        {
            // Water
            if (e < SaltWaterThreshold) return TerrainKind.SaltWater;
            if (e < WaterThreshold)     return TerrainKind.FreshWater;

            // High, rugged terrain overrides climate
            if (rugged > MountainThreshold) return temp < 0.20f ? TerrainKind.IceSheet : TerrainKind.Mountain;
            if (rugged > HillThreshold)     return TerrainKind.Hill;

            // Lowland: Whittaker biome (temperature × moisture)
            if (temp < 0.15f) return TerrainKind.IceSheet;
            if (temp < 0.28f) return TerrainKind.Tundra;
            if (temp > TropicalTemp)
            {
                if (m < 0.18f) return TerrainKind.Desert;
                if (m < 0.42f) return TerrainKind.Savanna;
                if (m > 0.88f) return TerrainKind.Wetland;
                if (m > 0.62f) return TerrainKind.Rainforest;
                return TerrainKind.Plain;
            }
            if (m < 0.15f) return TerrainKind.Desert; // cold desert
            if (m < 0.35f) return TerrainKind.Steppe;
            if (m > 0.82f) return TerrainKind.Wetland;
            return TerrainKind.Plain;
        }
    }
}
