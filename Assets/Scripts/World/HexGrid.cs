using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    public class HexGrid : MonoBehaviour
    {
        public static HexGrid Instance { get; private set; }

        [SerializeField] private int width = 60;
        [SerializeField] private int height = 40;
        [SerializeField] private float cellSize = 1f;
        [SerializeField] private HexCell cellPrefab;
        [SerializeField] private TerrainType defaultTerrain;

        private HexCell[,] cells;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        public void Generate()
        {
            cells = new HexCell[width, height];
            for (int r = 0; r < height; r++)
            {
                for (int q = 0; q < width; q++)
                {
                    CreateCell(q, r);
                }
            }
            Debug.Log($"[HexGrid] Generated {width}×{height} grid ({width * height} cells)");
        }

        private void CreateCell(int col, int row)
        {
            var coords = HexCoordinates.FromOffsetCoordinates(col, row);
            var worldPos = coords.ToWorldPosition(cellSize);

            var cell = Instantiate(cellPrefab, worldPos, Quaternion.identity, transform);
            cell.name = $"Cell{coords}";
            cell.Initialize(coords, defaultTerrain);
            cells[col, row] = cell;
        }

        public HexCell GetCell(int col, int row)
        {
            if (col < 0 || col >= width || row < 0 || row >= height) return null;
            return cells[col, row];
        }

        public HexCell GetCell(HexCoordinates coords)
        {
            int col = coords.Q + (coords.R - (coords.R & 1)) / 2;
            int row = coords.R;
            return GetCell(col, row);
        }

        public List<HexCell> GetNeighbors(HexCell cell)
        {
            var result = new List<HexCell>(6);
            for (int i = 0; i < 6; i++)
            {
                var neighbor = GetCell(cell.Coordinates.Neighbor(i));
                if (neighbor != null) result.Add(neighbor);
            }
            return result;
        }

        public List<HexCell> GetCellsInRange(HexCell origin, int range)
        {
            var result = new List<HexCell>();
            for (int q = -range; q <= range; q++)
            {
                for (int r = Mathf.Max(-range, -q - range); r <= Mathf.Min(range, -q + range); r++)
                {
                    var coords = origin.Coordinates + new HexCoordinates(q, r);
                    var cell = GetCell(coords);
                    if (cell != null) result.Add(cell);
                }
            }
            return result;
        }
    }
}
