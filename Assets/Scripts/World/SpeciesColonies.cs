using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Players;
using UnityEngine;

namespace NaturalHistory.World
{
    // How a species' group looks and moves on its tile (species.json "mapStyle").
    public enum ColonyStyle
    {
        Drift, // micro-organisms: a cluster hovering over the tile, slowly tumbling and bobbing
        Fixed, // doesn't move: corals, sponges, mounds, and small animals modelled on a perch
        Float, // sits on the water surface (pivot at the waterline), rocking gently
        Ground,// stands on the tile (pivot at the feet) and wanders around its spot
        Soar,  // circles high above the tile, banked into the turn
        Swarm, // a jittery cloud of small fliers
        Swim,  // a school circling just above the water (tiles are opaque, so they can't go under it)
    }

    // How a Ground animal moves between spots (species.json "mapGait").
    // Run: walks while ambling about its spot, gallops with long bounding strides when travelling (big cats).
    public enum ColonyGait { Walk, Hop, Slither, Run }

    // Shows a group of every species that has a map model (species.json "model") on one of its
    // habitat tiles, as a ColonyGroup that can be ordered to move or attack (click it, then a marked
    // neighbouring tile). Groups are children of their cell, so they follow the east–west wrap and are
    // destroyed when the map regenerates. Models face +Z with their pivot as described in
    // tools/blender/nh_model.py; they are rescaled from their mesh bounds, so file units don't matter.
    public class SpeciesColonies : MonoBehaviour
    {
        // count, size (longest dimension, in cells), spread radius from the cell centre
        private static readonly Dictionary<ColonyStyle, (int count, float span, float radius)> Layouts = new()
        {
            [ColonyStyle.Drift]  = (7, 0.32f, 0.36f),
            [ColonyStyle.Fixed]  = (3, 0.34f, 0.30f),
            [ColonyStyle.Float]  = (4, 0.26f, 0.32f),
            [ColonyStyle.Ground] = (3, 0.34f, 0.30f),
            [ColonyStyle.Soar]   = (3, 0.42f, 0.45f),
            [ColonyStyle.Swarm]  = (9, 0.11f, 0.30f),
            [ColonyStyle.Swim]   = (5, 0.26f, 0.32f),
        };

        // Map size grows with real body size (sqrt of length in metres), so a T. rex towers over a
        // lion; small animals keep their style's minimum size so they stay visible.
        private const float SizeSpanPerSqrtMetre = 0.8f;
        private const float MaxSpan              = 3f;   // in cells
        // Whatever the real size or framing, nothing is drawn smaller than this, so even a
        // half-millimetre water bear or a perched kingfisher reads clearly on its tile. Swarms have
        // many members flying close together, so each can be a little smaller.
        private const float MinSpan              = 0.32f;
        private const float MinSwarmSpan         = 0.24f;
        private const float ReserveSpan          = 0.9f; // bigger than this: keep neighbouring tiles free
        // Each species shows several wild colonies spread over its habitat, so browsing the map shows
        // the age's diversity everywhere, not only once near the start. Ages with few species get more
        // of each, aiming at about this many groups in all (see CopiesOf).
        private const int TargetWildGroups       = 800; // 5× the original 160
        private const int MinCopies              = 10;
        private const int MaxCopies              = 30;
        private const int TilesPerCopy           = 6;   // a species with little habitat gets fewer copies
        private const int MaxBigCopies           = 10;  // animals spilling over their tile (ReserveSpan)
        // Sizes are relative to the age: an age whose biggest animal is small is drawn zoomed in, as
        // if that animal were this long, so a Cambrian trilobite reads clearly next to Anomalocaris
        // and gets smaller again once dinosaurs and whales set the scale. Zoomed-in groups show
        // fewer members (see AgeZoom).
        private const float AgeReferenceCm       = 600f;
        private const float MaxAgeZoom           = 3f;
        // Microbes (protists, and animals under a millimetre such as water bears and mites) keep the
        // minimum size up to the Cambrian, then shrink as bigger life sets the scale, down to
        // LateMicrobeScale of it from the Devonian on.
        private const float LateMicrobeScale     = 0.3f;
        private static bool IsMicrobe(SpeciesDefinition def) => def.kingdom == "Protista" || def.sizeCm < 0.1f;
        private static float MicrobeScale(GeologicalAge age) =>
            Mathf.Lerp(1f, LateMicrobeScale, Mathf.InverseLerp((float)GeologicalAge.Cambrian, (float)GeologicalAge.Devonian, (float)age));

