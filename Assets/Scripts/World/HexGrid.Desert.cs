using UnityEngine;

namespace NaturalHistory.World
{
    // Deserts show one of three sands, in broad regions: dense, fine ripples; the ordinary pattern;
    // or sparse, smooth sand with only faint wind streaks. Desert tiles and their land neighbours
    // blend across tile edges (the terrain shader's _CellBlend), so the sands change without a seam.
    public partial class HexGrid
    {
        private Material desertDense, desertSparse;

        private void DressDesertGround()
        {
            desertDense  ??= Resources.Load<Material>("Materials/Ground/DesertDense");
            desertSparse ??= Resources.Load<Material>("Materials/Ground/DesertSparse");
            var offset = new Vector3(97f, 431f, 263f) + Vector3.one * (WorldSeed % 991);
            foreach (var cell in cells) cell?.SetCellBlend(false);
            foreach (var cell in cells)
            {
                if (cell?.Terrain == null || cell.Terrain.kind != TerrainKind.Desert || cell.IsMountain) continue;
                var pos = cell.Coordinates.ToWorldPosition(cellSize);
                var p = OnMapLoop(new Vector2(pos.x, pos.z)) * (0.2f / cellSize) + offset;
                float n = PerlinNoise3D.Sample(p.x, p.y, p.z);
                // ±0.128 splits PerlinNoise3D's values into thirds
                var mat = n < -0.128f ? desertDense : n > 0.128f ? desertSparse : null;
                if (mat != null) cell.SetGroundMaterial(mat);
                cell.SetCellBlend(true);
                foreach (var nb in GetNeighbors(cell))
                    if (nb?.Terrain != null && !nb.IsWater && !nb.IsMountain) nb.SetCellBlend(true);
            }
        }
    }
}
