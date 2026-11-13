using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Data;
using NaturalHistory.Progression;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Draws a ProgressionTree (Morphology or Ethology) as columns of nodes joined by
    // prerequisite curves, with a details strip and an Evolve button underneath.
    public class TreePanel
    {
        private const float ColumnWidth = 260f;
        private const float RowHeight   = 92f;
        private const float Padding     = 24f;
        private const float NodeWidth   = 200f;
        private const float NodeHeight  = 66f;

        private static readonly Color LineUnlocked = new(0.45f, 0.75f, 0.45f);
        private static readonly Color LineLocked   = new(0.40f, 0.42f, 0.40f);

        private readonly VisualElement overlay;
        private readonly Label title, epLabel, detailsName, detailsDescription, detailsMeta;
        private readonly VisualElement canvas;
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
            detailsName        = root.Q<Label>("details-name");
            detailsDescription = root.Q<Label>("details-description");
            detailsMeta        = root.Q<Label>("details-meta");
            evolveButton       = root.Q<Button>("evolve-button");

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

            foreach (var node in tree.Nodes)
            {
                var view  = nodeViews[node.id];
                var state = Progression.GetState(tree, node);
                view.EnableInClassList("unlocked",  state == NodeState.Unlocked);
                view.EnableInClassList("available", state == NodeState.Available);
                view.EnableInClassList("locked",    state == NodeState.Locked);
                view.EnableInClassList("selected",  node == selected);
                view.Q<Label>(className: "node-cost").text = state == NodeState.Unlocked ? "Evolved" : $"{node.cost} EP · {node.age}";
            }
            lines.MarkDirtyRepaint();
            RefreshDetails();
        }

        private void Build()
        {
            canvas.Clear();
            nodeViews.Clear();

            int maxTier = tree.Nodes.Count > 0 ? tree.Nodes.Max(n => n.tier) : 0;
            int maxRow  = tree.Nodes.Count > 0 ? tree.Nodes.Max(n => n.row)  : 0;
            canvas.style.width  = Padding * 2 + maxTier * ColumnWidth + NodeWidth;
            canvas.style.height = Padding * 2 + maxRow  * RowHeight   + NodeHeight;

            lines = new VisualElement { pickingMode = PickingMode.Ignore };
            lines.AddToClassList("tree-lines");
            lines.generateVisualContent += DrawLines;
            canvas.Add(lines);

            foreach (var node in tree.Nodes)
            {
                var view = new VisualElement();
                view.AddToClassList("tree-node");
                view.style.left = NodePosition(node).x;
                view.style.top  = NodePosition(node).y;
                view.Add(new Label(node.displayName) { pickingMode = PickingMode.Ignore }.WithClass("node-name"));
                view.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("node-cost"));

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

            foreach (var node in tree.Nodes)
            foreach (var preId in node.prerequisites)
            {
                var pre = tree.Get(preId);
                if (pre == null) continue;

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
                detailsName.text        = "Select a trait";
                detailsDescription.text = $"Click a node to see details. Double-click to evolve it.";
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
            var meta = $"Cost {selected.cost} EP  ·  From the {selected.age}";
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
