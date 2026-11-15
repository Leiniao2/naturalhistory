using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Data;
using NaturalHistory.Progression;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Draws a ProgressionTree (Functions or Behaviors) of the focused species, whose name and portrait
    // sit at the top centre, in a near full-screen panel: one tab per
    // branch (Nervous System, Hunting, …), the branch's nodes in columns joined by prerequisite
    // curves, and a details strip with an Evolve button underneath. Prerequisites in another branch
    // are listed on the node instead of drawn.
    public class TreePanel
    {
        private const float ColumnWidth = 250f;
        private const float RowHeight   = 96f;
        private const float Padding     = 24f;
        private const float NodeWidth   = 206f;
        private const float NodeHeight  = 74f;

        private static readonly Color LineUnlocked = new(0.45f, 0.75f, 0.45f);
        private static readonly Color LineLocked   = new(0.40f, 0.42f, 0.40f);

        private readonly VisualElement overlay;
        private readonly Label title, epLabel, detailsName, detailsDescription, detailsMeta, speciesName;
        private readonly VisualElement speciesPortrait;
        private readonly VisualElement canvas, branchTabs;
        private readonly Label progressLabel;
        private readonly Dictionary<string, Button> tabViews = new();
        private readonly Dictionary<ProgressionTree, string> branchByTree = new(); // last tab per tree
        private string branch;
        private readonly Button evolveButton;
        private readonly Dictionary<string, VisualElement> nodeViews = new();
        private VisualElement lines;

        private ProgressionTree tree;
        private TreeNodeDefinition selected;

        private static ProgressionManager Progression => ProgressionManager.Instance;

        public bool IsOpen => !overlay.ClassListContains("hidden");
        public ProgressionTree CurrentTree => tree;

        public TreePanel(VisualElement root)
        {
            overlay            = root.Q("tree-overlay");
            title              = root.Q<Label>("tree-title");
            epLabel            = root.Q<Label>("tree-ep-label");
            canvas             = root.Q("tree-canvas");
            branchTabs         = root.Q("tree-branches");
            progressLabel      = root.Q<Label>("tree-progress");
            detailsName        = root.Q<Label>("details-name");
            detailsDescription = root.Q<Label>("details-description");
            detailsMeta        = root.Q<Label>("details-meta");
            evolveButton       = root.Q<Button>("evolve-button");
            speciesName        = root.Q<Label>("tree-species-name");
            speciesPortrait    = root.Q("tree-species-portrait");

            root.Q<Button>("tree-close-button").clicked += Close;
            evolveButton.clicked += OnEvolveClicked;
        }

        public void Open(ProgressionTree newTree)
        {
            if (newTree == null) return;
            if (tree != newTree)
            {
                tree = newTree;
                selected = null;
                BuildTabs();
                branch = branchByTree.TryGetValue(tree, out var last) ? last : tree.Branches.FirstOrDefault()?.id;
                Build();
            }
            overlay.RemoveFromClassList("hidden");
            Refresh();
        }

        public void Close() => overlay.AddToClassList("hidden");

        // Re-applies node states, labels and details (after unlocks / point changes / loading).
        public void Refresh()
        {
            if (tree == null || Progression == null) return;
            title.text   = tree.DisplayName;
            epLabel.text = $"EP {Progression.EvolutionPoints}";
            var species = Progression.Species;
            speciesName.text = species != null ? species.commonName : "No species";
            speciesPortrait.style.backgroundImage = SpeciesPortraits.Get(species) is RenderTexture rt
                ? Background.FromRenderTexture(rt) : new StyleBackground(StyleKeyword.None);
            int acquirable = tree.Nodes.Count(n => Progression.CanAcquire(tree, n));
            progressLabel.text = $"{tree.Nodes.Count(n => tree.IsUnlocked(n.id))} / {acquirable} acquired";
            RefreshTabs();

            foreach (var node in tree.Nodes)
            {
                if (!nodeViews.TryGetValue(node.id, out var view)) continue; // other branch
                var state = Progression.GetState(tree, node);
                view.EnableInClassList("unlocked",  state == NodeState.Unlocked);
                view.EnableInClassList("available", state == NodeState.Available);
                view.EnableInClassList("locked",    state == NodeState.Locked);
                view.EnableInClassList("unavailable", state == NodeState.Unavailable);
                view.EnableInClassList("selected",  node == selected);
                view.Q<Label>(className: "node-cost").text = state switch
                {
                    NodeState.Unlocked    => "Acquired",
                    NodeState.Unavailable => "Not for this species",
                    _                     => $"{node.cost} EP · {node.age}",
                };
            }
            lines.MarkDirtyRepaint();
            RefreshDetails();
        }

        // ---------- Branch tabs ----------

        private void BuildTabs()
        {
            branchTabs.Clear();
            tabViews.Clear();
            foreach (var b in tree.Branches)
            {
                var id = b.id;
                var tab = new Button(() => SelectBranch(id)).WithClass("branch-tab");
                tab.Add(new Label(b.displayName) { pickingMode = PickingMode.Ignore }.WithClass("branch-tab-name"));
                tab.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("branch-tab-count"));
                tab.tooltip = b.description;
                branchTabs.Add(tab);
                tabViews[id] = tab;
            }
        }

        private void SelectBranch(string id)
        {
            if (id == branch) return;
            branch = id;
            branchByTree[tree] = id;
            if (selected != null && selected.branch != id) selected = null;
            Build();
            Refresh();
        }

        // "evolved / total" per tab; highlighted when something there can be evolved right now
        private void RefreshTabs()
        {
            foreach (var b in tree.Branches)
            {
                if (!tabViews.TryGetValue(b.id, out var tab)) continue;
                var members = tree.Nodes.Where(n => n.branch == b.id && Progression.CanAcquire(tree, n)).ToList();
                tab.Q<Label>(className: "branch-tab-count").text = $"{members.Count(n => tree.IsUnlocked(n.id))}/{members.Count}";
                tab.EnableInClassList("selected", b.id == branch);
                tab.EnableInClassList("has-available", members.Any(n => Progression.UnlockBlocker(tree, n) == null));
            }
        }

        private IEnumerable<TreeNodeDefinition> BranchNodes => tree.Nodes.Where(n => n.branch == branch);

        // ---------- Nodes ----------

        private void Build()
        {
            canvas.Clear();
            nodeViews.Clear();

            var nodes   = BranchNodes.ToList();
            int maxTier = nodes.Count > 0 ? nodes.Max(n => n.tier) : 0;
            int maxRow  = nodes.Count > 0 ? nodes.Max(n => n.row)  : 0;
            canvas.style.width  = Padding * 2 + maxTier * ColumnWidth + NodeWidth;
            canvas.style.height = Padding * 2 + maxRow  * RowHeight   + NodeHeight;

            lines = new VisualElement { pickingMode = PickingMode.Ignore };
            lines.AddToClassList("tree-lines");
            lines.generateVisualContent += DrawLines;
            canvas.Add(lines);

            foreach (var node in nodes)
            {
                var view = new VisualElement();
                view.AddToClassList("tree-node");
                view.style.left = NodePosition(node).x;
                view.style.top  = NodePosition(node).y;
                view.Add(new Label(node.displayName) { pickingMode = PickingMode.Ignore }.WithClass("node-name"));
                view.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("node-cost"));
                var external = node.prerequisites.Select(tree.Get).Where(p => p != null && p.branch != node.branch).ToList();
                if (external.Count > 0)
                    view.Add(new Label("Needs " + string.Join(", ", external.Select(p => p.displayName))) { pickingMode = PickingMode.Ignore }
                        .WithClass("node-external"));

                var captured = node;
                view.RegisterCallback<ClickEvent>(e =>
                {
                    selected = captured;
                    // Double-click evolves straight away
                    if (e.clickCount == 2) Progression.TryUnlock(tree, captured);
                    Refresh();
                });

                canvas.Add(view);
                nodeViews[node.id] = view;
            }
        }

        private static Vector2 NodePosition(TreeNodeDefinition node)
            => new(Padding + node.tier * ColumnWidth, Padding + node.row * RowHeight);

        private void DrawLines(MeshGenerationContext ctx)
        {
            if (tree == null) return;
            var p = ctx.painter2D;
            p.lineWidth = 3f;
            p.lineCap   = LineCap.Round;

            foreach (var node in BranchNodes)
            foreach (var preId in node.prerequisites)
            {
                var pre = tree.Get(preId);
                if (pre == null || pre.branch != node.branch) continue;

                var from = NodePosition(pre)  + new Vector2(NodeWidth, NodeHeight * 0.5f);
                var to   = NodePosition(node) + new Vector2(0f,        NodeHeight * 0.5f);
                float bend = (to.x - from.x) * 0.5f;

                p.strokeColor = tree.IsUnlocked(preId) ? LineUnlocked : LineLocked;
                p.BeginPath();
                p.MoveTo(from);
                p.BezierCurveTo(from + new Vector2(bend, 0f), to - new Vector2(bend, 0f), to);
                p.Stroke();
            }
        }

        private void RefreshDetails()
        {
            if (selected == null)
            {
                detailsName.text        = "Select an item";
                detailsDescription.text = "Click an item to see details. Double-click to acquire it. Tabs above switch between branches. Greyed-out items aren't in this species' trees.";
                detailsMeta.text        = "";
                evolveButton.SetEnabled(false);
                return;
            }

            detailsName.text        = selected.displayName;
            detailsDescription.text = selected.description;

            var genes = selected.unlocksGenes
                .Select(id => GameDataLoader.GetGene(id)?.displayName ?? id)
                .ToList();
            var blocker = Progression.UnlockBlocker(tree, selected);
            var meta = $"{tree.BranchName(selected.branch)}  ·  Cost {selected.cost} EP  ·  From the {selected.age}";
            if (genes.Count > 0) meta += $"  ·  Unlocks genes: {string.Join(", ", genes)}";
            if (blocker != null) meta += $"\n{blocker}";
            detailsMeta.text = meta;

            evolveButton.SetEnabled(blocker == null);
        }

        private void OnEvolveClicked()
        {
            if (selected != null) Progression.TryUnlock(tree, selected);
            Refresh();
        }
    }

    internal static class VisualElementExtensions
    {
        public static T WithClass<T>(this T element, string className) where T : VisualElement
        {
            element.AddToClassList(className);
            return element;
        }
    }
}