        private const float SoarHeight  = 0.75f;
        private const float SwarmHeight = 0.35f;

        // Wing/fin beat amplitude (radians) by style; soarers only flap in short bursts between glides
        private const float SoarFlap  = 0.45f;
        private const float SwarmFlap = 0.6f;
        private const float SwimFlap  = 0.35f;
        private static readonly int FlapRootId = Shader.PropertyToID("_FlapRoot");
        private static readonly int FlapSpanId = Shader.PropertyToID("_FlapSpan");
        private static readonly int StrideLegsId = Shader.PropertyToID("_StrideLegs");
        private static readonly int StrideModeId = Shader.PropertyToID("_StrideMode");
        private static readonly int UndulateBodyId = Shader.PropertyToID("_UndulateBody");
        private static readonly int CoilId         = Shader.PropertyToID("_Coil");

        // Body wave of snakes and eels (heading swing, radians): snakes bend in even S-curves along
        // the whole body; eels swing mostly the back half
        private const float SnakeWave = 0.85f;
        private const float EelWave   = 0.55f;
        // A resting snake's coil (fractions of its length): inner radius, ring spacing, head held up
        private static readonly Vector4 SnakeCoil = new(1f, 0.06f, 0.055f, 0.07f);

        // Leg swing at full stride (radians); hoppers kick both legs together, further
        private const float WalkStride = 0.42f;
        private const float HopStride  = 0.6f;
        private const float RunStride  = 0.8f; // galloping: about twice the walking stride

        public static SpeciesColonies Instance { get; private set; }

        private HexGrid grid;
        private Material material;
        private readonly List<ColonyGroup> groups = new();
        // One group per niche of a tile (see Niches): up to six groups share a tile
        private readonly Dictionary<(HexCell, Niche), ColonyGroup> occupants = new();

        // Ordering a group around: click it, then click a marked neighbouring tile to move there,
        // or a marked tile holding another group to attack it.
        private ColonyGroup selected;
        private readonly List<HexCell> marked = new();
        private int clickFrame = -1;

        public ColonyGroup Selected => selected;
        public IReadOnlyList<ColonyGroup> Groups => groups;
        public ColonyGroup GroupAt(HexCell cell, Niche niche) => cell != null && occupants.TryGetValue((cell, niche), out var g) ? g : null;

        // Every group on a tile, in niche order (aerial first, underground last)
        public IEnumerable<ColonyGroup> GroupsAt(HexCell cell)
        {
            if (cell == null) yield break;
            foreach (var n in Niches.All)
                if (occupants.TryGetValue((cell, n), out var g) && g != null) yield return g;
        }

        // Any group on the tile (the first by niche), or null if it has none
        public ColonyGroup GroupAt(HexCell cell)
        {
            foreach (var g in GroupsAt(cell)) return g;
            return null;
        }

        // Which group a click on the tile picks: clicking the same tile again cycles through its
        // groups (those the current view shows), yours first.
        private ColonyGroup PickAt(HexCell cell, ColonyGroup current)
        {
            // only what the current view shows: underground-niche animals in the under view, the rest on the surface
            var list = new List<ColonyGroup>(GroupsAt(cell));
            list.RemoveAll(g => !UnderView.Shows(g));
            if (list.Count == 0) return null;
            list.Sort((a, b) => Mine(b).CompareTo(Mine(a)));
            int i = current != null ? list.IndexOf(current) : -1;
            return list[(i + 1) % list.Count];
        }
        private static bool Mine(ColonyGroup g) => g.Owner != null && g.Owner.IsHuman;

