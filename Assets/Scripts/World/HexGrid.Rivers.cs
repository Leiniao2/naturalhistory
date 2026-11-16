using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Rivers: they rise on wet high ground and run downhill tile to tile, joining as they meet,
    // until they reach a lake or the sea. Each is drawn as a meandering channel of flowing water
    // (River.shader) with muddy banks, widening downstream; each river system has its own width
    // and water colour (clear, green or silty). Near the mouth of a big river the land is
    // floodplain (lusher ground with wet hollows) and the river splits into a delta.
    public partial class HexGrid
    {
        private const float RiverSourceChance = 0.45f;  // of the candidate source tiles
        private const int   RiverMinLength    = 3;      // tiles; shorter streams are dropped
        private const float RiverLift         = 0.006f; // above the ground, so it doesn't flicker
        private const int   DeltaFlow         = 5;      // river tiles draining through the mouth for a delta and floodplain
        private const int   FloodplainReach   = 3;      // tiles upstream from the mouth that are floodplain

        private Material riverMaterial;

        private void GenerateRivers(int worldSeed)
        {
            foreach (var cell in cells) { cell.SetRiver(-1, 0, 0); cell.SetFloodplain(false); }
            var rng      = new System.Random(worldSeed ^ 0x51ab);
            var toWater  = LandDistanceToWater();
            var outEdge  = new Dictionary<HexCell, int>();
            var inEdges  = new Dictionary<HexCell, int>();
            var flow     = new Dictionary<HexCell, int>();

            // Lower is further downhill: terrace level first, then closeness to water
            int Downhill(HexCell c) => c.IsWater ? -1 : c.Elevation * 100 + toWater[c];
            bool Source(HexCell c) =>
                !c.IsWater && !c.IsMountain && c.Terrain.kind != TerrainKind.IceSheet && c.Moisture > 0.35f &&
                toWater[c] >= 3 && (c.Elevation >= 3 || NextToMountain(c));

            var sources = new List<HexCell>();
            foreach (var cell in cells)
                if (cell.Terrain != null && Source(cell) && rng.NextDouble() < RiverSourceChance) sources.Add(cell);
            // wettest first, so the big rivers claim their valleys before the small streams
            sources.Sort((a, b) => b.Moisture.CompareTo(a.Moisture));

            foreach (var source in sources)
            {
                if (outEdge.ContainsKey(source) || inEdges.ContainsKey(source)) continue;
                var path  = new List<(HexCell cell, int edge)>();
                var here  = source;
                bool ends = false; // reached water or joined another river
                while (path.Count < 60)
                {
                    // the gentlest way down (a random pick among equals), so rivers wind across the
                    // lowland instead of taking the shortest way to the sea; water is taken at once
                    var n = EdgeNeighbors(here);
                    int here0 = Downhill(here), best = -1, bestKey = int.MinValue;
                    for (int e = 0; e < 6; e++)
                    {
                        var c = n[e];
                        if (c == null || c.Terrain == null || c.IsMountain || c.Terrain.kind == TerrainKind.IceSheet) continue;
                        int k = Downhill(c);
                        if (k >= here0) continue;
                        if (c.IsWater && toWater[here] > 1) continue; // only the last tile reaches the water
                        if (k > bestKey || k == bestKey && rng.NextDouble() < 0.5) { best = e; bestKey = k; }
                    }
                    if (best < 0) break; // a hollow with no way down: the stream sinks away
                    path.Add((here, best));
                    here = n[best];
                    if (here.IsWater || outEdge.ContainsKey(here)) { ends = true; break; }
                }
                if (!ends || path.Count < RiverMinLength && !outEdge.ContainsKey(here)) continue;

                int carried = 0;
                foreach (var (cell, edge) in path)
                {
                    outEdge[cell] = edge;
                    flow[cell] = ++carried;
                }
                foreach (var (cell, edge) in path)
                {
                    var next = EdgeNeighbors(cell)[edge];
                    if (next.IsWater) continue;
                    inEdges[next] = (inEdges.TryGetValue(next, out int m) ? m : 0) | 1 << ((edge + 3) % 6);
                }
                // a tributary swells the river it joins all the way to the sea
                var down = here;
                for (int guard = 0; !down.IsWater && outEdge.TryGetValue(down, out int e) && guard < 200; guard++)
                {
                    flow[down] = (flow.TryGetValue(down, out int f) ? f : 0) + carried;
                    down = EdgeNeighbors(down)[e];
                }
            }

            // Course to the mouth (for the flow pattern) and which system each tile belongs to
            var mouths = new List<HexCell>();
            foreach (var kv in outEdge)
            {
                var cell = kv.Key;
                int steps = 1;
                var at = cell;
                for (int guard = 0; guard < 200; guard++)
                {
                    var next = EdgeNeighbors(at)[outEdge[at]];
                    if (next.IsWater || !outEdge.ContainsKey(next)) break;
                    at = next;
                    steps++;
                }
                if (steps == 1) mouths.Add(cell);
                int system = at.Coordinates.R * width + (at.Coordinates.Q + (at.Coordinates.R - (at.Coordinates.R & 1)) / 2);
                cell.SetRiver(kv.Value, inEdges.TryGetValue(cell, out int m) ? m : 0, flow[cell], steps, system);
            }

            // Floodplains: the last few tiles of each big river and the low land around its mouth
            int flooded = 0;
            foreach (var mouth in mouths)
            {
                if (mouth.RiverFlow < DeltaFlow) continue;
                foreach (var kv in outEdge)
                {
                    var c = kv.Key;
                    if (c.RiverSystem != mouth.RiverSystem || c.RiverToMouth > FloodplainReach || c.Elevation > 3) continue;
                    c.SetFloodplain(true);
                    flooded++;
                }
                foreach (var n in GetNeighbors(mouth))
                    if (!n.IsWater && !n.IsMountain && n.Elevation <= 2 && !n.Floodplain) { n.SetFloodplain(true); flooded++; }
            }
            Debug.Log($"[HexGrid] GenerateRivers — {outEdge.Count} river tiles, {mouths.Count} mouths, {flooded} floodplain tiles");
        }

        private bool NextToMountain(HexCell cell)
        {
            foreach (var n in GetNeighbors(cell)) if (n.IsMountain) return true;
            return false;
        }

        // Hex steps from each land cell to the nearest water (1 = on the shore).
        private Dictionary<HexCell, int> LandDistanceToWater()
        {
            var dist  = new Dictionary<HexCell, int>();
            var queue = new Queue<HexCell>();
            foreach (var cell in cells)
            {
                if (cell.Terrain == null) continue;
                if (cell.IsWater) { dist[cell] = 0; queue.Enqueue(cell); }
            }
            while (queue.Count > 0)
            {
                var c = queue.Dequeue();
                foreach (var n in GetNeighbors(c))
                {
                    if (n.Terrain == null || dist.ContainsKey(n)) continue;
                    dist[n] = dist[c] + 1;
                    queue.Enqueue(n);
                }
            }
            foreach (var cell in cells) if (cell.Terrain != null && !dist.ContainsKey(cell)) dist[cell] = 99;
            return dist;
        }

        // ---------- Drawing ----------

        // Water colours: clear mountain blue, green, silty olive, muddy brown
        private static readonly Color[] RiverWaters =
        {
            new(0.22f, 0.45f, 0.62f), new(0.22f, 0.47f, 0.5f), new(0.34f, 0.43f, 0.38f), new(0.45f, 0.4f, 0.3f),
        };
        private static readonly Color RiverBank  = new(0.42f, 0.36f, 0.24f);
        private static readonly Color SandyBank  = new(0.68f, 0.58f, 0.42f);
        private static readonly Color GrassyBank = new(0.34f, 0.38f, 0.2f);

        // Per river system: width multiplier, water colour and bank colour, all from its mouth tile.
        private (float width, Color water, Color bank) RiverStyle(int system)
        {
            var rng   = new System.Random(system * 7919 ^ WorldSeed);
            var mouth = cells[system % width, Mathf.Clamp(system / width, 0, height - 1)];
            float w   = 0.75f + 0.55f * (float)rng.NextDouble();
            float pick = (float)rng.NextDouble();
            // dry-country rivers run muddy, cold ones clear, the rest anywhere in between
            if (mouth.Biome is TerrainKind.Desert or TerrainKind.Savanna or TerrainKind.Steppe) pick = 0.6f + pick * 0.4f;
            else if (mouth.Biome is TerrainKind.Tundra or TerrainKind.IceSheet) pick *= 0.4f;
            float f = pick * (RiverWaters.Length - 1);
            int i = Mathf.Min((int)f, RiverWaters.Length - 2);
            var water = Color.Lerp(RiverWaters[i], RiverWaters[i + 1], f - i);
            var bank  = mouth.Biome is TerrainKind.Desert ? SandyBank : RiverBank;
            return (w, water, bank);
        }

        private float RiverWidth(int flow, float mul) => cellSize * Mathf.Min(0.035f + 0.02f * Mathf.Sqrt(Mathf.Max(flow, 1)), 0.17f) * mul;

        private void PlaceRivers()
        {
            if (riverMaterial == null) riverMaterial = Resources.Load<Material>("Materials/River");
            int drawn = 0;
            foreach (var cell in cells)
            {
                if (cell.Terrain == null || cell.IsWater || !cell.HasRiver) continue;
                var mesh = CreateRiverMesh(cell);
                if (mesh == null) continue;
                AddFeatureObject(cell, Track(mesh), 0f, Vector3.one, Color.white);
                if (riverMaterial != null) featureObjects[^1].GetComponent<MeshRenderer>().sharedMaterial = riverMaterial;
                drawn++;
            }
            if (drawn > 0) Debug.Log($"[HexGrid] PlaceRivers — {drawn} river tiles");
        }

        // Each inflow curves from its edge to a junction near the middle of the tile, and one channel
        // runs on from there to the outflow edge (at a delta, a few more fan out to the shore).
        // Channels leave and meet each edge square to it, so they join up smoothly with the
        // neighbouring tiles; in between they bend in a random meander, more on flat lowland.
        // Points are in the cell's space, relative to its top face.
        private Mesh CreateRiverMesh(HexCell cell)
        {
            var n     = EdgeNeighbors(cell);
            float apo = cellSize * 0.8660254f; // to the edge midpoint, across the groove to the neighbour
            Vector2 EdgeMid(int e)
            {
                float a = (60f * e + 30f) * Mathf.Deg2Rad;
                return new Vector2(Mathf.Sin(a), Mathf.Cos(a)) * apo;
            }

            var rng   = new System.Random(cell.Coordinates.Q * 73856093 ^ cell.Coordinates.R * 19349663 ^ WorldSeed);
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);
            var (wMul, water, bank) = RiverStyle(cell.RiverSystem);
            if (cell.Floodplain) bank = Color.Lerp(bank, GrassyBank, 0.6f);
            float meander = (cell.Elevation <= 3 ? 0.2f : 0.09f) * apo;

            int outE  = cell.RiverOut;
            var outP  = EdgeMid(outE);
            float outW = RiverWidth(cell.RiverFlow, wMul);
            bool mouth = n[outE] != null && n[outE].IsWater;
            // a low coast: run on past the shore and dip to the water; off a cliff the river stops
            // at the brink and AmbientWater's waterfall carries it down
            bool overCliff = mouth && cell.Elevation >= CliffElevation;
            float drop = mouth && !overCliff ? n[outE].SurfaceHeight - cell.SurfaceHeight + 0.004f : float.NaN;
            if (mouth && !overCliff) outP *= 1.12f;

            // flow coordinate (uv.y): 0 where the river meets the water, rising... negative upstream
            float seg  = 2f * apo;
            float vIn  = -cell.RiverToMouth * seg;
            float vMid = vIn + seg * 0.5f;
            float vOut = vIn + seg;

            var junction = new Vector2(R(-0.15f, 0.15f), R(-0.15f, 0.15f)) * apo;
            // direction through the junction: from the average inflow toward the outflow
            var inDir = Vector2.zero;
            for (int e = 0; e < 6; e++) if ((cell.RiverIn & (1 << e)) != 0) inDir += EdgeMid(e).normalized;
            var through = (outP.normalized - (inDir.sqrMagnitude > 1e-4f ? inDir.normalized : -outP.normalized)).normalized;

            var verts  = new List<Vector3>();
            var colors = new List<Color>();
            var uvs    = new List<Vector2>();
            var tris   = new List<int>();

            // Hermite curve a→b with end tangents ta, tb, plus a meander that is zero (and flat) at
            // both ends; width and flow coordinate interpolate along it.
            void Channel(Vector2 a, Vector2 ta, float wa, float va, Vector2 b, Vector2 tb, float wb, float vb, float dropAt)
            {
                const int steps = 14;
                float len   = (b - a).magnitude;
                float bendA = R(-1f, 1f), bendB = R(-1f, 1f), wobble = R(-1f, 1f);
                int start = verts.Count;
                for (int i = 0; i <= steps; i++)
                {
                    float t = i / (float)steps, t2 = t * t, t3 = t2 * t;
                    var p = (2 * t3 - 3 * t2 + 1) * a + (t3 - 2 * t2 + t) * len * ta + (-2 * t3 + 3 * t2) * b + (t3 - t2) * len * tb;
                    var d = (6 * t2 - 6 * t) * a + (3 * t2 - 4 * t + 1) * len * ta + (-6 * t2 + 6 * t) * b + (3 * t2 - 2 * t) * len * tb;
                    if (d.sqrMagnitude < 1e-8f) d = b - a;
                    var side = new Vector2(d.y, -d.x).normalized;
                    float env = Mathf.Sin(Mathf.PI * t); env *= env;
                    p += side * (meander * env * (bendA + bendB * Mathf.Sin(2f * Mathf.PI * t)) * 0.6f);
                    float w = Mathf.Lerp(wa, wb, t) * (1f + 0.22f * wobble * Mathf.Sin(Mathf.PI * t));
                    float v = Mathf.Lerp(va, vb, t);

                    // across: bank, water edge, middle, water edge, bank
                    float[] across = { -1f, -0.6f, 0f, 0.6f, 1f };
                    float[] us     = { 0f, 0f, 0.5f, 1f, 1f };
                    for (int k = 0; k < 5; k++)
                    {
                        var q = p + side * (w * across[k]);
                        float y = LocalGround(cell, q) + RiverLift;
                        if (!float.IsNaN(dropAt) && t > 0.7f) y = Mathf.Lerp(y, dropAt, Mathf.InverseLerp(0.7f, 1f, t));
                        verts.Add(new Vector3(q.x, y, q.y));
                        uvs.Add(new Vector2(us[k], v));
                        var c = k == 0 || k == 4 ? bank : k == 2 ? water * 0.82f : water;
                        c.a = k == 0 || k == 4 ? 0f : 1f;
                        colors.Add(c);
                    }
                    if (i == 0) continue;
                    int r0 = start + (i - 1) * 5, r1 = start + i * 5;
                    for (int k = 0; k < 4; k++)
                    {
                        tris.Add(r0 + k); tris.Add(r1 + k);     tris.Add(r0 + k + 1);
                        tris.Add(r0 + k + 1); tris.Add(r1 + k); tris.Add(r1 + k + 1);
                    }
                }
            }

            bool any = false;
            for (int e = 0; e < 6; e++)
            {
                if ((cell.RiverIn & (1 << e)) == 0) continue;
                var up = n[e];
                float wIn = RiverWidth(up != null ? up.RiverFlow : cell.RiverFlow, wMul);
                var a = EdgeMid(e);
                Channel(a, -a.normalized, wIn, vIn, junction, through, Mathf.Lerp(wIn, outW, 0.5f), vMid, float.NaN);
                any = true;
            }
            if (any) Channel(junction, through, outW * 0.95f, vMid, outP, outP.normalized, outW, vOut, drop);
            else
            {
                // the source: a spring that starts narrow inside the tile
                var spring = -outP * 0.3f + junction * 0.5f;
                Channel(spring, outP.normalized, outW * 0.35f, vIn + seg * 0.35f, outP, outP.normalized, outW, vOut, drop);
            }

            // Delta: big rivers split into a fan of smaller channels across the other shore edges
            if (mouth && !overCliff && cell.RiverFlow >= DeltaFlow)
            {
                int extra = 0;
                for (int k = 1; k <= 2 && extra < 2; k++)
                foreach (int e in new[] { (outE + k) % 6, (outE + 6 - k) % 6 })
                {
                    if (extra >= 2 || n[e] == null || !n[e].IsWater) continue;
                    var to = EdgeMid(e) * 1.12f;
                    Channel(junction, through, outW * 0.5f, vMid, to, to.normalized, outW * 0.6f, vOut, n[e].SurfaceHeight - cell.SurfaceHeight + 0.004f);
                    extra++;
                }
            }
            if (verts.Count == 0) return null;

            var mesh = new Mesh { name = "River" };
            mesh.SetVertices(verts);
            mesh.SetColors(colors);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}
