using System;
using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.World;
using UnityEngine;

namespace NaturalHistory.Progression
{
    // Owns the Morphology (tech) and Ethology (civics) trees and the Evolution Points spent on them.
    public class ProgressionManager : MonoBehaviour
    {
        public static ProgressionManager Instance { get; private set; }

        [SerializeField] private int startingPoints = 20;
        [SerializeField] private int pointsPerTurn  = 5;

        public ProgressionTree Morphology { get; private set; }
        public ProgressionTree Ethology   { get; private set; }
        public int EvolutionPoints { get; private set; }

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
            Morphology = ProgressionTree.Load("Morphology", "Data/morphology");
            Ethology   = ProgressionTree.Load("Ethology",   "Data/ethology");
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

        public NodeState GetState(ProgressionTree tree, TreeNodeDefinition node)
        {
            if (tree.IsUnlocked(node.id)) return NodeState.Unlocked;
            return tree.PrerequisitesMet(node) && AgeAllows(node) ? NodeState.Available : NodeState.Locked;
        }

        // Null when the node can be unlocked now, otherwise a player-facing reason.
        public string UnlockBlocker(ProgressionTree tree, TreeNodeDefinition node)
        {
            if (tree.IsUnlocked(node.id))  return "Already evolved";
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
            Debug.Log($"[Progression] {tree.DisplayName}: evolved {node.displayName} (-{node.cost} EP)");
            NodeUnlocked?.Invoke(tree, node);
            Changed?.Invoke();
            return true;
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
                if (!tree.IsUnlocked(id)) yield return tree.Get(id)?.displayName ?? id;
        }

        // Age gating only applies once an AgeManager is running the geological clock.
        private static bool AgeAllows(TreeNodeDefinition node)
        {
            if (AgeManager.Instance == null || string.IsNullOrEmpty(node.age)) return true;
            return !Enum.TryParse<GeologicalAge>(node.age, out var required) || required <= AgeManager.Instance.CurrentAge;
        }
    }
}
