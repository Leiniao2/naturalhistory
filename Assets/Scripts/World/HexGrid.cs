using System;
using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // ExecuteAlways: the map is also built in Edit mode so it is visible in the
    // Scene/Game views without pressing Play. Edit-mode cells are DontSave, so they
    // never get written into Game.unity.
    [ExecuteAlways]
    public class HexGrid : MonoBehaviour
    {
        public static HexGrid Instance { get; private set; }

        // Raised after every Generate(); listeners place units on the new map
        public event Action Generated;
        public bool IsGenerated => cells != null;
        public int Width => width;
        public int Height => height;
        public int WorldSeed { get; private set; } // seed of the current map; saves store this instead of every cell

        // World-space XZ extent of all cell centers (x → Rect.x, z → Rect.y).
        // Odd rows are shifted right by half a cell (offset coordinates).
        public Rect MapRectXZ
        {
            get
            {
                float xMax = Mathf.Sqrt(3f) * cellSize * (width - 1 + (height > 1 ? 0.5f : 0f));
                float zMax = 1.5f * cellSize * (height - 1);
                var origin = transform.position;
                return new Rect(origin.x, origin.z, xMax, zMax);
            }
        }

        [SerializeField] private int width = 20;
        [SerializeField] private int height = 30;
        [SerializeField] private float cellSize = 1f;
        [SerializeField] private HexCell cellPrefab;
        [SerializeField] private TerrainType defaultTerrain;
        [SerializeField] private int seed = 0;          // 0 = random each Play
        [SerializeField] private int previewSeed = 12345; // used in Edit mode when seed is 0
        [SerializeField] private float elevationStep = 0.2f; // world height of one terrace level

        private HexCell[,] cells;
        private Mesh sharedHexMesh;
        private readonly Dictionary<float, Mesh> meshCache = new();
        private readonly List<Mesh> featureMeshes = new();
        private Material featureMaterial;

        private const int FeatureVariants = 4; // distinct meshes per prop type, reused with random rotation

        private void Awake()
        {
            if (!Application.isPlaying) return;
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            if (!Application.isPlaying) return;
            if (cellPrefab != null && defaultTerrain != null)
                Generate();
            else
                Debug.LogWarning("[HexGrid] Assign cellPrefab and defaultTerrain in the Inspector before entering Play mode.");
        }

#if UNITY_EDITOR
        private void OnEnable()
        {
            if (!Application.isPlaying) SchedulePreview();
        }

        private void OnDisable()
        {
            if (!Application.isPlaying) ClearCells();
        }

        // Inspector changes (size, seed…) rebuild the preview. Instantiate is not
        // allowed inside OnValidate, so defer to the next editor tick.
        private void OnValidate()
        {
            if (!Application.isPlaying) SchedulePreview();
        }

        private void SchedulePreview()
        {
            UnityEditor.EditorApplication.delayCall -= BuildPreview;
            UnityEditor.EditorApplication.delayCall += BuildPreview;
        }

        private void BuildPreview()
        {
            if (this == null || !isActiveAndEnabled || Application.isPlaying) return;
            if (cellPrefab == null || defaultTerrain == null) return;
            Generate();
        }

        [ContextMenu("Regenerate Preview")]
        private void RegeneratePreview() => BuildPreview();
#endif

        // Destroys any previously generated cells and meshes (Edit-mode preview or an earlier Generate call).
        private void ClearCells()
        {
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                var child = transform.GetChild(i).gameObject;
                if (Application.isPlaying) Destroy(child); else DestroyImmediate(child);
            }
            foreach (var mesh in meshCache.Values) DestroyMesh(mesh);
            meshCache.Clear();
            foreach (var mesh in featureMeshes) DestroyMesh(mesh);
            featureMeshes.Clear();
            DestroyMesh(sharedHexMesh);
            sharedHexMesh = null;
            cells = null;
        }

        private static void DestroyMesh(Mesh mesh)
        {
            if (mesh == null) return;
            if (Application.isPlaying) Destroy(mesh); else DestroyImmediate(mesh);
        }

        public void Generate()
        {
            int worldSeed = seed != 0 ? seed : Application.isPlaying ? System.Environment.TickCount : previewSeed;
            Generate(width, height, worldSeed);
        }

        // Rebuilds the map at a given size from a known seed (used when loading a save).
        public void Generate(int cols, int rows, int worldSeed)
        {
            width  = cols;
            height = rows;
            WorldSeed = worldSeed;
            ClearCells();
            sharedHexMesh = HexMeshGenerator.Create(cellSize * 0.95f);
            sharedHexMesh.hideFlags = HideFlags.DontSave;
            cells = new HexCell[width, height];
            for (int r = 0; r < height; r++)
                for (int q = 0; q < width; q++)
                    CreateCell(q, r);
            Debug.Log($"[HexGrid] Generated {width}×{height} grid ({width * height} cells)");

            WorldGenerator.Generate(cells, width, height, worldSeed);
            UpdateCellMeshes();
            PlaceFeatures(worldSeed);
            Generated?.Invoke();
        }

        // Puts mountain peaks and forests on top of the tiles. Seeded from the world seed,
        // so a regenerated map (e.g. a loaded save) looks the same.
        private void PlaceFeatures(int worldSeed)
        {
            if (featureMaterial == null) featureMaterial = Resources.Load<Material>("Materials/MapFeatures");
            if (featureMaterial == null)
            {
                Debug.LogWarning("[HexGrid] Resources/Materials/MapFeatures not found; skipping mountains and forests.");
                return;
            }

            var rng = new System.Random(worldSeed);
            var rockyPeaks = CreateFeatureVariants(() => MapFeatureMeshes.CreateMountain(rng, cellSize, snowLine: 0.35f));
            var icyPeaks   = CreateFeatureVariants(() => MapFeatureMeshes.CreateMountain(rng, cellSize, snowLine: 0.75f));
            var broadleaf  = CreateFeatureVariants(() => MapFeatureMeshes.CreateForest(rng, cellSize, conifer: false));
            var conifers   = CreateFeatureVariants(() => MapFeatureMeshes.CreateForest(rng, cellSize, conifer: true));

            int mountains = 0, forests = 0;
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null) continue;

                Mesh[] pool;
                if (cell.IsMountain) { pool = cell.Terrain.kind == TerrainKind.IceSheet ? icyPeaks : rockyPeaks; mountains++; }
                else if (cell.Feature == TerrainFeature.ConiferForest)   { pool = conifers;  forests++; }
                else if (cell.Feature == TerrainFeature.BroadleafForest) { pool = broadleaf; forests++; }
                else continue;

                AddFeatureObject(cell, pool[rng.Next(pool.Length)], (float)rng.NextDouble() * 360f);
            }
            Debug.Log($"[HexGrid] PlaceFeatures — {mountains} mountains, {forests} forests");
        }

        private Mesh[] CreateFeatureVariants(System.Func<Mesh> create)
        {
            var variants = new Mesh[FeatureVariants];
            for (int i = 0; i < variants.Length; i++)
            {
                variants[i] = create();
                variants[i].hideFlags = HideFlags.DontSave;
                featureMeshes.Add(variants[i]);
            }
            return variants;
        }

        // No collider: clicks pass through the prop to the hex tile underneath.
        private void AddFeatureObject(HexCell cell, Mesh mesh, float yaw)
        {
            var go = new GameObject(mesh.name);
            if (!Application.isPlaying) go.hideFlags = HideFlags.DontSave;
            go.transform.SetParent(cell.transform, false);
            go.transform.localPosition = Vector3.up * cell.SurfaceHeight;
            go.transform.localRotation = Quaternion.Euler(0f, yaw, 0f);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = featureMaterial;
        }

        // Water sits flat near sea level; land rises one elevationStep per terrace level.
        private float CellVisualHeight(HexCell cell) => cell.Terrain.kind switch
        {
            TerrainKind.SaltWater  => 0.02f,
            TerrainKind.FreshWater => 0.06f,
            _                      => 0.1f + cell.Elevation * elevationStep,
        };

        private void UpdateCellMeshes()
        {
            int updated = 0;
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null) continue;
                var h = CellVisualHeight(cell);
                cell.SetSurfaceHeight(h);
                if (!meshCache.TryGetValue(h, out var mesh))
                {
                    mesh = HexMeshGenerator.Create(cellSize * 0.95f, h);
                    mesh.hideFlags = HideFlags.DontSave;
                    meshCache[h] = mesh;
                }
                var mf = cell.GetComponent<MeshFilter>();
                var mc = cell.GetComponent<MeshCollider>();
                if (mf != null) { mf.sharedMesh = mesh; updated++; }
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
            if (!Application.isPlaying) cell.gameObject.hideFlags = HideFlags.DontSave;

            var mf = cell.GetComponent<MeshFilter>();
            if (mf != null) mf.sharedMesh = sharedHexMesh;

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
