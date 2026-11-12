using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    public class HexGrid : MonoBehaviour
    {
        public static HexGrid Instance { get; private set; }

        [SerializeField] private int width = 12;
        [SerializeField] private int height = 8;
        [SerializeField] private float cellSize = 1f;
        [SerializeField] private HexCell cellPrefab;
        [SerializeField] private TerrainType defaultTerrain;
        [SerializeField] private int seed = 0;

        private HexCell[,] cells;
        private Mesh sharedHexMesh;
        private readonly Dictionary<float, Mesh> meshCache = new();

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            if (cellPrefab != null && defaultTerrain != null)
                Generate();
            else
                Debug.LogWarning("[HexGrid] Assign cellPrefab and defaultTerrain in the Inspector before entering Play mode.");
        }

        public void Generate()
        {
            sharedHexMesh = HexMeshGenerator.Create(cellSize * 0.95f);
            cells = new HexCell[width, height];
            for (int r = 0; r < height; r++)
                for (int q = 0; q < width; q++)
                    CreateCell(q, r);
            Debug.Log($"[HexGrid] Generated {width}×{height} grid ({width * height} cells)");

            WorldGenerator.Generate(cells, width, height, seed == 0 ? System.Environment.TickCount : seed);
            UpdateCellMeshes();
        }

        private static float TerrainVisualHeight(TerrainKind kind) => kind switch
        {
            TerrainKind.Mountain   => 1.6f,
            TerrainKind.IceSheet   => 1.0f,
            TerrainKind.Hill       => 0.7f,
            TerrainKind.Tundra     => 0.4f,
            TerrainKind.Plain      => 0.2f,
            TerrainKind.Desert     => 0.15f,
            TerrainKind.Wetland    => 0.12f,
            TerrainKind.FreshWater => 0.06f,
            TerrainKind.SaltWater  => 0.02f,
            _                      => 0.2f,
        };

        private void UpdateCellMeshes()
        {
            int updated = 0;
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null) continue;
                var h = TerrainVisualHeight(cell.Terrain.kind);
                if (!meshCache.TryGetValue(h, out var mesh))
                {
                    mesh = HexMeshGenerator.Create(cellSize * 0.95f, h);
                    meshCache[h] = mesh;
                }
                var mf = cell.GetComponent<MeshFilter>();
                var mc = cell.GetComponent<MeshCollider>();
                if (mf != null) { mf.mesh = null; mf.sharedMesh = mesh; updated++; }
                if (mc != null) mc.sharedMesh = mesh;
            }
            Debug.Log($"[HexGrid] UpdateCellMeshes — updated {updated} cells, {meshCache.Count} unique heights");
        }

        private void CreateCell(int col, int row)
        {
            var coords   = HexCoordinates.FromOffsetCoordinates(col, row);
            var worldPos = coords.ToWorldPosition(cellSize);

            var cell = Instantiate(cellPrefab, worldPos, Quaternion.identity, transform);
            cell.name = $"Cell{coords}";

            var mf = cell.GetComponent<MeshFilter>();
            if (mf != null) mf.mesh = sharedHexMesh;

            var mc = cell.GetComponent<MeshCollider>();
            if (mc == null) mc = cell.gameObject.AddComponent<MeshCollider>();
            mc.sharedMesh = sharedHexMesh;

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
