using System.Collections.Generic;
using NaturalHistory.Players;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Territory
{
    // Civilization-style borders: along every edge of a player's territory that doesn't face more of
    // the same player's territory, a solid band in the player's primary colour, a thin stripe in their
    // secondary colour inside it, and a soft glow fading into the territory.
    //
    // Each bordered hex gets its own small mesh as a child of the cell, so borders follow the
    // east–west wrap (which moves whole cells) and are destroyed with the map.
    public static class TerritoryBorders
    {
        // Must match HexGrid.TileRadius / TileSolid
        private const float TileRadius = 0.985f; // tile top face size relative to cellSize
        private const float TileSolid  = 0.6f;   // flat middle of a land tile, as a fraction of its apothem

        private const float Lift = 0.025f; // above the tile surface

        // Bands inward from the tile edge, in cells: (from, to, colour at from, colour at to)
        private const float SolidFrom = 0.015f, SolidTo = 0.085f;
        private const float StripeTo  = 0.12f;
        private const float GlowTo    = 0.32f;
        private const float GlowAlpha = 0.4f;

        private const int Steps = 4; // segments along each edge, so the band follows the tile's slope

        private static readonly List<GameObject> borders = new();
        private static Material material;

        public static void Clear()
        {
            foreach (var b in borders) if (b != null) Object.Destroy(b);
            borders.Clear();
        }

        public static void Rebuild(IReadOnlyDictionary<HexCell, Player> owners, HexGrid grid)
        {
            Clear();
            if (material == null)
            {
                var shader = Resources.Load<Shader>("Shaders/TerritoryBorder");
                if (shader == null) { Debug.LogWarning("[TerritoryBorders] Resources/Shaders/TerritoryBorder not found."); return; }
                material = new Material(shader) { name = "TerritoryBorder" };
            }

            float cellSize = grid.WrapWidth / (Mathf.Sqrt(3f) * grid.Width);
            var verts  = new List<Vector3>();
            var colors = new List<Color>();
            var tris   = new List<int>();

            foreach (var (cell, player) in owners)
            {
                if (cell == null || player == null) continue;
                var across = EdgeNeighbors(cell, grid);
                verts.Clear(); colors.Clear(); tris.Clear();
                var bordered = new bool[6];
                for (int e = 0; e < 6; e++)
                {
                    var n = across[e];
                    bordered[e] = !(n != null && owners.TryGetValue(n, out var other) && other == player);
                }
                for (int e = 0; e < 6; e++)
                    if (bordered[e])
                        AddEdge(cell, e, cellSize, player, !bordered[(e + 5) % 6], !bordered[(e + 1) % 6], verts, colors, tris);
                if (tris.Count == 0) continue;

                var mesh = new Mesh { name = "TerritoryBorder" };
                mesh.SetVertices(verts);
                mesh.SetColors(colors);
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateBounds();

                var go = new GameObject("TerritoryBorder");
                go.transform.SetParent(cell.transform, false);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterial = material;
                mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                mr.receiveShadows = false;
                go.AddComponent<DestroyMeshWithObject>();
                borders.Add(go);
            }
        }

        // The three bands along edge e (from corner e to corner e+1; corner i is 60i degrees
        // clockwise from +Z, as in HexMeshGenerator). openStart / openEnd: the edge before / after
        // has no border, so the border carries on into the neighbouring tile at that corner.
        private static void AddEdge(HexCell cell, int e, float cellSize, Player player, bool openStart, bool openEnd,
                                    List<Vector3> verts, List<Color> colors, List<int> tris)
        {
            var primary   = player.Primary;
            var secondary = player.Secondary;
            var clear     = new Color(primary.r, primary.g, primary.b, 0f);
            var glow      = new Color(primary.r, primary.g, primary.b, GlowAlpha);
            AddBand(cell, e, cellSize, SolidFrom * cellSize, SolidTo * cellSize,  primary,   primary,   openStart, openEnd, verts, colors, tris);
            AddBand(cell, e, cellSize, SolidTo * cellSize,   StripeTo * cellSize, secondary, secondary, openStart, openEnd, verts, colors, tris);
            AddBand(cell, e, cellSize, StripeTo * cellSize,  GlowTo * cellSize,   glow,      clear,     openStart, openEnd, verts, colors, tris);
        }

        // A strip parallel to edge e between inset distances d0 and d1 from the edge. Points are the
        // edge scaled toward the centre, so neighbouring bordered edges' strips meet in clean mitres.
        // At an open end the strip runs on until it meets the next edge of the tile instead, where the
        // neighbouring tile's band starts, so the two join along the shared edge without a cut
        // across the middle of the tile.
        private static void AddBand(HexCell cell, int e, float cellSize, float d0, float d1, Color c0, Color c1,
                                    bool openStart, bool openEnd, List<Vector3> verts, List<Color> colors, List<int> tris)
        {
            float radius  = cellSize * TileRadius;
            float apothem = radius * 0.8660254f;
            var a = Corner(e, radius);
            var b = Corner(e + 1, radius);
            int start = verts.Count;
            for (int i = 0; i <= Steps; i++)
            {
                float f = i / (float)Steps;
                var p = Vector2.Lerp(a, b, f);
                if (i == 0 && openStart)
                {
                    verts.Add(AlongEdge(cell, (e + 5) % 6, a, Corner(e - 1 + 6, radius), d0, radius, apothem, true));
                    verts.Add(AlongEdge(cell, (e + 5) % 6, a, Corner(e - 1 + 6, radius), d1, radius, apothem, true));
                }
                else if (i == Steps && openEnd)
                {
                    verts.Add(AlongEdge(cell, (e + 1) % 6, b, Corner(e + 2, radius), d0, radius, apothem, false));
                    verts.Add(AlongEdge(cell, (e + 1) % 6, b, Corner(e + 2, radius), d1, radius, apothem, false));
                }
                else
                {
                    verts.Add(Point(cell, e, f, p * (1f - d0 / apothem), apothem - d0, apothem));
                    verts.Add(Point(cell, e, f, p * (1f - d1 / apothem), apothem - d1, apothem));
                }
                colors.Add(c0);
                colors.Add(c1);
            }
            for (int i = 0; i < Steps; i++)
            {
                int o0 = start + 2 * i, i0 = o0 + 1, o1 = o0 + 2, i1 = o0 + 3;
                tris.Add(o0); tris.Add(o1); tris.Add(i1);
                tris.Add(o0); tris.Add(i1); tris.Add(i0);
            }
        }

        // Where the line inset d from one edge meets the adjacent edge `edge`: d / sin(120°) from the
        // shared corner toward that edge's other corner. atEnd: the shared corner is the end of `edge`.
        private static Vector3 AlongEdge(HexCell cell, int edge, Vector2 corner, Vector2 other, float d,
                                         float radius, float apothem, bool atEnd)
        {
            float t = Mathf.Clamp01(d / 0.8660254f / radius);
            var p = Vector2.Lerp(corner, other, t);
            return Point(cell, edge, atEnd ? 1f - t : t, p, apothem, apothem);
        }

        private static Vector2 Corner(int i, float radius)
        {
            float angle = Mathf.Deg2Rad * 60f * (i % 6);
            return new Vector2(Mathf.Sin(angle), Mathf.Cos(angle)) * radius;
        }

        // Point on the tile's top surface (cell-local), following the slope a land tile has toward its
        // rim like HexGrid.LocalGround. f = 0..1 along edge e; dist = distance from the tile centre
        // toward the edge.
        private static Vector3 Point(HexCell cell, int e, float f, Vector2 p, float dist, float apothem)
        {
            float y = cell.SurfaceHeight;
            var rim = cell.RimHeights;
            if (rim != null)
            {
                float edgeY = f < 0.5f ? Mathf.Lerp(rim[2 * e], rim[2 * e + 1], f * 2f)
                                       : Mathf.Lerp(rim[2 * e + 1], rim[(2 * e + 2) % 12], f * 2f - 1f);
                float s = Mathf.Clamp01(Mathf.InverseLerp(apothem * TileSolid, apothem, dist));
                y += (edgeY - cell.SurfaceHeight) * s;
            }
            return new Vector3(p.x, y + Lift, p.y);
        }

        // Neighbour across each edge (edge e faces 60e + 30 degrees clockwise from +Z), null at the
        // poles. Mirrors HexGrid.EdgeNeighbors, using unit-size coordinates.
        private static HexCell[] EdgeNeighbors(HexCell cell, HexGrid grid)
        {
            var result    = new HexCell[6];
            float wrap    = Mathf.Sqrt(3f) * grid.Width;
            var here      = cell.Coordinates.ToWorldPosition(1f);
            foreach (var n in grid.GetNeighbors(cell))
            {
                var d = n.Coordinates.ToWorldPosition(1f) - here;
                d.x -= Mathf.Round(d.x / wrap) * wrap;
                float angle = Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;
                result[((Mathf.RoundToInt((angle - 30f) / 60f) % 6) + 6) % 6] = n;
            }
            return result;
        }
    }

    // Frees a generated mesh along with its GameObject
    public class DestroyMeshWithObject : MonoBehaviour
    {
        private void OnDestroy()
        {
            var filter = GetComponent<MeshFilter>();
            if (filter != null && filter.sharedMesh != null) Destroy(filter.sharedMesh);
        }
    }
}
