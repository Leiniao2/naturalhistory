using System;
using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Progression
{
    // Owns the Functions (morphology, tech) and Behaviors (ethology, civics) trees and the Evolution
    // Points spent on them. Each species has its own acquired items; the trees show those of the
    // species bound with BindSpecies (EvolutionManager binds the focused species). EP are shared.
    public class ProgressionManager : MonoBehaviour
    {
        public static ProgressionManager Instance { get; private set; }

        [SerializeField] private int startingPoints = 20;
        [SerializeField] private int pointsPerTurn  = 5;

        public ProgressionTree Morphology { get; private set; } // "Functions" in the game
        public ProgressionTree Ethology   { get; private set; } // "Behaviors" in the game
        public SpeciesDefinition Species  { get; private set; } // whose items the trees show; null = none bound
        public int EvolutionPoints { get; private set; }
        public int StartingPoints => startingPoints;

        // Raised whenever points or unlocks change, so UI can refresh
        public event Action Changed;
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
        }

        private void OnDestroy()
        {
            if (TurnManager.Instance != null) TurnManager.Instance.OnTurnBegin -= OnTurnBegin;
            if (Instance == this) Instance = null;
        }

        private void OnTurnBegin(int turn)
        {
            if (turn <= 1) return;
            EvolutionPoints += pointsPerTurn;
            Changed?.Invoke();
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
            if (Species == null)           return "None of your species is selected";
            if (tree.IsUnlocked(node.id))  return "Already acquired";
            if (!CanAcquire(tree, node))   return $"Not in the {Species?.commonName ?? "species"}'s {tree.DisplayName.ToLowerInvariant()}";
            if (!tree.PrerequisitesMet(node)) return "Requires: " + string.Join(", ", MissingPrerequisites(tree, node));
            if (!AgeAllows(node))          return $"Available from the {node.age}";
            if (EvolutionPoints < node.cost) return $"Needs {node.cost} EP (you have {EvolutionPoints})";
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

        // Bonus points from outside the trees (e.g. a faction's iconic animal activating)
        public void AddPoints(int amount)
        {
            if (amount == 0) return;
            EvolutionPoints += amount;
            Changed?.Invoke();
        }

        public void Restore(int points, IEnumerable<string> morphology, IEnumerable<string> ethology)
        {
            EvolutionPoints = points;
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
                else yield return pre.branch == node.branch ? pre.displayName : $"{pre.displayName} ({tree.BranchName(pre.branch)})";
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
