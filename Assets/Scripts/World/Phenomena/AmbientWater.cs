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
                    if (down.IsWater ? c.Elevation >= PhenomenaUtil.CliffElevation : c.Elevation - down.Elevation >= 3)
                        falls.Add((c, c.RiverOut));
                }
            }
            nextScan = 0f;
            Debug.Log($"[AmbientWater] {openSea.Count} open-sea tiles, {shores.Count} coast edges, {falls.Count} waterfalls");
        }

        private void Update()
        {
            if (grid == null || !grid.IsGenerated || material == null) return;
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
            beachDue    += dt * Mathf.Min(beachInView.Count / ShoreWaveEvery, 16f);
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
                bool near = Near(falls[i].cell);
                bool shown = fallsShown.TryGetValue(i, out var fx) && fx != null;
                if (near && !shown)
                {
                    var go = new GameObject("Waterfall");
                    go.transform.SetParent(falls[i].cell.transform, false);
                    var w = go.AddComponent<WaterfallFx>();
                    w.edge = falls[i].edge;
                    w.Begin(grid, falls[i].cell, float.PositiveInfinity, i * 7919);
                    fallsShown[i] = w;
                }
                else if (!near && shown)
                {
                    Destroy(fx.gameObject);
                    fallsShown.Remove(i);
                }
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

        // A wave rolls in, slams into the cliff foot and throws a fan of spray up the rock face that
        // falls back, while a ring of foam spreads out from the foot
        private void AnimateCliffWave(Burst b, float u)
        {
            float rise = Mathf.Max(b.top - b.sea, 0.05f * s);
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
                var p = b.at - b.dir * (0.02f + 0.07f * t) * s + b.across * j * (0.06f + 0.1f * t) * s;
                p.y = b.sea + 0.015f * s + height;
                float size = (0.03f + 0.05f * t) * s * (1f - Ramp(t, 0.6f, 1f));
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

    // A river spilling over a cliff or steep step: a curved sheet of water arcing off the lip with
    // streaks pouring down it (River.shader, run fast), a white lip where it tips over, and
    // churning foam rings and rising mist at the foot. Lives as long as AmbientWater keeps it.
    public class WaterfallFx : PhenomenonFx
    {
        public int edge;                     // the edge the river leaves by
        private Part curtain, lipFoam;
        private Part[] mist, churn;
        private Vector3 dir, across, lip, foot;
        private float width, drop;
        private static Material fallMaterial;

        protected override void Build()
        {
            dir    = PhenomenaUtil.EdgeDirection(edge);
            across = Vector3.Cross(Vector3.up, dir);
            float apothem = s * 0.8660254f;
            lip = OnGround(dir * apothem * 0.97f, 0.006f);
            var down = PhenomenaUtil.EdgeNeighbors(grid, cell)[edge];
            if (down != null && down.IsWater) foot = new Vector3(dir.x, 0f, dir.z) * apothem * 1.1f + Vector3.up * down.SurfaceHeight;
            else                              foot = OnGround(dir * apothem * 1.25f);
            width = Mathf.Clamp(0.05f + 0.015f * cell.RiverFlow, 0.06f, 0.18f) * s;
            drop  = Mathf.Max(lip.y - foot.y, 0.03f * s);

            curtain = AddPart(BuildCurtain(), "FallSheet");
            if (fallMaterial == null)
            {
                var river = Resources.Load<Material>("Materials/River");
                if (river != null)
                {
                    fallMaterial = new Material(river) { name = "Waterfall" };
                    fallMaterial.SetFloat("_FlowSpeed", 0.45f);
                    fallMaterial.SetFloat("_Ripple", 0.55f);
                }
            }
            if (fallMaterial != null) curtain.renderer.sharedMaterial = fallMaterial;
            lipFoam = AddPart(WaterMeshes.Crest, "Lip");
            churn   = AddParts(WaterMeshes.FoamLine, 3, "Churn");
            mist    = AddParts(Puff, 6, "Mist");
        }

        // The sheet in this tile's space: rows from the lip down to the foot along a falling arc,
        // widening a little as it falls; both faces, so it shows from any side.
        private Mesh BuildCurtain()
        {
            const int rows = 14, cols = 4;
            var verts = new List<Vector3>(); var colors = new List<Color>(); var uvs = new List<Vector2>(); var tris = new List<int>();
            float throwOut = Mathf.Min(0.05f * s + drop * 0.15f, 0.12f * s);
            for (int r = 0; r <= rows; r++)
            {
                float t = r / (float)rows;
                var centre = lip + dir * throwOut * Mathf.Sqrt(t) + Vector3.Lerp(Vector3.zero, new Vector3(foot.x - lip.x, 0f, foot.z - lip.z) * 0.5f, t * t);
                centre.y = lip.y - drop * t * t;
                float w = width * (1f + 0.25f * t);
                for (int c = 0; c <= cols; c++)
                {
                    float x = c / (float)cols * 2f - 1f;
                    verts.Add(centre + across * x * w + dir * 0.008f * s * Mathf.Sin(x * 3f + t * 5f));
                    // white where it tips over and where it breaks up near the foot, blue between
                    float white = Mathf.Max(1f - t * 4f, Mathf.InverseLerp(0.6f, 1f, t)) * 0.7f + 0.25f * Mathf.Abs(x);
                    var col = Color.Lerp(new Color(0.45f, 0.68f, 0.8f), new Color(0.95f, 0.97f, 1f), Mathf.Clamp01(white));
                    col.a = 1f;
                    colors.Add(col);
                    uvs.Add(new Vector2(c / (float)cols, t * drop * 3f)); // runs down the sheet
                }
                if (r == 0) continue;
                int a = (r - 1) * (cols + 1), b = r * (cols + 1);
                for (int c = 0; c < cols; c++)
                {
                    tris.Add(a + c); tris.Add(b + c); tris.Add(a + c + 1);
                    tris.Add(a + c + 1); tris.Add(b + c); tris.Add(b + c + 1);
                    tris.Add(a + c); tris.Add(a + c + 1); tris.Add(b + c);       // back face
                    tris.Add(a + c + 1); tris.Add(b + c + 1); tris.Add(b + c);
                }
            }
            var mesh = new Mesh { name = "WaterfallSheet" };
            mesh.SetVertices(verts);
            mesh.SetColors(colors);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        private void OnDestroy()
        {
            if (curtain.transform != null) Destroy(curtain.transform.GetComponent<MeshFilter>().sharedMesh); // built for this fall only
        }

        protected override void Animate(float u, float t)
        {
            Show(curtain, Vector3.zero, Vector3.one, Color.white, Quaternion.identity);
            // a smooth white lip, shimmering a little
            float k = 1f + 0.08f * Mathf.Sin(t * 6f);
            Show(lipFoam, lip, new Vector3(width * 1.05f, 0.012f * s * k, 0.025f * s), new Color(1.02f, 1.04f, 1.06f), Quaternion.LookRotation(dir));

            // foam rings spreading out from where it lands, one after another
            var landing = foot + new Vector3(dir.x, 0f, dir.z) * 0.02f * s;
            for (int i = 0; i < churn.Length; i++)
            {
                float c = Mathf.Repeat(t / 1.6f + i / (float)churn.Length, 1f);
                float spread = Mathf.Lerp(0.6f, 1.5f, c);
                var p = landing + new Vector3(dir.x, 0f, dir.z) * c * 0.06f * s + Vector3.up * 0.004f * s;
                Show(churn[i], p, new Vector3(width * spread, 0.012f * s * (1f - c), 0.05f * s * spread * (1f - c * 0.6f)),
                     new Color(1.02f, 1.04f, 1.06f), Quaternion.LookRotation(dir));
            }
            // mist billowing up from the foot and drifting away from the fall
            for (int i = 0; i < mist.Length; i++)
            {
                float c = Mathf.Repeat(t / 2.6f + i / (float)mist.Length, 1f);
                var p = landing + dir * (0.02f + 0.06f * c) * s + across * ((i % 3) - 1) * width * 0.45f + Vector3.up * c * drop * 0.55f;
                Show(mist[i], p, (0.035f + 0.06f * c) * s * Mathf.Sin(c * Mathf.PI), new Color(1.2f, 1.25f, 1.3f) * PuffBoost);
            }
        }
    }
}
