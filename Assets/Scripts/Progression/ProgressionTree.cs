using System;
using System.Collections.Generic;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.Progression
{
    public enum NodeState { Unlocked, Available, Locked }

    // One unlock tree (Morphology or Ethology), loaded from Resources/Data/{file}.json.
    // Holds which nodes are unlocked; ProgressionManager decides whether an unlock is affordable.
    public class ProgressionTree
    {
        public string DisplayName { get; }
        public IReadOnlyList<TreeNodeDefinition> Nodes => nodes;
        public IEnumerable<string> UnlockedIds => unlocked;

        private readonly List<TreeNodeDefinition> nodes;
        private readonly Dictionary<string, TreeNodeDefinition> byId = new();
        private readonly HashSet<string> unlocked = new();

        private ProgressionTree(string displayName, List<TreeNodeDefinition> nodes)
        {
            DisplayName = displayName;
            this.nodes = nodes;
            foreach (var n in nodes)
            {
                n.prerequisites ??= new List<string>();
                n.unlocksGenes  ??= new List<string>();
                byId[n.id] = n;
            }
            UnlockStartingNodes();
        }

        public static ProgressionTree Load(string displayName, string resourcePath)
        {
            var asset = Resources.Load<TextAsset>(resourcePath);
            if (asset == null)
            {
                Debug.LogError($"[ProgressionTree] Missing Resources/{resourcePath}.json");
                return new ProgressionTree(displayName, new List<TreeNodeDefinition>());
            }
            var collection = JsonUtility.FromJson<TreeNodeCollection>(asset.text);
            return new ProgressionTree(displayName, collection?.nodes ?? new List<TreeNodeDefinition>());
        }

        public TreeNodeDefinition Get(string id) => byId.TryGetValue(id, out var n) ? n : null;

        public bool IsUnlocked(string id) => unlocked.Contains(id);

        public bool PrerequisitesMet(TreeNodeDefinition node) => node.prerequisites.TrueForAll(unlocked.Contains);

        internal void MarkUnlocked(string id) => unlocked.Add(id);

        // Replaces the unlocked set (loading a save). Unknown ids from older saves are dropped.
        internal void Restore(IEnumerable<string> ids)
        {
            unlocked.Clear();
            UnlockStartingNodes();
            if (ids == null) return;
            foreach (var id in ids)
                if (byId.ContainsKey(id)) unlocked.Add(id);
        }

        // Free (cost 0) root nodes are known from the start
        private void UnlockStartingNodes()
        {
            foreach (var n in nodes)
                if (n.cost <= 0 && n.prerequisites.Count == 0) unlocked.Add(n.id);
        }
    }
}
