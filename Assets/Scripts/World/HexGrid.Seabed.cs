using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // The relief of the seabed, shown in the under view: water tiles drop below sea level with their
    // depth (shallow shelf to abyssal plain), deeper still along winding ocean trenches, and rise
    // to sea level where they meet the coast. Neighbouring seabed tiles share their rim heights, so
    // the floor is one continuous surface. Lakebeds are shallow basins.
    public partial class HexGrid
    {
        // Some seven terrace steps from the shore to the deepest trench: a shelving, rolling floor
        private const float ShelfDepth   = 0.04f;  // seabed right at the coast, below the sea surface
        private const float ShelfDrop    = 0.07f;  // the shelf deepens this much toward its edge
        private const float ShelfHills   = 0.05f;  // sand banks and hollows on the shelf
        private const float Clearance    = 0.012f; // the floor stays at least this far below the sea surface
        private const float AbyssDepth   = 0.1f;   // the abyssal plain, below the shelf edge
        private const float AbyssDeepen  = 0.12f;  // ...deepening further out into the open ocean
        private const float TrenchDepth  = 0.15f;  // extra depth in a trench
        private const float RidgeHeight  = 0.08f;  // mid-ocean ridges rise this much off the abyssal plain
        private const float HillHeight   = 0.08f;  // abyssal hills and basins in the deep ocean
        private const float LakeDepth    = 0.05f;
        private const float WallBottom   = 3.2f;   // seabed tiles' walls reach down this far (below any trench)

        private float[] seabedY;                    // per cell (r * width + q): local Y of the seabed top
        private readonly Dictionary<HexCell, Mesh> surfaceMeshes = new();
        private readonly Dictionary<string, Mesh> seabedMeshCache = new();

        // Where the floor is under a tile in the under view (the tile top for land)
        public float UnderSurface(HexCell cell)
        {
            if (cell == null) return 0f;
            if (seabedY == null || !cell.IsWater) return cell.SurfaceHeight;
            var (q, r) = cell.Coordinates.ToOffsetCoordinates();
            int i = r * width + ((q % width) + width) % width;
            return i >= 0 && i < seabedY.Length ? seabedY[i] : cell.SurfaceHeight;
        }

        // Called with the rest of the under layer (generation, and whenever the coast moves)
        private void ComputeSeabedRelief(int worldSeed)
        {
            seabedY = new float[width * height];
            foreach (var m in seabedMeshCache.Values) DestroyMesh(m);
            seabedMeshCache.Clear();
            seabedSamples.Clear();
            var rng = new System.Random(worldSeed ^ 0x7E4C);
            var off = new Vector3((float)rng.NextDouble(), (float)rng.NextDouble(), (float)rng.NextDouble()) * 1000f;
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var c = cells[q, r];
                if (c?.Terrain == null || !c.IsWater) { seabedY[r * width + q] = c != null ? c.SurfaceHeight : 0f; continue; }
                float y;
                if (c.Terrain.kind == TerrainKind.FreshWater)
                    y = c.SurfaceHeight - 0.03f - LakeDepth * c.Depth;
                else
                {
                    // shallow shelf, then a steep continental slope down to the abyssal plain
                    float d = c.Depth;
                    // the shelf takes the shallower ~60% of the sea, so shallow seabed is the most of it
                    float shelf = Mathf.InverseLerp(0f, 0.55f, d);
                    float slope = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.55f, 0.72f, d));
                    float open  = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.72f, 1f, d));
                    y = c.SurfaceHeight - ShelfDepth - ShelfDrop * shelf - AbyssDepth * slope - AbyssDeepen * open;
                    var pos = c.Coordinates.ToWorldPosition(cellSize);
                    var loop = OnMapLoop(new Vector2(pos.x, pos.z));
                    float abyss = Mathf.InverseLerp(0.65f, 0.8f, d); // ridges, trenches and hills belong to the deep ocean
                    // trenches: narrow, winding lines of ridged noise
                    var p = loop * (0.12f / cellSize) + off;
                    float trench = 1f - Mathf.Abs(PerlinNoise3D.Sample(p.x, p.y, p.z) * 2f);
                    y -= TrenchDepth * Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.82f, 0.95f, trench)) * Mathf.InverseLerp(0.7f, 0.9f, d);
                    // mid-ocean ridges: long raised spines with a rift valley down the middle
                    var pr = loop * (0.08f / cellSize) + off * 1.7f + Vector3.one * 333f;
                    float spine = 1f - Mathf.Abs(PerlinNoise3D.Sample(pr.x, pr.y, pr.z) * 2f);
                    float rise = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.65f, 0.88f, spine));
                    float rift = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.95f, 0.99f, spine));
                    y += (RidgeHeight * rise - RidgeHeight * 0.45f * rift) * abyss;
                    // abyssal hills: broad rises and basins plus a finer roughness
                    var ph = loop * (0.35f / cellSize) + off * 0.3f;
                    var pk = loop * (0.9f / cellSize) + off * 0.6f + Vector3.one * 77f;
                    float hills = PerlinNoise3D.Sample(ph.x, ph.y, ph.z) * 2f + PerlinNoise3D.Sample(pk.x, pk.y, pk.z) * 0.8f;
                    y += HillHeight * hills * Mathf.Lerp(0.1f, 1f, abyss);
                    // the shelf: long sand banks and hollows between them, fading out down the slope
                    var pb = loop * (0.45f / cellSize) + off * 0.45f + Vector3.one * 191f;
                    var pf = loop * (1.1f / cellSize) + off * 0.8f + Vector3.one * 59f;
                    float banks = PerlinNoise3D.Sample(pb.x, pb.y, pb.z) * 2f + PerlinNoise3D.Sample(pf.x, pf.y, pf.z) * 0.9f;
                    y += ShelfHills * banks * (1f - slope);
                    y = Mathf.Min(y, c.SurfaceHeight - Clearance);
                }
                seabedY[r * width + q] = y;
            }
            SmoothSeabed();
        }

        // Like the land: neighbouring seabed tiles differ by no more than a terrace step, so the
        // floor runs in long, gradual slopes instead of jumping from tile to tile. A pass of
        // neighbour averaging takes off the tile-to-tile noise; then any step steeper than
        // MaxSeabedStep is eased by pulling both sides toward each other, so ridges and trenches
        // widen into slopes rather than being cut away.
        private const float MaxSeabedStep = 0.07f; // a land terrace step (HexGrid.elevationStep)

        private void SmoothSeabed()
        {
            bool Wet(HexCell c) => c?.Terrain != null && c.IsWater;
            int Index(HexCell c) { var (q, r) = c.Coordinates.ToOffsetCoordinates(); return r * width + ((q % width) + width) % width; }
            var next = new float[seabedY.Length];
            for (int pass = 0; pass < 1; pass++)
            {
                System.Array.Copy(seabedY, next, seabedY.Length);
                foreach (var c in cells)
                {
                    if (!Wet(c)) continue;
                    int i = Index(c);
                    float sum = seabedY[i] * 2f, w = 2f;
                    foreach (var n in GetNeighbors(c))
                        if (Wet(n) && n.Terrain.kind == c.Terrain.kind) { sum += seabedY[Index(n)]; w += 1f; }
                    next[i] = Mathf.Min(sum / w, c.SurfaceHeight - Clearance);
                }
                (seabedY, next) = (next, seabedY);
            }
            for (int it = 0; it < 24; it++)
            {
                bool eased = false;
                foreach (var c in cells)
                {
                    if (!Wet(c)) continue;
                    int i = Index(c);
                    foreach (var n in GetNeighbors(c))
                    {
                        if (!Wet(n) || n.Terrain.kind != c.Terrain.kind) continue;
                        int j = Index(n);
                        float excess = seabedY[i] - seabedY[j] - MaxSeabedStep;
                        if (excess <= 1e-4f) continue;
                        seabedY[i] -= excess * 0.5f;
                        seabedY[j] = Mathf.Min(seabedY[j] + excess * 0.5f, n.SurfaceHeight - Clearance);
                        eased = true;
                    }
                }
                if (!eased) break;
            }
        }

        // ---- The floor as one smooth surface. Its height anywhere is a weighted blend of the depths
        // of the water tiles around (a smooth falloff reaching about one tile into the neighbours),
        // rising to just under the water surface at the coast. It's a function of map position only,
        // so neighbouring tiles' meshes meet exactly, in height and in shading.

        private struct SeabedSample { public Vector2 at; public float y, sea; public bool wet; }
        private readonly Dictionary<HexCell, List<SeabedSample>> seabedSamples = new();
        private const float SeabedReach = 1.9f;    // × cellSize: how far a tile's depth reaches
        private const float CoastRise   = 0.9f;    // × cellSize: the floor rises to the shore over this distance
        private const int   SeabedGrid  = 7;       // lattice steps from the tile centre to a corner

        // This tile and two rings round it, positions relative to the tile centre (across the wrap seam too)
        private List<SeabedSample> SeabedSamples(HexCell cell)
        {
            if (seabedSamples.TryGetValue(cell, out var list)) return list;
            list = new List<SeabedSample>();
            var seen = new HashSet<HexCell> { cell };
            var ring = new List<HexCell> { cell };
            for (int k = 0; k < 2; k++)
            {
                var next = new List<HexCell>();
                foreach (var c in ring) foreach (var n in GetNeighbors(c)) if (n != null && seen.Add(n)) next.Add(n);
                ring = next;
            }
            var o = cell.Coordinates.ToWorldPosition(cellSize);
            float W = WrapWidth;
            foreach (var c in seen)
            {
                if (c.Terrain == null) continue;
                var p = c.Coordinates.ToWorldPosition(cellSize);
                float dx = Mathf.Repeat(p.x - o.x + W * 0.5f, W) - W * 0.5f;
                list.Add(new SeabedSample { at = new Vector2(dx, p.z - o.z), y = UnderSurface(c), sea = c.SurfaceHeight, wet = c.IsWater });
            }
            seabedSamples[cell] = list;
            return list;
        }

        // Height of the floor at p (relative to a water tile's centre, in its local frame)
        public float SeabedAt(HexCell cell, Vector2 p)
        {
            float reach = SeabedReach * cellSize, apothem = cellSize * 0.8660254f;
            float sum = 0f, seaSum = 0f, w = 0f, coast = float.MaxValue;
            foreach (var s in SeabedSamples(cell))
            {
                var d = p - s.at;
                if (!s.wet) { coast = Mathf.Min(coast, HexDistance(d) - apothem); continue; }
                float t = d.sqrMagnitude / (reach * reach);
                if (t >= 1f) continue;
                float k = (1f - t) * (1f - t) * (1f - t);
                sum += k * s.y; seaSum += k * s.sea; w += k;
            }
            if (w <= 0f) return UnderSurface(cell);
            float shore = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(coast / (CoastRise * cellSize)));
            return Mathf.Lerp(seaSum / w - Clearance, sum / w, shore);
        }

        // "Hex distance" from a cell centre: 1 × the apothem on the cell's edges (edges face 30° + 60e)
        private static float HexDistance(Vector2 d) =>
            Mathf.Max(Mathf.Abs(d.x), Mathf.Max(Mathf.Abs(d.x * 0.5f + d.y * 0.8660254f), Mathf.Abs(d.x * 0.5f - d.y * 0.8660254f)));

        // The tile mesh for a water cell in the under view: a fine lattice over the whole hex, out to
        // the cell boundary, smooth-shaded from the surface's own slope; along the coast and the map
        // edge a skirt drops below it so no gap shows.
        private Mesh SeabedMesh(HexCell cell)
        {
            var (cq, cr) = cell.Coordinates.ToOffsetCoordinates();
            string k = cq + "," + cr;
            if (seabedMeshCache.TryGetValue(k, out var mesh) && mesh != null) return mesh;

            int n = SeabedGrid;
            float R = cellSize;
            var e1 = new Vector2(0f, 1f) * R / n;
            var e2 = new Vector2(0.8660254f, 0.5f) * R / n;
            bool In(int i, int j) => Mathf.Abs(i) <= n && Mathf.Abs(j) <= n && Mathf.Abs(i + j) <= n;
            var index = new Dictionary<(int, int), int>();
            var verts = new List<Vector3>(); var normals = new List<Vector3>(); var uvs = new List<Vector2>(); var tris = new List<int>();
            float eps = 0.03f * cellSize;
            Vector2 Uv(Vector2 p) => new(0.5f + 0.35f * p.x / R, 0.5f + 0.35f * p.y / R); // inside the shader's rim-darkening radius
            for (int i = -n; i <= n; i++)
            for (int j = -n; j <= n; j++)
            {
                if (!In(i, j)) continue;
                var p = e1 * i + e2 * j;
                float y = SeabedAt(cell, p);
                float dx = (SeabedAt(cell, p + Vector2.right * eps) - SeabedAt(cell, p - Vector2.right * eps)) / (2f * eps);
                float dz = (SeabedAt(cell, p + Vector2.up * eps) - SeabedAt(cell, p - Vector2.up * eps)) / (2f * eps);
                index[(i, j)] = verts.Count;
                verts.Add(new Vector3(p.x, y, p.y));
                normals.Add(new Vector3(-dx, 1f, -dz).normalized);
                uvs.Add(Uv(p));
            }
            void Tri(int a, int b, int c)
            {
                // clockwise seen from above: the face normal points up
                if (Vector3.Cross(verts[b] - verts[a], verts[c] - verts[a]).y < 0f) (b, c) = (c, b);
                tris.Add(a); tris.Add(b); tris.Add(c);
            }
            for (int i = -n; i < n; i++)
            for (int j = -n; j < n; j++)
            {
                if (In(i, j) && In(i + 1, j) && In(i, j + 1)) Tri(index[(i, j)], index[(i + 1, j)], index[(i, j + 1)]);
                if (In(i + 1, j) && In(i + 1, j + 1) && In(i, j + 1)) Tri(index[(i + 1, j)], index[(i + 1, j + 1)], index[(i, j + 1)]);
            }
            // skirts where the neighbour isn't water (edge e lies between corners e and e + 1)
            var nb = EdgeNeighbors(cell);
            (int, int) Corner(int c) => (c % 6) switch { 0 => (n, 0), 1 => (0, n), 2 => (-n, n), 3 => (-n, 0), 4 => (0, -n), _ => (n, -n) };
            for (int e = 0; e < 6; e++)
            {
                if (nb[e] != null && nb[e].Terrain != null && nb[e].IsWater) continue;
                var (ai, aj) = Corner(e); var (bi, bj) = Corner(e + 1);
                float ang = (60f * e + 30f) * Mathf.Deg2Rad;
                var outward = new Vector3(Mathf.Sin(ang), 0f, Mathf.Cos(ang));
                for (int s = 0; s < n; s++)
                {
                    var top0 = verts[index[(ai + (bi - ai) * s / n, aj + (bj - aj) * s / n)]];
                    var top1 = verts[index[(ai + (bi - ai) * (s + 1) / n, aj + (bj - aj) * (s + 1) / n)]];
                    var low0 = new Vector3(top0.x, -WallBottom, top0.z);
                    var low1 = new Vector3(top1.x, -WallBottom, top1.z);
                    int b0 = verts.Count;
                    verts.Add(top0); verts.Add(top1); verts.Add(low1); verts.Add(low0);
                    for (int m = 0; m < 4; m++) { normals.Add(outward); uvs.Add(Uv(new Vector2(top0.x, top0.z))); }
                    bool flip = Vector3.Dot(Vector3.Cross(top1 - top0, low1 - top0), outward) < 0f;
                    if (flip) { tris.Add(b0); tris.Add(b0 + 2); tris.Add(b0 + 1); tris.Add(b0); tris.Add(b0 + 3); tris.Add(b0 + 2); }
                    else      { tris.Add(b0); tris.Add(b0 + 1); tris.Add(b0 + 2); tris.Add(b0); tris.Add(b0 + 2); tris.Add(b0 + 3); }
                }
            }
            mesh = new Mesh { name = "Seabed", hideFlags = HideFlags.DontSave };
            mesh.SetVertices(verts); mesh.SetNormals(normals); mesh.SetUVs(0, uvs); mesh.SetTriangles(tris, 0);
            mesh.RecalculateBounds();
            seabedMeshCache[k] = mesh;
            return mesh;
        }

        // Seabed props follow the floor's slope across the tile: a quadratic fit of the floor height
        // (relative to the tile centre's) over the hex, handed to MapFeature.shader (ApplyGroundFit),
        // which lifts or lowers each vertex by it. Cheaper than a bent copy of every shared prop mesh.
        private static readonly int GroundFitAId = Shader.PropertyToID("_GroundFitA");
        private static readonly int GroundFitBId = Shader.PropertyToID("_GroundFitB");

        private void FitPropsToSeabed(HexCell cell, Renderer rend)
        {
            if (seabedY == null || !cell.IsWater || rend == null) return;
            // least squares over a lattice of the hex: y ≈ a + b x + c z + d x² + e x z + f z²
            var M = new double[6, 6]; var v = new double[6];
            float h0 = UnderSurface(cell);
            const int n = 4;
            for (int i = -n; i <= n; i++)
            for (int j = -n; j <= n; j++)
            {
                if (Mathf.Abs(i + j) > n) continue;
                var p = new Vector2(0.8660254f * j, i + 0.5f * j) * (cellSize / n);
                double[] f = { 1, p.x, p.y, p.x * p.x, p.x * p.y, p.y * p.y };
                double y = SeabedAt(cell, p) - h0;
                for (int r = 0; r < 6; r++) { v[r] += f[r] * y; for (int c = 0; c < 6; c++) M[r, c] += f[r] * f[c]; }
            }
            var x = Solve6(M, v);
            var block = new MaterialPropertyBlock();
            rend.GetPropertyBlock(block);
            block.SetVector(GroundFitAId, new Vector4((float)x[0], (float)x[1], (float)x[2], (float)x[3]));
            block.SetVector(GroundFitBId, new Vector4((float)x[4], (float)x[5], 1f, 0f)); // z = 1: fit on
            rend.SetPropertyBlock(block);
        }

        private static double[] Solve6(double[,] A, double[] b)
        {
            int n = 6; var a = (double[,])A.Clone(); var x = (double[])b.Clone();
            for (int c = 0; c < n; c++)
            {
                int piv = c;
                for (int r = c + 1; r < n; r++) if (System.Math.Abs(a[r, c]) > System.Math.Abs(a[piv, c])) piv = r;
                for (int k = 0; k < n; k++) (a[c, k], a[piv, k]) = (a[piv, k], a[c, k]);
                (x[c], x[piv]) = (x[piv], x[c]);
                if (System.Math.Abs(a[c, c]) < 1e-12) continue;
                for (int r = 0; r < n; r++)
                {
                    if (r == c) continue;
                    double f = a[r, c] / a[c, c];
                    for (int k = c; k < n; k++) a[r, k] -= f * a[c, k];
                    x[r] -= f * x[c];
                }
            }
            for (int c = 0; c < n; c++) x[c] = System.Math.Abs(a[c, c]) < 1e-12 ? 0 : x[c] / a[c, c];
            return x;
        }

        // Swap water tiles' meshes (and colliders, so clicks land on the seabed) between surface and seabed
        private void ShowSeabedRelief(bool on)
        {
            if (seabedY == null) return;
            foreach (var cell in cells)
            {
                if (cell?.Terrain == null || !cell.IsWater) continue;
                var mf = cell.GetComponent<MeshFilter>();
                var mc = cell.GetComponent<MeshCollider>();
                if (mf == null) continue;
                if (on)
                {
                    if (mf.sharedMesh != null && mf.sharedMesh.name != "Seabed") surfaceMeshes[cell] = mf.sharedMesh; // remember the surface tile
                    var m = SeabedMesh(cell);
                    mf.sharedMesh = m;
                    if (mc != null) mc.sharedMesh = m;
                }
                else if (surfaceMeshes.TryGetValue(cell, out var s) && s != null)
                {
                    mf.sharedMesh = s;
                    if (mc != null) mc.sharedMesh = s;
                }
            }
            if (!on) surfaceMeshes.Clear();
        }
    }
}
