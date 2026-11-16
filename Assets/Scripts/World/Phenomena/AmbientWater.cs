using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace NaturalHistory.World
{
    // Water that is always moving, shown around wherever the camera looks: crests rising, curling
    // over and breaking on the open sea, scalloped lines of foam running up beaches and drawing back,
    // waves bursting into spray against sea cliffs, and waterfalls where a river drops off a cliff
    // or a steep step. Bursts are pooled and animated from this one Update; waterfalls are built
    // when they come into view and removed when far away. Purely visual.
    public class AmbientWater : MonoBehaviour
    {
        private const float ScanInterval    = 0.5f;  // seconds between looks at what is in view
        private const float WhitecapPerTile = 0.05f; // whitecaps per second per open-sea tile in view
        private const float ShoreWaveEvery  = 4.5f;  // seconds between waves on each beach edge
        private const float CliffWaveEvery  = 3.5f;  // seconds between waves on each cliff edge
        private const int   MaxBursts       = 120;
        private const int   PuffsPerBurst   = 8;

        private enum Kind { Whitecap, ShoreWave, CliffWave }

        private struct Shore
        {
            public HexCell sea, land;
            public bool cliff;
        }

        // A pooled wave: one shaped sheet (crest or foam line) and a few foam/spray puffs
        private class Burst
        {
            public GameObject root;
            public Transform sheet;
            public MeshFilter sheetFilter;
            public MeshRenderer sheetRenderer;
            public Transform[] puffs;
            public MeshRenderer[] puffRenderers;
            public Kind kind;
            public float start, life;
            public HexCell cell;
            public Vector3 at, dir, across;   // tile space of `cell`
            public float sea, top, length;    // water surface, (cliffs) land height, (lines) length along the shore
            public float seed;
        }

        private static readonly int ColorId = Shader.PropertyToID("_Color");

        private HexGrid grid;
        private Material material;
        private MaterialPropertyBlock block;
        private readonly System.Random rng = new(1234);
        private float s;
        private Vector3 wind = new(1f, 0f, 0.3f);

        private readonly List<HexCell> openSea = new();
        private readonly List<Shore> shores = new();
        private readonly List<(HexCell cell, int edge)> falls = new();

        private readonly List<int> seaInView = new(), beachInView = new(), cliffInView = new();
        private readonly Dictionary<int, WaterfallFx> fallsShown = new();
        // Waterfalls not built yet, nearest the camera first. They are built a couple per frame
        // after the map changes and then kept (hidden out of view), so none has to be built at the
        // moment it scrolls into view.
        private readonly List<int> fallsPending = new();
        private const int FallsPerFrame = 2;
        private readonly List<Burst> active = new(), pool = new();
        private float nextScan, whitecapDue, beachDue, cliffDue;

        private void Start()
        {
            grid = HexGrid.Instance;
            if (grid == null) return;
            material = Resources.Load<Material>("Materials/MapFeatures");
            block = new MaterialPropertyBlock();
            wind.Normalize();
            grid.Generated      += Rebuild;
            grid.TerrainChanged += Rebuild;
            if (grid.IsGenerated) Rebuild();
        }

        private void OnDestroy()
        {
            if (grid == null) return;
            grid.Generated      -= Rebuild;
            grid.TerrainChanged -= Rebuild;
        }

        // Finds the open sea, the coast edges (beach or cliff) and the waterfalls of the current map.
        private void Rebuild()
        {
            openSea.Clear(); shores.Clear(); falls.Clear();
            foreach (var w in fallsShown.Values) if (w != null) Destroy(w.gameObject);
            fallsShown.Clear();
            foreach (var b in active) Recycle(b);
            active.Clear();
            if (grid == null || !grid.IsGenerated) return;
            s = PhenomenaUtil.CellSize(grid);

            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var c = grid.GetCell(q, r);
                if (c == null || c.Terrain == null) continue;
                var n = PhenomenaUtil.EdgeNeighbors(grid, c);
                if (PhenomenaUtil.IsSea(c))
                {
                    bool coastal = false;
                    for (int e = 0; e < 6; e++)
                    {
                        if (!PhenomenaUtil.IsLand(n[e])) continue;
                        coastal = true;
                        shores.Add(new Shore { sea = c, land = n[e], cliff = n[e].Elevation >= PhenomenaUtil.CliffElevation });
                    }
                    if (!coastal) openSea.Add(c);
                }
                else if (PhenomenaUtil.IsLand(c) && c.RiverOut >= 0)
                {
                    // a river that leaves a cliffed coast into the sea or a lake, or drops steeply inland
                    var down = n[c.RiverOut];
                    if (down == null || down.Terrain == null) continue;
                    if (down.IsWater ? c.Elevation >= PhenomenaUtil.CliffElevation : c.Elevation - down.Elevation >= HexGrid.FallLevels)
                        falls.Add((c, c.RiverOut));
                }
            }
            fallsPending.Clear();
            for (int i = 0; i < falls.Count; i++) fallsPending.Add(i);
            if (PhenomenaUtil.CameraFocus(out var focus, out _))
                fallsPending.Sort((a, b) => FlatDistance(falls[a].cell, focus).CompareTo(FlatDistance(falls[b].cell, focus)));
            nextScan = 0f;
            Debug.Log($"[AmbientWater] {openSea.Count} open-sea tiles, {shores.Count} coast edges, {falls.Count} waterfalls");
        }

        private static float FlatDistance(HexCell c, Vector3 focus)
        {
            var p = c.transform.position;
            return (p.x - focus.x) * (p.x - focus.x) + (p.z - focus.z) * (p.z - focus.z);
        }

        private WaterfallFx BuildFall(int i)
        {
            fallsPending.Remove(i);
            var go = new GameObject("Waterfall");
            go.transform.SetParent(falls[i].cell.transform, false);
            var w = go.AddComponent<WaterfallFx>();
            w.edge = falls[i].edge;
            w.Begin(grid, falls[i].cell, float.PositiveInfinity, i * 7919);
            fallsShown[i] = w;
            return w;
        }

        private void Update()
        {
            if (grid == null || !grid.IsGenerated || material == null) return;
            // build the remaining waterfalls in the background, hidden until they come into view
            for (int k = 0; k < FallsPerFrame && fallsPending.Count > 0; k++)
                BuildFall(fallsPending[0]).gameObject.SetActive(false);
            // waves are on the surface: none in the Underground view (waterfalls hide themselves)
            if (UnderView.On)
            {
                foreach (var b in active) Recycle(b);
                active.Clear();
                whitecapDue = beachDue = cliffDue = 0f;
                return;
            }
            float now = Time.time;
            if (now >= nextScan) { nextScan = now + ScanInterval; Scan(); }

            // new bursts at a steady rate for what is in view
            float dt = Time.deltaTime;
            whitecapDue += dt * Mathf.Min(seaInView.Count * WhitecapPerTile, 10f);
            // no foam lines along beaches: the land runs into the water without a white edge
            beachDue     = 0f;
            cliffDue    += dt * Mathf.Min(cliffInView.Count / CliffWaveEvery, 10f);
            while (whitecapDue >= 1f) { whitecapDue -= 1f; if (seaInView.Count > 0) SpawnWhitecap(openSea[seaInView[rng.Next(seaInView.Count)]]); }
            while (beachDue >= 1f)    { beachDue -= 1f;    if (beachInView.Count > 0) SpawnWave(shores[beachInView[rng.Next(beachInView.Count)]]); }
            while (cliffDue >= 1f)    { cliffDue -= 1f;    if (cliffInView.Count > 0) SpawnWave(shores[cliffInView[rng.Next(cliffInView.Count)]]); }

            for (int i = active.Count - 1; i >= 0; i--)
            {
                var b = active[i];
                float u = (now - b.start) / b.life;
                if (u >= 1f || b.cell == null) { Recycle(b); active.RemoveAt(i); continue; }
                switch (b.kind)
                {
                    case Kind.Whitecap:  AnimateWhitecap(b, u); break;
                    case Kind.ShoreWave: AnimateShoreWave(b, u); break;
                    default:             AnimateCliffWave(b, u); break;
                }
            }
        }

        // What lies within view of the camera, and which waterfalls to show
        private void Scan()
        {
            seaInView.Clear(); beachInView.Clear(); cliffInView.Clear();
            if (!PhenomenaUtil.CameraFocus(out var focus, out float radius)) return;
            float r2 = radius * s * radius * s;
            bool Near(HexCell c)
            {
                var p = c.transform.position;
                float dx = p.x - focus.x, dz = p.z - focus.z;
                return dx * dx + dz * dz <= r2;
            }
            for (int i = 0; i < openSea.Count; i++) if (Near(openSea[i])) seaInView.Add(i);
            for (int i = 0; i < shores.Count; i++)
                if (Near(shores[i].sea)) (shores[i].cliff ? cliffInView : beachInView).Add(i);

            for (int i = 0; i < falls.Count; i++)
            {
                // built ones are kept and just switched on and off (out of view they don't animate)
                bool near = FlatDistance(falls[i].cell, focus) <= r2 * 2.25f; // a margin past the view, so they're on before they show
                bool built = fallsShown.TryGetValue(i, out var fx) && fx != null;
                if (near && !built) fx = BuildFall(i);
                if (fx != null && fx.gameObject.activeSelf != near) fx.gameObject.SetActive(near);
            }
        }

        // ---- Bursts

        private MeshRenderer NewRenderer(Transform parent, string name, Mesh mesh, out Transform t, out MeshFilter filter)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            filter = go.AddComponent<MeshFilter>();
            filter.sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = material;
            mr.shadowCastingMode = ShadowCastingMode.Off;
            mr.receiveShadows = false;
            t = go.transform;
            return mr;
        }

        private Burst Take(HexCell cell, Kind kind, float life)
        {
            if (active.Count >= MaxBursts) return null;
            Burst b;
            if (pool.Count > 0) { b = pool[pool.Count - 1]; pool.RemoveAt(pool.Count - 1); }
            else
            {
                b = new Burst { root = new GameObject("WaterBurst"), puffs = new Transform[PuffsPerBurst] };
                b.puffRenderers = new MeshRenderer[PuffsPerBurst];
                b.sheetRenderer = NewRenderer(b.root.transform, "Sheet", WaterMeshes.Crest, out b.sheet, out b.sheetFilter);
                for (int i = 0; i < PuffsPerBurst; i++)
                    b.puffRenderers[i] = NewRenderer(b.root.transform, "Foam", PhenomenonFx.Puff, out b.puffs[i], out _);
            }
            b.root.SetActive(true);
            b.root.transform.SetParent(cell.transform, false);
            b.root.transform.localPosition = Vector3.zero;
            b.sheetFilter.sharedMesh = kind == Kind.Whitecap ? WaterMeshes.Crest : WaterMeshes.FoamLine;
            b.kind  = kind;
            b.cell  = cell;
            b.start = Time.time;
            b.life  = life;
            b.seed  = (float)rng.NextDouble() * 100f;
            active.Add(b);
            return b;
        }

        private void Recycle(Burst b)
        {
            if (b.root == null) return;
            b.root.SetActive(false);
            b.root.transform.SetParent(transform, false);
            b.cell = null;
            pool.Add(b);
        }

        private void Place(Transform t, MeshRenderer mr, Vector3 pos, Vector3 scale, Color color, Quaternion rotation)
        {
            bool visible = scale.x > 1e-4f && scale.y > 1e-4f && scale.z > 1e-4f;
            mr.enabled = visible;
            if (!visible) return;
            t.localPosition = pos;
            t.localScale    = scale;
            t.localRotation = rotation;
            block.SetColor(ColorId, color);
            mr.SetPropertyBlock(block);
        }

        private void Puff(Burst b, int i, Vector3 pos, Vector3 scale, Color color) =>
            Place(b.puffs[i], b.puffRenderers[i], pos, scale, color, Quaternion.Euler(0f, b.seed * 37f + i * 53f, 0f));

        private void HidePuffs(Burst b, int from)
        {
            for (int i = from; i < PuffsPerBurst; i++) b.puffRenderers[i].enabled = false;
        }

        private float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);

        private static readonly Color Foam      = new Color(1.25f, 1.3f, 1.35f) * PhenomenonFx.PuffBoost;
        private static readonly Color Spray     = new Color(1.3f, 1.35f, 1.4f) * PhenomenonFx.PuffBoost;
        private static readonly Color SheetFoam = new(1.02f, 1.04f, 1.06f); // the sheets' vertex colours are already the colours asked for

        private void SpawnWhitecap(HexCell sea)
        {
            var b = Take(sea, Kind.Whitecap, R(2.4f, 3.4f));
            if (b == null) return;
            b.at     = new Vector3(R(-0.55f, 0.55f), 0f, R(-0.55f, 0.55f)) * s;
            b.dir    = Quaternion.Euler(0f, R(-25f, 25f), 0f) * wind;
            b.across = Vector3.Cross(Vector3.up, b.dir);
            b.sea    = sea.SurfaceHeight;
            b.length = R(0.1f, 0.18f) * s;
        }

        private void SpawnWave(Shore shore)
        {
            var b = Take(shore.sea, shore.cliff ? Kind.CliffWave : Kind.ShoreWave, shore.cliff ? R(2.6f, 3.2f) : R(3.6f, 4.6f));
            if (b == null) return;
            var d = PhenomenaUtil.Offset(grid, shore.sea, shore.land);
            b.dir    = d.normalized;
            b.across = Vector3.Cross(Vector3.up, b.dir);
            b.at     = d * 0.5f + b.across * R(-0.15f, 0.15f) * s; // the shoreline, somewhere along the edge
            b.sea    = shore.sea.SurfaceHeight;
            b.top    = grid.GroundHeight(shore.sea, b.at + b.dir * 0.06f * s);
            b.length = R(0.34f, 0.5f) * s;
        }

        private Quaternion Facing(Burst b) => Quaternion.LookRotation(b.dir, Vector3.up);

        // A swell rises, its crest curls forward and whitens, breaks into a spill of foam that
        // spreads and sinks back into the sea
        private void AnimateWhitecap(Burst b, float u)
        {
            float rise  = Ramp(u, 0f, 0.4f);
            float fall  = Ramp(u, 0.45f, 1f);
            float h     = rise * (1f - fall) * 0.05f * s;         // crest height
            float lenK  = Mathf.Lerp(0.6f, 1.1f, rise) + 0.3f * fall;
            var c = b.at + b.dir * u * 0.14f * s;
            Place(b.sheet, b.sheetRenderer, c + Vector3.up * b.sea, new Vector3(b.length * lenK, Mathf.Max(h, 0f), b.length * 0.32f), SheetFoam, Facing(b));

            // the spill: foam tumbling off the front of the crest once it breaks, spreading flat
            for (int i = 0; i < 4; i++)
            {
                float k = Ramp(u, 0.35f + i * 0.05f, 0.6f + i * 0.05f) * (1f - Ramp(u, 0.75f, 1f));
                float l = (i - 1.5f) / 1.5f * b.length * 0.7f * lenK;
                var p = c + b.dir * (0.02f + 0.03f * k) * s + b.across * l;
                p.y = b.sea + 0.003f * s;
                float size = (0.025f + 0.02f * Mathf.Sin(b.seed + i * 2.1f) * 0.5f) * s * k;
                Puff(b, i, p, new Vector3(size * 1.5f, size * 0.22f, size), Foam);
            }
            HidePuffs(b, 4);
        }

        // A scalloped line of foam rushes up the beach, slows and spreads, then draws back thinning,
        // leaving a few patches of bubbles that fade on the wet sand
        private void AnimateShoreWave(Burst b, float u)
        {
            float run   = u < 0.5f ? Mathf.Lerp(-0.3f, 0.06f, 1f - (1f - u / 0.5f) * (1f - u / 0.5f)) // rushes in, slowing
                                   : Mathf.Lerp(0.06f, -0.12f, Mathf.SmoothStep(0f, 1f, (u - 0.5f) / 0.5f));
            float thick = Mathf.Lerp(0.04f, 0.09f, Ramp(u, 0f, 0.5f)) * (1f - Ramp(u, 0.55f, 1f)) * s;
            float lenK  = Mathf.Lerp(0.8f, 1.05f, Ramp(u, 0f, 0.5f));
            var c = b.at + b.dir * run * s;
            float front = Mathf.Max(b.sea, grid.GroundHeight(b.cell, c + b.dir * thick)) ;
            float back  = Mathf.Max(b.sea, grid.GroundHeight(b.cell, c));
            c.y = back + 0.003f * s;
            // tilt the sheet to lie along the beach slope
            var slope = Quaternion.LookRotation(b.dir * Mathf.Max(thick, 1e-4f) + Vector3.up * (front - back), Vector3.up);
            Place(b.sheet, b.sheetRenderer, c, new Vector3(b.length * lenK, 0.02f * s, thick), SheetFoam, slope);

            // bubbles left behind as the water draws back
            for (int i = 0; i < 5; i++)
            {
                float k = Ramp(u, 0.5f, 0.62f) * (1f - Ramp(u, 0.75f + i * 0.04f, 1f));
                float l = (i - 2f) / 2f * b.length * 0.45f + Mathf.Sin(b.seed + i) * 0.04f * s;
                var p = b.at + b.dir * (0.03f + 0.02f * Mathf.Sin(b.seed * 3f + i)) * s + b.across * l;
                p.y = Mathf.Max(b.sea, grid.GroundHeight(b.cell, p)) + 0.003f * s;
                float size = 0.022f * s * k;
                Puff(b, i, p, new Vector3(size * 1.4f, size * 0.2f, size), Foam);
            }
            HidePuffs(b, 5);
        }

        // A wave rolls in, breaks against the cliff foot in a low burst of spray that falls back, and
        // a ring of foam spreads out from the foot: only a little livelier than surf on a beach, so
        // the splash stays near the waterline whatever the height of the cliff.
        private void AnimateCliffWave(Burst b, float u)
        {
            float rise = Mathf.Min(0.07f * s, Mathf.Max(b.top - b.sea, 0.03f * s) * 0.25f);
            const float hit = 0.32f;

            // the incoming swell, then the foam spreading back out from the foot
            Vector3 c; float h, thick;
            if (u < hit)
            {
                float k = u / hit;
                c = b.at - b.dir * Mathf.Lerp(0.32f, 0.03f, k * k) * s;
                h = Mathf.Lerp(0.015f, 0.04f, k) * s;
                thick = 0.05f * s;
            }
            else
            {
                float k = (u - hit) / (1f - hit);
                c = b.at - b.dir * Mathf.Lerp(0.03f, 0.14f, Mathf.Sqrt(k)) * s;
                h = 0.012f * s * (1f - k);
                thick = Mathf.Lerp(0.06f, 0.12f, k) * s * (1f - Ramp(k, 0.6f, 1f));
            }
            c.y = b.sea;
            Place(b.sheet, b.sheetRenderer, c, new Vector3(b.length * 0.8f, h, thick), SheetFoam,
                  u < hit ? Facing(b) : Quaternion.LookRotation(-b.dir, Vector3.up));

            // spray: thrown up the face in a fan, each drop on its own arc, falling back and spreading
            for (int i = 0; i < PuffsPerBurst; i++)
            {
                float t = (u - hit - i * 0.012f) / (1f - hit);
                if (t <= 0f || t >= 1f) { b.puffRenderers[i].enabled = false; continue; }
                float j = (i / (PuffsPerBurst - 1f)) * 2f - 1f;          // -1..1 across the fan
                float up = rise * (0.7f + 0.45f * (1f - Mathf.Abs(j)) + 0.15f * Mathf.Sin(b.seed + i * 1.3f));
                float height = up * 4f * t * (1f - t);
                var p = b.at - b.dir * (0.02f + 0.05f * t) * s + b.across * j * (0.05f + 0.08f * t) * s;
                p.y = b.sea + 0.008f * s + height;
                float size = (0.02f + 0.03f * t) * s * (1f - Ramp(t, 0.6f, 1f));
                Puff(b, i, p, Vector3.one * size, Spray);
            }
        }

        private static float Ramp(float x, float a, float b) => Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(a, b, x));
    }

    // Shared shapes for moving water: all built once, white/blue vertex colours, sized ~1.
    public static class WaterMeshes
    {
        private static Mesh crest, foamLine;

        // A breaking wave crest along x (-1..1): a ridge whose top leans forward (+z) into a curl,
        // blue-green at the foot, white along the crest. Height 1 at the middle, tapering to the ends.
        public static Mesh Crest => crest ??= Ridge("WaveCrest",
            new[] { new Vector2(-0.9f, 0f), new Vector2(-0.45f, 0.45f), new Vector2(-0.05f, 0.85f), new Vector2(0.3f, 1f),
                    new Vector2(0.55f, 0.82f), new Vector2(0.5f, 0.55f), new Vector2(0.75f, 0f) },
            new[] { 0.15f, 0.35f, 0.75f, 1f, 1f, 0.85f, 0.55f });

        // A line of beach foam along x (-1..1), z 0..1 with a scalloped front edge; a thin lip.
        public static Mesh FoamLine => foamLine ??= CreateFoamLine();

        private static readonly Color WaterBlue = new(0.36f, 0.62f, 0.72f);
        private static readonly Color White     = new(0.97f, 0.98f, 1f);

        // Extrudes a (z, y) profile along x with the height tapering to 0 at both ends; `white` per
        // profile point blends the water colour into foam.
        private static Mesh Ridge(string name, Vector2[] profile, float[] white)
        {
            const int segs = 16;
            var verts = new List<Vector3>(); var cols = new List<Color>(); var tris = new List<int>();
            int pn = profile.Length;
            for (int i = 0; i <= segs; i++)
            {
                float x = i / (float)segs * 2f - 1f;
                float taper = Mathf.Sqrt(Mathf.Max(0f, 1f - x * x));
                float wob = 1f + 0.12f * Mathf.Sin(x * 7.3f) + 0.06f * Mathf.Sin(x * 17f);
                for (int k = 0; k < pn; k++)
                {
                    var p = profile[k];
                    verts.Add(new Vector3(x, p.y * taper * wob, p.x * (0.5f + 0.5f * taper)));
                    cols.Add(Color.Lerp(WaterBlue, White, white[k]));
                }
                if (i == 0) continue;
                int a = (i - 1) * pn, b = i * pn;
                for (int k = 0; k < pn - 1; k++)
                {
                    tris.Add(a + k); tris.Add(a + k + 1); tris.Add(b + k);
                    tris.Add(a + k + 1); tris.Add(b + k + 1); tris.Add(b + k);
                }
            }
            return Finish(name, verts, cols, tris);
        }

        private static Mesh CreateFoamLine()
        {
            const int segs = 28;
            var verts = new List<Vector3>(); var cols = new List<Color>(); var tris = new List<int>();
            // rows across the line: back (thin, bluish), middle, raised lip, front edge
            float[] zs = { 0f, 0.55f, 0.85f, 1f };
            float[] ys = { 0f, 0.4f, 1f, 0.15f };
            float[] wh = { 0.45f, 0.8f, 1f, 1f };
            for (int i = 0; i <= segs; i++)
            {
                float x = i / (float)segs * 2f - 1f;
                float taper = Mathf.Sqrt(Mathf.Max(0f, 1f - x * x));
                float scallop = 1f + 0.22f * Mathf.Sin(x * 9.1f) + 0.12f * Mathf.Sin(x * 23.7f + 1f);
                for (int k = 0; k < zs.Length; k++)
                {
                    float z = zs[k] * scallop * (0.35f + 0.65f * taper);
                    verts.Add(new Vector3(x, ys[k] * taper, z));
                    cols.Add(Color.Lerp(WaterBlue, White, wh[k]));
                }
                if (i == 0) continue;
                int a = (i - 1) * zs.Length, b = i * zs.Length;
                for (int k = 0; k < zs.Length - 1; k++)
                {
                    tris.Add(a + k); tris.Add(a + k + 1); tris.Add(b + k);
                    tris.Add(a + k + 1); tris.Add(b + k + 1); tris.Add(b + k);
                }
            }
            return Finish("FoamLine", verts, cols, tris);
        }

        private static Mesh Finish(string name, List<Vector3> verts, List<Color> cols, List<int> tris)
        {
            var mesh = new Mesh { name = name, hideFlags = HideFlags.DontSave };
            mesh.SetVertices(verts);
            mesh.SetColors(cols);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }
    }

    // A river pouring off a cliff or a steep step, shown as a grand set piece in the style of a
    // natural wonder: a horseshoe of layered rock pushed out over the lower ground, with mossy crags
    // rising on either side; the river spreading into a wide brink of rapids across its top; a
    // broad curtain arcing over the lip (Waterfall.shader: foam streaks racing down and breaking up
    // toward the foot); a churning plunge pool ringed with boulders; mist rolling up out of it and a
    // faint rainbow in the spray. Lives as long as AmbientWater keeps it.
    public class WaterfallFx : PhenomenonFx
    {
        public int edge;                     // the edge the river leaves by
        private Part rock, brink, curtain, pool, rainbow;
        private Part[] mist, veil, boulders;
        private Vector3[] boulderAt;
        private Vector3 dir, across, poolMid, impact;
        private float halfW, riverHalf, top, foot, drop, lipD, recess, poolAlong, poolAcross;
        private Color ground; // the upper tile's ground colour: the rock either side is cut from it
        // The ground colours of the land tiles beside it (alpha 0: none, or the tile downstream), which
        // the rock blends into where it runs over their edge, as the tiles' textures blend there
        private readonly Color[] sideGround = new Color[6];
        private bool intoWater;
        private readonly List<Mesh> built = new();
        private static Material waterMaterial;

        // How far the rock runs out beside the water (in half-widths) and how high its crags rise
        // (× the usual), separately for each side (−x, +x): real falls are lopsided, a tall crag on
        // one bank and a low shoulder on the other.
        private float reachL, reachR, cragL, cragR, cragSeed;

        // How much moss and grass grows on the rock in the displayed period (0 before land plants)
        private float greenery = 1f;

        private static readonly Color WaterDeep  = new(0.14f, 0.42f, 0.48f, 1f);
        private static readonly Color WaterBlue  = new(0.27f, 0.56f, 0.64f, 0.92f);
        private static readonly Color WaterPale  = new(0.55f, 0.76f, 0.82f, 0.9f);
        private static readonly Color StoneDark  = new(0.40f, 0.31f, 0.25f);
        private static readonly Color StoneLight = new(0.70f, 0.58f, 0.44f);
        private static readonly Color StoneGrey  = new(0.52f, 0.50f, 0.48f);
        private static readonly Color Moss       = new(0.30f, 0.46f, 0.20f);
        private static readonly Color MistWhite  = new(0.96f, 0.98f, 1f);

        protected override void Build()
        {
            dir    = PhenomenaUtil.EdgeDirection(edge);
            across = Vector3.Cross(Vector3.up, dir);
            greenery = grid.DisplayedAge switch
            {
                <= NaturalHistory.Core.GeologicalAge.Ordovician => 0f,
                NaturalHistory.Core.GeologicalAge.Silurian      => 0.25f,
                NaturalHistory.Core.GeologicalAge.Devonian      => 0.6f,
                _                                               => 1f,
            };
            float a = s * 0.8660254f;
            var down = PhenomenaUtil.EdgeNeighbors(grid, cell)[edge];
            intoWater = down != null && down.IsWater;

            riverHalf = Mathf.Max(grid.RiverHalfWidth(cell), 0.03f * s);
            halfW  = Mathf.Max(Mathf.Clamp(0.2f + 0.018f * cell.RiverFlow, 0.21f, 0.36f) * s, riverHalf * 1.1f); // the brink spreads wider than the river
            // the banks spread a little over half way along the tile edge on each side
            reachL = R(0.52f, 0.7f) * s / halfW;
            reachR = R(0.52f, 0.7f) * s / halfW;
            // ...but only onto land at about the same height: over water or lower ground the bank
            // would hang off its edge as a slanted sheet, so on that side it stays within this tile.
            // +across (reachR) is the side of edge + 1, -across (reachL) that of edge + 5.
            var beside = PhenomenaUtil.EdgeNeighbors(grid, cell);
            float own = 0.48f * s / halfW;
            if (!LevelLand(beside[(edge + 1) % 6])) reachR = Mathf.Min(reachR, own);
            if (!LevelLand(beside[(edge + 5) % 6])) reachL = Mathf.Min(reachL, own);
            cragL  = R(0.25f, 0.7f);
            cragR  = Mathf.Abs(cragL - 0.45f) < 0.12f ? R(0.25f, 0.35f) : R(0.25f, 0.7f); // keep the sides a little different
            cragSeed = R(0f, 100f);
            recess = 0.1f * s;                                   // the middle of the lip lies further back
            lipD   = a * 0.9f;                                  // just inside the tile edge, where it steps down (to the sea, or to lower land: HexGrid.IsFallStep)
            top    = Ground(dir * a * 0.3f) + 0.004f * s;        // the upper tile's flat top
            bool LevelLand(HexCell n) => n != null && n.Terrain != null && !n.IsWater && n.SurfaceHeight >= cell.SurfaceHeight - 0.05f * s;
            foot   = intoWater ? Ground(dir * a * 1.4f) : Ground(dir * (lipD + 0.3f * s));
            drop   = Mathf.Max(top - foot, 0.08f * s);
            poolAlong  = 0.24f * s;
            poolAcross = halfW * 1.3f;
            poolMid = dir * (lipD + 0.02f * s + poolAlong * 0.85f) + Vector3.up * (foot + (intoWater ? 0.004f : 0.01f) * s);
            impact  = dir * (lipD + Throw) + Vector3.up * poolMid.y;

            waterMaterial ??= Resources.Load<Material>("Materials/Waterfall");
            ground  = GroundColour(cell);
            for (int e = 0; e < 6; e++)
            {
                var n = beside[e];
                sideGround[e] = e == edge || n == null || n.Terrain == null || n.IsWater ? Color.clear : GroundColour(n);
            }
            rock    = AddPart(Keep(BuildRock()), "FallRock");
            brink   = AddPart(Keep(BuildBrink()), waterMaterial, "Brink");
            curtain = AddPart(Keep(BuildCurtain()), waterMaterial, "FallSheet");
            pool    = AddPart(Keep(BuildPool()), waterMaterial, "PlungePool");
            rainbow = AddGlowPart(Keep(BuildRainbow()), "Rainbow");
            mist    = AddSmoke(14, "Mist");
            veil    = AddSmoke(6, "Spray");

            // boulders around the pool (leaving the outflow clear) and tumbled at the foot of the crags
            boulders  = new Part[11];
            boulderAt = new Vector3[11];
            for (int i = 0; i < boulders.Length; i++)
            {
                boulders[i] = AddPart(Rock(i + (int)(R(0f, 8f))), "Boulder");
                Vector3 p;
                if (i < 8)
                {
                    // round the two sides: not under the curtain (upstream) nor in the outflow (downstream)
                    float th = (i < 4 ? Mathf.Lerp(0.72f, 1.2f, i / 3f) : Mathf.Lerp(1.8f, 2.28f, (i - 4) / 3f)) * Mathf.PI + R(-0.06f, 0.06f);
                    p = poolMid + across * Mathf.Cos(th) * poolAcross * 1.05f + dir * Mathf.Sin(th) * poolAlong * 1.08f;
                }
                else
                {
                    float side = i % 2 == 0 ? 1f : -1f;
                    p = dir * (Lip(side * 1.25f) + R(0.02f, 0.08f) * s) + across * side * halfW * R(1.15f, 1.5f);
                }
                p.y = Ground(p) - 0.004f * s;
                boulderAt[i] = p;
            }
        }

        private Mesh Keep(Mesh m) { built.Add(m); return m; }

        private void OnDestroy()
        {
            foreach (var m in built) if (m != null) Destroy(m); // built for this fall only
        }

        // Where the rock's top and the brink begin, as a share of the way out to the tile edge: close
        // to the edge, so the brink is short along the flow (about a quarter of the tile)
        private const float BackAlong = 0.85f;

        // Distance out along `dir` of the lip at x half-widths across (a horseshoe: the middle further back)
        private float Lip(float x) => lipD + recess * (Mathf.Min(x * x, 1.4f) - 1f);

        private float Throw => 0.03f * s + 0.18f * drop; // how far out the falling sheet carries

        // ---- The rock: a faceted mass, flat on top under the brink, rising into crags at the sides
        //      and dropping as a sheer, layered wall to the foot

        // Rock surface builder: vertices at the same spot are shared (separately for the front and
        // back faces), so normals and colours are smooth across the rock instead of a facet mosaic
        private sealed class Facets
        {
            private readonly List<Vector3> verts = new();
            private readonly List<Vector3> normals = new();
            private readonly List<int> tris = new();
            private readonly Dictionary<(Vector3Int, bool), int> index = new();
            private readonly System.Func<Vector3, Vector3, Color> paint;
            private readonly float weld;
            public Facets(System.Func<Vector3, Vector3, Color> paint, float weld) { this.paint = paint; this.weld = weld; }

            // both faces
            public void Tri(Vector3 a, Vector3 b, Vector3 c)
            {
                Add(a, b, c, false);
                Add(a, c, b, true);
            }

            public void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d) { Tri(a, b, c); Tri(a, c, d); }

            private void Add(Vector3 a, Vector3 b, Vector3 c, bool back)
            {
                var n = Vector3.Cross(b - a, c - a); // area-weighted
                if (n.sqrMagnitude < 1e-14f) return;
                tris.Add(Vertex(a, back, n));
                tris.Add(Vertex(b, back, n));
                tris.Add(Vertex(c, back, n));
            }

            private int Vertex(Vector3 p, bool back, Vector3 n)
            {
                var key = (Vector3Int.RoundToInt(p / weld), back);
                if (!index.TryGetValue(key, out int i))
                {
                    i = verts.Count;
                    index[key] = i;
                    verts.Add(p);
                    normals.Add(Vector3.zero);
                }
                normals[i] += n;
                return i;
            }

            public Mesh ToMesh(string name)
            {
                var cols = new Color[verts.Count];
                for (int i = 0; i < verts.Count; i++)
                {
                    normals[i] = normals[i].sqrMagnitude > 0f ? normals[i].normalized : Vector3.up;
                    cols[i] = paint(verts[i], normals[i]);
                }
                var mesh = new Mesh { name = name, indexFormat = IndexFormat.UInt32 };
                mesh.SetVertices(verts);
                mesh.SetNormals(normals);
                mesh.SetColors(cols);
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateBounds();
                return mesh;
            }
        }

        // The colour a tile's ground shows, as the terrain shader paints it: the average of the tile's
        // own ground texture (the region's surface, HexCell.SetSurface — not the shared material's),
        // repainted in its sand/soil colour (SetGroundLook) and times its terrain tint and per-tile
        // jitter. Read from the cell rather than its renderer, so a highlight or the under view
        // (which swaps the tile's material) doesn't colour the rock.
        private static readonly Dictionary<Texture, Color> textureAverage = new();
        private static Color GroundColour(HexCell c)
        {
            if (c == null) return StoneLight;
            var tex = c.BlendTexture;
            var avg = tex != null ? Average(tex) : StoneLight;
            var recolor = c.GroundRecolor;
            if (recolor.w > 0f) avg = Color.Lerp(avg, new Color(recolor.x, recolor.y, recolor.z), recolor.w);
            var col = avg * c.BlendTint;
            col.a = 1f;
            return col;
        }

        // The ground colour under a point of the rock: this tile's, blending into a neighbour's across
        // the last stretch before their shared edge (half and half on the edge itself), as the
        // tiles' textures do
        private Color GroundAt(Vector3 p)
        {
            float a = s * 0.8660254f, blend = 0.14f * s;
            var c = ground;
            for (int e = 0; e < 6; e++)
            {
                if (sideGround[e].a <= 0f) continue;
                var d = PhenomenaUtil.EdgeDirection(e);
                float inside = a - (p.x * d.x + p.z * d.z); // distance in from that edge (negative past it)
                float t = Mathf.Clamp01(0.5f - inside / (2f * blend));
                if (t > 0f) c = Color.Lerp(c, sideGround[e], t);
            }
            return c;
        }

        private static Color Average(Texture tex)
        {
            if (textureAverage.TryGetValue(tex, out var c)) return c;
            const int n = 32;
            var rt = RenderTexture.GetTemporary(n, n, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            var prev = RenderTexture.active;
            Graphics.Blit(tex, rt);
            RenderTexture.active = rt;
            var read = new Texture2D(n, n, TextureFormat.RGBA32, false);
            read.ReadPixels(new Rect(0, 0, n, n), 0, 0);
            RenderTexture.active = prev;
            RenderTexture.ReleaseTemporary(rt);
            var sum = Vector4.zero;
            foreach (var p in read.GetPixels()) sum += (Vector4)p;
            Object.Destroy(read);
            c = (Color)(sum / (n * n));
            textureAverage[tex] = c;
            return c;
        }

        private float Jitter(Vector3 p, float seed) =>
            Mathf.PerlinNoise(p.x / s * 7.3f + seed + cell.Coordinates.Q * 1.7f, p.z / s * 7.3f - seed + cell.Coordinates.R * 1.3f) * 2f - 1f;

        private Color PaintRock(Vector3 p, Vector3 n)
        {
            float h = (p.y - foot) / drop;
            // horizontal strata of light and dark sandstone, wavering a little
            // in the upper tile's own ground colour (red desert rock in a desert, and so on): its top
            // as the ground, its faces a little darker, in soft horizontal strata
            // (the strata and the darkening only on the faces: the flat tops are exactly the ground's colour)
            float band = Mathf.Sin(p.y / s * 60f + Jitter(p, 3.1f) * 1.4f) * 0.5f + 0.5f;
            float flat = Ramp(n.y, 0.55f, 0.9f);
            var c = GroundAt(p);
            c *= Mathf.Lerp(Mathf.Lerp(0.8f, 1.05f, band * 0.8f + 0.2f * Mathf.Clamp01(h)) * 0.85f, 1f, flat);
            c *= 1f + 0.06f * Jitter(p, 5.3f) * (1f - flat);
            float x = Mathf.Abs(Vector3.Dot(p, across)) / halfW;
            if (x < 1.05f && n.y < 0.5f) c *= 0.62f;
            c.a = 1f;
            return c;
        }

        private float RockTop(float x, float f)
        {
            float ax    = Mathf.Abs(x);
            float reach = x < 0f ? reachL : reachR;
            float side  = x < 0f ? cragL : cragR;
            // an irregular skyline (not mirrored), dying away into the ground at the outer end
            float rough = 0.55f + 0.45f * Mathf.PerlinNoise(x * 2.3f + cragSeed, f * 1.7f + (x < 0f ? 0f : 31f));
            // rises gently from the water's edge, so the banks read as ground rather than walls
            float crag  = (0.03f * s + drop * 0.2f) * side * rough * Ramp(ax, 1.05f, Mathf.Lerp(1.05f, reach, 0.45f)) * (1f - Ramp(ax, Mathf.Lerp(1.05f, reach, 0.6f), reach));
            float shelf = ax < 1.02f ? -0.004f * s : 0f;
            return top + shelf + crag * Mathf.Lerp(0.55f, 1f, f);
        }

        private Mesh BuildRock()
        {
            const int cols = 56, rows = 12, wall = 16;
            float back   = s * 0.8660254f * BackAlong;
            float bottom = foot - 0.04f * s;
            var fx = new Facets(PaintRock, 0.0005f * s);
            var g = new Vector3[cols + 1, rows + 1];       // top surface, back (0) to lip (rows)
            var w = new Vector3[cols + 1, wall + 1];       // the face, top (0) to foot (wall)
            for (int c = 0; c <= cols; c++)
            {
                float x = Mathf.Lerp(-reachL, reachR, c / (float)cols);
                // away from the water the rock settles onto the terrain, ending just below it, so the
                // banks merge into the ground instead of ending in walls; their front edge follows
                // the tile's edge rather than jutting out over the lower ground like the brink
                float merge = Ramp(Mathf.Abs(x), 1.1f, (x < 0f ? reachL : reachR) * 0.9f);
                float lipX  = Mathf.Lerp(Lip(x), s * 0.8660254f, merge * 0.85f);
                for (int r = 0; r <= rows; r++)
                {
                    float f = r / (float)rows;
                    float d = Mathf.Lerp(back, lipX, f);
                    var p = dir * d + across * x * halfW;
                    if (r > 0 && r < rows) p += (dir * Jitter(p, 2f) + across * Jitter(p, 4f)) * 0.012f * s;
                    p.y = RockTop(x, f) + (Mathf.Abs(x) > 1.02f ? Jitter(p, 6f) * 0.012f * s : 0f);
                    p.y = Mathf.Lerp(p.y, Ground(p) - 0.006f * s, merge);
                    g[c, r] = p;
                }
                // the face drops to the foot of the fall beside the water, but only to the ground in
                // front of it out on the merged banks
                var front = g[c, rows] + dir * 0.05f * s;
                float faceBottom = Mathf.Lerp(bottom, Ground(front) - 0.01f * s, merge);
                for (int k = 0; k <= wall; k++)
                {
                    float f = k / (float)wall;
                    var p = g[c, rows];
                    p.y = Mathf.Lerp(p.y, faceBottom, f);
                    // rugged, slightly undercut behind the water, buttressed out at the sides
                    float out_ = (Mathf.Abs(x) < 1.02f ? -0.03f : 0.025f * (x < 0f ? cragL : cragR)) * s * Mathf.Sin(f * Mathf.PI * 0.9f);
                    p += dir * (out_ + (k > 0 ? Jitter(p, 9f) * 0.02f * s : 0f));
                    w[c, k] = p;
                }
            }
            for (int c = 0; c < cols; c++)
            {
                for (int r = 0; r < rows; r++) fx.Quad(g[c, r], g[c, r + 1], g[c + 1, r + 1], g[c + 1, r]);
                for (int k = 0; k < wall; k++) fx.Quad(w[c, k], w[c, k + 1], w[c + 1, k + 1], w[c + 1, k]);
                // the back sinks into the upper ground
                var b0 = g[c, 0]; var b1 = g[c + 1, 0];
                fx.Quad(b0, b1, new Vector3(b1.x, top - 0.05f * s, b1.z), new Vector3(b0.x, top - 0.05f * s, b0.z));
            }
            // the two ends: the banks have settled into the ground there, so just a short skirt below
            // it (dropping all the way to the foot showed as a wall wherever the ground falls away)
            foreach (int c in new[] { 0, cols })
                for (int r = 0; r < rows; r++)
                {
                    Vector3 a0 = g[c, r], a1 = g[c, r + 1];
                    float y0 = Mathf.Min(a0.y, Ground(a0) - 0.03f * s), y1 = Mathf.Min(a1.y, Ground(a1) - 0.03f * s);
                    fx.Quad(a0, a1, new Vector3(a1.x, y1, a1.z), new Vector3(a0.x, y0, a0.z));
                }
            return fx.ToMesh("WaterfallRock");
        }

        // ---- Water meshes (Waterfall.shader): colour, uv (across, along the flow) and uv2 (foam, speed)

        private sealed class WaterMesh
        {
            public readonly List<Vector3> v = new();
            public readonly List<Color> c = new();
            public readonly List<Vector2> uv = new(), uv2 = new();
            public readonly List<int> tris = new();

            public void Add(Vector3 p, Color col, Vector2 flow, float foam, float speed)
            {
                v.Add(p); c.Add(col); uv.Add(flow); uv2.Add(new Vector2(Mathf.Clamp01(foam), speed));
            }

            // a grid of (cols + 1) x (rows + 1) vertices added row by row from `start`
            public void Grid(int start, int cols, int rows)
            {
                for (int r = 0; r < rows; r++)
                for (int k = 0; k < cols; k++)
                {
                    int a = start + r * (cols + 1) + k, b = a + cols + 1;
                    tris.Add(a); tris.Add(b); tris.Add(a + 1);
                    tris.Add(a + 1); tris.Add(b); tris.Add(b + 1);
                }
            }

            public Mesh ToMesh(string name)
            {
                var mesh = new Mesh { name = name, indexFormat = IndexFormat.UInt32 };
                mesh.SetVertices(v);
                mesh.SetColors(c);
                mesh.SetUVs(0, uv);
                mesh.SetUVs(1, uv2);
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateNormals();
                mesh.RecalculateBounds();
                return mesh;
            }
        }

        // The river widening over the flat top of the rock into a broad brink, roughening toward the lip
        private Mesh BuildBrink()
        {
            const int cols = 12, rows = 10;
            float back = s * 0.8660254f * BackAlong;
            var m = new WaterMesh();
            for (int r = 0; r <= rows; r++)
            {
                float f = r / (float)rows;
                float hw = Mathf.Lerp(riverHalf, halfW * 1.02f, Ramp(f, 0f, 0.7f));
                for (int k = 0; k <= cols; k++)
                {
                    float x = k / (float)cols * 2f - 1f;
                    float d = Mathf.Lerp(back - 0.02f * s, Lip(x * hw / halfW), f);
                    var p = dir * d + across * x * hw;
                    p.y = top + 0.003f * s - 0.006f * s * f * f;
                    float foam = Ramp(f, 0.45f, 1f) * 0.75f + 0.12f + 0.25f * Mathf.Abs(x) * f;
                    m.Add(p, Color.Lerp(WaterBlue, WaterPale, f * 0.5f), new Vector2(x * hw, d), foam, 0.45f);
                }
            }
            m.Grid(0, cols, rows);
            return m.ToMesh("WaterfallBrink");
        }

        // The sheet pouring over the lip: off the edge nearly level, then falling ever more steeply
        private Mesh BuildCurtain()
        {
            const int cols = 28, rows = 18;
            float bottom = poolMid.y - 0.004f * s;
            float fall = top - bottom;
            var m = new WaterMesh();
            for (int r = 0; r <= rows; r++)
            {
                float f = r / (float)rows;
                for (int k = 0; k <= cols; k++)
                {
                    float x = k / (float)cols * 2f - 1f;
                    // the lip, falling away along a parabola; a slight spread and a ripple across
                    float d = Lip(x) + 0.004f * s + Throw * Mathf.Sqrt(f) + 0.006f * s * Mathf.Sin(x * 9f + f * 3f);
                    var p = dir * d + across * x * halfW * (1f + 0.07f * f);
                    p.y = top - 0.002f * s - fall * f;
                    float edgeFoam = Ramp(Mathf.Abs(x), 0.8f, 1f) * 0.35f;
                    float foam = 0.12f + Ramp(f, 0.5f, 1f) * 0.7f + (1f - Ramp(f, 0f, 0.1f)) * 0.35f + edgeFoam;
                    var col = Color.Lerp(WaterBlue, WaterPale, f * 0.6f);
                    col.a = Mathf.Lerp(0.88f, 0.7f, Ramp(Mathf.Abs(x), 0.85f, 1f));
                    m.Add(p, col, new Vector2(x * halfW, f * (fall + Throw)), foam, 1.7f);
                }
            }
            m.Grid(0, cols, rows);
            return m.ToMesh("WaterfallSheet");
        }

        // A round pool below: white and churning where the curtain lands, deep green-blue beyond it,
        // its foam running outward. Into the sea it is just a field of foam fading into the waves.
        private Mesh BuildPool()
        {
            const int rings = 6, segs = 36;
            var m = new WaterMesh();
            var centre = new Vector3(poolMid.x, 0f, poolMid.z);
            var hit = new Vector3(impact.x, 0f, impact.z);
            for (int r = 0; r <= rings; r++)
            {
                float rho = r / (float)rings;
                for (int k = 0; k <= segs; k++)
                {
                    float th = k / (float)segs * Mathf.PI * 2f;
                    float wob = 1f + 0.08f * Mathf.Sin(th * 3f + cell.Coordinates.Q) * rho;
                    var p = centre + (across * Mathf.Cos(th) * poolAcross + dir * Mathf.Sin(th) * poolAlong) * rho * wob;
                    float near = 1f - Mathf.Clamp01((p - hit).magnitude / (poolAlong * 1.6f));
                    float foam = 0.1f + near * 0.85f + (intoWater ? 0.15f : 0f);
                    var col = Color.Lerp(WaterDeep, WaterBlue, Mathf.Max(rho, near));
                    col.a = intoWater ? (1f - Ramp(rho, 0.55f, 1f)) * 0.85f : Mathf.Lerp(0.96f, 0.85f, rho);
                    p.y = poolMid.y;
                    m.Add(p, col, new Vector2(Vector3.Dot(p - hit, across), (p - hit).magnitude), foam, 0.22f);
                }
            }
            m.Grid(0, segs, rings);
            return m.ToMesh("WaterfallPool");
        }

        // A faint arc of colours standing in the spray in front of the fall (additive)
        private Mesh BuildRainbow()
        {
            const int segs = 28;
            var bands = new[]
            {
                new Color(1f, 0.25f, 0.2f), new Color(1f, 0.6f, 0.15f), new Color(1f, 0.95f, 0.3f),
                new Color(0.35f, 1f, 0.35f), new Color(0.3f, 0.6f, 1f), new Color(0.55f, 0.35f, 1f),
            };
            float radius = halfW * 1.15f, thick = 0.07f * s;
            var centre = poolMid + dir * 0.06f * s;
            var verts = new List<Vector3>(); var cols = new List<Color>(); var normals = new List<Vector3>(); var tris = new List<int>();
            for (int face = 0; face < 2; face++)
            {
                int start = verts.Count;
                for (int k = 0; k <= segs; k++)
                {
                    float f = k / (float)segs;
                    float th = Mathf.Lerp(0.12f, 0.88f, f) * Mathf.PI;
                    float fade = Mathf.Sin(f * Mathf.PI);
                    for (int b = 0; b <= bands.Length; b++)
                    {
                        float rr = radius + thick * (b / (float)bands.Length - 0.5f);
                        verts.Add(centre + across * Mathf.Cos(th) * rr + Vector3.up * Mathf.Sin(th) * rr);
                        var c = bands[Mathf.Min(b, bands.Length - 1)];
                        c.a = fade * (b == 0 || b == bands.Length ? 0f : 1f);
                        cols.Add(c);
                        normals.Add(Vector3.up);
                    }
                }
                int n = bands.Length + 1;
                for (int k = 0; k < segs; k++)
                for (int b = 0; b < bands.Length; b++)
                {
                    int a0 = start + k * n + b, a1 = a0 + n;
                    if (face == 0) { tris.Add(a0); tris.Add(a1); tris.Add(a0 + 1); tris.Add(a0 + 1); tris.Add(a1); tris.Add(a1 + 1); }
                    else           { tris.Add(a0); tris.Add(a0 + 1); tris.Add(a1); tris.Add(a0 + 1); tris.Add(a1 + 1); tris.Add(a1); }
                }
            }
            var mesh = new Mesh { name = "WaterfallRainbow" };
            mesh.SetVertices(verts);
            mesh.SetColors(cols);
            mesh.SetNormals(normals);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        protected override void Animate(float u, float t)
        {
            Show(rock,    Vector3.zero, Vector3.one, Color.white, Quaternion.identity);
            Show(brink,   Vector3.zero, Vector3.one, Color.white, Quaternion.identity);
            Show(curtain, Vector3.zero, Vector3.one, Color.white, Quaternion.identity);
            Show(pool,    Vector3.zero, Vector3.one, Color.white, Quaternion.identity);
            for (int i = 0; i < boulders.Length; i++)
                Show(boulders[i], boulderAt[i], Vector3.one * (i < 8 ? 0.035f : 0.05f) * s * (0.8f + 0.25f * (i % 3)),
                     new Color(0.58f, 0.53f, 0.47f), Quaternion.Euler(0f, i * 47f, 0f));

            float breathe = 0.5f + 0.5f * Mathf.Sin(t * 0.6f);
            Show(rainbow, Vector3.zero, Vector3.one, Color.white, 0.16f + 0.12f * breathe, Quaternion.identity);

            // a low veil of spray hugging the foot of the curtain
            var rot = Quaternion.LookRotation(dir);
            for (int i = 0; i < veil.Length; i++)
            {
                float c = Mathf.Repeat(t / 1.8f + i / (float)veil.Length, 1f);
                float x = ((i % 3) - 1) * 0.6f;
                var p = impact + across * x * halfW + dir * c * 0.08f * s + Vector3.up * (0.015f + c * 0.04f) * s;
                var size = new Vector3(halfW * 0.9f, 0.05f * s, 0.12f * s) * (0.7f + 0.6f * c);
                Show(veil[i], p, size, MistWhite, 0.55f * Mathf.Sin(c * Mathf.PI), rot);
            }
            // mist billowing up out of the pool and drifting away downstream, some rising past the lip
            for (int i = 0; i < mist.Length; i++)
            {
                float c = Mathf.Repeat(t / 4.2f + i / (float)mist.Length, 1f);
                float x = Mathf.Sin(i * 2.39f) * 0.9f;
                var p = impact + across * x * halfW + dir * (0.03f + 0.22f * c) * s
                      + Vector3.up * (c * (drop * 0.9f + 0.12f * s));
                float size = (0.06f + 0.16f * c) * s;
                Show(mist[i], p, size, MistWhite, 0.4f * Mathf.Sin(c * Mathf.PI) * (0.7f + 0.3f * breathe));
            }
        }
    }
}
