using System;
using System.Collections.Generic;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.World
{
    // ExecuteAlways: the map is also built in Edit mode so it is visible in the
    // Scene/Game views without pressing Play. Edit-mode cells are DontSave, so they
    // never get written into Game.unity.
    [ExecuteAlways]
    public partial class HexGrid : MonoBehaviour
    {
        public static HexGrid Instance { get; private set; }

        // Raised after every Generate(); listeners place units on the new map
        public event Action Generated;
        // Raised when the map is re-dressed for another geological period (terrain kinds, forests
        // and props change; land, water and elevation stay the same)
        public event Action TerrainChanged;
        // Period whose ground cover and plants the map currently shows (see EraFlora)
        public GeologicalAge DisplayedAge { get; private set; }
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
        [SerializeField] private int height = 30;
        [SerializeField] private float cellSize = 1f;
        [SerializeField] private HexCell cellPrefab;
        [SerializeField] private TerrainType defaultTerrain;
        [SerializeField] private int seed = 0;          // 0 = random each Play
        [SerializeField] private int previewSeed = 12345; // used in Edit mode when seed is 0
        [SerializeField] private float elevationStep = 0.2f;  // world height of one terrace level (tiles slope into each other, so land still reads as continuous)
        [Tooltip("Period whose plants the Edit-mode preview shows. In Play mode the map follows AgeManager.")]
        [SerializeField] private GeologicalAge previewAge = GeologicalAge.Quaternary;

        private HexCell[,] cells;
        private Mesh sharedHexMesh;
        private readonly Dictionary<string, Mesh> meshCache = new(); // keyed by height (water) or height + rim (land)
        private readonly List<Mesh> featureMeshes = new();
        private readonly List<GameObject> featureObjects = new(); // props only; cells also carry colonies and markers
        private Dictionary<TerrainKind, TerrainType> terrainTypes;
        private Vector3 reliefOffset; // mountain relief noise, from the world seed
        private Material featureMaterial;
        private float wrapFocusX = float.NaN; // local X the cells were last recentred around

        // Meshes per pooled prop type (forests, reefs, grass…). Each placement also gets a random
        // rotation, scale, mirroring and tint. Mountains and volcanoes are built per tile instead.
        private const int FeatureVariants = 12;

        private const float TileRadius = 0.985f; // tile size relative to cellSize; the rest is a thin groove between tiles
        private const float TileBevel  = 0.06f;  // width of each tile's rounded top edge, relative to cellSize
        private const float TileBlendWidth = 0.35f; // how far terrain fades into its neighbour from each edge, relative to cellSize
        private const int   CliffElevation = 5;      // coastal land this high (hills, mountains) meets the water in a cliff
        private const float ShoreLip       = 0.008f; // lower coasts slope down to just this far above the water they meet: a beach, no step
        private const float TileSolid  = 0.6f;   // flat middle of a land tile, relative to its radius; the rest slopes to meet the neighbours

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
            if (AgeManager.Instance != null) AgeManager.Instance.TimeChanged += OnTimeChanged;
            UnderView.Changed += ApplyUnderView;
        }

        private void OnDestroy()
        {
            if (Application.isPlaying && AgeManager.Instance != null) AgeManager.Instance.TimeChanged -= OnTimeChanged;
            if (Application.isPlaying) UnderView.Changed -= ApplyUnderView;
        }


        // Before AgeManager has started a game its CurrentAge is the first period, which is where
        // a new game begins anyway.
        private GeologicalAge CurrentAge =>
            Application.isPlaying && AgeManager.Instance != null ? AgeManager.Instance.CurrentAge : previewAge;

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
            featureObjects.Clear(); // children of the cells destroyed above
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
            GenerateRivers(worldSeed);
            GenerateUnder(worldSeed);
            UpdateCellMeshes();
            DressForAge(CurrentAge);
            wrapFocusX = float.NaN; // new cells sit in the base copy; recentre on the next call
            Generated?.Invoke();
        }

        // Shows the map as it looked in another geological period: same land, water and elevation,
        // but that period's ground cover, forests and props.
        public void SetAge(GeologicalAge age)
        {
            if (cells == null || age == DisplayedAge) return;
            DressForAge(age);
            Debug.Log($"[HexGrid] Map now shows the {age}");
            TerrainChanged?.Invoke();
        }

        private void DressForAge(GeologicalAge age)
        {
            ApplyClimate(age); // sea level, deserts, tundra, forests, volcanoes of the date (HexGrid.Climate)
            DisplayedAge = age;
            terrainTypes ??= LoadTerrainTypes();
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null) continue;
                var kind = EraFlora.TerrainFor(cell, age);
                if (terrainTypes.TryGetValue(kind, out var terrain)) cell.SetTerrain(terrain);
                else kind = cell.Terrain.kind; // asset missing: keep what the cell has
                var feature = EraFlora.FeatureFor(cell, kind, age);
                if (cell.HasRiver && feature == TerrainFeature.Oasis) feature = TerrainFeature.None; // no pond where a river runs through
                cell.SetFeature(feature);
            }
            PlaceLandforms(age);
            PlaceGeothermal();
            DressMountainGround();
            DressDesertGround(); // dense, ordinary or sparse sand by region (HexGrid.Desert)
            ClearFeatures();
            PlaceFeatures(WorldSeed, age);
            UpdateEdgeBlends();
            DressUnder(age);
            CountShares();
        }

        // A mountain tile's ground (seen where the massif tapers off toward a lowland neighbour)
        // takes the skin of the most common land around it instead of bare mountain rock, so the
        // range doesn't get a grey margin of mountain texture around its foot.
        private void DressMountainGround()
        {
            var counts = new Dictionary<TerrainType, int>();
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null || !cell.IsMountain || cell.Feature == TerrainFeature.Volcano) continue;
                counts.Clear();
                TerrainType best = null;
                foreach (var n in GetNeighbors(cell))
                {
                    if (n.Terrain == null || n.IsWater || n.IsMountain || n.Terrain.material == null) continue;
                    counts[n.Terrain] = counts.TryGetValue(n.Terrain, out int c) ? c + 1 : 1;
                    if (best == null || counts[n.Terrain] > counts[best]) best = n.Terrain;
                }
                if (best != null) cell.SetGroundMaterial(best.material);
            }
        }

        private static Dictionary<TerrainKind, TerrainType> LoadTerrainTypes()
        {
            var types = new Dictionary<TerrainKind, TerrainType>();
            foreach (var t in Resources.LoadAll<TerrainType>("Terrains")) types[t.kind] = t;
            return types;
        }

        private void ClearFeatures()
        {
            foreach (var go in featureObjects)
                if (go != null) { if (Application.isPlaying) Destroy(go); else DestroyImmediate(go); }
            featureObjects.Clear();
            foreach (var mesh in featureMeshes) DestroyMesh(mesh);
            featureMeshes.Clear();
        }

        // Puts mountain peaks and forests on top of the tiles and gives every tile its colour
        // variation. Seeded from the world seed, so a regenerated map (e.g. a loaded save) looks the same.
        private void PlaceFeatures(int worldSeed, GeologicalAge age)
        {
            if (featureMaterial == null) featureMaterial = Resources.Load<Material>("Materials/MapFeatures");
            if (featureMaterial == null)
            {
                Debug.LogWarning("[HexGrid] Resources/Materials/MapFeatures not found; skipping mountains and forests.");
                return;
            }

            var rng = new System.Random(worldSeed);
            var reliefRng = new System.Random(worldSeed ^ 0x2C1B3C6D);
            reliefOffset  = new Vector3((float)reliefRng.NextDouble(), (float)reliefRng.NextDouble(), (float)reliefRng.NextDouble()) * 1000f;
            // The period decides the plants: lycopsids and tree ferns, cycads, Araucaria, flowering trees…
            var broadleaf  = CreateFeatureVariants(() => MapFeatureMeshes.CreateEraForest(rng, cellSize, age, TerrainFeature.BroadleafForest));
            var conifers   = CreateFeatureVariants(() => MapFeatureMeshes.CreateEraForest(rng, cellSize, age, TerrainFeature.ConiferForest));
            var jungles    = CreateFeatureVariants(() => MapFeatureMeshes.CreateEraForest(rng, cellSize, age, TerrainFeature.Jungle));
            var reefs      = CreateFeatureVariants(() => MapFeatureMeshes.CreateEraReef(rng, cellSize, age));
            var oases      = CreateFeatureVariants(() => MapFeatureMeshes.CreateEraOasis(rng, cellSize, age));
            // Small terrain props (grass, rocks, dunes…) for cells without a feature
            var details = new Dictionary<TerrainKind, Mesh[]>();
            foreach (TerrainKind kind in System.Enum.GetValues(typeof(TerrainKind)))
            {
                var variants = CreateFeatureVariants(() => MapFeatureMeshes.CreateEraDetail(rng, cellSize, kind, age));
                if (variants != null) details[kind] = variants;
            }

            var oceanDepth  = DistanceFromLand(6);
            var noiseOffset = new Vector3((float)rng.NextDouble(), (float)rng.NextDouble(), (float)rng.NextDouble()) * 1000f;
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);
            Mesh Pick(Mesh[] pool) => pool?[rng.Next(pool.Length)]; // null pool: nothing grows there in this period
            Mesh Detail(TerrainKind kind) => details.TryGetValue(kind, out var d) ? Pick(d) : null;

            // Plant species of the period (plants.json): each tile gets its region's dominant species,
            // named in the tile panel. Forest tiles: a canopy species over an understory species.
            var plants = new PlantPlanner(age, worldSeed, cellSize, WrapWidth, Track);
            bool hexStand = false; // the mesh fills the hex: turn it by multiples of 60° so it meets its neighbours
            Mesh Forest(HexCell cell, string type, Mesh[] fallback)
            {
                var (tree, tree2) = plants.Choose(cell, type);
                if (tree == null) return Pick(fallback);
                var (under, _) = plants.Choose(cell, null);
                cell.SetPlants(tree, tree2, under);
                hexStand = true;
                return plants.Stand(rng, tree, tree2, under);
            }
            Mesh Ground(HexCell cell)
            {
                var (main, second) = plants.Choose(cell, null);
                if (main == null) return rng.NextDouble() < 0.75 ? Detail(cell.Terrain.kind) : null; // no plants yet: rocks, mats
                cell.SetPlants(main, second);
                if (cell.Terrain.kind == TerrainKind.Desert && rng.NextDouble() < 0.1) return Detail(TerrainKind.Desert); // the odd dune
                hexStand = true;
                return plants.Ground(rng, main, second, cell.Terrain.kind);
            }

            int mountains = 0, forests = 0, others = 0;
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null) continue;
                cell.SetTintVariation(TileTint(cell, oceanDepth[q, r], rng, noiseOffset));
                SetGroundLook(cell, noiseOffset);
                cell.SetPlants();

                Mesh mesh   = null;
                bool unique = false;
                hexStand    = false;
                switch (cell.Feature)
                {
                    case TerrainFeature.Volcano:
                        mesh = Track(MapFeatureMeshes.CreateVolcano(rng, cellSize, R(1.1f, 1.75f), p => LocalGround(cell, p),
                                     MapFeatureMeshes.PickVolcanoForm(rng, ColdPeak(cell, r), false))); unique = true; others++;
                        break;
                    case TerrainFeature.ConiferForest:   mesh = Forest(cell, "Conifer",   conifers);  forests++; break;
                    case TerrainFeature.BroadleafForest: mesh = Forest(cell, "Broadleaf", broadleaf); forests++; break;
                    case TerrainFeature.Jungle:          mesh = Forest(cell, "Jungle",    jungles);   forests++; break;
                    case TerrainFeature.Geothermal:
                        mesh = Track(MapFeatureMeshes.CreateGeothermalField(rng, cellSize, p => LocalGround(cell, p))); unique = true; others++;
                        break;
                    case TerrainFeature.Mesa:    // a table mountain: a mountain tile built flat-topped (CreateMountainFor)
                        mesh = Track(CreateMountainFor(cell, r, rng, age)); unique = true; mountains++; break;
                    case TerrainFeature.Canyon:  // cut along the tile's river, so its water joins the neighbours' rivers
                        mesh = Track(MapFeatureMeshes.CreateCanyon(rng, cellSize, p => LocalGround(cell, p), RiverCenterlines(cell),
                                                                   cell.HasRiver ? RiverWidth(cell.RiverFlow, RiverStyle(cell.RiverSystem).Item1) : 0f));
                        unique = true; others++; break;
                    case TerrainFeature.Danxia:  mesh = Track(MapFeatureMeshes.CreateDanxia(rng, cellSize, p => LocalGround(cell, p)));  unique = true; others++; break;
                    case TerrainFeature.Karst: // drowned towers rise from a sea floor below the water (surface at 0, as for fjords)
                        mesh = Track(cell.IsWater ? MapFeatureMeshes.CreateKarst(rng, cellSize, _ => -0.05f * cellSize, true)
                                                  : MapFeatureMeshes.CreateKarst(rng, cellSize, p => LocalGround(cell, p), false, cell.Moisture));
                        unique = true; others++; break;
                    case TerrainFeature.SaltLake:
                    case TerrainFeature.PinkSaltLake:
                        mesh = Track(MapFeatureMeshes.CreateSaltLake(rng, cellSize, cell.Feature == TerrainFeature.PinkSaltLake, p => LocalGround(cell, p)));
                        unique = true; others++; break;
                    case TerrainFeature.WhiteCliffs:
                    {
                        var nb = EdgeNeighbors(cell);
                        var seaward = new bool[6];
                        float seaY = 0.02f - cell.SurfaceHeight;
                        for (int e = 0; e < 6; e++)
                            if (nb[e]?.Terrain != null && nb[e].Terrain.kind == TerrainKind.SaltWater) { seaward[e] = true; seaY = nb[e].SurfaceHeight - cell.SurfaceHeight; }
                        mesh = Track(MapFeatureMeshes.CreateWhiteCliffs(rng, cellSize, seaward, seaY, p => LocalGround(cell, p))); unique = true; others++;
                        break;
                    }
                    case TerrainFeature.Reef:            mesh = Pick(reefs);     others++;  break;
                    case TerrainFeature.Oasis:           mesh = Pick(oases);     others++;  break;
                    default:
                        if (cell.IsMountain) { mesh = Track(CreateMountainFor(cell, r, rng, age)); unique = true; mountains++; }
                        else if (cell.Terrain.kind == TerrainKind.SaltWater && CliffEdge(cell, out var toCliff) && rng.NextDouble() < 0.3)
                        {
                            mesh = Track(MapFeatureMeshes.CreateSeaStacks(rng, cellSize, toCliff, cellSize * 0.8660254f));
                            unique = true; others++;
                        }
                        else if (!cell.IsWater) mesh = Ground(cell);
                        else if (rng.NextDouble() < 0.75) mesh = Detail(cell.Terrain.kind);
                        break;
                }
                if (mesh == null) continue;

                // Pooled meshes get a random size, height and mirror image so neighbours never match
                float s   = unique || hexStand ? 1f : R(0.85f, 1.08f); // hex-filling stands keep their footprint so edges meet
                var scale = new Vector3(s * (!unique && rng.NextDouble() < 0.5 ? -1f : 1f), s * (unique ? 1f : R(0.85f, 1.2f)), s);
                float v   = R(0.9f, 1.08f);
                var tint  = new Color(v * R(0.96f, 1.04f), v, v * R(0.96f, 1.04f));
                float yaw = hexStand ? 60f * rng.Next(6) : R(0f, 360f);
                // Mountains and volcanoes are built to fit this tile's slopes and its neighbours'
                // ridges, so they keep their orientation and colour (it varies inside the mesh)
                if (unique) { yaw = 0f; tint = Color.white; }
                var feature = AddFeatureObject(cell, mesh, yaw, scale, tint);
                if (cell.Feature == TerrainFeature.Volcano && Application.isPlaying)
                    feature.AddComponent<VolcanoSmoke>().Init(cellSize, WorldSeed ^ (q * 7919 + r * 104729));
                if (cell.Feature == TerrainFeature.Geothermal && Application.isPlaying && MapFeatureMeshes.TryGetSteamVents(mesh, out var steam))
                    feature.AddComponent<GeothermalSteam>().Init(cellSize, WorldSeed ^ (q * 7919 + r * 104729), steam, 0, underwater: false);
            }
            PlaceRivers();
            Debug.Log($"[HexGrid] PlaceFeatures — {mountains} mountains, {forests} forests/jungles, {others} volcanoes/reefs/oases");
        }

        // A mountain tile's piece of a continuous massif: neighbouring mountain tiles carry the rock
        // on across the shared edge, other neighbours get a foot that sinks into the ground. Rock
        // colour comes from the land around (red sandstone near deserts, blue-grey near ice,
        // grey/brown elsewhere) and snow from latitude; both ease to the pair's shared value at each
        // edge. Pines only where the land around is green and conifers exist.
        private Mesh CreateMountainFor(HexCell cell, int row, System.Random rng, GeologicalAge age)
        {
            var (_, _, _, green) = Surroundings(cell);
            bool icy  = cell.Terrain.kind == TerrainKind.IceSheet;
            var site  = new MapFeatureMeshes.MassifSite
            {
                Apothem  = cellSize * 0.8660254f,
                BaseY    = cell.SurfaceHeight,
                Joined   = new bool[6],
                Rock     = MountainRock(cell),
                EdgeRock = new Color[6],
                Snow     = MountainSnow(cell),
                EdgeSnow = new float[6],
                Green    = !icy && green >= 2 && age >= GeologicalAge.Carboniferous, // first conifers
                Lush     = MountainLush(cell, age),
                Table    = cell.Feature == TerrainFeature.Mesa,
                TableTop = cell.Feature == TerrainFeature.Mesa ? MesaTop(cell) : 0f,
                GroundAt = p => LocalGround(cell, p),
            };
            var origin = cell.Coordinates.ToWorldPosition(cellSize);
            site.Relief = p => MountainRelief(new Vector2(origin.x + p.x, origin.z + p.y));
            site.Detail = p => MountainDetail(new Vector2(origin.x + p.x, origin.z + p.y));

            var neighbors = EdgeNeighbors(cell);
            for (int e = 0; e < 6; e++)
            {
                var n = neighbors[e];
                site.Joined[e]   = InSameMassif(cell, n);
                site.EdgeRock[e] = site.Joined[e] ? (site.Rock + MountainRock(n)) * 0.5f : site.Rock;
                site.EdgeSnow[e] = site.Joined[e] ? (site.Snow + MountainSnow(n)) * 0.5f : site.Snow;
            }
            return MapFeatureMeshes.CreateMassif(rng, cellSize, site);
        }

        // Direction (local XZ) from a sea cell toward a neighbouring cliffed coast, if it has one.
        private bool CliffEdge(HexCell cell, out Vector2 toCliff)
        {
            var neighbors = EdgeNeighbors(cell);
            for (int e = 0; e < 6; e++)
            {
                var n = neighbors[e];
                if (n == null || n.Terrain == null || n.IsWater || n.Elevation < CliffElevation) continue;
                float a = (60f * e + 30f) * Mathf.Deg2Rad;
                toCliff = new Vector2(Mathf.Sin(a), Mathf.Cos(a));
                return true;
            }
            toCliff = default;
            return false;
        }

        // World height of the flat top of the table a mesa tile belongs to (all the mesa tiles joined
        // to it): a set height above its highest tile, so every tile of a table meets the next level.
        private float MesaTop(HexCell cell)
        {
            float highest = cell.SurfaceHeight;
            var seen = new HashSet<HexCell> { cell };
            var open = new Queue<HexCell>();
            open.Enqueue(cell);
            while (open.Count > 0)
            {
                var c = open.Dequeue();
                highest = Mathf.Max(highest, c.SurfaceHeight);
                foreach (var n in EdgeNeighbors(c))
                    if (n != null && n.Feature == TerrainFeature.Mesa && InSameMassif(c, n) && seen.Add(n)) open.Enqueue(n);
            }
            return highest + MapFeatureMeshes.MassifHeight * cellSize * 0.62f;
        }

        // Volcanoes stand alone; other neighbouring mountains are one massif.
        private static bool InSameMassif(HexCell a, HexCell b) =>
            b != null && a.IsMountain && b.IsMountain && a.Feature != TerrainFeature.Volcano && b.Feature != TerrainFeature.Volcano
            && (a.Feature == TerrainFeature.Mesa) == (b.Feature == TerrainFeature.Mesa); // a mesa's table ends in its own cliff

        // Snow line (fraction of the massif height from the top): low on ice sheets; elsewhere from how
        // cold the mountain is in the period shown (latitude, height and the period's warmth), from a
        // small cap on hot tropical peaks to snow far down the slopes in cold times and near the poles
        private float MountainSnow(HexCell cell)
        {
            if (cell.Terrain.kind == TerrainKind.IceSheet) return 0.8f;
            return Mathf.Lerp(0.62f, 0.05f, Mathf.InverseLerp(0.1f, 0.7f, MountainTemperature(cell)));
        }

        private float MountainTemperature(HexCell cell) => cell.HasInputs
            ? WorldGenerator.Temperature(cell.Inputs, cell.Elevation, DisplayedConditions)
            : 1f - Latitude(cell.Coordinates.R);

        // 0..1: how far up a mountain is cloaked in green, on warm, wet mountains once there are
        // forests (Devonian on): tropical ranges green almost to the snow
        private float MountainLush(HexCell cell, GeologicalAge age)
        {
            if (age < GeologicalAge.Devonian || cell.Terrain.kind == TerrainKind.IceSheet) return 0f;
            return Mathf.InverseLerp(0.4f, 0.62f, MountainTemperature(cell)) * Mathf.InverseLerp(0.3f, 0.6f, cell.Moisture);
        }

        // Ruggedness of mountains at a map position (grid-local XZ), 0..1: ridged noise for crests and
        // valleys, scaled by a broad field so some ranges are higher than others. Sampled around the
        // map's east–west loop, so it matches up across the wrap seam.
        private float MountainRelief(Vector2 pos)
        {
            var p = OnMapLoop(pos) + reliefOffset;

            // 5 octaves: the finest (about 1/12 of a tile) gives the dense mesh gullies and spurs to show
            float v = 0f, amp = 0.5f, freq = 1.3f / cellSize, max = 0f;
            for (int o = 0; o < 5; o++)
            {
                float r = 1f - Mathf.Abs(PerlinNoise3D.Sample(p.x * freq, p.y * freq, p.z * freq));
                v += r * r * amp; max += amp;
                amp *= 0.5f; freq *= 2.1f;
            }
            v = Mathf.Clamp01((v / max - 0.3f) / 0.65f);
            float broad = 0.5f + 0.5f * PerlinNoise3D.Sample(p.x * 0.25f / cellSize + 71f, p.y * 0.25f / cellSize, p.z * 0.25f / cellSize);
            return Mathf.Clamp01(v * (0.55f + 0.6f * broad));
        }

        // Smooth 0..1 noise for rock colour, snow line and grass line on mountains
        private float MountainDetail(Vector2 pos)
        {
            var p = OnMapLoop(pos) * (3f / cellSize) + reliefOffset * 0.5f;
            return Mathf.Clamp01(0.5f + 0.6f * PerlinNoise3D.Sample(p.x, p.y, p.z + 37f) + 0.25f * PerlinNoise3D.Sample(p.x * 2.7f, p.y * 2.7f, p.z * 2.7f));
        }

        // A grid-local XZ position as a point on the map's east–west loop (a cylinder), so noise
        // sampled there matches up across the wrap seam.
        private Vector3 OnMapLoop(Vector2 pos)
        {
            float angle = pos.x / WrapWidth * Mathf.PI * 2f;
            float rad   = WrapWidth / (Mathf.PI * 2f);
            return new Vector3(Mathf.Cos(angle) * rad, Mathf.Sin(angle) * rad, pos.y);
        }

        // 0 = equator, 1 = pole
        private float Latitude(int row) => height > 1 ? Mathf.Abs(row / (float)(height - 1) * 2f - 1f) : 0f;

        // Neighbouring mountains, and dry / cold / green land around a cell.
        private (int ridge, int dry, int cold, int green) Surroundings(HexCell cell)
        {
            int ridge = 0, dry = 0, cold = 0, green = 0;
            foreach (var n in GetNeighbors(cell))
            {
                if (n.Terrain == null) continue;
                if (n.IsMountain) { ridge++; continue; }
                switch (n.Terrain.kind)
                {
                    case TerrainKind.Desert: case TerrainKind.Savanna: case TerrainKind.Steppe:
                    case TerrainKind.Barren:                                                    dry++; break;
                    case TerrainKind.Tundra: case TerrainKind.IceSheet:                         cold++; break;
                    case TerrainKind.Plain:  case TerrainKind.Hill: case TerrainKind.Wetland:
                    case TerrainKind.Rainforest: case TerrainKind.FernPrairie: case TerrainKind.CoalSwamp:
                    case TerrainKind.Mossland:                                                  green++; break;
                }
                if (n.IsForest || n.Feature == TerrainFeature.Jungle) green++;
            }
            return (ridge, dry, cold, green);
        }

        // Rock tint of a mountain cell. Depends only on the cell and its surroundings (not on the
        // order mountains are built in), so a neighbour can blend its ridge toward it.
        private Color MountainRock(HexCell cell)
        {
            var (_, dry, cold, green) = Surroundings(cell);
            if (dry > cold && dry >= green) return Color.Lerp(new Color(1.3f, 0.95f, 0.72f), new Color(1.15f, 1.0f, 0.8f), PairNoise(cell, cell, 2));
            if (cold > green)               return new Color(0.92f, 0.96f, 1.06f);
            return Mathf.FloorToInt(PairNoise(cell, cell, 3) * 3f) switch
            {
                0 => Color.white,
                1 => new Color(1.1f, 1.0f, 0.88f),
                _ => new Color(0.82f, 0.82f, 0.85f),
            };
        }

        // Deterministic 0..1 value for an unordered pair of cells (a == b for a single cell), from the world seed.
        private float PairNoise(HexCell a, HexCell b, int salt)
        {
            var (aq, ar) = a.Coordinates.ToOffsetCoordinates();
            var (bq, br) = b.Coordinates.ToOffsetCoordinates();
            int i = ar * width + aq, j = br * width + bq;
            if (i > j) (i, j) = (j, i);
            unchecked
            {
                uint h = (uint)WorldSeed;
                h = (h ^ (uint)i) * 0x9E3779B1u;
                h = (h ^ (uint)j) * 0x85EBCA77u;
                h = (h ^ (uint)salt) * 0xC2B2AE3Du;
                h ^= h >> 16;
                return (h & 0xFFFFFF) / (float)0x1000000;
            }
        }

        // Colour multiplier for a tile. Water darkens with depth: the sea goes from turquoise shallows
        // (greener toward the poles) over the shelf to deep navy, lakes from weedy, greenish shallows
        // to clear dark blue in the middle of deep ones. Land drifts by region (seamless noise around
        // the wrapped map) plus per-tile jitter; what kind of sand or rock it is comes from SetGroundLook.
        private Color TileTint(HexCell cell, int oceanDepth, System.Random rng, Vector3 noiseOffset)
        {
            float regional = Regional(cell, noiseOffset, 1f);
            float jitter   = 0.94f + 0.12f * (float)rng.NextDouble();
            float lat      = Latitude(cell.Coordinates.R);

            switch (cell.Terrain.kind)
            {
                case TerrainKind.SaltWater:
                {
                    // distance from land sets the shelf; the sea floor's own depth adds deeps and banks
                    float fromLand = Mathf.Sqrt(Mathf.InverseLerp(1f, 6f, oceanDepth));
                    float deep     = Mathf.Clamp01(fromLand * 0.55f + cell.Depth * 0.6f - (oceanDepth <= 1 ? 0.25f : 0f));
                    var shallow    = Color.Lerp(new Color(1.45f, 1.6f, 1.25f), new Color(1.15f, 1.3f, 1.1f), Mathf.InverseLerp(0.35f, 0.8f, lat));
                    var mid        = new Color(0.86f, 0.98f, 1.05f);
                    var abyss      = new Color(0.4f, 0.48f, 0.76f);
                    var sea = deep < 0.45f ? Color.Lerp(shallow, mid, deep / 0.45f) : Color.Lerp(mid, abyss, (deep - 0.45f) / 0.55f);
                    return sea * Mathf.Lerp(0.95f, 1.05f, regional) * (0.97f + 0.06f * (float)rng.NextDouble());
                }
                case TerrainKind.FreshWater:
                {
                    float deep = Mathf.Clamp01(cell.Depth * 0.7f + (LakeShore(cell) ? 0f : 0.35f));
                    var shallow = Color.Lerp(new Color(1.05f, 1.15f, 0.82f), new Color(1.12f, 1.05f, 0.85f), regional); // weedy green or peaty brown
                    return Color.Lerp(shallow, new Color(0.62f, 0.74f, 0.98f), deep) * jitter;
                }
                case TerrainKind.Desert:
                case TerrainKind.Barren:
                    return Color.white * jitter; // the sand or rock colour itself comes from SetGroundLook
                default:
                    return Color.Lerp(new Color(0.88f, 1.0f, 0.95f), new Color(1.1f, 1.0f, 0.86f), regional) * jitter;
            }
        }

        // Seamless noise around the wrapped map, 0..1; a different `seed` gives an independent pattern.
        private float Regional(HexCell cell, Vector3 noiseOffset, float seed)
        {
            var pos     = cell.Coordinates.ToWorldPosition(cellSize);
            float angle = pos.x / WrapWidth * Mathf.PI * 2f;
            float rad   = WrapWidth / (Mathf.PI * 2f);
            var p       = new Vector3(Mathf.Cos(angle) * rad, Mathf.Sin(angle) * rad, pos.z) + noiseOffset * seed;
            return Mathf.Clamp01(0.5f + 0.5f * (0.7f * PerlinNoise3D.Sample(p.x * 0.06f, p.y * 0.06f, p.z * 0.06f)
                                             + 0.3f * PerlinNoise3D.Sample(p.x * 0.2f,  p.y * 0.2f,  p.z * 0.2f)) * 1.6f);
        }

        private bool LakeShore(HexCell cell)
        {
            foreach (var n in GetNeighbors(cell)) if (n.Terrain != null && !n.IsWater) return true;
            return false;
        }

        // Landform tiles, each on the ground that makes it, on a few of the tiles that qualify (the
        // same ones in every period while they still qualify): mesas, canyons, Danxia hills and salt
        // lakes in dry country, karst in warm wet country (and drowned karst in warm coastal seas), fjords on cold highland coasts and
        // white chalk cliffs on mild coasts from the Cretaceous on. Not where a river runs.
        private void PlaceLandforms(GeologicalAge age)
        {
            var counts = new Dictionary<TerrainFeature, int>();
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null || cell.HasRiver) continue;
                var form = LandformFor(cell, q, r, age);
                if (form == TerrainFeature.None) continue;
                cell.SetFeature(form);
                counts[form] = counts.TryGetValue(form, out int c) ? c + 1 : 1;
            }
            if (counts.Count > 0) Debug.Log("[HexGrid] Landforms — " + string.Join(", ", System.Linq.Enumerable.Select(counts, kv => $"{kv.Value} {kv.Key}")));
        }

        private float TileRoll(int q, int r, int salt)
        {
            uint h = (uint)(WorldSeed * 73856093) ^ (uint)(q * 19349663) ^ (uint)(r * 83492791) ^ (uint)(salt * 2654435761u);
            h ^= h >> 13; h *= 0x5bd1e995; h ^= h >> 15;
            return (h & 0xFFFF) / 65535f;
        }

        // A mountain in a dry region where the ranges are tables (broad map-wide noise, so a range
        // turns to mesas as a whole rather than tile by tile); not icy
        private const float MesaThreshold = 0.45f; // higher = rarer mesas

        private bool MesaRange(HexCell cell)
        {
            // rare: only the few peaks of a broad noise field, so most dry ranges have none, but where
            // there is one it usually spans two or three neighbouring tiles
            if (cell.Terrain.kind != TerrainKind.Mountain || cell.Moisture > 0.32f) return false;
            var pos = cell.Coordinates.ToWorldPosition(cellSize);
            var p = OnMapLoop(new Vector2(pos.x, pos.z)) * (0.22f / cellSize) + reliefOffset * 0.3f + Vector3.one * 211f;
            return PerlinNoise3D.Sample(p.x, p.y, p.z) > MesaThreshold;
        }

        private TerrainFeature LandformFor(HexCell cell, int q, int r, GeologicalAge age)
        {
            var kind = cell.Terrain.kind;
            float lat = Latitude(r);
            var n = EdgeNeighbors(cell);
            int land = 0, sea = 0, high = 0;
            foreach (var x in n)
            {
                if (x?.Terrain == null) continue;
                if (x.Terrain.kind == TerrainKind.SaltWater) sea++;
                else if (!x.IsWater) { land++; if (x.IsMountain || x.Elevation >= 3) high++; }
            }
            if (kind == TerrainKind.SaltWater)
            {
                if (cell.Feature != TerrainFeature.None || land < 2) return TerrainFeature.None;
                if (lat < 0.4f && TileRoll(q, r, 9) < 0.06f) return TerrainFeature.Karst; // drowned towers in warm coastal seas (Ha Long Bay)
                return TerrainFeature.None;
            }
            // Mesas are table mountains: whole dry ranges (or parts of them) flat-topped and sheer-sided
            if (cell.IsMountain) return MesaRange(cell) ? TerrainFeature.Mesa : TerrainFeature.None;
            if (cell.IsWater) return TerrainFeature.None;

            bool forest = cell.Feature is TerrainFeature.BroadleafForest or TerrainFeature.ConiferForest or TerrainFeature.Jungle;
            if (cell.Feature != TerrainFeature.None && !forest) return TerrainFeature.None;
            bool dry = kind is TerrainKind.Desert or TerrainKind.Steppe or TerrainKind.Barren
                    || (kind is TerrainKind.Savanna or TerrainKind.Hill or TerrainKind.Plain && cell.Moisture < 0.3f);
            bool wetWarm = lat < 0.45f && cell.Moisture > 0.5f && kind is TerrainKind.Hill or TerrainKind.Plain or TerrainKind.Rainforest or TerrainKind.Savanna;

            if (wetWarm && TileRoll(q, r, 2) < 0.07f) return TerrainFeature.Karst; // towers rise out of the forest too
            if (forest) return TerrainFeature.None;
            if (age >= GeologicalAge.Cretaceous && sea > 0 && cell.Elevation < CliffElevation && lat > 0.25f && lat < 0.7f
                && kind is TerrainKind.Plain or TerrainKind.Hill or TerrainKind.Steppe && TileRoll(q, r, 3) < 0.14f)
                return TerrainFeature.WhiteCliffs;
            if (!dry || sea > 0) return TerrainFeature.None;
            // canyons are cut by rivers: only where a river crosses dry upland
            if (cell.Elevation >= 2 && cell.HasRiver && cell.RiverOut >= 0 && TileRoll(q, r, 4) < 0.35f) return TerrainFeature.Canyon;
            if (kind == TerrainKind.Desert && TileRoll(q, r, 6) < 0.035f) return TerrainFeature.Danxia; // rainbow hills: arid desert only (Zhangye)
            if (cell.Elevation <= 2 && TileRoll(q, r, 7) < 0.05f)
                return TileRoll(q, r, 8) < 0.5f ? TerrainFeature.PinkSaltLake : TerrainFeature.SaltLake;
            return TerrainFeature.None;
        }

        // Geothermal fields on the open lowland around the period's volcanoes (about one in four
        // tiles within two of one), and very rarely far from any; the same tiles each time.
        private void PlaceGeothermal()
        {
            int placed = 0;
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null || cell.IsWater || cell.IsMountain || cell.Feature != TerrainFeature.None) continue;
                if (cell.Terrain.kind is TerrainKind.IceSheet || cell.HasRiver) continue; // its pools would sit under the river
                uint hash = (uint)(WorldSeed * 73856093) ^ (uint)(q * 19349663) ^ (uint)(r * 83492791);
                hash ^= hash >> 13; hash *= 0x5bd1e995; hash ^= hash >> 15;
                float roll = (hash & 0xFFFF) / 65535f;
                if (NearVolcano(cell) ? roll < 0.25f : roll < 0.004f) { cell.SetFeature(TerrainFeature.Geothermal); placed++; }
            }
            if (placed > 0) Debug.Log($"[HexGrid] {placed} geothermal fields");
        }

        // Cold enough for a volcano to carry snow: near the poles or beside tundra and ice
        private bool ColdPeak(HexCell cell, int row)
        {
            float lat = Mathf.Abs(row / (float)Mathf.Max(1, height - 1) * 2f - 1f);
            if (lat > 0.6f) return true;
            foreach (var n in GetNeighbors(cell))
                if (n.Terrain != null && n.Terrain.kind is TerrainKind.Tundra or TerrainKind.IceSheet) return true;
            return false;
        }

        private bool NearVolcano(HexCell cell)
        {
            foreach (var n in GetCellsInRange(cell, 2)) if (n.Feature == TerrainFeature.Volcano) return true;
            return false;
        }

        // Sand colours (shading of the ground texture repainted in this colour) and rock tints
        private static readonly Vector4 NoRecolor  = Vector4.zero;
        private static readonly Color   WhiteSand  = new(0.98f, 0.96f, 0.9f);
        private static readonly Color   GoldenSand = new(0.93f, 0.8f, 0.55f);
        private static readonly Color   RedSand    = new(0.92f, 0.52f, 0.32f);
        private static readonly Color   BlackSand  = new(0.3f, 0.29f, 0.3f);
        private static readonly Color   Gravel     = new(0.58f, 0.55f, 0.52f);
        private static readonly Color   Granite    = new(1f, 0.97f, 0.93f);   // the rock texture's own grey
        private static readonly Color   Sandstone  = new(1.2f, 0.82f, 0.62f);
        private static readonly Color   Basalt     = new(0.55f, 0.55f, 0.6f);
        private static readonly Color   Chalk      = new(1.45f, 1.42f, 1.34f);
        private static readonly Color   Limestone  = new(1.22f, 1.16f, 1.02f);

        // Gives each tile its kind of ground: deserts of golden, white (gypsum, quartz), red or
        // black-gravel sand; bare land of grey, rusty, dark volcanic or pale rock; cliffs of granite,
        // red sandstone, basalt near volcanoes or white chalk; and beaches of white coral sand in the
        // tropics, golden sand in mild climates, black sand by volcanoes and shingle and rock in the cold.
        // Regions share a look, so a white-sand desert or a chalk coast runs on for several tiles.
        private void SetGroundLook(HexCell cell, Vector3 noiseOffset)
        {
            float a   = Regional(cell, noiseOffset, 1.7f); // which sand/rock family
            float b   = Regional(cell, noiseOffset, 2.9f); // second, independent pattern
            float lat = Latitude(cell.Coordinates.R);
            bool volcanic = NearVolcano(cell);

            // What the ground is made of: a surface texture of its own (TerrainSurfaces, see
            // tools/terrain/surfaces.py) and/or the terrain texture repainted in another colour
            var recolor = NoRecolor;
            Texture ground = null;
            bool dryLand = cell.Moisture < 0.3f;
            switch (cell.Terrain.kind)
            {
                case TerrainKind.Desert:
                    if (volcanic)                          { ground = Surface("DuneSand"); recolor = Paint(BlackSand, 0.75f); } // black volcanic dunes
                    else if (a < 0.22f)                    { ground = Surface("DuneSand"); recolor = Paint(WhiteSand, 0.85f); } // gypsum and quartz dunes
                    else if (a > 0.7f)                     { ground = Surface("DuneSand"); recolor = Paint(RedSand, 0.7f); }    // red dune seas
                    else if (b > 0.78f)                      ground = Surface("DesertPavement");                                  // stony reg and gibber plains
                    else if (b < 0.18f)                      ground = Cracked(cell, "SaltFlat");                                        // salt pans
                    else if (a > 0.42f && a < 0.55f && b > 0.55f) ground = Cracked(cell, "CrackedClay");                                // dry lake beds
                    else if (a > 0.3f && a < 0.42f && b < 0.4f)   ground = Surface("Slickrock");                                  // red-rock canyon country
                    else if (a > 0.55f)                      ground = Surface("DuneSand");                                        // golden ergs
                    break;
                case TerrainKind.Barren:
                    if (volcanic)       ground = Surface("LavaField");
                    else if (a > 0.68f) ground = Surface("Slickrock");
                    else if (b > 0.72f) { ground = Surface("DesertPavement"); recolor = Paint(new Color(0.38f, 0.37f, 0.4f), 0.6f); } // dark basalt gravel
                    break;
                case TerrainKind.Savanna:
                    if (a > 0.62f) ground = Surface("RedEarth");                    // laterite: red soil under the grass
                    break;
                case TerrainKind.Steppe:
                    if (b > 0.8f) ground = Surface("DesertPavement");               // gravel steppe
                    else if (a < 0.15f && dryLand) ground = Cracked(cell, "CrackedClay"); // takyr: dried-out clay flats
                    break;
                case TerrainKind.Tundra:
                    if (a < 0.4f) ground = Cracked(cell, "PatternedGround");              // frost-sorted stone polygons
                    break;
                case TerrainKind.IceSheet:
                    if (b > 0.5f) ground = Cracked(cell, "CrevassedIce");
                    break;
                case TerrainKind.Hill:
                    if (dryLand && a > 0.78f) ground = Surface("Slickrock");
                    break;
            }

            // Rock faces: red sandstone in dry country, basalt by volcanoes, chalk and limestone on
            // some mild coasts, granite elsewhere
            var cliff = Granite;
            bool dry = cell.Moisture < 0.3f || cell.Biome is TerrainKind.Desert or TerrainKind.Savanna or TerrainKind.Steppe;
            if (volcanic)                        cliff = Basalt;
            else if (dry && a > 0.4f)            cliff = Sandstone;
            else if (lat > 0.3f && lat < 0.65f && b < 0.25f) cliff = Chalk;
            else if (a < 0.2f)                   cliff = Limestone;
            else if (b > 0.8f)                   cliff = Basalt;

            // Beaches (only low coasts have them; highland meets the sea in a cliff)
            var shore = new Vector4(0f, 0f, 0f, 0f);
            if (!cell.IsWater && cell.Elevation < CliffElevation)
            {
                Color sand; float amount;
                if (volcanic)        { sand = BlackSand;  amount = 1f; }
                else if (lat < 0.35f){ sand = WhiteSand;  amount = b < 0.85f ? 1f : 0f; }       // coral sand, a few rocky stretches
                else if (lat < 0.7f) { sand = GoldenSand; amount = b < 0.65f ? 1f : 0.3f; }     // sand, or shingle
                else                 { sand = Gravel;     amount = 0.35f; }                      // cold shores: pebbles and rock
                shore = new Vector4(sand.r, sand.g, sand.b, amount);
            }
            // Floodplains and deltas near big river mouths: lush, silt-fed ground (green even in the
            // desert, like the Nile's) dotted with wet hollows and pools
            float flood = 0f;
            if (cell.Floodplain && !cell.IsWater)
            {
                // before land plants (Devonian) there is nothing green to grow on it: dark, wet silt
                // with a film of microbial mat
                recolor = DisplayedAge < GeologicalAge.Devonian
                        ? Paint(new Color(0.4f, 0.37f, 0.31f), 0.55f)
                        : Paint(lat > 0.65f ? new Color(0.46f, 0.5f, 0.32f) : new Color(0.38f, 0.52f, 0.2f),
                                cell.Biome is TerrainKind.Desert ? 0.75f : 0.5f);
                flood = 0.85f;
            }
            if (flood > 0f) ground = null; // silt covers whatever was there
            // Landforms (mesas, canyons, Danxia hills, salt lakes) keep the ground of their region, so the
            // tile's colours run on from its neighbours; the landform brings its own rock. White cliffs
            // have no beach and chalk faces.
            if (cell.Feature == TerrainFeature.WhiteCliffs) { shore = Vector4.zero; cliff = Chalk; }
            // a geothermal field's ground: pale, mineral-crusted and stained a little ochre
            if (cell.Feature == TerrainFeature.Geothermal) { ground = null; recolor = Paint(new Color(0.7f, 0.65f, 0.52f), 0.45f); }

            // Cliff faces get the texture of their rock; it carries its own colour, so the tint
            // only warms or cools it slightly
            string cliffTex = cliff == Sandstone ? "CliffSandstone" : cliff == Basalt ? "CliffBasalt" : cliff == Chalk ? "CliffChalk"
                            : cliff == Limestone ? "CliffLimestone" : "CliffGranite";
            var cliffSurface = Surface(cliffTex);
            if (cliffSurface != null) cliff = Color.Lerp(Color.white, cliff, 0.15f);

            cell.SetGroundLook(recolor, cliff, shore, flood);
            cell.SetSurface(ground, cliffSurface);
        }

        // Cracked and crazed ground (salt pans, dried clay, frost polygons,
        // crevassed ice) is kept to one in twenty of the tiles that would have it: a little goes a long way
        private Texture2D Cracked(HexCell cell, string name)
        {
            var (q, r) = cell.Coordinates.ToOffsetCoordinates();
            return TileRoll(q, r, 31) < 0.05f ? Surface(name) : null;
        }

        // Ground surfaces from Resources/TerrainSurfaces, loaded once
        private static readonly Dictionary<string, Texture2D> surfaces = new();
        private static Texture2D Surface(string name)
        {
            if (!surfaces.TryGetValue(name, out var tex))
                surfaces[name] = tex = Resources.Load<Texture2D>("TerrainSurfaces/" + name);
            return tex;
        }

        private static Vector4 Paint(Color c, float amount) => new(c.r, c.g, c.b, amount);

        // Tells every tile which terrain lies across each of its edges so the terrain shader can fade
        // into it. Land blends only with land and water only with water, so coastlines stay crisp.
        private void UpdateEdgeBlends()
        {
            Shader.SetGlobalFloat("_HexApothem", cellSize * TileRadius * 0.8660254f);
            Shader.SetGlobalFloat("_HexBlendWidth", cellSize * TileBlendWidth);
            // Steep land faces (cliffs) use the Mountain terrain's rock texture
            terrainTypes ??= LoadTerrainTypes();
            if (terrainTypes.TryGetValue(TerrainKind.Mountain, out var mountain) && mountain.material != null &&
                mountain.material.HasProperty("_BaseMap"))
                Shader.SetGlobalTexture("_CliffTex", mountain.material.GetTexture("_BaseMap"));

            var textures = new Texture[6];
            var tints    = new Vector4[6];
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null) continue;
                System.Array.Clear(textures, 0, 6);
                System.Array.Clear(tints, 0, 6);

                var neighbors = EdgeNeighbors(cell);
                for (int edge = 0; edge < 6; edge++)
                {
                    var n = neighbors[edge];
                    if (n == null || n.Terrain == null || n.IsWater != cell.IsWater) continue;
                    var tint = n.BlendTint;
                    textures[edge] = n.BlendTexture;
                    tints[edge]    = new Vector4(tint.r, tint.g, tint.b, 1f);
                }
                cell.SetEdgeBlends(textures, tints);
            }
        }

        // Neighbour across each edge of a cell (edge e faces 60e + 30 degrees clockwise from +Z),
        // null where the map ends.
        private HexCell[] EdgeNeighbors(HexCell cell)
        {
            var result = new HexCell[6];
            var here   = cell.Coordinates.ToWorldPosition(cellSize);
            foreach (var n in GetNeighbors(cell))
            {
                var d = n.Coordinates.ToWorldPosition(cellSize) - here;
                d.x -= Mathf.Round(d.x / WrapWidth) * WrapWidth; // neighbour across the wrap seam
                float angle = Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;
                result[((Mathf.RoundToInt((angle - 30f) / 60f) % 6) + 6) % 6] = n;
            }
            return result;
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
        private GameObject AddFeatureObject(HexCell cell, Mesh mesh, float yaw, Vector3 scale, Color tint)
        {
            var go = new GameObject(mesh.name);
            if (!Application.isPlaying) go.hideFlags = HideFlags.DontSave;
            go.transform.SetParent(cell.transform, false);
            go.transform.localPosition = Vector3.up * cell.SurfaceHeight;
            go.transform.localRotation = Quaternion.Euler(0f, yaw, 0f);
            go.transform.localScale    = scale;
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            featureObjects.Add(go);
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial = featureMaterial;
            var block = new MaterialPropertyBlock();
            block.SetColor("_Color", tint);
            mr.SetPropertyBlock(block);
            return go;
        }

        // Inland waterfalls: a river leaving a land tile for land at least this many levels lower
        public const int FallLevels = 3;

        // Whether a waterfall drops between these two neighbouring land tiles (either way round).
        // The tiles then meet in a step instead of sloping into each other (UpdateCellMeshes).
        public bool IsFallStep(HexCell a, HexCell b) => Falls(a, b) || Falls(b, a);

        private bool Falls(HexCell from, HexCell to)
        {
            if (from.RiverOut < 0 || from.Elevation - to.Elevation < FallLevels) return false;
            return EdgeNeighbors(from)[from.RiverOut] == to;
        }

        // Water sits flat near sea level; land rises one elevationStep per terrace level.
        private float CellVisualHeight(HexCell cell) => cell.Terrain.kind switch
        {
            TerrainKind.SaltWater  => 0.02f,
            TerrainKind.FreshWater => 0.06f,
            _                      => 0.12f + cell.Elevation * elevationStep,
        };

        // Water tiles are flat, bevelled prisms. Land tiles slope from a flat middle to a rim that
        // sits halfway to each land neighbour's height (corners: the average of the land tiles
        // meeting there), so a difference in elevation becomes a slope instead of a step. Coasts
        // keep their edge. Neighbouring mountains are joined with no groove between them.
        private void UpdateCellMeshes()
        {
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
                if (cells[q, r].Terrain != null) cells[q, r].SetSurfaceHeight(CellVisualHeight(cells[q, r]));

            int updated = 0;
            var corners = new float[6];
            var edges   = new float[6];
            var joined  = new bool[6];
            var cliff   = new bool[6];
            var key     = new System.Text.StringBuilder();
            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                var cell = cells[q, r];
                if (cell.Terrain == null) continue;
                float h = cell.SurfaceHeight;
                Mesh mesh;
                if (cell.IsWater)
                {
                    cell.SetRimHeights(null);
                    string waterKey = $"w{h}";
                    if (!meshCache.TryGetValue(waterKey, out mesh))
                    {
                        mesh = HexMeshGenerator.Create(cellSize * TileRadius, h, cellSize * TileBevel);
                        mesh.hideFlags = HideFlags.DontSave;
                        meshCache[waterKey] = mesh;
                    }
                }
                else
                {
                    var n = EdgeNeighbors(cell);
                    bool Land(HexCell c)  => c != null && c.Terrain != null && !c.IsWater;
                    bool Water(HexCell c) => c != null && c.Terrain != null && c.IsWater;
                    bool Sea(HexCell c)   => Water(c) && c.Terrain.kind == TerrainKind.SaltWater;
                    bool Low(HexCell c)   => c.Elevation < CliffElevation;
                    bool Step(HexCell c)  => Land(c) && IsFallStep(cell, c); // a waterfall drops here: a step, not a slope
                    // Coasts: low land slopes down to a beach at the water's edge; highland ends in
                    // a cliff. Rim heights depend only on the cells sharing each edge / corner, so
                    // neighbouring land tiles still agree on them.
                    for (int e = 0; e < 6; e++)
                    {
                        bool shore = Water(n[e]);
                        cliff[e]  = Sea(n[e]) && !Low(cell); // only the open sea cuts cliffs; lake shores slope down
                        edges[e]  = Step(n[e]) ? h : Land(n[e]) ? (h + n[e].SurfaceHeight) * 0.5f : shore && !cliff[e] ? n[e].SurfaceHeight + ShoreLip : h;
                        joined[e] = cell.IsMountain && Land(n[e]) && n[e].IsMountain && !Step(n[e]);
                    }
                    for (int i = 0; i < 6; i++)
                    {
                        float sum = h; int count = 1;
                        var a = n[(i + 5) % 6]; var b = n[i]; // the two edges meeting at corner i
                        bool low = Low(cell);
                        // (each side of a waterfall step leaves the other side out, keeping its own level)
                        if (Land(a)) { if (!Step(a)) { sum += a.SurfaceHeight; count++; } low &= Low(a); }
                        if (Land(b)) { if (!Step(b)) { sum += b.SurfaceHeight; count++; } low &= Low(b); }
                        // Shore height unless highland next to the sea makes it a clifftop
                        bool wet   = Water(a) || Water(b);
                        bool cliffTop = !low && (Sea(a) || Sea(b));
                        // (at the lower of the waters meeting there, so a beach runs down to the sea
                        // even where a lake is next to it; the rule depends only on the cells sharing the corner)
                        float waterY = Mathf.Min(Water(a) ? a.SurfaceHeight : 9f, Water(b) ? b.SurfaceHeight : 9f);
                        corners[i] = wet && !cliffTop ? waterY + ShoreLip : sum / count;
                    }

                    var rim = new float[12];
                    key.Clear().Append(Mathf.RoundToInt(h * 10000f));
                    for (int i = 0; i < 6; i++)
                    {
                        rim[2 * i]     = corners[i];
                        rim[2 * i + 1] = edges[i];
                        key.Append(',').Append(Mathf.RoundToInt(corners[i] * 10000f))
                           .Append(',').Append(Mathf.RoundToInt(edges[i] * 10000f)).Append(joined[i] ? 'j' : cliff[i] ? 'c' : '-');
                    }
                    cell.SetRimHeights(rim);
                    string landKey = key.ToString();
                    if (!meshCache.TryGetValue(landKey, out mesh))
                    {
                        mesh = HexMeshGenerator.CreateSloped(cellSize * TileRadius, cellSize, h, TileSolid, corners, edges, joined, cliff);
                        mesh.hideFlags = HideFlags.DontSave;
                        meshCache[landKey] = mesh;
                    }
                }
                var mf = cell.GetComponent<MeshFilter>();
                var mc = cell.GetComponent<MeshCollider>();
                if (mf != null) { mf.sharedMesh = mesh; updated++; }
                if (mc != null) mc.sharedMesh = mesh;
            }
            Debug.Log($"[HexGrid] UpdateCellMeshes — updated {updated} cells, {meshCache.Count} unique tile meshes");
            if (UnderView.On) { ShowSeabedRelief(true); ShowPlateau(true); } // tiles were just reset to the surface: back to the seabed and plateau
        }

        // Height of a land tile's top surface above its own top face at a point given relative to
        // the tile centre (0 in the flat middle, following the slope toward the rim). Approximates
        // the sloped mesh closely enough to stand props on.
        private float LocalGround(HexCell cell, Vector2 p)
        {
            var rim = cell.RimHeights;
            if (rim == null) return 0f;
            float deg = Mathf.Atan2(p.x, p.y) * Mathf.Rad2Deg;
            if (deg < 0f) deg += 360f;
            int e   = Mathf.Min(5, Mathf.FloorToInt(deg / 60f));
            float f = deg / 60f - e; // 0 at corner e, 0.5 at the edge midpoint, 1 at corner e+1
            float edgeY = f < 0.5f ? Mathf.Lerp(rim[2 * e], rim[2 * e + 1], f * 2f)
                                   : Mathf.Lerp(rim[2 * e + 1], rim[(2 * e + 2) % 12], f * 2f - 1f);

            float a     = (60f * e + 30f) * Mathf.Deg2Rad;
            float d     = p.x * Mathf.Sin(a) + p.y * Mathf.Cos(a); // distance toward edge e
            float outer = cellSize * TileRadius * 0.8660254f;
            float s     = Mathf.Clamp01(Mathf.InverseLerp(outer * TileSolid, outer, d));
            return (edgeY - cell.SurfaceHeight) * s;
        }

        // Local Y, in `cell`'s space, of the ground under a point given in `cell`'s space (x, z from its
        // centre). The point may lie over a neighbouring tile; it is measured on whichever tile it is
        // over, and neighbours share their rim heights, so the result is continuous across borders.
        // Water and other flat tiles return their top face.
        public float GroundHeight(HexCell cell, Vector3 local)
        {
            var here = cell;
            var p = new Vector2(local.x, local.z);
            float y = 0f;
            float inside = cellSize * TileRadius * 0.8660254f; // within the inscribed circle: on this tile
            for (int hop = 0; hop < 3 && p.sqrMagnitude > inside * inside; hop++)
            {
                // the point is over the tile whose centre is nearest (hex cells are the Voronoi cells of their centres)
                HexCell best = null;
                Vector3 bestStep = default;
                float bestDist = p.sqrMagnitude;
                for (int i = 0; i < 6; i++)
                {
                    var n = GetCell(here.Coordinates.Neighbor(i));
                    if (n == null) continue;
                    var step = n.transform.localPosition - here.transform.localPosition;
                    step.x -= Mathf.Round(step.x / WrapWidth) * WrapWidth; // across the wrap seam
                    float d = (p - new Vector2(step.x, step.z)).sqrMagnitude;
                    if (d < bestDist) { bestDist = d; best = n; bestStep = step; }
                }
                if (best == null) break;
                p   -= new Vector2(bestStep.x, bestStep.z);
                y   += bestStep.y;
                here = best;
            }
            return y + here.SurfaceHeight + LocalGround(here, p);
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
