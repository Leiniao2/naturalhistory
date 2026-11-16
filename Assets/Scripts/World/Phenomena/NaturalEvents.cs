using System;
using System.Collections.Generic;
using NaturalHistory.Climate;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.World
{
    public enum Phenomenon
    {
        Meteor,
        Eruption,
        Tornado,
        Sandstorm,
        Blizzard,
        Flood,
        Rockslide,
        Earthquake,
        Tsunami,
        GlacierCalving,
        Avalanche,
    }

    // Rare natural events: now and then, as a turn begins, one plays out on a suitable tile near
    // where the camera is looking (so the player sees it) and is announced. Each kind needs the
    // right ground and climate: tornadoes on open temperate lowland, sandstorms in deserts,
    // blizzards where it is freezing, floods along big rivers, eruptions at volcanoes, tsunamis on
    // low coasts... They are purely visual for now; Occurred lets other systems react later.
    public class NaturalEvents : MonoBehaviour
    {
        private const float ChancePerTurn = 0.35f; // that some event happens this turn
        private const float EffectSeconds = 14f;

        // Testing the animations: an event every few seconds, taking each kind in turn (the next
        // one with somewhere to happen near the camera), and one at every turn. Off for real play.
        public static bool TestMode = false;

        // Random events at the start of each turn. Off for now: events come only from the admin
        // panel's Trigger (or TestMode).
        public static bool AutoEvents = false;
        private const float TestInterval = 6f;
        private float nextTest;
        private int nextTestKind;

        public static NaturalEvents Instance { get; private set; }

        // Message for the player (e.g. a toast) and the tile it happened on
        public static event Action<string, HexCell> Announced;
        public event Action<Phenomenon, HexCell> Occurred;

        public static readonly string[] Names =
        {
            "Meteor fall", "Volcanic eruption", "Tornado", "Sandstorm", "Blizzard", "Flood",
            "Rockslide", "Earthquake", "Tsunami", "Glacier calving", "Avalanche",
        };

        // How often each kind is picked when it has somewhere to happen
        private static readonly float[] Weights = { 0.5f, 1.4f, 1f, 1f, 1f, 1f, 1f, 0.8f, 0.5f, 0.8f, 0.9f };

        private HexGrid grid;
        private System.Random rng;
        private Vector3 wind;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<NaturalEvents>() != null) return;
            var go = new GameObject("NaturalPhenomena");
            go.AddComponent<NaturalEvents>();
            go.AddComponent<AmbientWater>();
        }

        private void Awake() => Instance = this;

        private void Start()
        {
            grid = HexGrid.Instance;
            rng  = new System.Random(Environment.TickCount);
            float a = (float)rng.NextDouble() * Mathf.PI * 2f;
            wind = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
            if (TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin += OnTurnBegin;
        }

        // Felt in the layer below the surface too; everything else happens on the surface only
        public static bool ReachesUnderground(Phenomenon kind) => kind == Phenomenon.Earthquake;

        private void OnDestroy()
        {
            if (TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin -= OnTurnBegin;
            if (Instance == this) Instance = null;
        }

        private void Update()
        {
            if (!TestMode || grid == null || !grid.IsGenerated || Time.time < nextTest) return;
            nextTest = Time.time + TestInterval;
            var sites = SitesNearCamera(1.5f);
            for (int i = 0; i < Names.Length; i++)
            {
                int k = (nextTestKind + i) % Names.Length;
                if (sites[k].Count == 0) continue;
                if (UnderView.On && !ReachesUnderground((Phenomenon)k)) continue; // it wouldn't show
                nextTestKind = k + 1;
                Play((Phenomenon)k, sites[k][rng.Next(Mathf.Min(3, sites[k].Count))]);
                return;
            }
        }

        private void OnTurnBegin(int turn)
        {
            if (turn <= 1 || grid == null || !grid.IsGenerated) return;
            if (!AutoEvents && !TestMode) return;
            if (!TestMode && rng.NextDouble() >= ChancePerTurn) return;
            // the wind veers a little from turn to turn
            wind = Quaternion.Euler(0f, (float)(rng.NextDouble() * 60.0 - 30.0), 0f) * wind;

            var sites = SitesNearCamera(1f);
            float total = 0f;
            for (int k = 0; k < sites.Length; k++) if (sites[k].Count > 0) total += Weight(k);
            if (total <= 0f) return;
            float pick = (float)rng.NextDouble() * total;
            for (int k = 0; k < sites.Length; k++)
            {
                if (sites[k].Count == 0) continue;
                pick -= Weight(k);
                if (pick > 0f) continue;
                Play((Phenomenon)k, sites[k][rng.Next(sites[k].Count)]);
                return;
            }
        }

        // How likely each kind is this turn: eruptions and meteors follow the geological record
        // (more during large igneous provinces and impact showers, see EarthHistory)
        private float Weight(int k)
        {
            float ma = AgeManager.Instance != null ? AgeManager.Instance.MillionYearsAgo : 0f;
            return (Phenomenon)k switch
            {
                Phenomenon.Eruption => Weights[k] * EarthHistory.Volcanism(ma),
                Phenomenon.Meteor   => Weights[k] * EarthHistory.MeteorRate(ma),
                _                   => Weights[k],
            };
        }

        // Plays `kind` on the nearest suitable tile to the camera (admin / testing). False if there is none.
        public bool Trigger(Phenomenon kind)
        {
            if (grid == null || !grid.IsGenerated) return false;
            var sites = SitesNearCamera(1f)[(int)kind];
            if (sites.Count == 0) sites = SitesNearCamera(4f)[(int)kind];
            if (sites.Count == 0) { Announced?.Invoke(Loc.F("No place for a {0} near here", InSentence(Loc.T(Names[(int)kind]))), null); return false; }
            Play(kind, sites[rng.Next(Mathf.Min(3, sites.Count))]);
            return true;
        }

        // A (translated) name used mid-sentence: lower case, except in German, which capitalises nouns
        private static string InSentence(string name) => Loc.Current == "de" ? name : name.ToLower();

        // Candidate tiles per kind within the camera's view (scaled by `reach`), nearest first.
        private List<HexCell>[] SitesNearCamera(float reach)
        {
            var sites = new List<HexCell>[Names.Length];
            for (int k = 0; k < sites.Length; k++) sites[k] = new List<HexCell>();
            if (!PhenomenaUtil.CameraFocus(out var focus, out float radius)) return sites;
            radius *= reach * PhenomenaUtil.CellSize(grid);

            var near = new List<(HexCell cell, float d)>();
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var c = grid.GetCell(q, r);
                if (c == null || c.Terrain == null) continue;
                var p = c.transform.position;
                float d = new Vector2(p.x - focus.x, p.z - focus.z).magnitude;
                if (d <= radius) near.Add((c, d));
            }
            near.Sort((a, b) => a.d.CompareTo(b.d));
            foreach (var (c, _) in near)
                for (int k = 0; k < sites.Length; k++)
                    if (Suits((Phenomenon)k, c)) sites[k].Add(c);
            return sites;
        }

        private float Temperature(HexCell c) =>
            ClimateSystem.Instance != null && ClimateSystem.Instance.HasData ? ClimateSystem.Instance.Get(c).TemperatureC : 12f;

        private bool Suits(Phenomenon kind, HexCell c)
        {
            bool land = PhenomenaUtil.IsLand(c);
            var t = c.Terrain.kind;
            switch (kind)
            {
                case Phenomenon.Meteor:     return true;
                case Phenomenon.Eruption:   return c.Feature == TerrainFeature.Volcano;
                case Phenomenon.Tornado:
                    return land && !c.IsMountain && t is TerrainKind.Plain or TerrainKind.Savanna or TerrainKind.Steppe or TerrainKind.FernPrairie
                           && Temperature(c) is > 4f and < 30f;
                case Phenomenon.Sandstorm:  return land && (t == TerrainKind.Desert || t == TerrainKind.Barren && c.Moisture < 0.4f);
                case Phenomenon.Blizzard:
                    return land && (t is TerrainKind.Tundra or TerrainKind.IceSheet || Temperature(c) < -3f);
                case Phenomenon.Flood:
                    return land && !c.IsMountain && (c.Floodplain || c.HasRiver && c.RiverFlow >= 3 || t is TerrainKind.Wetland or TerrainKind.CoalSwamp);
                case Phenomenon.Rockslide:
                    return land && (c.IsMountain || t == TerrainKind.Hill) && !Snowy(c) && LowerNeighbor(c, 2) != null;
                case Phenomenon.Avalanche:
                    return land && c.IsMountain && Snowy(c) && LowerNeighbor(c, 1) != null;
                case Phenomenon.Earthquake: return land;
                case Phenomenon.Tsunami:    return PhenomenaUtil.IsSea(c) && LowCoast(c) != null;
                case Phenomenon.GlacierCalving:
                    return land && t == TerrainKind.IceSheet && SeaNeighbor(c) != null;
            }
            return false;
        }

        private bool Snowy(HexCell c) => c.Terrain.kind == TerrainKind.IceSheet || Temperature(c) < 2f;

        private HexCell LowerNeighbor(HexCell c, int drop)
        {
            HexCell best = null;
            foreach (var n in grid.GetNeighbors(c))
                if (PhenomenaUtil.IsLand(n) && n.Elevation <= c.Elevation - drop && (best == null || n.Elevation < best.Elevation)) best = n;
            return best;
        }

        private HexCell LowCoast(HexCell sea)
        {
            foreach (var n in grid.GetNeighbors(sea))
                if (PhenomenaUtil.IsLand(n) && n.Elevation < PhenomenaUtil.CliffElevation) return n;
            return null;
        }

        private HexCell SeaNeighbor(HexCell c)
        {
            foreach (var n in grid.GetNeighbors(c)) if (PhenomenaUtil.IsSea(n)) return n;
            return null;
        }

        private void Play(Phenomenon kind, HexCell c)
        {
            var go = new GameObject($"Phenomenon_{kind}");
            go.transform.SetParent(c.transform, false);
            int seed = rng.Next();
            var local = Quaternion.Inverse(c.transform.rotation) * wind;
            float seconds = EffectSeconds;
            PhenomenonFx fx;
            switch (kind)
            {
                case Phenomenon.Meteor:     fx = Add<MeteorFx>(go, m => m.wind = local); seconds = 7f; break;
                case Phenomenon.Eruption:   fx = Add<EruptionFx>(go, e => e.wind = local); seconds = 16f; break;
                case Phenomenon.Tornado:    fx = Add<TornadoFx>(go, e => e.wind = local); break;
                case Phenomenon.Sandstorm:  fx = Add<SandstormFx>(go, e => e.wind = local); break;
                case Phenomenon.Blizzard:   fx = Add<BlizzardFx>(go, e => e.wind = local); break;
                case Phenomenon.Flood:      fx = Add<FloodFx>(go, e => { e.area = FloodArea(c); e.flow = Downstream(c); }); seconds = 16f; break;
                case Phenomenon.Rockslide:  fx = Add<SlideFx>(go, e => { e.toward = LowerNeighbor(c, 2); e.snow = false; }); seconds = 9f; break;
                case Phenomenon.Avalanche:  fx = Add<SlideFx>(go, e => { e.toward = LowerNeighbor(c, 1); e.snow = true; }); seconds = 10f; break;
                case Phenomenon.Earthquake: fx = Add<EarthquakeFx>(go, e => e.area = grid.GetCellsInRange(c, 1)); seconds = 8f; break;
                case Phenomenon.Tsunami:
                    var coast = LowCoast(c);
                    fx = Add<TsunamiFx>(go, e => { e.coast = coast; e.flooded = LowLandAround(coast); });
                    seconds = 16f;
                    break;
                default:                    fx = Add<CalvingFx>(go, e => e.sea = SeaNeighbor(c)); break;
            }
            fx.Begin(grid, c, seconds, seed);

            string where = InSentence(EraFlora.DisplayName(c.Terrain.kind));
            string msg = kind switch
            {
                Phenomenon.Meteor         => c.IsWater ? Loc.T("A meteor plunges into the water!") : Loc.F("A meteor strikes the {0}!", where),
                Phenomenon.Eruption       => Loc.T("A volcano erupts!"),
                Phenomenon.Tornado        => Loc.F("A tornado tears across the {0}", where),
                Phenomenon.Sandstorm      => Loc.T("A sandstorm sweeps the desert"),
                Phenomenon.Blizzard       => Loc.F("A blizzard rages over the {0}", where),
                Phenomenon.Flood          => Loc.T("A river bursts its banks"),
                Phenomenon.Rockslide      => Loc.T("A rockslide thunders down the slope"),
                Phenomenon.Earthquake     => Loc.T("An earthquake shakes the land"),
                Phenomenon.Tsunami        => Loc.T("A tsunami strikes the coast!"),
                Phenomenon.GlacierCalving => Loc.T("Ice breaks away from the glacier front"),
                _                         => Loc.T("An avalanche roars down the mountain"),
            };
            Debug.Log($"[NaturalEvents] {kind} at {c}");
            Announced?.Invoke(msg, c);
            Occurred?.Invoke(kind, c);
        }

        private static T Add<T>(GameObject go, Action<T> setup) where T : PhenomenonFx
        {
            var fx = go.AddComponent<T>();
            setup(fx);
            return fx;
        }

        // The flooded tile and its neighbours along the same river, floodplain or wetland that lie no higher
        private List<HexCell> FloodArea(HexCell c)
        {
            var area = new List<HexCell> { c };
            foreach (var n in grid.GetNeighbors(c))
                if (PhenomenaUtil.IsLand(n) && !n.IsMountain && n.Elevation <= c.Elevation &&
                    (n.HasRiver || n.Floodplain || n.Terrain.kind is TerrainKind.Wetland or TerrainKind.CoalSwamp))
                    area.Add(n);
            return area;
        }

        private Vector3 Downstream(HexCell c)
        {
            if (c.RiverOut >= 0) return PhenomenaUtil.EdgeDirection(c.RiverOut);
            return wind;
        }

        private List<HexCell> LowLandAround(HexCell coast)
        {
            var list = new List<HexCell>();
            if (coast == null) return list;
            list.Add(coast);
            foreach (var n in grid.GetNeighbors(coast))
                if (PhenomenaUtil.IsLand(n) && n.Elevation <= Mathf.Max(coast.Elevation, 2) && !n.IsMountain) list.Add(n);
            return list;
        }
    }
}
