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
        // Kept well below the land's relief (a few terrace steps from the shore to the deepest
        // trench), so the seabed reads as a gently shelving floor rather than a second mountain range
        private const float ShelfDepth   = 0.04f;  // seabed right at the coast, below the sea surface
        private const float ShelfDrop    = 0.03f;  // the shelf deepens this much toward its edge
        private const float AbyssDepth   = 0.1f;   // the abyssal plain, below the shelf edge
        private const float TrenchDepth  = 0.07f;  // extra depth in a trench
        private const float RidgeHeight  = 0.045f; // mid-ocean ridges rise this much off the abyssal plain
        private const float HillHeight   = 0.015f; // abyssal hills: tile-to-tile relief
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
                    y = c.SurfaceHeight - ShelfDepth - ShelfDrop * shelf - AbyssDepth * slope;
                    var pos = c.Coordinates.ToWorldPosition(cellSize);
                    var loop = OnMapLoop(new Vector2(pos.x, pos.z));
                    float abyss = Mathf.InverseLerp(0.65f, 0.8f, d); // ridges, trenches and hills belong to the deep ocean
                    // trenches: narrow, winding lines of ridged noise
                    var p = loop * (0.12f / cellSize) + off;
                    float trench = 1f - Mathf.Abs(PerlinNoise3D.Sample(p.x, p.y, p.z) * 2f);
                    y -= TrenchDepth * Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.86f, 0.97f, trench)) * Mathf.InverseLerp(0.7f, 0.9f, d);
                    // mid-ocean ridges: long raised spines with a rift valley down the middle
                    var pr = loop * (0.08f / cellSize) + off * 1.7f + Vector3.one * 333f;
                    float spine = 1f - Mathf.Abs(PerlinNoise3D.Sample(pr.x, pr.y, pr.z) * 2f);
                    float rise = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.7f, 0.9f, spine));
                    float rift = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.95f, 0.99f, spine));
                    y += (RidgeHeight * rise - RidgeHeight * 0.45f * rift) * abyss;
                    // abyssal hills: relief from tile to tile, like hills on land
                    var ph = loop * (0.55f / cellSize) + off * 0.3f;
                    y += HillHeight * PerlinNoise3D.Sample(ph.x, ph.y, ph.z) * 2f * Mathf.Lerp(0.3f, 1f, abyss);
                    y = Mathf.Min(y, c.SurfaceHeight - ShelfDepth);
                }
                seabedY[r * width + q] = y;
            }
            SmoothSeabed();
        }

        // Like the land: neighbouring seabed tiles differ by no more than about a terrace step, so the
        // floor runs in long, gradual slopes instead of jumping from tile to tile. Two passes of
        // neighbour averaging take off the tile-to-tile noise; then any step steeper than
        // MaxSeabedStep is eased by pulling both sides toward each other, so ridges and trenches
        // widen into slopes rather than being cut away.
        private const float MaxSeabedStep = 0.045f;

        private void SmoothSeabed()
        {
            bool Wet(HexCell c) => c?.Terrain != null && c.IsWater;
            int Index(HexCell c) { var (q, r) = c.Coordinates.ToOffsetCoordinates(); return r * width + ((q % width) + width) % width; }
            var next = new float[seabedY.Length];
            for (int pass = 0; pass < 2; pass++)
            {
                System.Array.Copy(seabedY, next, seabedY.Length);
                foreach (var c in cells)
                {
                    if (!Wet(c)) continue;
                    int i = Index(c);
                    float sum = seabedY[i] * 2f, w = 2f;
                    foreach (var n in GetNeighbors(c))
                        if (Wet(n) && n.Terrain.kind == c.Terrain.kind) { sum += seabedY[Index(n)]; w += 1f; }
                    next[i] = Mathf.Min(sum / w, c.SurfaceHeight - ShelfDepth);
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
                        seabedY[j] = Mathf.Min(seabedY[j] + excess * 0.5f, n.SurfaceHeight - ShelfDepth);
                        eased = true;
                    }
                }
                if (!eased) break;
            }
        }

        // The tile mesh for a water cell in the under view: its seabed, sloped to meet the
        // neighbouring seabed (shared rim heights) and rising to sea level at the coast.
        private Mesh SeabedMesh(HexCell cell)
        {
            var n = EdgeNeighbors(cell);
            float h = UnderSurface(cell);
            bool Water(HexCell c) => c != null && c.Terrain != null && c.IsWater;
            var corners = new float[6];
            var edges   = new float[6];
            var joined  = new bool[6];
            for (int e = 0; e < 6; e++)
                edges[e] = Water(n[e]) ? (h + UnderSurface(n[e])) * 0.5f : n[e] == null ? h : 0f; // the coast: up to the land's foot
            for (int i = 0; i < 6; i++)
            {
                var a = n[(i + 5) % 6]; var b = n[i];
                bool coast = (a != null && !Water(a)) || (b != null && !Water(b));
                float sum = h; int count = 1;
                if (Water(a)) { sum += UnderSurface(a); count++; }
                if (Water(b)) { sum += UnderSurface(b); count++; }
                corners[i] = coast ? 0f : sum / count;
            }
            var key = new System.Text.StringBuilder().Append(Mathf.RoundToInt(h * 10000f));
            for (int i = 0; i < 6; i++) key.Append(',').Append(Mathf.RoundToInt(corners[i] * 10000f)).Append(',').Append(Mathf.RoundToInt(edges[i] * 10000f));
            string k = key.ToString();
            if (seabedMeshCache.TryGetValue(k, out var mesh) && mesh != null) return mesh;

            // CreateSloped builds walls down to y = 0: build it raised by WallBottom, then lower it
            var raisedC = new float[6]; var raisedE = new float[6];
            for (int i = 0; i < 6; i++) { raisedC[i] = corners[i] + WallBottom; raisedE[i] = edges[i] + WallBottom; }
            mesh = HexMeshGenerator.CreateSloped(cellSize * TileRadius, cellSize, h + WallBottom, TileSolid, raisedC, raisedE, joined);
            var v = mesh.vertices;
            for (int i = 0; i < v.Length; i++) v[i].y -= WallBottom;
            mesh.vertices = v;
            mesh.RecalculateBounds();
            mesh.name = "Seabed";
            mesh.hideFlags = HideFlags.DontSave;
            seabedMeshCache[k] = mesh;
            return mesh;
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
