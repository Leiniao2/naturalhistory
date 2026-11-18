using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Territory;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Progression
{
    // Owns the Functions (morphology, tech) and Behaviors (ethology, civics) trees and the Evolution
    // Points spent on them. Each species has its own acquired items; the trees show those of the
    // species bound with BindSpecies (EvolutionManager binds the focused species). EP are shared.
    //
    // The human player's EP:
    //  - each turn, PointsPerCenter for every habitat center they have
    //  - KillReward for wiping out a foreign group (Combat), DiscoveryReward the first time a wild or
    //    other player's species comes into sight (FogOfWar; not in Safari Mode)
    //  - spent on the trees' items, on evolving (EvolutionManager.EvolveCost) and reproducing
    //    (EvolutionManager.ReproduceCost)
    public class ProgressionManager : MonoBehaviour
    {
        public static ProgressionManager Instance { get; private set; }

        [SerializeField] private int startingPoints = 20;
        [SerializeField] private int pointsPerCenter = 5; // per habitat center, each turn

        public const int KillReward      = 3;
        public const int DiscoveryReward = 2;

        public ProgressionTree Morphology { get; private set; } // "Functions" in the game
        public ProgressionTree Ethology   { get; private set; } // "Behaviors" in the game
        public SpeciesDefinition Species  { get; private set; } // whose items the trees show; null = none bound
        public int EvolutionPoints { get; private set; }
        public int StartingPoints => startingPoints;
        public int PointsPerCenter => pointsPerCenter;

        // EP the next turn brings: PointsPerCenter for each of the human player's habitat centers,
        // scaled by the difficulty (GameOptions.IncomeShare)
        public int Income
        {
            get
            {
                var territory = TerritoryManager.Instance;
                int centers = territory == null ? 1 : territory.Centers.Count(c => c.Owner != null && c.Owner.IsHuman);
                return Mathf.RoundToInt(pointsPerCenter * centers * GameOptions.IncomeShare); // fewer on harder difficulties
            }
        }

        // Species the human player has seen (a first sighting earns DiscoveryReward)
        private readonly HashSet<string> discovered = new();
        public IEnumerable<string> Discovered => discovered;
        private bool discoveryPending;

        // Raised whenever points or unlocks change, so UI can refresh
        public event Action Changed;
        // Points earned outside the turn's income, with what for (a toast)
        public event Action<string> Earned;
        public event Action<ProgressionTree, TreeNodeDefinition> NodeUnlocked;

        // Like PlayerBall: spawn in any scene with a map, so Game.unity doesn't need editing.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<ProgressionManager>() != null) return;
            new GameObject("ProgressionManager").AddComponent<ProgressionManager>();
        }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            Morphology = ProgressionTree.Load("Functions", "Data/morphology");
            Ethology   = ProgressionTree.Load("Behaviors", "Data/ethology");
            EvolutionPoints = startingPoints;
        }

        private void Start()
        {
            if (TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin += OnTurnBegin;
            FogOfWar.Changed += RequestDiscovery;
        }

        private void OnDestroy()
        {
            if (TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin -= OnTurnBegin;
            FogOfWar.Changed -= RequestDiscovery;
            if (Instance == this) Instance = null;
        }

        private void OnTurnBegin(int turn)
        {
            RequestDiscovery(); // groups have moved
            if (turn <= 1) return;
            EvolutionPoints += Income;
            Changed?.Invoke();
        }

        // ---------- Discovering species ----------

        // Checked once the frame's work is done: a save being loaded restores the discovered species
        // after the turn and the map, in the same frame
        private void RequestDiscovery() => discoveryPending = true;

        private void LateUpdate()
        {
            if (!discoveryPending) return;
            discoveryPending = false;
            CheckDiscoveries();
        }

        // Every wild or other player's species in sight that the human player hasn't seen before,
        // and doesn't have themselves
        private void CheckDiscoveries()
        {
            var colonies = SpeciesColonies.Instance;
            var human = Players.PlayerManager.Instance != null ? Players.PlayerManager.Instance.Human : null;
            if (colonies == null || human == null || !FogOfWar.Active || SpeciesColonies.SafariMode) return;
            var evolution = EvolutionManager.Instance;
            var found = new List<SpeciesDefinition>();
            foreach (var g in colonies.Groups)
            {
                if (g == null || g.Definition == null || g.Cell == null || g.Owner == human) continue;
                if (discovered.Contains(g.Definition.id) || !FogOfWar.IsVisible(g.Cell)) continue;
                if (evolution != null && evolution.HumanOwns(g.Definition.id)) continue;
                discovered.Add(g.Definition.id);
                found.Add(g.Definition);
            }
            if (found.Count == 0) return;
            int ep = found.Count * DiscoveryReward;
            EvolutionPoints += ep;
            Changed?.Invoke();
            Earned?.Invoke(found.Count == 1 ? Loc.F("Discovered the {0} (+{1} EP)", Loc.T(found[0].commonName), ep)
                                            : Loc.F("Discovered {0} new species (+{1} EP)", found.Count, ep));
        }

        // Show and edit `species`' items: functions / behaviors are its sets (used directly).
        public void BindSpecies(SpeciesDefinition species, HashSet<string> functions, HashSet<string> behaviors)
        {
            Species = species;
            Morphology.Bind(functions);
            Ethology.Bind(behaviors);
            Changed?.Invoke();
        }

        // Whether the bound species can ever acquire the item (body plan, see EvolutionData)
        public bool CanAcquire(ProgressionTree tree, TreeNodeDefinition node) =>
            EvolutionData.CanAcquire(Species, node, tree == Morphology);

        public NodeState GetState(ProgressionTree tree, TreeNodeDefinition node)
        {
            if (tree.IsUnlocked(node.id)) return NodeState.Unlocked;
            if (!CanAcquire(tree, node)) return NodeState.Unavailable;
            return tree.PrerequisitesMet(node) && AgeAllows(node) ? NodeState.Available : NodeState.Locked;
        }

        // Null when the node can be unlocked now, otherwise a player-facing reason.
        public string UnlockBlocker(ProgressionTree tree, TreeNodeDefinition node)
        {
            if (Species == null)           return Loc.T("None of your species is selected");
            if (tree.IsUnlocked(node.id))  return Loc.T("Already acquired");
            if (!CanAcquire(tree, node))   return Loc.F("Not in the {0}'s {1}", Loc.T(Species?.commonName ?? "species"), Loc.T(tree.DisplayName).ToLowerInvariant());
            if (!tree.PrerequisitesMet(node)) return Loc.F("Requires: {0}", string.Join(", ", MissingPrerequisites(tree, node)));
            if (!AgeAllows(node))          return Loc.F("Available from the {0}", Loc.T(node.age));
            if (EvolutionPoints < node.cost) return Loc.F("Needs {0} EP (you have {1})", node.cost, EvolutionPoints);
            return null;
        }

        public bool TryUnlock(ProgressionTree tree, TreeNodeDefinition node)
        {
            if (UnlockBlocker(tree, node) != null) return false;
            EvolutionPoints -= node.cost;
            tree.MarkUnlocked(node.id);
            Debug.Log($"[Progression] {Species?.commonName}: acquired {node.displayName} ({tree.DisplayName}, -{node.cost} EP)");
            NodeUnlocked?.Invoke(tree, node);
            Changed?.Invoke();
            return true;
        }

        // Points spent outside the trees (evolving a copy, EvolutionManager.EvolveCost)
        public void SpendPoints(int amount)
        {
            if (amount <= 0) return;
            EvolutionPoints = Mathf.Max(0, EvolutionPoints - amount);
            Changed?.Invoke();
        }

        // Bonus points from outside the trees (e.g. a faction's iconic animal activating)
        public void AddPoints(int amount)
        {
            if (amount == 0) return;
            EvolutionPoints += amount;
            Changed?.Invoke();
        }

        // discovered: the species seen so far (null: none, a new game or an older save)
        public void Restore(int points, IEnumerable<string> morphology, IEnumerable<string> ethology, IEnumerable<string> discovered = null)
        {
            EvolutionPoints = points;
            this.discovered.Clear();
            if (discovered != null) this.discovered.UnionWith(discovered);
            Morphology.Restore(morphology);
            Ethology.Restore(ethology);
            Changed?.Invoke();
        }

        private IEnumerable<string> MissingPrerequisites(ProgressionTree tree, TreeNodeDefinition node)
        {
            foreach (var id in node.prerequisites)
            {
                if (tree.IsUnlocked(id)) continue;
                var pre = tree.Get(id);
                if (pre == null) yield return id;
                else yield return pre.branch == node.branch ? Loc.T(pre.displayName) : $"{Loc.T(pre.displayName)} ({Loc.T(tree.BranchName(pre.branch))})";
            }
        }

        // Age gating only applies once an AgeManager is running the geological clock.
        private static bool AgeAllows(TreeNodeDefinition node)
        {
            if (AgeManager.Instance == null || string.IsNullOrEmpty(node.age)) return true;
            return !Enum.TryParse<GeologicalAge>(node.age, out var required) || required <= AgeManager.Instance.CurrentAge;
        }
    }
}
