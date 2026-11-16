using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // The land in the under view: one flat, raised plateau standing well above the seabed, so where
    // the sea floor meets it there is a clear wall (sea animals can see they can't go on), and its
    // top is the ground the underground animals live on. Groundwater lies in shallow basins sunk into
    // it: buried lakes lake-blue, old sea floors under the land their seabed colour.
    public partial class HexGrid
    {
        private const float PlateauHeight  = 0.26f; // above the sea surface (0.02): some four terrace steps over the shore
        private const float GroundwaterDip = 0.06f; // groundwater basins lie this far below the plateau

        private readonly Dictionary<HexCell, Mesh> landSurfaceMeshes = new();
        private readonly Dictionary<int, Mesh> plateauMeshCache = new();

        // Lake-blue groundwater under the land (HexGrid.UnderTint; its stromatolites take it too)
        private static readonly Color Groundwater = MapFeatureMeshes.Groundwater;

        // Height of the floor of a land tile in the under view
        private float PlateauSurface(HexCell cell) => WaterBed(cell.Under) ? PlateauHeight - GroundwaterDip : PlateauHeight;

        // A flat hexagonal prism at height h, its walls reaching down below the deepest seabed
        private Mesh PlateauMesh(float h)
        {
            int key = Mathf.RoundToInt(h * 10000f);
            if (plateauMeshCache.TryGetValue(key, out var mesh) && mesh != null) return mesh;
            var corners = new float[6]; var edges = new float[6]; var joined = new bool[6];
            for (int i = 0; i < 6; i++) corners[i] = edges[i] = h + WallBottom;
            // CreateSloped builds walls down to y = 0: build it raised by WallBottom, then lower it
            mesh = HexMeshGenerator.CreateSloped(cellSize * TileRadius, cellSize, h + WallBottom, TileSolid, corners, edges, joined);
            var v = mesh.vertices;
            for (int i = 0; i < v.Length; i++) v[i].y -= WallBottom;
            mesh.vertices = v;
            mesh.RecalculateBounds();
            mesh.name = "Plateau";
            mesh.hideFlags = HideFlags.DontSave;
            plateauMeshCache[key] = mesh;
            return mesh;
        }

        // Swap land tiles' meshes (and colliders) between the surface relief and the plateau
        private void ShowPlateau(bool on)
        {
            if (cells == null) return;
            foreach (var cell in cells)
            {
                if (cell?.Terrain == null || cell.IsWater) continue;
                var mf = cell.GetComponent<MeshFilter>();
                var mc = cell.GetComponent<MeshCollider>();
                if (mf == null) continue;
                if (on)
                {
                    if (mf.sharedMesh != null && mf.sharedMesh.name != "Plateau") landSurfaceMeshes[cell] = mf.sharedMesh; // remember the surface tile
                    var m = SmoothTileMesh(cell, false); // one smooth plateau, walled at the coast (HexGrid.Seabed)
                    mf.sharedMesh = m;
                    if (mc != null) mc.sharedMesh = m;
                }
                else if (landSurfaceMeshes.TryGetValue(cell, out var s) && s != null)
                {
                    mf.sharedMesh = s;
                    if (mc != null) mc.sharedMesh = s;
                }
            }
            if (!on) landSurfaceMeshes.Clear();
        }
    }
}
