using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Progression;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Draws a ProgressionTree (Functions or Behaviors) of the focused species in a near full-screen
    // panel: a tab per species of yours along the top (SpeciesTabs) to switch whose trees these are,
    // then one tab per
    // branch (Nervous System, Hunting, …), the branch's nodes in columns joined by prerequisite
    // curves, and a details strip with an Evolve button underneath. Prerequisites in another branch
    // are listed on the node instead of drawn.
    // Each item is a card like the Evolution Tree's (ZoologyPanel): its painting (TraitIcons) on the
    // left, its name, state and the bonus it gives the species' groups (TraitBonuses) in the middle,
    // and an Acquire icon button on the right, lit when it can be acquired now, whose tip says what
    // it costs and needs.
    public class TreePanel
    {
        private const float ColumnWidth = 400f;
        private const float RowHeight   = 120f;
        private const float Padding     = 24f;
        private const float NodeWidth   = 350f; // .trait-node in the USS
        private const float NodeHeight  = 100f;

        private const float ForkRadius  = 10f;   // rounded corners of the lines, as in the Evolution Tree

        private static readonly Color LineUnlocked = new(0.45f, 0.75f, 0.45f);
        private static readonly Color LineReady    = new(0.95f, 0.80f, 0.35f);
        private static readonly Color LineLocked   = new(0.36f, 0.40f, 0.36f);

        private readonly VisualElement overlay;
        private readonly Label title, epLabel, detailsName, detailsDescription, detailsMeta;
        private readonly SpeciesTabs speciesTabs;
        private SpeciesDefinition builtFor; // the species the nodes were laid out for
        private readonly VisualElement canvas, branchTabs;
        private readonly Label progressLabel;
        private readonly Dictionary<string, Button> tabViews = new();
        private readonly Dictionary<ProgressionTree, string> branchByTree = new(); // last tab per tree
        private string branch;
        private readonly Button evolveButton;
        private readonly Dictionary<string, VisualElement> nodeViews = new();
        private VisualElement lines;
        private readonly Label tip; // follows the pointer over an Acquire button (as in the Evolution Tree)

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
            speciesTabs        = new SpeciesTabs(root.Q("tree-species-tabs"));
            speciesTabs.Picked += id => EvolutionManager.Instance?.Focus(id); // its trees rebind and Refresh follows

            tip = new Label { pickingMode = PickingMode.Ignore }.WithClass("zoology-tip");
            tip.AddToClassList("hidden");
            overlay.Add(tip);

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
                builtFor = Progression?.Species;
                branch = branchByTree.TryGetValue(tree, out var last) ? last : tree.Branches.FirstOrDefault()?.id;
                Build();
            }
            // each tree its own colours, so the two read as different things: Functions blue,
            // Behaviors purple (the Evolution tree is green, ZoologyPanel)
            overlay.EnableInClassList("theme-functions", tree == Progression?.Morphology);
            overlay.EnableInClassList("theme-behaviors", tree == Progression?.Ethology);
            overlay.RemoveFromClassList("hidden");
            Refresh();
        }

        public void Close()
        {
            overlay.AddToClassList("hidden");
            tip.AddToClassList("hidden");
        }

        // Re-applies node states, labels and details (after unlocks / point changes / loading).
        public void Refresh()
        {
            if (tree == null || Progression == null) return;
            title.text   = Loc.T(tree.DisplayName);
            epLabel.text = Loc.F("EP {0}", Progression.EvolutionPoints);
            var species = Progression.Species;
            speciesTabs.Refresh(species?.id);
            if (species != builtFor)
            {
                // another species: its own items are available, the rest greyed out
                builtFor = species;
                if (selected != null && !Progression.CanAcquire(tree, selected)) selected = null;
                Build();
            }
            int acquirable = tree.Nodes.Count(n => Progression.CanAcquire(tree, n));
            progressLabel.text = Loc.F("{0} / {1} acquired", tree.Nodes.Count(n => tree.IsUnlocked(n.id)), acquirable);
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
                    NodeState.Unlocked    => Loc.T("Acquired"),
                    NodeState.Unavailable => Loc.T("Not for this species"),
                    _                     => Loc.F("{0} EP · {1}", EpCosts.Of(node.cost), Loc.T(node.age)),
                };
                view.Q<Label>(className: "trait-node-bonus").text = BonusText(node);
                if (view.Q<Button>(className: "zoology-icon") is { } acquire)
                {
                    bool can = Progression.UnlockBlocker(tree, node) == null;
                    acquire.style.display = state == NodeState.Unlocked || state == NodeState.Unavailable ? DisplayStyle.None : DisplayStyle.Flex;
                    acquire.EnableInClassList("ready", can);
                    acquire.EnableInClassList("locked", !can);
                }
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
                tab.Add(new Label(Loc.T(b.displayName)) { pickingMode = PickingMode.Ignore }.WithClass("branch-tab-name"));
                tab.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("branch-tab-count"));
                tab.tooltip = Loc.T(b.description);
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
                var view = new VisualElement().WithClass("tree-node").WithClass("trait-node");
                view.style.left = NodePosition(node).x;
                view.style.top  = NodePosition(node).y;
                var pic = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("trait-node-image");
                if (TraitIcons.Get(tree == Progression.Morphology, node.id) is { } image) pic.style.backgroundImage = new StyleBackground(image);
                else pic.Add(new Label(Loc.T(node.displayName).Substring(0, 1)) { pickingMode = PickingMode.Ignore }.WithClass("trait-node-initial"));
                view.Add(pic);
                var text = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("trait-node-text");
                text.Add(new Label(Loc.T(node.displayName)) { pickingMode = PickingMode.Ignore }.WithClass("node-name"));
                text.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("node-cost"));
                text.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("trait-node-bonus"));
                var external = node.prerequisites.Select(tree.Get).Where(p => p != null && p.branch != node.branch).ToList();
                if (external.Count > 0)
                    text.Add(new Label(Loc.F("Needs {0}", string.Join(", ", external.Select(p => Loc.T(p.displayName))))) { pickingMode = PickingMode.Ignore }
                        .WithClass("node-external"));
                view.Add(text);

                var captured = node;
                if (node.prerequisites.Count > 0) // the free roots are had from the start
                {
                    var acquire = new Button(() => { Progression.TryUnlock(tree, captured); selected = captured; Refresh(); }).WithClass("zoology-icon");
                    acquire.style.backgroundImage = new StyleBackground(UiIcons.Upgrade);
                    acquire.EnableInClassList("drawn", !UiIcons.Painted(UiIcons.Upgrade));
                    Hint(acquire, () => AcquireTip(captured));
                    view.Add(acquire);
                }
                view.RegisterCallback<ClickEvent>(e =>
                {
                    if (e.target is Button) return; // the card's own button
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

            // grey first, green last, so where lines share a trunk the progress shows on top
            var links = BranchNodes
                .SelectMany(n => n.prerequisites.Select(id => (pre: tree.Get(id), node: n)))
                .Where(l => l.pre != null && l.pre.branch == l.node.branch)
                .OrderBy(l => !tree.IsUnlocked(l.pre.id) ? 0 : tree.IsUnlocked(l.node.id) ? 2 : 1);
            foreach (var (pre, node) in links)
            {
                var preId = pre.id;
                var from = NodePosition(pre)  + new Vector2(NodeWidth, NodeHeight * 0.5f);
                var to   = NodePosition(node) + new Vector2(0f,        NodeHeight * 0.5f);

                p.strokeColor = !tree.IsUnlocked(preId) ? LineLocked
                              : tree.IsUnlocked(node.id) ? LineUnlocked
                              : Progression.GetState(tree, node) == NodeState.Available ? LineReady : LineLocked;
                // Like the Evolution Tree: out of the prerequisite, along a trunk in the gap just
                // before the item's column (shared by everything leading into it, and by the forks
                // of a prerequisite in the column before), then across into it, with rounded corners
                float trunk = to.x - (ColumnWidth - NodeWidth) * 0.5f;
                float dy = to.y - from.y;
                p.BeginPath();
                p.MoveTo(from);
                if (Mathf.Abs(dy) < 1f) p.LineTo(to);
                else
                {
                    float r = Mathf.Min(ForkRadius, Mathf.Abs(dy) * 0.5f, (trunk - from.x) * 0.9f);
                    float sy = Mathf.Sign(dy);
                    p.LineTo(new Vector2(trunk - r, from.y));
                    p.ArcTo(new Vector2(trunk, from.y), new Vector2(trunk, from.y + sy * r), r);
                    p.LineTo(new Vector2(trunk, to.y - sy * r));
                    p.ArcTo(new Vector2(trunk, to.y), new Vector2(trunk + r, to.y), r);
                    p.LineTo(to);
                }
                p.Stroke();
            }
        }

        // "+1 Attack", the item's bonus for the species whose trees these are (era factor included)
        private string BonusText(TreeNodeDefinition node)
        {
            var b = World.TraitBonuses.Scaled(node, Progression.Species);
            if (b == null) return "";
            var parts = new List<string>();
            if (b.attack  != 0) parts.Add(Loc.F("Attack +{0}", b.attack));
            if (b.defense != 0) parts.Add(Loc.F("Defense +{0}", b.defense));
            if (b.hp      != 0) parts.Add(Loc.F("HP +{0}", b.hp));
            if (b.moves   != 0) parts.Add(Loc.F("Actions +{0}", b.moves));
            return string.Join("  ", parts);
        }

        // What the item is, gives, costs and still needs, ticked off
        private string AcquireTip(TreeNodeDefinition node)
        {
            var lines = new List<string> { Loc.T(node.displayName), Loc.T(node.description) };
            var bonus = BonusText(node);
            if (bonus != "") lines.Add(Loc.F("Your groups of it: {0}", bonus));
            lines.Add("");
            int cost = EpCosts.Of(node.cost);
            lines.Add((Progression.EvolutionPoints >= cost ? "✓  " : "✗  ") + Loc.F("Needs {0} EP (you have {1})", cost, Progression.EvolutionPoints));
            var blocker = Progression.UnlockBlocker(tree, node);
            if (blocker != null && Progression.EvolutionPoints >= cost) lines.Add("✗  " + blocker);
            return string.Join("\n", lines);
        }

        // A tip that follows the pointer over `target` (UI Toolkit's own tooltips only show in the Editor)
        private void Hint(VisualElement target, System.Func<string> text)
        {
            target.RegisterCallback<PointerEnterEvent>(e => { tip.text = text(); tip.RemoveFromClassList("hidden"); tip.BringToFront(); PlaceTip(e.position); });
            target.RegisterCallback<PointerMoveEvent>(e => PlaceTip(e.position));
            target.RegisterCallback<PointerLeaveEvent>(_ => tip.AddToClassList("hidden"));
        }

        private void PlaceTip(Vector2 pointer)
        {
            var area = overlay.worldBound;
            var size = tip.layout.size;
            float x = pointer.x + 18f, y = pointer.y + 18f;
            if (!float.IsNaN(size.x) && x + size.x > area.xMax - 8f) x = pointer.x - size.x - 18f;
            if (!float.IsNaN(size.y) && y + size.y > area.yMax - 8f) y = pointer.y - size.y - 18f;
            tip.style.left = x - area.xMin;
            tip.style.top  = y - area.yMin;
        }

        private void RefreshDetails()
        {
            if (selected == null)
            {
                detailsName.text        = Loc.T("Select an item");
                detailsDescription.text = Loc.T("Click an item to see details. Double-click to acquire it. Tabs above switch between branches. Greyed-out items aren't in this species' trees.");
                detailsMeta.text        = "";
                evolveButton.SetEnabled(false);
                return;
            }

            detailsName.text        = Loc.T(selected.displayName);
            detailsDescription.text = Loc.T(selected.description);

            var genes = selected.unlocksGenes
                .Select(id => Loc.T(GameDataLoader.GetGene(id)?.displayName ?? id))
                .ToList();
            var blocker = Progression.UnlockBlocker(tree, selected);
            var meta = Loc.F("{0}  ·  Cost {1} EP  ·  From the {2}", Loc.T(tree.BranchName(selected.branch)), EpCosts.Of(selected.cost), Loc.T(selected.age));
            var bonusText = BonusText(selected);
            if (bonusText != "") meta += "  ·  " + bonusText;
            if (genes.Count > 0) meta += "  ·  " + Loc.F("Unlocks genes: {0}", string.Join(", ", genes));
            // abilities of the bound species this item switches on (World.Abilities)
            bool function = tree == Progression.Morphology;
            var abilities = World.Abilities.Of(Progression.Species)
                .Where(ab => (function ? ab.unlockFunctions : ab.unlockBehaviors).Contains(selected.id))
                .Select(ab => Loc.T(ab.name)).ToList();
            if (abilities.Count > 0) meta += "  ·  " + Loc.F("Unlocks ability: {0}", string.Join(", ", abilities));
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