        // Raised after the groups for the displayed period have been (re)placed; all earlier groups,
        // including player-owned ones, are gone by then.
        public event System.Action ColoniesPlaced;

        // True if this click is (or was just) about colonies, so other click handlers (the player
        // ball) should leave it alone. Safe to call before or after this component handles the click.
        public bool HandlesClick(HexCell cell) =>
            clickFrame == Time.frameCount || selected != null || GroupAt(cell) != null;

        // Spawns the component in any scene that has a HexGrid, so Game.unity doesn't need editing.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<SpeciesColonies>() != null) return;
            new GameObject("SpeciesColonies").AddComponent<SpeciesColonies>();
        }

        private void Awake() => Instance = this;

        private void Start()
        {
            grid = HexGrid.Instance;
            if (grid == null) { Debug.LogWarning("[SpeciesColonies] No HexGrid in scene."); return; }
            if (GameDataLoader.Species == null) GameDataLoader.Initialize();

            grid.Generated      += PlaceColonies;
            grid.TerrainChanged += PlaceColonies; // another period: different species are alive
            if (grid.IsGenerated) PlaceColonies();
            CellSelector.CellClicked += OnCellClicked;
        }

        private void OnDestroy()
        {
            if (grid != null) { grid.Generated -= PlaceColonies; grid.TerrainChanged -= PlaceColonies; }
            CellSelector.CellClicked -= OnCellClicked;
            if (Instance == this) Instance = null;
        }

        private void OnCellClicked(HexCell cell)
        {
            if (selected != null)
            {
                clickFrame = Time.frameCount;
                var group = selected;
                if (marked.Contains(cell))
                {
                    // Only a group in the same niche competes; the others on the tile are left alone
                    var other = GroupAt(cell, group.Niche);
                    var from  = group.Cell;
                    Select(null);
                    if (other != null) group.Attack(cell);
                    else if (group.MoveTo(cell))
                    {
                        occupants.Remove((from, group.Niche));
                        occupants[(group.Cell, group.Niche)] = group;
                    }
                    return;
                }
                var clicked = PickAt(cell, cell == group.Cell ? group : null);
                bool orderable = clicked != null && (clicked.Owner == null || clicked.Owner.IsHuman);
                Select(clicked != group && orderable && clicked.CanAttack && !clicked.IsBusy ? clicked : null);
                return;
            }

            var g = PickAt(cell, null);
            if (g == null) return;
            clickFrame = Time.frameCount;
            if (g.Owner != null && !g.Owner.IsHuman) return; // other players' colonies aren't yours to order
            if (g.CanAttack && !g.IsBusy) Select(g); // fixed colonies can't move but can still strike a neighbour
        }

        // Marks the tiles the group can go to: green to move (only where it would find food and its
        // niche is free), red to attack the group holding its niche there.
        private void Select(ColonyGroup group)
        {
            foreach (var c in marked) if (c != null) c.SetGroupTarget(HexCell.GroupTarget.None);
            marked.Clear();
            selected = group;
            if (group == null) return;
            foreach (var n in grid.GetNeighbors(group.Cell))
            {
                var rival = GroupAt(n, group.Niche);
                bool attackable = rival != null && (group.CanEnter(n) || !group.CanMove); // fixed colonies strike in place
                if (!attackable && (rival != null || !group.CanMove || !group.CanEnter(n) || !group.CanLiveAt(n))) continue;
                marked.Add(n);
                n.SetGroupTarget(rival != null ? HexCell.GroupTarget.Attack : HexCell.GroupTarget.Move);
            }
        }

