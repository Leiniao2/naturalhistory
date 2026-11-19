using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Players;
using NaturalHistory.Progression;
using NaturalHistory.Territory;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Evolution
{
    // The Function (morphology) and Behavior (ethology) items one species has acquired.
    public class SpeciesTraits
    {
        public readonly HashSet<string> functions = new();
        public readonly HashSet<string> behaviors = new();
    }

    // One of a player's animal groups on the map (a "copy" of its species).
    public class OwnedCopy
    {
        public int player;              // Player.Index
        public string species;          // species.json id
        public ColonyGroup group;       // null (or destroyed) while the map's groups are being re-placed
        public HexCell cell;            // where it was last
        public int lastBred = -999;     // turn it last reproduced
        public int bornTurn = -1;       // turn it was born or evolved: no actions until the next (ColonyGroup.JustBorn)
        public CombatState combat;      // its group's HP and the turn's actions left while the group is re-spawned or saved (ColonyGroup.Stats)
        public bool JustBorn => group != null ? group.JustBorn : bornTurn >= 0 && bornTurn == (TurnManager.Instance != null ? TurnManager.Instance.CurrentTurn : 0);
    }

    // One line of the evolution requirements shown in the Evolution Tree panel
    public struct Requirement
    {
        public string text;
        public bool met;
        public Requirement(string text, bool met) { this.text = text; this.met = met; }
    }

    // Players' copies and what each species has evolved.
    //
    //  - Every species has its own Function and Behavior trees (SpeciesTraits); the trees on screen
    //    show the focused species (ProgressionManager.BindSpecies). Evolution Points are shared.
    //  - A copy evolves along a link in evolution.json once its species has acquired every item the
    //    link requires (items of the ORIGIN species' trees), the target's period has begun and the
    //    copy stands on or next to a tile the target can live on. Only that copy changes, for good;
    //    the new species inherits all the origin's items plus the link's granted ones, and what it
    //    acquires later doesn't flow back to the origin.
    //  - Once a player has evolved some copy from A into B, their other A copies can't become B (they
    //    can still evolve into other species). This is each player's own: what one player has evolved
    //    never stops another from evolving the same species, so no one can cut the others off from a
    //    branch of the tree by taking its key species first.
    //  - A copy can reproduce onto a free neighbouring tile once every ReproduceCooldown turns; that
    //    takes one of its actions for the turn (ColonyGroup.Stats) and, for the human player,
    //    ReproduceCost EP.
    //  - The young, and a copy that has just evolved, can't act (move, attack, reproduce, evolve)
    //    until the next turn.
    //
    // TerritoryManager founds each player's first copy and asks this to re-place the copies whenever
    // SpeciesColonies rebuilds the map's groups (another period is shown).
    public class EvolutionManager : MonoBehaviour
    {
        public const int ReproduceCooldown = 3; // turns
        public const int ReproduceCost     = 1; // EP, the human player's copies

        public static EvolutionManager Instance { get; private set; }

        // Copies, items or focus changed
        public event Action Changed;

        public string FocusSpecies { get; private set; } // whose trees the Functions / Behaviors panels show
        public IReadOnlyList<OwnedCopy> Copies => copies;

        private readonly Dictionary<string, SpeciesTraits> traits = new(); // the human player's species
        private readonly List<OwnedCopy> copies = new();                    // every player's
        private readonly Dictionary<int, HashSet<string>> evolved = new();  // link keys each player (index) has used
        private int mapSeed;
        private SpeciesTraits legacyTraits; // tree items from a save made before species had their own trees

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<EvolutionManager>() != null) return;
            new GameObject("EvolutionManager").AddComponent<EvolutionManager>();
        }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            if (GameDataLoader.Species == null) GameDataLoader.Initialize();
            if (HexGrid.Instance != null) HexGrid.Instance.Generated += OnMapGenerated;
            if (PlayerManager.Instance != null) PlayerManager.Instance.PlayersChanged += ResetGame;
        }

        private void OnDestroy()
        {
            if (HexGrid.Instance != null) HexGrid.Instance.Generated -= OnMapGenerated;
            if (PlayerManager.Instance != null) PlayerManager.Instance.PlayersChanged -= ResetGame;
            if (Instance == this) Instance = null;
        }

        // A different map is a different game (loading a save restores everything right after)
        private void OnMapGenerated()
        {
            if (HexGrid.Instance.WorldSeed == mapSeed) return;
            mapSeed = HexGrid.Instance.WorldSeed;
            ResetGame();
        }

        private void ResetGame()
        {
            traits.Clear();
            aiTraits.Clear();
            copies.Clear();
            evolved.Clear();
            legacyTraits = null;
            FocusSpecies = null;
            ProgressionManager.Instance?.BindSpecies(null, new HashSet<string>(), new HashSet<string>());
            Changed?.Invoke();
        }

        private static Player Human => PlayerManager.Instance != null ? PlayerManager.Instance.Human : null;
        private static int CurrentTurn => TurnManager.Instance != null ? TurnManager.Instance.CurrentTurn : 0;

        // Evolving costs the human player EP (the trees' points, ProgressionManager), so EP set the pace of
        // evolution: a game starts with 20 and earns 5 a turn from turn 2, so 36 EP first come together
        // on turn 5 (sooner with bonus EP, later if some go on Functions and Behaviors).
        public const int EvolveCost = 36; // EP in the Ediacaran; EvolveCostNow grows with the periods (EpCosts)
        public static int EvolveCostNow => EpCosts.Of(EvolveCost);
        // Only the human player has EP; other players' copies evolve without paying
        private static bool PaysEP(OwnedCopy copy) => copy == null || (Human != null && copy.player == Human.Index);

        // The EP a copy's player has: the human's (ProgressionManager), an AI player's (AiPlayers)
        private static bool IsAi(OwnedCopy copy) => copy != null && !PaysEP(copy) && AiPlayers.Instance != null;
        private static int PointsFor(OwnedCopy copy) =>
            IsAi(copy) ? AiPlayers.Instance.Points(copy.player) : ProgressionManager.Instance != null ? ProgressionManager.Instance.EvolutionPoints : 0;
        private static void Spend(OwnedCopy copy, int amount)
        {
            if (IsAi(copy)) AiPlayers.Instance.Spend(copy.player, amount);
            else if (PaysEP(copy)) ProgressionManager.Instance?.SpendPoints(amount);
        }

        // ---------- Species items ----------

        // AI players' items, per player and species: each player evolves its own copy of a species
        // (all of them start with the same three), so what an AI acquires isn't the human's
        private readonly Dictionary<(int player, string species), SpeciesTraits> aiTraits = new();

        // A player's items of a species: the human's (player < 0 or the human) are TraitsOf's
        public SpeciesTraits TraitsOf(int player, string speciesId)
        {
            if (player < 0 || Human == null || player == Human.Index) return TraitsOf(speciesId);
            if (string.IsNullOrEmpty(speciesId)) return null;
            if (aiTraits.TryGetValue((player, speciesId), out var t)) return t;
            t = NewTraits(speciesId);
            aiTraits[(player, speciesId)] = t;
            return t;
        }

        private SpeciesTraits TraitsFor(OwnedCopy copy, string speciesId) => TraitsOf(copy?.player ?? -1, speciesId);

        // The species' acquired items, starting with the free root items it can have.
        public SpeciesTraits TraitsOf(string speciesId)
        {
            if (string.IsNullOrEmpty(speciesId)) return null;
            if (traits.TryGetValue(speciesId, out var t)) return t;
            t = NewTraits(speciesId);
            traits[speciesId] = t;
            return t;
        }

        private static SpeciesTraits NewTraits(string speciesId)
        {
            var t = new SpeciesTraits();
            var def = GameDataLoader.GetSpecies(speciesId);
            var progression = ProgressionManager.Instance;
            if (progression != null)
            {
                foreach (var n in progression.Morphology.StartingNodes)
                    if (EvolutionData.CanAcquire(def, n, true)) t.functions.Add(n.id);
                foreach (var n in progression.Ethology.StartingNodes)
                    if (EvolutionData.CanAcquire(def, n, false)) t.behaviors.Add(n.id);
            }
            return t;
        }

        // Show this species in the Functions / Behaviors trees
        public void Focus(string speciesId)
        {
            if (string.IsNullOrEmpty(speciesId) || speciesId == FocusSpecies) return;
            var def = GameDataLoader.GetSpecies(speciesId);
            if (def == null) return;
            FocusSpecies = speciesId;
            var t = TraitsOf(speciesId);
            ProgressionManager.Instance?.BindSpecies(def, t.functions, t.behaviors);
            Changed?.Invoke();
        }

        // ---------- Copies ----------

        public IEnumerable<OwnedCopy> CopiesOf(Player player) => player == null ? Enumerable.Empty<OwnedCopy>() : copies.Where(c => c.player == player.Index);
        public bool HasCopies(Player player) => player != null && copies.Any(c => c.player == player.Index);
        public OwnedCopy CopyOf(ColonyGroup group) => group == null ? null : copies.FirstOrDefault(c => c.group == group);
        public bool HumanOwns(string speciesId) => CopiesOf(Human).Any(c => c.species == speciesId);
        public IEnumerable<string> HumanSpecies => CopiesOf(Human).Select(c => c.species).Distinct();

        // A copy wiped out in combat (World/Combat): it's gone for good; what its species evolved stays
        public void RemoveCopy(ColonyGroup group)
        {
            if (group == null || copies.RemoveAll(c => c.group == group) == 0) return;
            if (FocusSpecies != null && !CopiesOf(Human).Any(c => c.species == FocusSpecies))
            {
                FocusSpecies = null; // the trees move on to another species of yours, if any
                var next = HumanSpecies.FirstOrDefault();
                if (next != null) Focus(next);
            }
            Changed?.Invoke();
        }

        // A player's first copy, founded by TerritoryManager
        public void RegisterFounder(Player player, ColonyGroup group)
        {
            if (player == null || group == null || group.Definition == null) return;
            var copy = new OwnedCopy { player = player.Index, species = group.Definition.id, group = group, cell = group.Cell };
            copies.Add(copy);
            Track(copy);
            if (player.IsHuman && legacyTraits != null)
            {
                var t = TraitsOf(copy.species);
                t.functions.UnionWith(legacyTraits.functions);
                t.behaviors.UnionWith(legacyTraits.behaviors);
                legacyTraits = null;
            }
            if (player.IsHuman && FocusSpecies == null) Focus(copy.species);
            Changed?.Invoke();
        }

        // Puts back every copy of the player whose group is gone (the map's groups were rebuilt, as
        // when another period begins): a new period keeps the players' animals and territory, only
        // the land and the wild animals change. Each copy goes back on its last tile if that is free
        // and fits, else the nearest such tile (the coast may have moved), else one of `fallback`.
        // A player's species lives on even past the period it died out in. Returns the groups spawned.
        public List<ColonyGroup> Respawn(Player player, IReadOnlyList<HexCell> fallback)
        {
            var spawned = new List<ColonyGroup>();
            var colonies = SpeciesColonies.Instance;
            if (player == null || colonies == null) return spawned;
            int i = 0;
            foreach (var copy in copies.Where(c => c.player == player.Index).ToList())
            {
                i++;
                // a group the map has just cleared away is only destroyed at the end of the frame
                if (copy.group != null && colonies.Groups.Contains(copy.group)) { copy.group.Owner = player; continue; }
                copy.group = null;
                var def = GameDataLoader.GetSpecies(copy.species);
                if (def == null) continue;
                // Not yet evolved in the period the map shows (the admin bar jumped back in time): keep
                // the copy, but only put it back on the map once its period comes round again
                if (!HasAppeared(def)) continue;
                var cell = FreeCellNear(def, copy.cell, RespawnReach) ?? fallback?.FirstOrDefault(c => IsFree(def, c));
                if (cell == null) { Debug.Log($"[Evolution] No room to put back {player.Name}'s {def.commonName}."); continue; }
                var group = colonies.SpawnColony(def, cell, player, Seed(player.Index, i));
                if (group == null) continue;
                copy.group = group;
                copy.cell  = cell;
                group.BornTurn = copy.bornTurn;
                group.RestoreCombat(copy.combat); // the same HP and actions left as before the map was rebuilt
                Track(copy);
                spawned.Add(group);
            }
            if (spawned.Count > 0) Changed?.Invoke();
            return spawned;
        }

        private void Track(OwnedCopy copy)
        {
            if (copy.group == null) return;
            copy.group.Arrived += g =>
            {
                if (copy.group == g) copy.cell = g.Cell;
            };
        }

        private int Seed(int player, int index) => (HexGrid.Instance != null ? HexGrid.Instance.WorldSeed : 0) ^ (player * 7919) ^ (index * 104729);

        private static bool IsFree(SpeciesDefinition def, HexCell cell) =>
            cell != null && SpeciesColonies.FitsHabitat(def, cell) && SpeciesColonies.Instance.GroupAt(cell, Niches.Of(def, cell)) == null; // its niche there is free

        // Nearest free habitat tile within `radius` steps of `from` (including `from`)
        private const int RespawnReach = 8; // tiles: how far a copy may be moved if its tile no longer suits it

        private static bool HasAppeared(SpeciesDefinition def) =>
            HexGrid.Instance == null || !Enum.TryParse(def.firstAge, true, out GeologicalAge first) || HexGrid.Instance.DisplayedAge >= first;

        private static HexCell FreeCellNear(SpeciesDefinition def, HexCell from, int radius)
        {
            var grid = HexGrid.Instance;
            if (from == null || grid == null) return null;
            for (int r = 0; r <= radius; r++)
                foreach (var c in grid.GetCellsInRange(from, r))
                    if (c.Coordinates.DistanceTo(from.Coordinates) == r && IsFree(def, c)) return c;
            return null;
        }

        // ---------- Reproduce ----------

        public int TurnsUntilReproduce(OwnedCopy copy) =>
            copy == null ? 0 : Mathf.Max(copy.JustBorn ? 1 : 0, copy.lastBred + Abilities.ReproduceCooldown(copy.group, ReproduceCooldown) - CurrentTurn);

        // The free neighbouring tiles the species can live on, the player's own territory first
        public List<HexCell> ReproduceCells(OwnedCopy copy)
        {
            if (copy?.group == null || copy.group.Cell == null) return new List<HexCell>();
            var def = GameDataLoader.GetSpecies(copy.species);
            var territory = TerritoryManager.Instance;
            return HexGrid.Instance.GetNeighbors(copy.group.Cell)
                .Where(c => IsFree(def, c))
                .OrderByDescending(c => territory != null && territory.OwnerOf(c)?.Index == copy.player)
                .ToList();
        }

        public HexCell ReproduceCell(OwnedCopy copy) => ReproduceCells(copy).FirstOrDefault();

        public bool CanAffordReproduce(OwnedCopy copy) =>
            !(PaysEP(copy) || IsAi(copy)) || PointsFor(copy) >= ReproduceCost;

        // at: the tile the player chose for the young (one of ReproduceCells), or null for the first
        public bool Reproduce(OwnedCopy copy, out string message, HexCell at = null)
        {
            message = null;
            if (copy?.group == null) { message = Loc.T("Nothing selected"); return false; }
            int wait = TurnsUntilReproduce(copy);
            if (wait > 0) { message = Loc.F(wait == 1 ? "Can reproduce again in {0} turn" : "Can reproduce again in {0} turns", wait); return false; }
            if (!copy.group.HasActions()) { message = Loc.T("No actions left this turn"); return false; }
            if (!CanAffordReproduce(copy))
            {
                message = Loc.F("Needs {0} EP (you have {1})", ReproduceCost, PointsFor(copy));
                return false;
            }
            var def  = GameDataLoader.GetSpecies(copy.species);
            var cell = at != null && ReproduceCells(copy).Contains(at) ? at : ReproduceCell(copy);
            if (cell == null) { message = Loc.F("No free {0} next to it", HabitatText(def)); return false; }

            var owner = copy.group.Owner;
            var group = SpeciesColonies.Instance.SpawnColony(def, cell, owner, Seed(copy.player, copies.Count + 1) ^ CurrentTurn);
            if (group == null) { message = Loc.T("Couldn't place the young"); return false; }
            copy.lastBred = CurrentTurn;
            copy.group.SpendActions(1);
            Spend(copy, ReproduceCost);
            group.BornTurn = CurrentTurn;
            var young = new OwnedCopy { player = copy.player, species = copy.species, group = group, cell = cell, lastBred = CurrentTurn, bornTurn = CurrentTurn };
            copies.Add(young);
            Track(young);
            TerritoryManager.Instance?.Refresh();
            message = Loc.F("{0} reproduced", Loc.T(def.commonName));
            Changed?.Invoke();
            return true;
        }

        // ---------- Evolve ----------

        public bool HasEvolved(EvolutionLink link) => HasEvolved(link, Human != null ? Human.Index : 0);
        public bool HasEvolved(EvolutionLink link, int player) =>
            link != null && evolved.TryGetValue(player, out var keys) && keys.Contains(link.Key);

        private HashSet<string> EvolvedBy(int player)
        {
            if (!evolved.TryGetValue(player, out var keys)) evolved[player] = keys = new HashSet<string>();
            return keys;
        }

        // Everything `link` needs, ticked off for `copy` (null: judged for the human's copies in general).
        public List<Requirement> Requirements(EvolutionLink link, OwnedCopy copy)
        {
            var list = new List<Requirement>();
            var origin = GameDataLoader.GetSpecies(link.from);
            var target = GameDataLoader.GetSpecies(link.to);
            var progression = ProgressionManager.Instance;
            if (origin == null || target == null || progression == null) return list;
            var t = TraitsFor(copy, link.from);
            var originCopies = copy != null ? new List<OwnedCopy> { copy } : CopiesOf(Human).Where(c => c.species == link.from).ToList();

            list.Add(new Requirement(Loc.F(copy != null ? "A {0}" : "You have a {0}", Loc.T(origin.commonName)), originCopies.Count > 0 && (copy == null || copy.species == link.from)));
            foreach (var id in link.functions)
                list.Add(new Requirement(Loc.F("Function: {0}", Loc.T(progression.Morphology.Get(id)?.displayName ?? id)), t.functions.Contains(id)));
            foreach (var id in link.behaviors)
                list.Add(new Requirement(Loc.F("Behavior: {0}", Loc.T(progression.Ethology.Get(id)?.displayName ?? id)), t.behaviors.Contains(id)));

            bool periodMet = !Enum.TryParse(target.firstAge, true, out GeologicalAge first) || AgeManager.Instance == null || AgeManager.Instance.CurrentAge >= first;
            list.Add(new Requirement(Loc.F("The {0} has begun", Loc.T(target.firstAge)), periodMet));
            list.Add(new Requirement(Loc.F("On or next to {0}", HabitatText(target)), originCopies.Any(c => EvolveCell(c, target) != null)));
            if (PaysEP(copy) || IsAi(copy))
            {
                int ep = PointsFor(copy);
                list.Add(new Requirement(Loc.F("Needs {0} EP (you have {1})", EvolveCostNow, ep), ep >= EvolveCostNow));
            }
            if (copy != null && copy.JustBorn)
                list.Add(new Requirement(Loc.T("New this turn: it can act from the next turn"), false));
            if (copy != null ? HasEvolved(link, copy.player) : HasEvolved(link))
                list.Add(new Requirement(Loc.F("A {0} has already become a {1}; evolve another copy into a different species", Loc.T(origin.commonName), Loc.T(target.commonName)), false));
            return list;
        }

        public bool CanEvolve(EvolutionLink link, OwnedCopy copy) =>
            copy != null && copy.group != null && Requirements(link, copy).All(r => r.met);

        // The copy's tile if the target can live there, else a free neighbour it can live on
        public HexCell EvolveCell(OwnedCopy copy, SpeciesDefinition target)
        {
            var cell = copy?.group != null ? copy.group.Cell : null;
            if (cell == null || target == null) return null;
            if (SpeciesColonies.FitsHabitat(target, cell)) return cell;
            return HexGrid.Instance.GetNeighbors(cell).FirstOrDefault(c => IsFree(target, c));
        }

        public bool Evolve(EvolutionLink link, OwnedCopy copy, out string message)
        {
            message = null;
            if (!CanEvolve(link, copy)) { message = Loc.T("Not ready to evolve yet"); return false; }
            var origin = GameDataLoader.GetSpecies(link.from);
            var target = GameDataLoader.GetSpecies(link.to);
            var cell   = EvolveCell(copy, target);
            var owner  = copy.group.Owner;

            SpeciesColonies.Instance.DespawnColony(copy.group);
            var group = SpeciesColonies.Instance.SpawnColony(target, cell, owner, Seed(copy.player, copies.IndexOf(copy)) ^ CurrentTurn);
            if (group == null)
            {
                // Shouldn't happen (targets have models), but don't lose the copy
                copy.group = SpeciesColonies.Instance.SpawnColony(origin, copy.cell, owner, Seed(copy.player, 1));
                Track(copy);
                message = Loc.F("Couldn't place a {0}", Loc.T(target.commonName));
                return false;
            }

            // The new species inherits everything the origin had, plus what evolving grants
            var from = TraitsFor(copy, link.from);
            var to   = TraitsFor(copy, link.to);
            to.functions.UnionWith(from.functions);
            to.behaviors.UnionWith(from.behaviors);
            to.functions.UnionWith(link.grantFunctions);
            to.behaviors.UnionWith(link.grantBehaviors);

            Spend(copy, EvolveCostNow);
            EvolvedBy(copy.player).Add(link.Key);
            copy.species  = link.to;
            copy.group    = group;
            copy.cell     = cell;
            copy.bornTurn = group.BornTurn = CurrentTurn;
            Track(copy);
            FocusSpecies = null; // force a rebind: the target's set may have just been created
            Focus(link.to);
            TerritoryManager.Instance?.Refresh();
            Debug.Log($"[Evolution] {owner?.Name}: a {origin.commonName} evolved into a {target.commonName}");
            message = Loc.F("Your {0} evolved into a {1}", Loc.T(origin.commonName), Loc.T(target.commonName));
            Changed?.Invoke();
            return true;
        }

        private static string HabitatText(SpeciesDefinition def)
        {
            if (def?.habitats == null || def.habitats.Count == 0) return Loc.T("a suitable tile");
            // German capitalises nouns; the other languages read better in lower case mid-sentence
            string Lower(string text) => Loc.Current == "de" ? text : text.ToLowerInvariant();
            var names = def.habitats.Select(h => Lower(Loc.T(Enum.TryParse(h, out TerrainKind k) ? EraFlora.DisplayName(k) : h))).ToList();
            return names.Count == 1 ? names[0] : Loc.F("{0} or {1}", string.Join(", ", names.Take(names.Count - 1)), names[^1]);
        }

        // ---------- Save / load ----------

        public void Capture(Save.SaveData data)
        {
            data.focusSpecies = FocusSpecies;
            data.speciesTraits = traits.Select(kv => new SpeciesTraitsSave
            {
                species = kv.Key, functions = kv.Value.functions.ToList(), behaviors = kv.Value.behaviors.ToList(),
            }).Concat(aiTraits.Select(kv => new SpeciesTraitsSave
            {
                player = kv.Key.player, species = kv.Key.species, functions = kv.Value.functions.ToList(), behaviors = kv.Value.behaviors.ToList(),
            })).ToList();
            data.copies = copies.Select(c =>
            {
                var cell = c.group != null && c.group.Cell != null ? c.group.Cell : c.cell;
                var (col, row) = cell != null ? cell.Coordinates.ToOffsetCoordinates() : (-1, -1);
                var combat = c.group != null ? c.group.CombatNow : c.combat;
                return new CopySave { player = c.player, species = c.species, col = col, row = row, lastBred = c.lastBred, bornTurn = c.group != null ? c.group.BornTurn : c.bornTurn,
                                      hp = combat?.hp ?? -1f, actionsLeft = combat?.actionsLeft ?? -1, attacksLeft = combat?.attacksLeft ?? -1, combatTurn = combat?.turn ?? -1 };
            }).ToList();
            // "player:from>to"
            data.evolved = evolved.SelectMany(kv => kv.Value.Select(key => $"{kv.Key}:{key}")).ToList();
        }

        // Called after the map has been regenerated; the copies are put back when TerritoryManager
        // next rebuilds (end of this frame). Saves from before evolution existed have no copies: the
        // first copy is founded as in a new game and its species gets the saved tree items.
        // Behaviors that are now Functions (body-based items live only in the Functions tree): the
        // same id moved, or folded into the Function that covers it. Applied to older saves.
        private static readonly Dictionary<string, string> BehaviorsNowFunctions = new()
        {
            { "echolocation_hunting", "echolocating_ears" }, { "venom_hunting", "venom_glands" },
            { "seasonal_dormancy", "hibernation_node" }, { "nursing", "mammary_glands" },
            { "ink_cloud", "ink_cloud" }, { "chemical_spray", "chemical_spray" }, { "tail_weapons", "tail_weapons" },
            { "countershading", "countershading" }, { "warning_colours", "warning_colours" }, { "mimicry", "mimicry" },
            { "gliding", "gliding" }, { "hermaphroditism", "hermaphroditism" }, { "diapause", "diapause" },
            { "colonial_living", "colonial_living" },
        };

        private static void MigrateItems(SpeciesTraits t)
        {
            foreach (var b in t.behaviors.Where(BehaviorsNowFunctions.ContainsKey).ToList())
            {
                t.behaviors.Remove(b);
                t.functions.Add(BehaviorsNowFunctions[b]);
            }
        }

        public void Restore(Save.SaveData data)
        {
            traits.Clear();
            aiTraits.Clear();
            copies.Clear();
            evolved.Clear();
            FocusSpecies = null;
            mapSeed = HexGrid.Instance != null ? HexGrid.Instance.WorldSeed : 0;
            foreach (var s in data.speciesTraits ?? new List<SpeciesTraitsSave>())
            {
                var t = new SpeciesTraits();
                t.functions.UnionWith(s.functions ?? new List<string>());
                t.behaviors.UnionWith(s.behaviors ?? new List<string>());
                MigrateItems(t);
                if (s.player >= 0) aiTraits[(s.player, s.species)] = t;
                else traits[s.species] = t;
            }
            foreach (var c in data.copies ?? new List<CopySave>())
                copies.Add(new OwnedCopy { player = c.player, species = c.species, cell = HexGrid.Instance?.GetCell(c.col, c.row), lastBred = c.lastBred, bornTurn = c.bornTurn,
                                           combat = c.hp >= 0f ? new CombatState { hp = c.hp, actionsLeft = c.actionsLeft, attacksLeft = c.attacksLeft, turn = c.combatTurn } : null });
            // saves from before players had their own: the human's
            foreach (var e in data.evolved ?? new List<string>())
            {
                int colon = e.IndexOf(':');
                if (colon > 0 && int.TryParse(e.Substring(0, colon), out int player)) EvolvedBy(player).Add(e.Substring(colon + 1));
                else EvolvedBy(Human != null ? Human.Index : 0).Add(e);
            }
            legacyTraits = null;
            if (copies.Count == 0 && traits.Count == 0) // older save: its items go to the first species founded
            {
                legacyTraits = new SpeciesTraits();
                legacyTraits.functions.UnionWith(data.morphology ?? new List<string>());
                legacyTraits.behaviors.UnionWith(data.ethology ?? new List<string>());
            }

            // Remove the groups left over from before loading; TerritoryManager puts the copies back
            if (copies.Count > 0 && SpeciesColonies.Instance != null)
                foreach (var g in SpeciesColonies.Instance.Groups.Where(g => g != null && g.Owner != null).ToList())
                    SpeciesColonies.Instance.DespawnColony(g);

            var focus = data.focusSpecies;
            if (string.IsNullOrEmpty(focus)) focus = copies.FirstOrDefault(c => c.player == Human?.Index)?.species;
            if (!string.IsNullOrEmpty(focus)) Focus(focus);
            Changed?.Invoke();
        }
    }

    [Serializable]
    public class SpeciesTraitsSave
    {
        public int player = -1; // an AI player's (EvolutionManager.TraitsOf(player, …)); -1 the human's
        public string species;
        public List<string> functions = new();
        public List<string> behaviors = new();
    }

    [Serializable]
    public class CopySave
    {
        public int player;
        public string species;
        public int col = -1;
        public int row = -1;
        public int lastBred = -999;
        public int bornTurn = -1;
        public float hp = -1f;          // -1: full (saves from before combat)
        public int actionsLeft = -1;
        public int attacksLeft = -1;
        public int combatTurn = -1;     // the turn actionsLeft / attacksLeft are for
    }
}
