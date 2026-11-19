using System.Linq;
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
        private const float LargeFlierCm         = 90f;  // fliers this long or longer stand alone on their tile
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
        // Every species alive in the period placed wild on the map (the old opening); off, the game
        // starts with only the players' founders and wild groups are born along the way (WildBirths)
        public static bool PlaceAllWild = false;

        // Safari Mode (Admin): every species alive in the period is placed wild, and the player can
        // take control of any group, wild ones too. Switching it off brings back the wild groups that
        // were born in the game (WildBirths) in place of the safari's.
        public static bool SafariMode { get; private set; }
        public static event System.Action<bool> SafariModeChanging; // before the map's groups are rebuilt

        public void SetSafariMode(bool on)
        {
            if (on == SafariMode) return;
            SafariMode = PlaceAllWild = on;
            SafariModeChanging?.Invoke(on);
            if (grid != null && grid.IsGenerated) PlaceColonies();
        }
        private const double RareShare          = 0.5;  // of each period's species, chosen at random, shown as one group only
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
        // Shelled snails and cephalopods with an outer shell rest where they are when settled,
        // swaying a little, rather than circling or wandering about the tile
        private static readonly HashSet<string> StillGroups = new()
        {
            "Ammonite", "Heteromorph ammonite", "Nautiloid cephalopod", "Bactritid", "Early cephalopod",
            "Sea snail", "Land snail", "Abalone",
        };
        private static bool RestsStill(SpeciesDefinition def) => def != null && StillGroups.Contains(def.group ?? "");

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

        // The map props' material, marking the animals in the stencil buffer so territory borders
        // (TerritoryBorder shader) are drawn around them, never over them, even under water
        private static readonly int StencilRefId = Shader.PropertyToID("_StencilRef");
        private static Material AnimalMaterial()
        {
            var shared = Resources.Load<Material>("Materials/MapFeatures");
            if (shared == null) return null;
            var m = new Material(shared) { name = "MapFeatures (animals)" };
            m.SetInt(StencilRefId, 1);
            return m;
        }
        private readonly List<ColonyGroup> groups = new();
        // One group per niche of a tile (see Niches); slots remembers which one each group holds
        private readonly Dictionary<(HexCell, Niche), ColonyGroup> occupants = new();
        private readonly Dictionary<ColonyGroup, (HexCell, Niche)> slots = new();

        // Moves a group along a path the way a player's order does (AI players and wild groups:
        // Players/AiPlayers): the group takes its niche on the tile it ends on
        public bool Travel(ColonyGroup group, IReadOnlyList<HexCell> path)
        {
            if (group == null || !group.MoveAlong(path)) return false;
            Occupy(group);
            return true;
        }

        // A group takes the niche it has on its (new) tile
        // Walks the group along `path` (MoveOrders) and gives it its new tile's niche
        public bool MoveGroup(ColonyGroup group, List<HexCell> path)
        {
            if (group == null || !group.MoveAlong(path)) return false;
            Occupy(group);
            return true;
        }

        private void Occupy(ColonyGroup group)
        {
            Vacate(group);
            var niche = Niches.Of(group.Definition, group.Cell);
            group.Niche = niche;
            occupants[(group.Cell, niche)] = group;
            slots[group] = (group.Cell, niche);
        }

        private void Vacate(ColonyGroup group)
        {
            if (!slots.TryGetValue(group, out var slot)) return;
            if (occupants.TryGetValue(slot, out var g) && g == group) occupants.Remove(slot);
            slots.Remove(group);
        }

        // Ordering a group around: click it, then click a tile inside its outlined range to move
        // there, or a tile ringed in red to attack the group on it.
        private ColonyGroup selected;
        private readonly List<HexCell> marked = new();
        private MoveRange range; // the selected group's, while it has orders to give
        private int clickFrame = -1;

        // Choosing a tile for something (where the young of a reproducing group go): the tiles on
        // offer are marked, a click on one of them chooses it, any other click cancels
        private readonly List<HexCell> offered = new();
        private System.Action<HexCell> onChosen;
        public bool IsChoosingTile => onChosen != null;

        public void ChooseTile(IEnumerable<HexCell> tiles, System.Action<HexCell> chosen)
        {
            var keep = selected;
            EndChoosing();
            foreach (var c in marked) if (c != null) c.SetGroupTarget(HexCell.GroupTarget.None); // the move marks give way
            marked.Clear();
            range = null;
            MovePathView.Hide();
            selected = keep;
            foreach (var c in tiles)
            {
                if (c == null) continue;
                offered.Add(c);
                c.SetGroupTarget(HexCell.GroupTarget.Move);
            }
            onChosen = offered.Count > 0 ? chosen : null;
        }

        private void EndChoosing()
        {
            foreach (var c in offered) if (c != null) c.SetGroupTarget(HexCell.GroupTarget.None);
            offered.Clear();
            onChosen = null;
        }

        public ColonyGroup Selected => selected;
        public IReadOnlyList<ColonyGroup> Groups => groups;
        public ColonyGroup GroupAt(HexCell cell, Niche niche) => cell != null && occupants.TryGetValue((cell, niche), out var g) ? g : null;

        // Every group on a tile, in niche order
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

        // Which group a click on the tile picks: the one the tile shows (UnderView.Focus); clicking
        // the same tile again moves on to its next group of the current layer.
        private static ColonyGroup PickAt(HexCell cell, bool again)
        {
            if (again) UnderView.Focus.Next(cell);
            return UnderView.Focus.Current(cell);
        }
        private HexCell lastClicked;

        // Tab: the selected tile shows its next group; a group picked for orders there follows
        public void CycleFocus()
        {
            var cell = CellSelector.Selected;
            if (cell == null) return;
            UnderView.Focus.Next(cell);
            if (selected == null || selected.Cell != cell) return;
            var g = UnderView.Focus.Current(cell);
            Select(g != null && (g.Owner == null || g.Owner.IsHuman) && g.CanAttack && !g.IsBusy ? g : null);
        }

        // Picks one of the player's groups for orders as clicking it would (UnitCycle): shows its
        // layer, selects its tile with it in front and marks where it can go
        public void Order(ColonyGroup g)
        {
            if (g == null || g.Cell == null) return;
            if (!UnderView.InLayer(g, UnderView.Layer))
                UnderView.Set(UnderView.InLayer(g, MapLayer.Surface) ? MapLayer.Surface : UnderView.InLayer(g, MapLayer.Under) ? MapLayer.Under : MapLayer.Sky);
            CellSelector.SelectCell(g.Cell);
            UnderView.Focus.Show(g);
            lastClicked = g.Cell;
            Select(g.CanAttack && !g.IsBusy ? g : null);
        }

        // Mountain tiles are only for species that list "Mountain" among their habitats
        public static bool LivesOnMountains(SpeciesDefinition def) =>
            def != null && def.habitats != null && def.habitats.Contains(nameof(TerrainKind.Mountain));

        // Raised after the groups for the displayed period have been (re)placed; all earlier groups,
        // including player-owned ones, are gone by then.
        public event System.Action ColoniesPlaced;
        public event System.Action ColoniesClearing; // just before PlaceColonies clears the map's groups (WildBirths)

        // True if this click is (or was just) about colonies, so other click handlers (the player
        // ball) should leave it alone. Safe to call before or after this component handles the click.
        public bool HandlesClick(HexCell cell) =>
            clickFrame == Time.frameCount || selected != null || IsChoosingTile || GroupAt(cell) != null;

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
            if (AgeManager.Instance != null) AgeManager.Instance.TimeChanged += OnTimeChanged;
        }

        private void OnDestroy()
        {
            if (grid != null) { grid.Generated -= PlaceColonies; grid.TerrainChanged -= PlaceColonies; }
            CellSelector.CellClicked -= OnCellClicked;
            if (AgeManager.Instance != null) AgeManager.Instance.TimeChanged -= OnTimeChanged;
            if (Instance == this) Instance = null;
        }

        // Reaching the present day (after the last turn of the Quaternary) ends the Ice Age: the
        // species that died out in the Quaternary (a lastAge) leave the map. Players' groups stay.
        private void OnTimeChanged()
        {
            if (!PresentDay) return;
            foreach (var g in groups.ToArray())
                if (g != null && g.Owner == null && !AliveIn(g.Definition, grid.DisplayedAge)) DespawnColony(g);
        }

        private static bool PresentDay => AgeManager.Instance != null && AgeManager.Instance.IsPresentDay;

        private void OnCellClicked(HexCell cell)
        {
            bool again = cell == lastClicked;
            lastClicked = cell;
            if (IsChoosingTile)
            {
                clickFrame = Time.frameCount;
                var chosen = onChosen;
                bool ok = offered.Contains(cell);
                var group = selected;
                EndChoosing();
                if (ok) chosen(cell);
                Select(group != null && group.CanAttack && !group.IsBusy ? group : null); // back to its orders
                lastClicked = null;
                return;
            }
            if (selected != null)
            {
                clickFrame = Time.frameCount;
                var group = selected;
                if (marked.Contains(cell) && range != null)
                {
                    // A tile with a foreign group it can fight is an attack (Combat: the biggest one
                    // there defends), from the nearest tile it can strike from: it goes there first
                    // and strikes on arrival. Otherwise it moves in along the shortest path.
                    var order = range;
                    Select(null);
                    lastClicked = null;
                    MoveOrders.Cancel(group); // an order of its own replaces a long move
                    if (order.AttackFrom.TryGetValue(cell, out var from))
                    {
                        if (from == group.Cell) { group.Attack(cell); return; }
                        if (!group.MoveAlong(order.PathTo(from))) return;
                        Occupy(group);
                        void StrikeOnArrival(ColonyGroup g)
                        {
                            g.Arrived -= StrikeOnArrival;
                            if (g != null && g.Cell == from) g.Attack(cell);
                        }
                        group.Arrived += StrikeOnArrival;
                    }
                    else if (group.MoveAlong(order.PathTo(cell))) Occupy(group);
                    return;
                }
                var clicked = PickAt(cell, again);
                bool orderable = clicked != null && (SafariMode || (clicked.Owner != null && clicked.Owner.IsHuman));
                // a tile beyond this turn's reach without an animal of yours to pick: go there over
                // the coming turns (MoveOrders; MovePathView shows how many)
                if (!orderable && cell != group.Cell && !group.JustBorn && MoveOrders.Give(group, cell))
                {
                    Select(null);
                    lastClicked = null;
                    return;
                }
                Select(clicked != group && orderable && clicked.CanAttack && !clicked.IsBusy ? clicked : null);
                return;
            }

            var g = PickAt(cell, again);
            // your own animal on this tile lives in another layer (plankton under the sea surface,
            // a soil animal under the land): show that layer and pick it
            if (!again && (g == null || g.Owner == null || !g.Owner.IsHuman))
            {
                var mine = GroupsAt(cell).FirstOrDefault(x => x.Owner != null && x.Owner.IsHuman && x.CanAttack && !x.IsBusy);
                if (mine != null && !UnderView.InLayer(mine, UnderView.Layer))
                {
                    UnderView.Set(UnderView.InLayer(mine, MapLayer.Surface) ? MapLayer.Surface : UnderView.InLayer(mine, MapLayer.Under) ? MapLayer.Under : MapLayer.Sky);
                    UnderView.Focus.Show(mine);
                    g = mine;
                }
            }
            if (g == null) return;
            clickFrame = Time.frameCount;
            if (!SafariMode && (g.Owner == null || !g.Owner.IsHuman)) return; // only your own colonies are yours to order (any in Safari Mode)
            if (g.CanAttack && !g.IsBusy) Select(g); // fixed colonies can't move but can still strike a neighbour
        }

        // Marks the tiles the group can go to with the actions it has left this turn: green to move
        // (only where it would find food and its niche is free), red to attack (a wild or another
        // player's group in its layer there that is within ten times its size, see Combat).
        // The group that would defend `cell` against `group`, if they can fight at all
        internal static ColonyGroup Attackable(ColonyGroup group, HexCell cell)
        {
            var foe = Combat.Defender(group, cell);
            return foe != null && Combat.CanFight(group, foe) ? foe : null;
        }

        // Marks everything the group can reach this turn (MoveRange): the tiles it can move to
        // (outlined, MovePathView, with the path to the tile under the mouse) and the groups it can
        // attack, on their tile or after moving next to them.
        private void Select(ColonyGroup group)
        {
            if (group != selected) EndChoosing();
            foreach (var c in marked) if (c != null) c.SetGroupTarget(HexCell.GroupTarget.None);
            marked.Clear();
            range = null;
            MovePathView.Hide();
            selected = group;
            if (group == null || group.JustBorn) return; // new this turn: its card shows, but no orders yet
            range = MoveRange.For(group, this);
            foreach (var n in range.Destinations) { marked.Add(n); n.SetGroupTarget(HexCell.GroupTarget.Move); }
            foreach (var n in range.AttackFrom.Keys) { marked.Add(n); n.SetGroupTarget(HexCell.GroupTarget.Attack); }
            MovePathView.Show(range);
        }

        // Clears the map's groups whenever the period changes (the players' are put back by
        // TerritoryManager/EvolutionManager, the wild ones by WildBirths). With PlaceAllWild it also
        // shows every species alive in the period; normally the wild ones only come from WildBirths.
        private void PlaceColonies()
        {
            ColoniesClearing?.Invoke();
            Select(null);
            foreach (var g in groups) if (g != null) Destroy(g.gameObject); // a regenerated map already destroyed them
            groups.Clear();
            occupants.Clear();
            slots.Clear();
            UnderView.Focus.Reset();
            if (material == null) material = AnimalMaterial();
            if (!PlaceAllWild) { ColoniesPlaced?.Invoke(); return; }
            var age  = grid.DisplayedAge;
            var rng  = new System.Random(grid.WorldSeed ^ 0x5eed ^ ((int)age * 7919));
            var used = new HashSet<(HexCell, Niche)>();
            // which species are rare this period (a single group each, so the map isn't crowded):
            // its own generator, so the choice doesn't shift where the others are placed
            var rare = new System.Random(grid.WorldSeed ^ 0x7a2e ^ ((int)age * 104729));

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
                var candidates = HabitatCells(def);
                if (candidates.Count == 0) { Debug.Log($"[SpeciesColonies] No habitat tile with food for {def.id}; skipping."); continue; }
                int copies = rare.NextDouble() < RareShare ? 1 : CopiesOf(alive, candidates.Count);
                var placed = new List<(int q, int r)>();
                for (int i = 0; i < copies; i++)
                {
                    var pick = PickHabitatCell(candidates, placed, def, used, rng);
                    if (pick == null) break;
                    var (cell, q, r) = pick.Value;
                    placed.Add((q, r));
                    used.Add((cell, Niches.Of(def, cell)));
                    // big animals spill over onto the neighbouring tiles; keep other big ones off them
                    if (BuildColony(cell, def, mesh, style, rng) > ReserveSpan)
                    {
                        foreach (var n in grid.GetNeighbors(cell)) used.Add((n, Niches.Of(def, n)));
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
            cell != null && cell.Terrain != null && def.habitats != null && (!cell.IsMountain || LivesOnMountains(def)) &&
            UnderView.FitsBelow(def, cell) && // no way into solid bedrock; seabed animals on a seabed
            (def.habitats.Contains(cell.Terrain.kind.ToString()) || def.habitats.Contains(cell.Biome.ToString()));

        public static bool CanTravel(SpeciesDefinition def) =>
            !string.IsNullOrEmpty(def.model) &&
            !(System.Enum.TryParse(def.mapStyle, true, out ColonyStyle style) && style == ColonyStyle.Fixed);

        // Builds a group of `def` on `cell` belonging to `owner`. Null if the model can't be loaded.
        public ColonyGroup SpawnColony(SpeciesDefinition def, HexCell cell, Player owner, int seed)
        {
            if (material == null) material = AnimalMaterial();
            var mesh = LoadMesh(def.model);
            if (mesh == null) return null;
            if (!System.Enum.TryParse(def.mapStyle, true, out ColonyStyle style)) style = ColonyStyle.Drift;
            BuildColony(cell, def, mesh, style, new System.Random(seed));
            var group = groups[groups.Count - 1];
            group.Owner = owner;
            if (owner == null) group.RestoreCombat(Combat.Carried(def, cell)); // a wild group put back after the map was rebuilt keeps its HP
            return group;
        }

        // Removes a group from the map (a copy that evolved, or a player's groups replaced on loading).
        public void DespawnColony(ColonyGroup group)
        {
            if (group == null) return;
            if (selected == group) Select(null);
            Vacate(group);
            groups.Remove(group);
            Destroy(group.gameObject);
        }

        // firstAge..lastAge inclusive; an empty or unknown firstAge counts as always, an empty lastAge as
        // still alive. In the present day only the still-living species are (any lastAge has passed).
        private static bool AliveIn(SpeciesDefinition def, GeologicalAge age)
        {
            if (System.Enum.TryParse(def.firstAge, true, out GeologicalAge first) && age < first) return false;
            if (System.Enum.TryParse(def.lastAge,  true, out GeologicalAge last)  && (age > last || PresentDay)) return false;
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
            var cells = new List<(HexCell, int, int)>();
            if (def.habitats == null) return cells;
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null || cell.Terrain == null || (cell.IsMountain && !LivesOnMountains(def))) continue;
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
            List<(int q, int r)> placed, SpeciesDefinition def, HashSet<(HexCell, Niche)> used, System.Random rng)
        {
            float Penalty(HexCell cell) =>
                (cell.Feature != TerrainFeature.None ? 1000f : 0f) + (used.Contains((cell, Niches.Of(def, cell))) ? 2000f : 0f);
            var free = candidates.FindAll(c => !occupants.ContainsKey((c.cell, Niches.Of(def, c.cell))));
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
            // big birds and pterosaurs (pelicans, condors, flamingos, Pteranodon...): one to a tile
            bool flier = style == ColonyStyle.Soar || !string.IsNullOrEmpty(def.flightModel);
            if (flier && def.sizeCm >= LargeFlierCm) count = 1;
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
            root.localPosition = Niches.Spot(Niches.Of(def, cell)) + Vector3.up * cell.SurfaceHeight; // its niche's spot on the tile
            if (!System.Enum.TryParse(def.mapGait, true, out ColonyGait gait)) gait = ColonyGait.Walk;
            var group = root.gameObject.AddComponent<ColonyGroup>();
            group.Init(def, style, gait, cell, memberSpan);
            groups.Add(group);
            Occupy(group);

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
                member.still = RestsStill(def);

                var go = new GameObject(def.id);
                go.transform.SetParent(root, false);
                go.transform.localPosition = pos;
                go.transform.localRotation = member.baseRotation;
                go.transform.localScale    = Vector3.one * (span / meshSpan);
                var filter = go.AddComponent<MeshFilter>();
                filter.sharedMesh = mesh;
                var mr = go.AddComponent<MeshRenderer>(); // no collider: clicks reach the hex below
                mr.sharedMaterial = material;
                var block = new MaterialPropertyBlock();
                float v = R(0.92f, 1.06f);
                block.SetColor("_Color", new Color(v, v * R(0.97f, 1.02f), v * R(0.94f, 1.0f)));
                block.SetVector(AnimalFur.FurId, AnimalFur.Of(def, mesh));
                if (def.wingBeat > 0f && flapAmplitude > 0f)
                {
                    block.SetFloat(FlapRootId, (def.wingRoot > 0f ? def.wingRoot : 0.15f) * halfSpan);
                    block.SetFloat(FlapSpanId, halfSpan);
                    member.flapRate      = def.wingBeat * R(0.9f, 1.1f) * Mathf.PI * 2f;
                    member.flapAmplitude = member.airFlapAmplitude = flapAmplitude;
                }
                else if (style is ColonyStyle.Ground or ColonyStyle.Float or ColonyStyle.Fixed && Niches.IsFlyer(def))
                {
                    // a flier that walks, swims or sits in its colony: still in the colony, beating
                    // its wings once it takes off in the sky view (ColonyGroup.Flight)
                    // its flight model, wings spread, is swapped in on take-off and beats them
                    var flight = string.IsNullOrEmpty(def.flightModel) ? null : LoadMesh(def.flightModel);
                    float wingHalf = flight != null ? Mathf.Max(-flight.bounds.min.x, flight.bounds.max.x) : halfSpan;
                    block.SetFloat(FlapRootId, (def.wingRoot > 0f ? def.wingRoot : 0.15f) * wingHalf);
                    block.SetFloat(FlapSpanId, wingHalf);
                    member.restMesh         = mesh;
                    member.flightMesh       = flight;
                    member.flapRate         = (def.wingBeat > 0f ? def.wingBeat : 2.5f) * R(0.9f, 1.1f) * Mathf.PI * 2f;
                    member.flapAmplitude    = 0f;
                    member.airFlapAmplitude = SoarFlap * 0.7f;
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
                member.filter    = filter;
                member.block     = block;
                group.AddMember(member);
            }
            return footprint;
        }
    }
}