        // Shows the species alive in the period the map currently shows. Runs again whenever the
        // period changes, replacing the previous period's groups.
        private void PlaceColonies()
        {
            Select(null);
            foreach (var g in groups) if (g != null) Destroy(g.gameObject); // a regenerated map already destroyed them
            groups.Clear();
            occupants.Clear();
            if (material == null) material = Resources.Load<Material>("Materials/MapFeatures");
            var age  = grid.DisplayedAge;
            var rng  = new System.Random(grid.WorldSeed ^ 0x5eed ^ ((int)age * 7919));
            var used = new HashSet<(HexCell, Niche)>();

            // food first, then what eats it (see FoodWeb), so hunters can be placed next to their prey
            var order = new List<SpeciesDefinition>(GameDataLoader.Species);
            order.Sort((a, b) => FoodWeb.Stage(a) != FoodWeb.Stage(b) ? FoodWeb.Stage(a).CompareTo(FoodWeb.Stage(b)) : a.sizeCm.CompareTo(b.sizeCm));
            int alive = order.FindAll(d => !string.IsNullOrEmpty(d.model) && AliveIn(d, age)).Count;
            foreach (var def in order)
            {
                if (string.IsNullOrEmpty(def.model) || !AliveIn(def, age)) continue;
                var mesh = LoadMesh(def.model);
                if (mesh == null) { Debug.LogWarning($"[SpeciesColonies] No mesh at Resources/{def.model} for {def.id}."); continue; }
                if (!System.Enum.TryParse(def.mapStyle, true, out ColonyStyle style)) style = ColonyStyle.Drift;
                var niche = Niches.Of(def);
                var candidates = HabitatCells(def);
                if (candidates.Count == 0) { Debug.Log($"[SpeciesColonies] No habitat tile with food for {def.id}; skipping."); continue; }
                int copies = CopiesOf(alive, candidates.Count);
                var placed = new List<(int q, int r)>();
                for (int i = 0; i < copies; i++)
                {
                    var pick = PickHabitatCell(candidates, placed, niche, used, rng);
                    if (pick == null) break;
                    var (cell, q, r) = pick.Value;
                    placed.Add((q, r));
                    used.Add((cell, niche));
                    // big animals spill over onto the neighbouring tiles; keep other big ones off them
                    if (BuildColony(cell, def, mesh, style, rng) > ReserveSpan)
                    {
                        foreach (var n in grid.GetNeighbors(cell)) used.Add((n, niche));
                        copies = Mathf.Min(copies, MaxBigCopies);
                    }
                }
                Debug.Log($"[SpeciesColonies] Placed {placed.Count} {def.commonName} ({style}) colonies.");
            }
            ColoniesPlaced?.Invoke();
        }

        // ---------- Player-owned colonies (see Territory/TerritoryManager) ----------

        public bool IsAliveNow(SpeciesDefinition def) => AliveIn(def, grid.DisplayedAge);

        // Same habitat test as wild placement: the tile's terrain or its present-day biome is listed.
        public static bool FitsHabitat(SpeciesDefinition def, HexCell cell) =>
            cell != null && cell.Terrain != null && !cell.IsMountain && def.habitats != null &&
            UnderView.FitsBelow(def, cell) && // no way into solid bedrock; seabed animals on a seabed
            (def.habitats.Contains(cell.Terrain.kind.ToString()) || def.habitats.Contains(cell.Biome.ToString()));

        public static bool CanTravel(SpeciesDefinition def) =>
            !string.IsNullOrEmpty(def.model) &&
            !(System.Enum.TryParse(def.mapStyle, true, out ColonyStyle style) && style == ColonyStyle.Fixed);

