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
    //    can still evolve into other species).
    //  - A copy can reproduce onto a free neighbouring tile once every ReproduceCooldown turns.
    //
    // TerritoryManager founds each player's first copy and asks this to re-place the copies whenever
    // SpeciesColonies rebuilds the map's groups (another period is shown).
    public class EvolutionManager : MonoBehaviour
    {
        public const int ReproduceCooldown = 3; // turns

        public static EvolutionManager Instance { get; private set; }

        // Copies, items or focus changed
        public event Action Changed;

        public string FocusSpecies { get; private set; } // whose trees the Functions / Behaviors panels show
        public IReadOnlyList<OwnedCopy> Copies => copies;

        private readonly Dictionary<string, SpeciesTraits> traits = new(); // the human player's species
        private readonly List<OwnedCopy> copies = new();                    // every player's
        private readonly HashSet<string> evolved = new();                   // link keys the human has used
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
            copies.Clear();
            evolved.Clear();
            legacyTraits = null;
            FocusSpecies = null;
            ProgressionManager.Instance?.BindSpecies(null, new HashSet<string>(), new HashSet<string>());
            Changed?.Invoke();
        }

        private static Player Human => PlayerManager.Instance != null ? PlayerManager.Instance.Human : null;
        private static int CurrentTurn => TurnManager.Instance != null ? TurnManager.Instance.CurrentTurn : 0;

        // ---------- Species items ----------

        // The species' acquired items, starting with the free root items it can have.
        public SpeciesTraits TraitsOf(string speciesId)
        {
            if (string.IsNullOrEmpty(speciesId)) return null;
            if (traits.TryGetValue(speciesId, out var t)) return t;
            t = new SpeciesTraits();
            var def = GameDataLoader.GetSpecies(speciesId);
            var progression = ProgressionManager.Instance;
            if (progression != null)
            {
                foreach (var n in progression.Morphology.StartingNodes)
                    if (EvolutionData.CanAcquire(def, n, true)) t.functions.Add(n.id);
                foreach (var n in progression.Ethology.StartingNodes)
                    if (EvolutionData.CanAcquire(def, n, false)) t.behaviors.Add(n.id);
            }
            traits[speciesId] = t;
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

        // Puts back every copy of the player whose group is gone (the map's groups were rebuilt):
        // on its last tile if that is free and fits, else the nearest such tile, else one of
        // `fallback`. Returns the groups spawned.
        public List<ColonyGroup> Respawn(Player player, IReadOnlyList<HexCell> fallback)
        {
            var spawned = new List<ColonyGroup>();
            var colonies = SpeciesColonies.Instance;
            if (player == null || colonies == null) return spawned;
            int i = 0;
            foreach (var copy in copies.Where(c => c.player == player.Index).ToList())
            {
                i++;
                if (copy.group != null) { copy.group.Owner = player; continue; }
                var def = GameDataLoader.GetSpecies(copy.species);
                if (def == null) continue;
                // Not alive in the period the map shows (e.g. the admin bar jumped back in time):
                // keep the copy, but only put it back on the map once its period comes round again
                if (!colonies.IsAliveNow(def)) continue;
                var cell = FreeCellNear(def, copy.cell, 3) ?? fallback?.FirstOrDefault(c => IsFree(def, c));
                if (cell == null) { Debug.Log($"[Evolution] No room to put back {player.Name}'s {def.commonName}."); continue; }
                var group = colonies.SpawnColony(def, cell, player, Seed(player.Index, i));
                if (group == null) continue;
                copy.group = group;
                copy.cell  = cell;
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
            copy == null ? 0 : Mathf.Max(0, copy.lastBred + ReproduceCooldown - CurrentTurn);

        // A free neighbouring tile the species can live on, preferring the player's own territory
        public HexCell ReproduceCell(OwnedCopy copy)
        {
            if (copy?.group == null || copy.group.Cell == null) return null;
            var def = GameDataLoader.GetSpecies(copy.species);
            var territory = TerritoryManager.Instance;
            return HexGrid.Instance.GetNeighbors(copy.group.Cell)
                .Where(c => IsFree(def, c))
                .OrderByDescending(c => territory != null && territory.OwnerOf(c)?.Index == copy.player)
                .FirstOrDefault();
        }

        public bool Reproduce(OwnedCopy copy, out string message)
        {
            message = null;
            if (copy?.group == null) { message = Loc.T("Nothing selected"); return false; }
            int wait = TurnsUntilReproduce(copy);
            if (wait > 0) { message = Loc.F(wait == 1 ? "Can reproduce again in {0} turn" : "Can reproduce again in {0} turns", wait); return false; }
            var def  = GameDataLoader.GetSpecies(copy.species);
            var cell = ReproduceCell(copy);
            if (cell == null) { message = Loc.F("No free {0} next to it", HabitatText(def)); return false; }

            var owner = copy.group.Owner;
            var group = SpeciesColonies.Instance.SpawnColony(def, cell, owner, Seed(copy.player, copies.Count + 1) ^ CurrentTurn);
            if (group == null) { message = Loc.T("Couldn't place the young"); return false; }
            copy.lastBred = CurrentTurn;
            var young = new OwnedCopy { player = copy.player, species = copy.species, group = group, cell = cell, lastBred = CurrentTurn };
            copies.Add(young);
            Track(young);
            TerritoryManager.Instance?.Refresh();
            message = Loc.F("{0} reproduced", Loc.T(def.commonName));
            Changed?.Invoke();
            return true;
        }

        // ---------- Evolve ----------

        public bool HasEvolved(EvolutionLink link) => link != null && evolved.Contains(link.Key);

        // Everything `link` needs, ticked off for `copy` (null: judged for the human's copies in general).
        public List<Requirement> Requirements(EvolutionLink link, OwnedCopy copy)
        {
            var list = new List<Requirement>();
            var origin = GameDataLoader.GetSpecies(link.from);
            var target = GameDataLoader.GetSpecies(link.to);
            var progression = ProgressionManager.Instance;
            if (origin == null || target == null || progression == null) return list;
            var t = TraitsOf(link.from);
            var originCopies = copy != null ? new List<OwnedCopy> { copy } : CopiesOf(Human).Where(c => c.species == link.from).ToList();

            list.Add(new Requirement(Loc.F(copy != null ? "A {0}" : "You have a {0}", Loc.T(origin.commonName)), originCopies.Count > 0 && (copy == null || copy.species == link.from)));
            foreach (var id in link.functions)
                list.Add(new Requirement(Loc.F("Function: {0}", Loc.T(progression.Morphology.Get(id)?.displayName ?? id)), t.functions.Contains(id)));
            foreach (var id in link.behaviors)
                list.Add(new Requirement(Loc.F("Behavior: {0}", Loc.T(progression.Ethology.Get(id)?.displayName ?? id)), t.behaviors.Contains(id)));

            bool periodMet = !Enum.TryParse(target.firstAge, true, out GeologicalAge first) || AgeManager.Instance == null || AgeManager.Instance.CurrentAge >= first;
            list.Add(new Requirement(Loc.F("The {0} has begun", Loc.T(target.firstAge)), periodMet));
            list.Add(new Requirement(Loc.F("On or next to {0}", HabitatText(target)), originCopies.Any(c => EvolveCell(c, target) != null)));
            if (HasEvolved(link))
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
            var from = TraitsOf(link.from);
            var to   = TraitsOf(link.to);
            to.functions.UnionWith(from.functions);
            to.behaviors.UnionWith(from.behaviors);
            to.functions.UnionWith(link.grantFunctions);
            to.behaviors.UnionWith(link.grantBehaviors);

            evolved.Add(link.Key);
            copy.species = link.to;
            copy.group   = group;
            copy.cell    = cell;
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
            }).ToList();
            data.copies = copies.Select(c =>
            {
                var cell = c.group != null && c.group.Cell != null ? c.group.Cell : c.cell;
                var (col, row) = cell != null ? cell.Coordinates.ToOffsetCoordinates() : (-1, -1);
                return new CopySave { player = c.player, species = c.species, col = col, row = row, lastBred = c.lastBred };
            }).ToList();
            data.evolved = evolved.ToList();
        }

        // Called after the map has been regenerated; the copies are put back when TerritoryManager
        // next rebuilds (end of this frame). Saves from before evolution existed have no copies: the
        // first copy is founded as in a new game and its species gets the saved tree items.
        public void Restore(Save.SaveData data)
        {
            traits.Clear();
            copies.Clear();
            evolved.Clear();
            FocusSpecies = null;
            mapSeed = HexGrid.Instance != null ? HexGrid.Instance.WorldSeed : 0;
            foreach (var s in data.speciesTraits ?? new List<SpeciesTraitsSave>())
            {
                var t = new SpeciesTraits();
                t.functions.UnionWith(s.functions ?? new List<string>());
                t.behaviors.UnionWith(s.behaviors ?? new List<string>());
                traits[s.species] = t;
            }
            foreach (var c in data.copies ?? new List<CopySave>())
                copies.Add(new OwnedCopy { player = c.player, species = c.species, cell = HexGrid.Instance?.GetCell(c.col, c.row), lastBred = c.lastBred });
            evolved.UnionWith(data.evolved ?? new List<string>());
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
    }
}
