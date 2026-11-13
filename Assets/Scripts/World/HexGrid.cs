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

        // The map wraps east–west (a cylinder): column -1 is column width-1. Cells are moved by
        // whole map widths to whichever copy of the world is nearest the camera (RecenterWrap).
        public float WrapWidth => Mathf.Sqrt(3f) * cellSize * width;

        [SerializeField] private int width = 50;
        [SerializeField] private int height = 80;
        [SerializeField] private float cellSize = 1f;
        [SerializeField] private HexCell cellPrefab;
        [SerializeField] private TerrainType defaultTerrain;
        [SerializeField] private int seed = 0;          // 0 = random each Play
        [SerializeField] private int previewSeed = 12345; // used in Edit mode when seed is 0
        [SerializeField] private float elevationStep = 0.07f; // world height of one terrace level (kept small so land reads as continuous)

        private HexCell[,] cells;
        private Mesh sharedHexMesh;
        private readonly Dictionary<float, Mesh> meshCache = new();
        private readonly List<Mesh> featureMeshes = new();
        private Material featureMaterial;
        private float wrapFocusX = float.NaN; // local X the cells were last recentred around

        // Meshes per pooled prop type (forests, reefs, grass…). Each placement also gets a random
        // rotation, scale, mirroring and tint. Mountains and volcanoes are built per tile instead.
        private const int FeatureVariants = 12;

        private const float TileRadius = 0.985f; // tile size relative to cellSize; the rest is a thin groove between tiles
        private const float TileBevel  = 0.06f;  // width of each tile's rounded top edge, relative to cellSize
        private const float TileBlendWidth = 0.35f; // how far terrain fades into its neighbour from each edge, relative to cellSize

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
            sharedHexMesh = HexMeshGenerator.Create(cellSize * TileRadius);
            sharedHexMesh.hideFlags = HideFlags.DontSave;
            cells = new HexCell[width, height];
            for (int r = 0; r < height; r++)
                for (int q = 0; q < width; q++)
                    CreateCell(q, r);
            Debug.Log($"[HexGrid] Generated {width}×{height} grid ({width * height} cells)");

            WorldGenerator.Generate(cells, width, height, worldSeed);
            UpdateCellMeshes();
            PlaceFeatures(worldSeed);
            UpdateEdgeBlends();
            wrapFocusX = float.NaN; // new cells sit in the base copy; recentre on the next call
            Generated?.Invoke();
        }

        // Puts mountain peaks and forests on top of the tiles and gives every tile its colour
        // variation. Seeded from the world seed, so a regenerated map (e.g. a loaded save) looks the same.
        private void PlaceFeatures(int worldSeed)
        {
            if (featureMaterial == null) featureMaterial = Resources.Load<Material>("Materials/MapFeatures");
            if (featureMaterial == null)
            {
                Debug.LogWarning("[HexGrid] Resources/Materials/MapFeatures not found; skipping mountains and forests.");
                return;
            }

            var rng = new System.Random(worldSeed);
            var broadleaf  = CreateFeatureVariants(() => MapFeatureMeshes.CreateForest(rng, cellSize, conifer: false));
            var conifers   = CreateFeatureVariants(() => MapFeatureMeshes.CreateForest(rng, cellSize, conifer: true));
            var jungles    = CreateFeatureVariants(() => MapFeatureMeshes.CreateJungle(rng, cellSize));
            var reefs      = CreateFeatureVariants(() => MapFeatureMeshes.CreateReef(rng, cellSize));
            var oases      = CreateFeatureVariants(() => MapFeatureMeshes.CreateOasis(rng, cellSize));
            // Small terrain props (grass, rocks, dunes…) for cells without a feature
            var details = new Dictionary<TerrainKind, Mesh[]>();
            foreach (TerrainKind kind in System.Enum.GetValues(typeof(TerrainKind)))
            {
                var variants = CreateFeatureVariants(() => MapFeatureMeshes.CreateDetail(rng, cellSize, kind));
                if (variants != null) details[kind] = variants;
            }

            var oceanDepth  = DistanceFromLand(6);
            var noiseOffset = new Vector3((float)rng.NextDouble(), (float)rng.NextDouble(), (float)rng.NextDouble()) * 1000f;
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);
            Mesh Pick(Mesh[] pool) => pool[rng.Next(pool.Length)];

            int mountains = 0, forests = 0, others = 0;
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null) continue;
                cell.SetTintVariation(TileTint(cell, oceanDepth[q, r], rng, noiseOffset));

                Mesh mesh   = null;
                bool unique = false;
                switch (cell.Feature)
                {
                    case TerrainFeature.Volcano:
                        mesh = Track(MapFeatureMeshes.CreateVolcano(rng, cellSize, R(0.8f, 1.25f))); unique = true; others++;
                        break;
                    case TerrainFeature.ConiferForest:   mesh = Pick(conifers);  forests++; break;
                    case TerrainFeature.BroadleafForest: mesh = Pick(broadleaf); forests++; break;
                    case TerrainFeature.Jungle:          mesh = Pick(jungles);   forests++; break;
                    case TerrainFeature.Reef:            mesh = Pick(reefs);     others++;  break;
                    case TerrainFeature.Oasis:           mesh = Pick(oases);     others++;  break;
                    default:
                        if (cell.IsMountain) { mesh = Track(CreateMountainFor(cell, r, rng)); unique = true; mountains++; }
                        else if (details.TryGetValue(cell.Terrain.kind, out var d) && rng.NextDouble() < 0.75) mesh = Pick(d);
                        break;
                }
                if (mesh == null) continue;

                // Pooled meshes get a random size, height and mirror image so neighbours never match
                float s   = unique ? 1f : R(0.85f, 1.08f);
                var scale = new Vector3(s * (!unique && rng.NextDouble() < 0.5 ? -1f : 1f), s * (unique ? 1f : R(0.85f, 1.2f)), s);
                float v   = R(0.9f, 1.08f);
                var tint  = new Color(v * R(0.96f, 1.04f), v, v * R(0.96f, 1.04f));
                AddFeatureObject(cell, mesh, R(0f, 360f), scale, tint);
            }
            Debug.Log($"[HexGrid] PlaceFeatures — {mountains} mountains, {forests} forests/jungles, {others} volcanoes/reefs/oases");
        }

        // Each mountain is unique: taller in the middle of a range, rock coloured by the land around
        // it (red sandstone near deserts, blue-grey near ice, grey/brown/dark elsewhere), snowier
        // toward the poles, and pines at the foot only where the neighbours are green.
        private Mesh CreateMountainFor(HexCell cell, int row, System.Random rng)
        {
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);
            int ridge = 0, dry = 0, cold = 0, green = 0;
            foreach (var n in GetNeighbors(cell))
            {
                if (n.Terrain == null) continue;
                if (n.IsMountain) { ridge++; continue; }
                switch (n.Terrain.kind)
                {
                    case TerrainKind.Desert: case TerrainKind.Savanna: case TerrainKind.Steppe: dry++; break;
                    case TerrainKind.Tundra: case TerrainKind.IceSheet:                         cold++; break;
                    case TerrainKind.Plain:  case TerrainKind.Hill: case TerrainKind.Wetland:
                    case TerrainKind.Rainforest:                                                green++; break;
                }
                if (n.IsForest || n.Feature == TerrainFeature.Jungle) green++;
            }

            bool icy    = cell.Terrain.kind == TerrainKind.IceSheet;
            float lat   = height > 1 ? Mathf.Abs(row / (float)(height - 1) * 2f - 1f) : 0f; // 0 = equator, 1 = pole
            float snow  = icy ? R(0.7f, 0.9f) : Mathf.Clamp01(Mathf.Lerp(0.12f, 0.6f, lat) + R(-0.08f, 0.08f));
            float scale = Mathf.Clamp(0.7f + 0.11f * ridge + R(-0.12f, 0.12f), 0.6f, 1.4f);

            Color rock;
            if (dry > cold && dry >= green) rock = Color.Lerp(new Color(1.3f, 0.95f, 0.72f), new Color(1.15f, 1.0f, 0.8f), R(0f, 1f));
            else if (cold > green)          rock = new Color(0.92f, 0.96f, 1.06f);
            else rock = rng.Next(3) switch
            {
                0 => Color.white,
                1 => new Color(1.1f, 1.0f, 0.88f),
                _ => new Color(0.82f, 0.82f, 0.85f),
            };
            return MapFeatureMeshes.CreateMountain(rng, cellSize, snow, scale, rock, allowTrees: !icy && green >= 2);
        }

        // Colour multiplier for a tile. Ocean goes from turquoise shallows to deep blue with distance
        // from land; land drifts by region (seamless noise around the wrapped map) plus per-tile
        // jitter, and deserts drift between pale, golden and red sand.
        private Color TileTint(HexCell cell, int oceanDepth, System.Random rng, Vector3 noiseOffset)
        {
            var pos     = cell.Coordinates.ToWorldPosition(cellSize);
            float angle = pos.x / WrapWidth * Mathf.PI * 2f;
            float rad   = WrapWidth / (Mathf.PI * 2f);
            var p       = new Vector3(Mathf.Cos(angle) * rad, Mathf.Sin(angle) * rad, pos.z) + noiseOffset;
            float regional = Mathf.Clamp01(0.5f + 0.5f * (0.7f * PerlinNoise3D.Sample(p.x * 0.06f, p.y * 0.06f, p.z * 0.06f)
                                                       + 0.3f * PerlinNoise3D.Sample(p.x * 0.2f,  p.y * 0.2f,  p.z * 0.2f)) * 1.6f);
            float jitter = 0.94f + 0.12f * (float)rng.NextDouble();

            switch (cell.Terrain.kind)
            {
                case TerrainKind.SaltWater:
                    float deep = Mathf.Sqrt(Mathf.InverseLerp(1f, 6f, oceanDepth));
                    var sea = Color.Lerp(new Color(1.45f, 1.55f, 1.2f), new Color(0.58f, 0.68f, 0.88f), deep);
                    return sea * Mathf.Lerp(0.94f, 1.06f, regional) * (0.97f + 0.06f * (float)rng.NextDouble());
                case TerrainKind.FreshWater:
                    return Color.Lerp(new Color(0.9f, 1.05f, 1.0f), new Color(1.1f, 1.0f, 0.92f), regional) * jitter;
                case TerrainKind.Desert:
                    var sand = regional < 0.5f
                        ? Color.Lerp(new Color(1.15f, 1.12f, 1.0f), Color.white, regional * 2f)
                        : Color.Lerp(Color.white, new Color(1.12f, 0.82f, 0.66f), (regional - 0.5f) * 2f);
                    return sand * jitter;
                default:
                    return Color.Lerp(new Color(0.88f, 1.0f, 0.95f), new Color(1.1f, 1.0f, 0.86f), regional) * jitter;
            }
        }

        // Tells every tile which terrain lies across each of its edges so the terrain shader can fade
        // into it. Land blends only with land and water only with water, so coastlines stay crisp.
        private void UpdateEdgeBlends()
        {
            Shader.SetGlobalFloat("_HexApothem", cellSize * TileRadius * 0.8660254f);
            Shader.SetGlobalFloat("_HexBlendWidth", cellSize * TileBlendWidth);

            var textures = new Texture[6];
            var tints    = new Vector4[6];
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null) continue;
                System.Array.Clear(textures, 0, 6);
                System.Array.Clear(tints, 0, 6);

                var here = cell.Coordinates.ToWorldPosition(cellSize);
                foreach (var n in GetNeighbors(cell))
                {
                    if (n.Terrain == null || n.IsWater != cell.IsWater) continue;
                    var d = n.Coordinates.ToWorldPosition(cellSize) - here;
                    d.x -= Mathf.Round(d.x / WrapWidth) * WrapWidth; // neighbour across the wrap seam
                    float angle = Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;
                    int edge = ((Mathf.RoundToInt((angle - 30f) / 60f) % 6) + 6) % 6;
                    var tint = n.BlendTint;
                    textures[edge] = n.BlendTexture;
                    tints[edge]    = new Vector4(tint.r, tint.g, tint.b, 1f);
                }
                cell.SetEdgeBlends(textures, tints);
            }
        }

        // Hex steps from each salt-water cell to the nearest other cell, capped at maxDist (non-ocean = 0).
        private int[,] DistanceFromLand(int maxDist)
        {
            var dist  = new int[width, height];
            var queue = new Queue<(int q, int r)>();
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var terrain = cells[q, r].Terrain;
                bool ocean  = terrain != null && terrain.kind == TerrainKind.SaltWater;
                dist[q, r]  = ocean ? maxDist : 0;
                if (!ocean) queue.Enqueue((q, r));
            }
            while (queue.Count > 0)
            {
                var (q, r) = queue.Dequeue();
                int d = dist[q, r] + 1;
                if (d >= maxDist) continue;
                foreach (var n in GetNeighbors(cells[q, r]))
                {
                    int nr = n.Coordinates.R;
                    int nq = ((n.Coordinates.Q + (nr - (nr & 1)) / 2) % width + width) % width;
                    if (dist[nq, nr] <= d) continue;
                    dist[nq, nr] = d;
                    queue.Enqueue((nq, nr));
                }
            }
            return dist;
        }

        // Null if `create` returns null (e.g. a terrain with no detail props).
        private Mesh[] CreateFeatureVariants(System.Func<Mesh> create)
        {
            var variants = new Mesh[FeatureVariants];
            for (int i = 0; i < variants.Length; i++)
            {
                variants[i] = create();
                if (variants[i] == null) return null;
                Track(variants[i]);
            }
            return variants;
        }

        // Registers a generated mesh so ClearCells destroys it.
        private Mesh Track(Mesh mesh)
        {
            mesh.hideFlags = HideFlags.DontSave;
            featureMeshes.Add(mesh);
            return mesh;
        }

        // No collider: clicks pass through the prop to the hex tile underneath.
        // A negative scale.x mirrors the prop; Unity flips culling for it automatically.
        private void AddFeatureObject(HexCell cell, Mesh mesh, float yaw, Vector3 scale, Color tint)
        {
            var go = new GameObject(mesh.name);
            if (!Application.isPlaying) go.hideFlags = HideFlags.DontSave;
            go.transform.SetParent(cell.transform, false);
            go.transform.localPosition = Vector3.up * cell.SurfaceHeight;
            go.transform.localRotation = Quaternion.Euler(0f, yaw, 0f);
            go.transform.localScale    = scale;
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = featureMaterial;
            var block = new MaterialPropertyBlock();
            block.SetColor("_Color", tint);
            mr.SetPropertyBlock(block);
        }

        // Water sits flat near sea level; land rises one elevationStep per terrace level.
        private float CellVisualHeight(HexCell cell) => cell.Terrain.kind switch
        {
            TerrainKind.SaltWater  => 0.02f,
            TerrainKind.FreshWater => 0.06f,
            _                      => 0.12f + cell.Elevation * elevationStep,
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
                    mesh = HexMeshGenerator.Create(cellSize * TileRadius, h, cellSize * TileBevel);
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

        // Columns wrap around; rows don't (the poles are edges).
        public HexCell GetCell(int col, int row)
        {
            if (cells == null || width <= 0 || row < 0 || row >= height) return null;
            col = ((col % width) + width) % width;
            return cells[col, row];
        }

        // Shifts each cell by a whole number of map widths so it lies within half a map width
        // of worldFocusX (normally the point the camera looks at). Called every frame by the
        // camera; only does work when the focus has moved.
        public void RecenterWrap(float worldFocusX)
        {
            if (cells == null) return;
            float focus = worldFocusX - transform.position.x;
            if (Mathf.Abs(focus - wrapFocusX) < 0.01f) return;
            wrapFocusX = focus;

            float wrap = WrapWidth;
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                var basePos = cell.Coordinates.ToWorldPosition(cellSize);
                float shift = Mathf.Round((focus - basePos.x) / wrap) * wrap;
                if (Mathf.Abs(cell.transform.localPosition.x - (basePos.x + shift)) < 0.001f) continue;
                cell.transform.localPosition = basePos + Vector3.right * shift;
                cell.SetWrapShift(shift);
            }
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