        // Builds a group of `def` on `cell` belonging to `owner`. Null if the model can't be loaded.
        public ColonyGroup SpawnColony(SpeciesDefinition def, HexCell cell, Player owner, int seed)
        {
            if (material == null) material = Resources.Load<Material>("Materials/MapFeatures");
            var mesh = LoadMesh(def.model);
            if (mesh == null) return null;
            if (!System.Enum.TryParse(def.mapStyle, true, out ColonyStyle style)) style = ColonyStyle.Drift;
            BuildColony(cell, def, mesh, style, new System.Random(seed));
            var group = occupants[(cell, Niches.Of(def))];
            group.Owner = owner;
            return group;
        }

        // Removes a group from the map (a copy that evolved, or a player's groups replaced on loading).
        public void DespawnColony(ColonyGroup group)
        {
            if (group == null) return;
            if (selected == group) Select(null);
            if (group.Cell != null && occupants.TryGetValue((group.Cell, group.Niche), out var g) && g == group) occupants.Remove((group.Cell, group.Niche));
            groups.Remove(group);
            Destroy(group.gameObject);
        }

        // firstAge..lastAge inclusive; an empty or unknown firstAge counts as always, an empty lastAge as still alive.
        private static bool AliveIn(SpeciesDefinition def, GeologicalAge age)
        {
            if (System.Enum.TryParse(def.firstAge, true, out GeologicalAge first) && age < first) return false;
            if (System.Enum.TryParse(def.lastAge,  true, out GeologicalAge last)  && age > last)  return false;
            return true;
        }

        // How much the age's animals are enlarged: enough that its biggest mapped species is drawn as
        // if it were AgeReferenceCm long (map size grows with the square root of length), between 1
        // (ages with big animals keep real relative sizes) and MaxAgeZoom.
        private static readonly Dictionary<GeologicalAge, float> ageZooms = new();
        private static float AgeZoom(GeologicalAge age)
        {
            if (ageZooms.TryGetValue(age, out float zoom)) return zoom;
            float largest = 0f;
            foreach (var def in GameDataLoader.Species)
                if (!string.IsNullOrEmpty(def.model) && AliveIn(def, age)) largest = Mathf.Max(largest, def.sizeCm);
            zoom = largest > 0f ? Mathf.Clamp(Mathf.Sqrt(AgeReferenceCm / largest), 1f, MaxAgeZoom) : 1f;
            ageZooms[age] = zoom;
            return zoom;
        }

        private static Mesh LoadMesh(string path)
        {
            var model = Resources.Load<GameObject>(path);
            var filter = model != null ? model.GetComponentInChildren<MeshFilter>() : null;
            return filter != null ? filter.sharedMesh : null;
        }

        // How many wild colonies of a species to show: more per species in ages with few of them,
        // fewer for species with little habitat.
        private static int CopiesOf(int aliveSpecies, int habitatTiles) =>
            Mathf.Min(Mathf.Clamp(TargetWildGroups / Mathf.Max(1, aliveSpecies), MinCopies, MaxCopies),
                      Mathf.Max(1, habitatTiles / TilesPerCopy));

