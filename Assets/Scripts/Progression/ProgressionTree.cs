using System;
using System.Collections.Generic;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.Progression
{
    // Unavailable: the shown species can never acquire it (see Evolution.EvolutionData)
    public enum NodeState { Unlocked, Available, Locked, Unavailable }

    // One unlock tree (Functions = morphology, Behaviors = ethology), loaded from Resources/Data/{file}.json.
    // Every species has its own set of acquired items; the tree shows whichever set is bound to it
    // (ProgressionManager.BindSpecies). ProgressionManager decides whether an unlock is affordable.
    public class ProgressionTree
    {
        public string DisplayName { get; }
        public IReadOnlyList<TreeNodeDefinition> Nodes => nodes;
        public IReadOnlyList<TreeBranchDefinition> Branches => branches;
        public IEnumerable<string> UnlockedIds => unlocked;

        private readonly List<TreeNodeDefinition> nodes;
        private readonly List<TreeBranchDefinition> branches;
        private readonly Dictionary<string, TreeNodeDefinition> byId = new();
        private HashSet<string> unlocked = new(); // the bound species' set (shared, not copied)

        private ProgressionTree(string displayName, List<TreeNodeDefinition> nodes, List<TreeBranchDefinition> branches)
        {
            DisplayName = displayName;
            this.nodes = nodes;
            this.branches = branches ?? new List<TreeBranchDefinition>();
            foreach (var n in nodes)
            {
                n.prerequisites ??= new List<string>();
                n.unlocksGenes  ??= new List<string>();
                byId[n.id] = n;
                // Nodes without a known branch go into a catch-all tab
                if (string.IsNullOrEmpty(n.branch) || !this.branches.Exists(b => b.id == n.branch))
                {
                    n.branch = string.IsNullOrEmpty(n.branch) ? "other" : n.branch;
                    if (!this.branches.Exists(b => b.id == n.branch))
                        this.branches.Add(new TreeBranchDefinition { id = n.branch, displayName = n.branch == "other" ? "Other" : n.branch });
                }
            }
            UnlockStartingNodes();
        }

        public static ProgressionTree Load(string displayName, string resourcePath)
        {
            var asset = Resources.Load<TextAsset>(resourcePath);
            if (asset == null)
            {
                Debug.LogError($"[ProgressionTree] Missing Resources/{resourcePath}.json");
                return new ProgressionTree(displayName, new List<TreeNodeDefinition>(), null);
            }
            var collection = JsonUtility.FromJson<TreeNodeCollection>(asset.text);
            return new ProgressionTree(displayName, collection?.nodes ?? new List<TreeNodeDefinition>(), collection?.branches);
        }

        public TreeNodeDefinition Get(string id) => byId.TryGetValue(id, out var n) ? n : null;

        public bool IsUnlocked(string id) => unlocked.Contains(id);

        public string BranchName(string branchId) => branches.Find(b => b.id == branchId)?.displayName ?? branchId;

        public bool PrerequisitesMet(TreeNodeDefinition node) => node.prerequisites.TrueForAll(unlocked.Contains);

        internal void MarkUnlocked(string id) => unlocked.Add(id);

        // Show and edit another species' acquired items. The set is used directly, so unlocks go
        // straight into it.
        internal void Bind(HashSet<string> set) => unlocked = set ?? new HashSet<string>();

        // Free root items (cost 0, no prerequisites) every species starts with, if it can have them.
        public IEnumerable<TreeNodeDefinition> StartingNodes => nodes.FindAll(n => n.cost <= 0 && n.prerequisites.Count == 0);

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
