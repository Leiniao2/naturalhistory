using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Players;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Territory
{
    // Each player's habitat center and the territory around it.
    //
    //   - A center is founded on every player's start hex and is named after a park or landmark of
    //     the player's faction that matches its surroundings (HabitatNames).
    //   - Its 7 hexes (the center and its neighbours) always belong to the player.
    //   - A colony of the player's that stands on the player's territory claims its 6 neighbours too.
    //     Territory follows the colonies: hexes no colony (or center) holds any more fall back to
    //     unclaimed, so a colony leaving its range carries the border with it one step at a time.
    //   - Every player starts with one colony of a species that fits their center, placed on the core.
    //
    // Other players' cores are never taken. Where two players' colonies claim the same hex, whoever
    // held it keeps it; otherwise the player listed first gets it.
    public class TerritoryManager : MonoBehaviour
    {
        public static TerritoryManager Instance { get; private set; }

        public event Action TerritoryChanged;

        public IReadOnlyList<HabitatCenter> Centers => centers;
        public Player OwnerOf(HexCell cell) => cell != null && owners.TryGetValue(cell, out var p) ? p : null;
        public HabitatCenter CenterOf(Player player) => centers.FirstOrDefault(c => c.Owner == player);

        private HexGrid grid;
        private SpeciesColonies colonies;
        private PlayerManager playerManager;

        private readonly List<HabitatCenter> centers = new();
        private Dictionary<HexCell, Player> owners = new();
        private readonly List<GameObject> labels = new();

        // Per player index: their colony, and where/what it was, so it comes back in the same place
        // when SpeciesColonies re-places every group (another period is shown).
        private readonly Dictionary<int, ColonyGroup> playerColonies = new();
        private readonly Dictionary<int, HexCell> lastColonyCell = new();
        private readonly Dictionary<int, string> lastColonySpecies = new();
        private int lastWorldSeed;

        private bool rebuildPending;

        // Spawns the component in any scene that has a HexGrid, so Game.unity doesn't need editing.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<TerritoryManager>() != null) return;
            new GameObject("TerritoryManager").AddComponent<TerritoryManager>();
        }

        private void Awake() => Instance = this;

        private void Start()
        {
            grid          = HexGrid.Instance;
            colonies      = SpeciesColonies.Instance;
            playerManager = PlayerManager.Instance;
            if (grid == null) { Debug.LogWarning("[TerritoryManager] No HexGrid in scene."); return; }
            if (GameDataLoader.Species == null) GameDataLoader.Initialize();

            grid.Generated += RequestRebuild;
            if (colonies != null) colonies.ColoniesPlaced += RequestRebuild;
            if (playerManager != null) playerManager.PlayersChanged += RequestRebuild;
            RequestRebuild();
        }

        private void OnDestroy()
        {
            if (grid != null) grid.Generated -= RequestRebuild;
            if (colonies != null) colonies.ColoniesPlaced -= RequestRebuild;
            if (playerManager != null) playerManager.PlayersChanged -= RequestRebuild;
            TerritoryBorders.Clear();
            if (Instance == this) Instance = null;
        }

        // The map, the players' start hexes and the colonies are all set up by handlers of the same
        // events, in no fixed order, so the territory is rebuilt once they have all run.
        private void RequestRebuild() => rebuildPending = true;

        private void LateUpdate()
        {
            if (!rebuildPending) return;
            rebuildPending = false;
            Rebuild();
        }

        private void Rebuild()
        {
            centers.Clear();
            foreach (var l in labels) if (l != null) Destroy(l);
            labels.Clear();
            if (grid == null || !grid.IsGenerated || playerManager == null) { ApplyOwners(new()); return; }

            if (grid.WorldSeed != lastWorldSeed) // a new map: forget where colonies used to be
            {
                lastWorldSeed = grid.WorldSeed;
                lastColonyCell.Clear();
                lastColonySpecies.Clear();
            }

            var taken = new HashSet<string>();
            foreach (var player in playerManager.Players)
            {
                var start = player.StartCell;
                if (start == null) continue;
                var core = new List<HexCell> { start };
                core.AddRange(grid.GetNeighbors(start));

                string name = HabitatNames.Pick(player.Faction?.id, core, taken, $"{player.Name} Range");
                taken.Add(name);
                centers.Add(new HabitatCenter(player, start, core, name));
                labels.Add(CreateLabel(start, name, player.Primary));
                EnsureColony(player, core);
            }
            RecomputeTerritory();
        }

        // ---------- Colonies ----------

        private void EnsureColony(Player player, List<HexCell> core)
        {
            if (playerColonies.TryGetValue(player.Index, out var existing) && existing != null)
            {
                existing.Owner = player; // the Player object is replaced when a game is set up again
                return;
            }
            if (colonies == null || GameDataLoader.Species == null) return;

            // Once founded, a player's copies (more after reproducing, other species after evolving)
            // are kept by EvolutionManager, which puts them back after the map's groups are rebuilt
            var evolution = EvolutionManager.Instance;
            if (evolution != null && evolution.HasCopies(player))
            {
                foreach (var g in evolution.Respawn(player, core)) g.Arrived += OnColonyArrived;
                var any = colonies.Groups.FirstOrDefault(g => g != null && g.Owner?.Index == player.Index);
                if (any != null) playerColonies[player.Index] = any;
                return;
            }

            // Back where it was if that tile is still there, otherwise on the core around the center
            // (the center itself holds the player's banner or ball).
            var cells = new List<HexCell>();
            if (lastColonyCell.TryGetValue(player.Index, out var last) && last != null) cells.Add(last);
            cells.AddRange(core.Skip(1));
            cells.Add(core[0]);

            var otherSpecies = new HashSet<string>(playerColonies
                .Where(kv => kv.Key != player.Index && kv.Value != null)
                .Select(kv => kv.Value.Definition.id));
            lastColonySpecies.TryGetValue(player.Index, out var previous);
            var alive = GameDataLoader.Species.Where(d => SpeciesColonies.CanTravel(d) && colonies.IsAliveNow(d)).ToList();
            var rng = new System.Random(grid.WorldSeed ^ ((player.Index + 1) * 7919) ^ ((int)grid.DisplayedAge * 31));

            foreach (var cell in cells)
            {
                if (cell == null || colonies.GroupAt(cell) != null) continue;
                var fits = alive.Where(d => SpeciesColonies.FitsHabitat(d, cell) && FoodWeb.HasFood(d, cell, colonies, null)).ToList();
                if (fits.Count == 0) continue;

                // Keep the same species if it still fits; else prefer playable species no other
                // player has and that can evolve further, picking at random among the best.
                var def = fits.FirstOrDefault(d => d.id == previous);
                if (def == null)
                {
                    int Rank(SpeciesDefinition d) => (otherSpecies.Contains(d.id) ? 4 : 0) + (d.playable ? 0 : 2) +
                                                     (EvolutionData.From(d.id).Any() ? 0 : 1);
                    int best = fits.Min(Rank);
                    var top = fits.Where(d => Rank(d) == best).ToList();
                    def = top[rng.Next(top.Count)];
                }

                var group = colonies.SpawnColony(def, cell, player, rng.Next());
                if (group == null) continue;
                playerColonies[player.Index]    = group;
                lastColonyCell[player.Index]    = cell;
                lastColonySpecies[player.Index] = def.id;
                group.Arrived += OnColonyArrived;
                evolution?.RegisterFounder(player, group);
                return;
            }
            Debug.Log($"[TerritoryManager] No species fits the habitat center of {player.Name}; it starts without a colony.");
        }

        private void OnColonyArrived(ColonyGroup group)
        {
            if (group == null || group.Owner == null) return;
            lastColonyCell[group.Owner.Index] = group.Cell;
            RecomputeTerritory();
        }

        // ---------- Territory ----------

        // Re-claims territory after colonies appeared or changed outside a move (reproducing, evolving)
        public void Refresh() => RecomputeTerritory();

        private void RecomputeTerritory()
        {
            // What each player would hold on their own: their core, then the neighbours of every
            // colony of theirs standing on what they hold, repeated so a chain of colonies reaches out.
            var wanted = new Dictionary<Player, HashSet<HexCell>>();
            foreach (var center in centers)
            {
                var set = new HashSet<HexCell>(center.Core.Where(c => c != null));
                var groups = colonies != null
                    ? colonies.Groups.Where(g => g != null && g.Owner != null && g.Owner.Index == center.Owner.Index).ToList()
                    : new List<ColonyGroup>();
                var claimed = new HashSet<ColonyGroup>();
                bool grew = true;
                while (grew)
                {
                    grew = false;
                    foreach (var g in groups)
                    {
                        if (claimed.Contains(g) || g.Cell == null || !set.Contains(g.Cell)) continue;
                        claimed.Add(g);
                        set.UnionWith(grid.GetNeighbors(g.Cell));
                        grew = true;
                    }
                }
                wanted[center.Owner] = set;
            }

            var result = new Dictionary<HexCell, Player>();
            foreach (var center in centers)                       // 1. cores
                foreach (var c in center.Core)
                    if (c != null && !result.ContainsKey(c)) result[c] = center.Owner;
            foreach (var (player, set) in wanted)                 // 2. hexes the player already held
                foreach (var c in set)
                    if (!result.ContainsKey(c) && owners.TryGetValue(c, out var prev) && prev?.Index == player.Index)
                        result[c] = player;
            foreach (var (player, set) in wanted)                 // 3. the rest, in player order
                foreach (var c in set)
                    if (!result.ContainsKey(c)) result[c] = player;

            ApplyOwners(result);
        }

        private void ApplyOwners(Dictionary<HexCell, Player> result)
        {
            owners = result;
            if (grid != null) TerritoryBorders.Rebuild(owners, grid);
            TerritoryChanged?.Invoke();
        }

        // Center name, lying on the near (south) side of the center hex so it doesn't cover the
        // banner or the player's unit. A child of the cell, so it follows the east–west wrap.
        private static GameObject CreateLabel(HexCell cell, string text, Color color)
        {
            var label = PlayerMarker.CreateLabel(cell.transform, text, color, cell.SurfaceHeight + 0.08f);
            label.gameObject.name = "HabitatName";
            label.transform.localPosition += new Vector3(0f, 0f, -0.42f);
            label.characterSize = 0.02f;
            label.fontStyle     = FontStyle.Italic;
            label.color         = Color.white;
            return label.gameObject;
        }
    }
}