        // The habitat tiles with food (see FoodWeb) for `def`, with their offset coordinates.
        // Habitats name present-day terrain, so a tile also matches by the biome its climate makes
        // today (a Cretaceous fern prairie is where the plains will be).
        private List<(HexCell cell, int q, int r)> HabitatCells(SpeciesDefinition def)
        {
            var niche = Niches.Of(def);
            var cells = new List<(HexCell, int, int)>();
            if (def.habitats == null) return cells;
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null || cell.Terrain == null || cell.IsMountain) continue;
                if (!def.habitats.Contains(cell.Terrain.kind.ToString()) && !def.habitats.Contains(cell.Biome.ToString())) continue;
                if (!UnderView.FitsBelow(def, cell)) continue;
                if (!FoodWeb.HasFood(def, cell, this, null)) continue;
                cells.Add((cell, q, r));
            }
            return cells;
        }

        // A free tile among `candidates` for the next colony of a species. The first goes near the map
        // centre, where the camera starts; later ones as far as possible from the species' colonies so
        // far (best of a random sample, minding the east–west wrap). Tiles that carry a reef, forest or
        // oasis prop, or that a big neighbouring animal spills onto, are a last resort.
        private (HexCell cell, int q, int r)? PickHabitatCell(List<(HexCell cell, int q, int r)> candidates,
            List<(int q, int r)> placed, Niche niche, HashSet<(HexCell, Niche)> used, System.Random rng)
        {
            float Penalty(HexCell cell) =>
                (cell.Feature != TerrainFeature.None ? 1000f : 0f) + (used.Contains((cell, niche)) ? 2000f : 0f);
            var free = candidates.FindAll(c => !occupants.ContainsKey((c.cell, niche)));
            if (free.Count == 0) return null;

            if (placed.Count == 0)
            {
                var center = new Vector2((grid.Width - 1) * 0.5f, (grid.Height - 1) * 0.5f);
                free.Sort((a, b) => (Vector2.Distance(new Vector2(a.q, a.r), center) + Penalty(a.cell))
                         .CompareTo(Vector2.Distance(new Vector2(b.q, b.r), center) + Penalty(b.cell)));
                return free[rng.Next(Mathf.Min(5, free.Count))];
            }

            float Spread(int q, int r)
            {
                float nearest = float.MaxValue;
                foreach (var (pq, pr) in placed)
                {
                    int dq = Mathf.Abs(q - pq);
                    dq = Mathf.Min(dq, grid.Width - dq);
                    nearest = Mathf.Min(nearest, new Vector2(dq, r - pr).magnitude);
                }
                return nearest;
            }
            (HexCell, int, int)? best = null;
            float bestScore = float.MinValue;
            for (int i = 0; i < Mathf.Min(24, free.Count); i++)
            {
                var c = free[rng.Next(free.Count)];
                float score = Spread(c.q, c.r) - Penalty(c.cell);
                if (score > bestScore) { bestScore = score; best = c; }
            }
            return best;
        }

        // Returns the size of one member on its tile (in cells).
        private float BuildColony(HexCell cell, SpeciesDefinition def, Mesh mesh, ColonyStyle style, System.Random rng)
        {
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);
            var (count, memberSpan, colonyRadius) = Layouts[style];
            if (def.colonySize > 0) count = def.colonySize;
            float zoom = AgeZoom(grid.DisplayedAge);
            count = Mathf.Max(1, Mathf.RoundToInt(count / Mathf.Sqrt(zoom))); // bigger members, fewer of them
            float sizeSpan = SizeSpanPerSqrtMetre * Mathf.Sqrt(Mathf.Max(def.sizeCm, 0f) / 100f) * zoom;
            // microbes are held up only by the minimum size, so they would look the same in every age;
            // instead they shrink after the Cambrian (MicrobeScale)
            float microbe = IsMicrobe(def) ? MicrobeScale(grid.DisplayedAge) : 1f;
            memberSpan = Mathf.Min(Mathf.Max(memberSpan * microbe, sizeSpan), MaxSpan);
            if (def.mapScale > 0f) memberSpan *= def.mapScale; // per-model framing (tall perch, wide web...)
            memberSpan = Mathf.Max(memberSpan, (style == ColonyStyle.Swarm ? MinSwarmSpan : MinSpan) * microbe);
            // a snake rests coiled up (see ColonyGroup), so it takes the room of its coil, not its length
            bool coiled = style == ColonyStyle.Ground && string.Equals(def.mapGait, "Slither", System.StringComparison.OrdinalIgnoreCase);
            float footprint = coiled ? memberSpan * 0.3f : memberSpan;
            colonyRadius = Mathf.Max(colonyRadius, footprint * 0.7f); // big animals need room
            var root = new GameObject($"Colony_{def.id}").transform;
            root.SetParent(cell.transform, false);
            root.localPosition = Niches.Spot(Niches.Of(def)) + Vector3.up * cell.SurfaceHeight; // its niche's spot on the tile
            if (!System.Enum.TryParse(def.mapGait, true, out ColonyGait gait)) gait = ColonyGait.Walk;
            var group = root.gameObject.AddComponent<ColonyGroup>();
            group.Init(def, style, gait, cell, memberSpan);
            groups.Add(group);
            occupants[(cell, group.Niche)] = group;

            // Microbes and swarms are sized by their longest dimension; everything else by its
            // footprint, so hanging tentacles or tall poses don't shrink the animal.
            var size = mesh.bounds.size;
            bool anyAxis = style is ColonyStyle.Drift or ColonyStyle.Swarm;
            float meshSpan = anyAxis ? Mathf.Max(size.x, size.y, size.z) : Mathf.Max(size.x, size.z);
            float schoolSpeed = rng.NextDouble() < 0.5 ? 0.18f : -0.18f; // Swim: radians per second
            float halfSpan = Mathf.Max(-mesh.bounds.min.x, mesh.bounds.max.x);
            float flapAmplitude = style switch
            {
                ColonyStyle.Soar  => SoarFlap,
                ColonyStyle.Swarm => SwarmFlap,
                ColonyStyle.Swim  => SwimFlap,
                _                 => 0f,
            };

            for (int i = 0; i < count; i++)
            {
                // One member in the middle, the rest scattered around it
                float angle = (i / (float)Mathf.Max(1, count - 1) + R(-0.06f, 0.06f)) * Mathf.PI * 2f;
                float dist  = i == 0 ? 0f : colonyRadius * R(0.55f, 1f);
                float span  = memberSpan * R(0.8f, 1.12f);
                var pos     = new Vector3(Mathf.Cos(angle) * dist, 0f, Mathf.Sin(angle) * dist);
                var member  = new ColonyGroup.Member
                {
                    span         = span,
                    phase        = R(0f, Mathf.PI * 2f),
                    baseRotation = Quaternion.Euler(0f, R(0f, 360f), 0f),
                };
                switch (style)
                {
                    case ColonyStyle.Drift:
                        pos.y        = span * R(0.35f, 0.5f);
                        member.axis  = new Vector3(R(-1f, 1f), 1f, R(-1f, 1f)).normalized;
                        member.baseRotation = Quaternion.identity;
                        break;
                    case ColonyStyle.Swarm:
                        pos   *= 0.8f;
                        pos.y  = SwarmHeight + R(-0.12f, 0.12f);
                        break;
                    case ColonyStyle.Soar:
                        pos.y         = SoarHeight + span * 0.3f + R(-0.1f, 0.15f); // big wings fly higher
                        member.radius = colonyRadius * R(0.6f, 1.1f);
                        member.speed  = R(0.25f, 0.4f) * (rng.NextDouble() < 0.8 ? 1f : -1f);
                        member.phase  = angle;
                        break;
                    case ColonyStyle.Swim:
                        // the whole school circles the same way, about three quarters above the
                        // surface (the opaque tile would hide anything deeper), at slightly different depths
                        pos.y         = (-mesh.bounds.min.y - 0.25f * size.y) * (span / meshSpan) + R(0f, 0.02f);
                        member.radius = i == 0 ? colonyRadius * 0.35f : dist;
                        member.speed  = schoolSpeed * R(0.9f, 1.1f);
                        member.phase  = angle;
                        break;
                    case ColonyStyle.Ground:
                        // big animals amble slowly over a wider patch; small ones scurry about their spot
                        member.radius    = Mathf.Clamp(span * 0.3f, 0.06f, 0.25f);
                        member.speed     = Mathf.Clamp(span * 0.15f, 0.03f, 0.15f) * (gait == ColonyGait.Hop ? 2f : 1f);
                        member.heading   = member.baseRotation.eulerAngles.y;
                        member.position  = member.target = pos;
                        member.restUntil = Time.time + R(0f, 4f);
                        break;
                }
                member.basePosition = pos;

                var go = new GameObject(def.id);
                go.transform.SetParent(root, false);
                go.transform.localPosition = pos;
                go.transform.localRotation = member.baseRotation;
                go.transform.localScale    = Vector3.one * (span / meshSpan);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                var mr = go.AddComponent<MeshRenderer>(); // no collider: clicks reach the hex below
                mr.sharedMaterial = material;
                var block = new MaterialPropertyBlock();
                float v = R(0.92f, 1.06f);
                block.SetColor("_Color", new Color(v, v * R(0.97f, 1.02f), v * R(0.94f, 1.0f)));
                if (def.wingBeat > 0f && flapAmplitude > 0f)
                {
                    block.SetFloat(FlapRootId, (def.wingRoot > 0f ? def.wingRoot : 0.15f) * halfSpan);
                    block.SetFloat(FlapSpanId, halfSpan);
                    member.flapRate      = def.wingBeat * R(0.9f, 1.1f) * Mathf.PI * 2f;
                    member.flapAmplitude = flapAmplitude;
                }
                if (style == ColonyStyle.Ground && gait != ColonyGait.Slither)
                {
                    // everything below the hips swings as legs (see MapFeatureFlap.cginc)
                    var b      = mesh.bounds;
                    float hipY = b.min.y + (def.mapHip > 0f ? def.mapHip : 0.45f) * b.size.y;
                    block.SetVector(StrideLegsId, new Vector4(hipY, hipY - b.min.y, b.min.z, b.max.z));
                    block.SetVector(StrideModeId, new Vector4(def.mapLegs > 0 ? def.mapLegs : 2, gait == ColonyGait.Hop ? 1f : 0f, 0f, 0f));
                    member.strideAmplitude = gait == ColonyGait.Hop ? HopStride : WalkStride;
                    if (gait == ColonyGait.Run)
                    {
                        member.runAmplitude = RunStride;
                        member.legPairs     = def.mapLegs > 0 ? def.mapLegs : 2;
                    }
                    if (gait == ColonyGait.Hop)
                    {
                        // two-legged hoppers (kangaroos) bound along with hardly a pause; frogs and
                        // toads sit between long, high leaps
                        bool bounds = def.mapLegs == 1;
                        member.jumps      = true;
                        member.jumpLength = Mathf.Max(span * (bounds ? 0.9f : 1.2f), 0.12f);
                        member.jumpTime   = bounds ? 0.42f : 0.32f;
                        member.jumpHeight = member.jumpLength * (bounds ? 0.25f : 0.45f);
                        member.jumpPause  = bounds ? 0f : 0.25f;
                    }
                    member.legLength       = (hipY - b.min.y) * (span / meshSpan);
                }
                if (style == ColonyStyle.Ground && gait == ColonyGait.Slither || def.mapUndulate)
                {
                    // the straight model is bent into a travelling wave (see MapFeatureFlap.cginc)
                    var b    = mesh.bounds;
                    bool eel = style != ColonyStyle.Ground;
                    member.undulateAmplitude = eel ? EelWave : SnakeWave;
                    member.undulateWaves     = eel ? 1f : 1.5f;
                    member.undulateInWater   = eel;
                    member.bodyLength        = b.size.z * (span / meshSpan);
                    member.coils             = !eel;
                    member.coilShape         = SnakeCoil;
                    block.SetVector(UndulateBodyId, new Vector4(b.min.z, b.max.z, member.undulateWaves, eel ? 0.75f : 0.2f));
                    if (member.coils) block.SetVector(CoilId, SnakeCoil);
                }
                mr.SetPropertyBlock(block);

                member.transform = go.transform;
                member.renderer  = mr;
                member.block     = block;
                group.AddMember(member);
            }
            return footprint;
        }
    }
}
