using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // The evolution tree (evolution.json): every species that evolves or can be evolved into, laid
    // out left to right by how many steps they are from their earliest ancestor, joined by curves.
    // Selecting a species shows where it comes from and, for each species it can become, the
    // requirements ticked off for your copies, with an Evolve button.
    //
    // Opened from the HUD (browse) or from a selected animal's Evolve button: then that copy is the
    // one that evolves, and its species is selected.
    public class ZoologyPanel
    {
        private const float ColumnWidth = 240f;
        private const float RowHeight   = 92f;
        private const float Padding     = 24f;
        private const float NodeWidth   = 200f;
        private const float NodeHeight  = 76f;

        private static readonly Color LineReady   = new(0.95f, 0.80f, 0.35f);
        private static readonly Color LineUsed    = new(0.45f, 0.75f, 0.45f);
        private static readonly Color LineOther   = new(0.36f, 0.40f, 0.36f);

        private readonly VisualElement overlay, canvas, linksBox, detailPortrait;
        private readonly Label subtitle, nameLabel, metaLabel, descriptionLabel;
        private readonly Dictionary<string, VisualElement> nodeViews = new();
        private readonly Dictionary<string, Vector2> positions = new();
        private VisualElement lines;
        private string selected;
        private OwnedCopy context; // the copy that evolves (from a selected animal), or null

        public event Action<string> Message;

        public bool IsOpen => !overlay.ClassListContains("hidden");
        private static EvolutionManager Evolution => EvolutionManager.Instance;

        public ZoologyPanel(VisualElement root)
        {
            overlay          = root.Q("zoology-overlay");
            canvas           = root.Q("zoology-canvas");
            linksBox         = root.Q("zoology-links");
            detailPortrait   = root.Q("zoology-portrait");
            subtitle         = root.Q<Label>("zoology-subtitle");
            nameLabel        = root.Q<Label>("zoology-name");
            metaLabel        = root.Q<Label>("zoology-meta");
            descriptionLabel = root.Q<Label>("zoology-description");
            root.Q<Button>("zoology-close-button").clicked += Close;
        }

        public void Open(OwnedCopy copy = null)
        {
            if (Evolution == null) return;
            context = copy;
            if (nodeViews.Count == 0) Build();
            selected = copy?.species ?? Evolution.FocusSpecies ?? Evolution.HumanSpecies.FirstOrDefault() ?? selected;
            overlay.RemoveFromClassList("hidden");
            Refresh();
        }

        public void Close()
        {
            overlay.AddToClassList("hidden");
            context = null;
        }

        // ---------- Layout ----------

        private void Build()
        {
            canvas.Clear();
            nodeViews.Clear();
            positions.Clear();

            var links   = EvolutionData.Links;
            var species = links.SelectMany(l => new[] { l.from, l.to }).Distinct()
                               .Where(id => GameDataLoader.GetSpecies(id) != null).ToList();

            // Column = longest chain of ancestors (so descendants always sit right of their origin)
            var depth = new Dictionary<string, int>();
            int Depth(string id, int guard)
            {
                if (depth.TryGetValue(id, out var d)) return d;
                if (guard > 64) return 0;
                var parents = links.Where(l => l.to == id).Select(l => l.from).ToList();
                d = parents.Count == 0 ? 0 : parents.Max(p => Depth(p, guard + 1)) + 1;
                depth[id] = d;
                return d;
            }
            foreach (var id in species) Depth(id, 0);

            // Rows: roots by period; then each column ordered by its parents' rows, so a lineage stays together
            var row = new Dictionary<string, float>();
            int maxDepth = species.Count > 0 ? species.Max(id => depth[id]) : 0;
            int maxRows = 0;
            for (int col = 0; col <= maxDepth; col++)
            {
                var members = species.Where(id => depth[id] == col)
                    .OrderBy(id => col == 0 ? AgeIndex(id) : links.Where(l => l.to == id && row.ContainsKey(l.from)).Select(l => row[l.from]).DefaultIfEmpty(0f).Average())
                    .ThenBy(id => AgeIndex(id))
                    .ToList();
                for (int i = 0; i < members.Count; i++)
                {
                    row[members[i]] = i;
                    positions[members[i]] = new Vector2(Padding + col * ColumnWidth, Padding + i * RowHeight);
                }
                maxRows = Mathf.Max(maxRows, members.Count);
            }
            canvas.style.width  = Padding * 2 + maxDepth * ColumnWidth + NodeWidth;
            canvas.style.height = Padding * 2 + Mathf.Max(0, maxRows - 1) * RowHeight + NodeHeight;

            lines = new VisualElement { pickingMode = PickingMode.Ignore };
            lines.AddToClassList("tree-lines");
            lines.generateVisualContent += DrawLines;
            canvas.Add(lines);

            foreach (var id in species)
            {
                var def  = GameDataLoader.GetSpecies(id);
                var view = new VisualElement().WithClass("zoology-node");
                view.style.left = positions[id].x;
                view.style.top  = positions[id].y;
                var pic = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("species-portrait").WithClass("zoology-node-portrait");
                view.Add(pic);
                var text = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("zoology-node-text");
                text.Add(new Label(def.commonName) { pickingMode = PickingMode.Ignore }.WithClass("node-name"));
                text.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("node-cost"));
                view.Add(text);
                var captured = id;
                view.RegisterCallback<ClickEvent>(_ => { selected = captured; Refresh(); });
                canvas.Add(view);
                nodeViews[id] = view;
            }
        }

        private static int AgeIndex(string id) =>
            Enum.TryParse(GameDataLoader.GetSpecies(id)?.firstAge, true, out GeologicalAge a) ? (int)a : 0;

        private void DrawLines(MeshGenerationContext ctx)
        {
            var p = ctx.painter2D;
            p.lineWidth = 3f;
            p.lineCap   = LineCap.Round;
            foreach (var link in EvolutionData.Links)
            {
                if (!positions.TryGetValue(link.from, out var a) || !positions.TryGetValue(link.to, out var b)) continue;
                var from = a + new Vector2(NodeWidth, NodeHeight * 0.5f);
                var to   = b + new Vector2(0f, NodeHeight * 0.5f);
                float bend = Mathf.Max(40f, (to.x - from.x) * 0.5f);
                p.strokeColor = Evolution.HasEvolved(link) ? LineUsed : ReadyFor(link) != null ? LineReady : LineOther;
                p.BeginPath();
                p.MoveTo(from);
                p.BezierCurveTo(from + new Vector2(bend, 0f), to - new Vector2(bend, 0f), to);
                p.Stroke();
            }
        }

        // ---------- State ----------

        // The copy that would evolve along `link` now: the context copy, else any of yours that can
        private OwnedCopy ReadyFor(EvolutionLink link)
        {
            if (context != null) return context.species == link.from && Evolution.CanEvolve(link, context) ? context : null;
            var human = Players.PlayerManager.Instance?.Human;
            return Evolution.CopiesOf(human).FirstOrDefault(c => c.species == link.from && Evolution.CanEvolve(link, c));
        }

        public void Refresh()
        {
            if (!IsOpen || Evolution == null) return;
            var owned = new HashSet<string>(Evolution.HumanSpecies);
            int ready = EvolutionData.Links.Count(l => ReadyFor(l) != null);
            subtitle.text = context != null
                ? $"Evolving one {GameDataLoader.GetSpecies(context.species)?.commonName}"
                : $"{owned.Count} of your species  ·  {ready} evolution{(ready == 1 ? "" : "s")} ready";

            foreach (var (id, view) in nodeViews)
            {
                bool canBecome = EvolutionData.To(id).Any(l => ReadyFor(l) != null);
                view.EnableInClassList("owned",    owned.Contains(id));
                view.EnableInClassList("ready",    canBecome);
                view.EnableInClassList("selected", id == selected);
                var def = GameDataLoader.GetSpecies(id);
                view.Q<Label>(className: "node-cost").text = owned.Contains(id) ? "Yours" : canBecome ? "Can evolve" : def.firstAge;
                var pic = view.Q(className: "zoology-node-portrait");
                if (pic.userData == null) // rendered once, the first time the panel opens
                {
                    pic.userData = true;
                    if (SpeciesPortraits.Get(def) is RenderTexture rt) pic.style.backgroundImage = Background.FromRenderTexture(rt);
                }
            }
            lines?.MarkDirtyRepaint();
            ShowDetails();
        }

        private void ShowDetails()
        {
            linksBox.Clear();
            var def = selected != null ? GameDataLoader.GetSpecies(selected) : null;
            if (def == null)
            {
                nameLabel.text = "Select a species";
                metaLabel.text = descriptionLabel.text = "";
                detailPortrait.style.backgroundImage = new StyleBackground(StyleKeyword.None);
                return;
            }

            nameLabel.text = def.commonName;
            var span = string.IsNullOrEmpty(def.lastAge) ? $"{def.firstAge} – today" : def.firstAge == def.lastAge ? def.firstAge : $"{def.firstAge} – {def.lastAge}";
            var count = Evolution.CopiesOf(Players.PlayerManager.Instance?.Human).Count(c => c.species == def.id);
            metaLabel.text = $"{def.scientificName}  ·  {def.group}  ·  {span}" + (count > 0 ? $"\nYou have {count} cop{(count == 1 ? "y" : "ies")}" : "");
            descriptionLabel.text = def.description;
            detailPortrait.style.backgroundImage = SpeciesPortraits.Get(def) is RenderTexture rt ? Background.FromRenderTexture(rt) : new StyleBackground(StyleKeyword.None);

            var parents = EvolutionData.To(def.id).Select(l => GameDataLoader.GetSpecies(l.from)?.commonName ?? l.from).ToList();
            if (parents.Count > 0) linksBox.Add(new Label($"Evolves from: {string.Join(", ", parents)}").WithClass("zoology-from"));

            var outgoing = EvolutionData.From(def.id).ToList();
            if (outgoing.Count == 0) { linksBox.Add(new Label("No known descendants among the game's species.").WithClass("zoology-from")); return; }
            linksBox.Add(new Label("Can evolve into").WithClass("age-section"));
            foreach (var link in outgoing) linksBox.Add(LinkCard(link));
        }

        private VisualElement LinkCard(EvolutionLink link)
        {
            var target = GameDataLoader.GetSpecies(link.to);
            var card = new VisualElement().WithClass("zoology-link");
            var head = new VisualElement().WithClass("zoology-link-head");
            var pic  = new VisualElement().WithClass("species-portrait").WithClass("zoology-link-portrait");
            if (SpeciesPortraits.Get(target) is RenderTexture rt) pic.style.backgroundImage = Background.FromRenderTexture(rt);
            head.Add(pic);
            var title = new Label(target?.commonName ?? link.to).WithClass("zoology-link-name");
            title.RegisterCallback<ClickEvent>(_ => { selected = link.to; Refresh(); });
            head.Add(title);
            card.Add(head);
            if (!string.IsNullOrEmpty(link.description)) card.Add(new Label(link.description).WithClass("zoology-link-text"));

            // The copy this card is about: the one being evolved, else one of yours that is ready
            var copy = context != null ? (context.species == link.from ? context : null) : ReadyFor(link);
            foreach (var r in Evolution.Requirements(link, copy))
                card.Add(new Label((r.met ? "✓  " : "✗  ") + r.text).WithClass("zoology-req").WithClass(r.met ? "met" : "unmet"));

            var grants = link.grantFunctions.Select(id => ProgressionNodeName(true, id))
                .Concat(link.grantBehaviors.Select(id => ProgressionNodeName(false, id))).ToList();
            if (grants.Count > 0) card.Add(new Label("Gains on evolving: " + string.Join(", ", grants)).WithClass("zoology-link-text"));

            bool can = copy != null && Evolution.CanEvolve(link, copy);
            var button = new Button(() => DoEvolve(link, copy)) { text = can ? $"Evolve into {target?.commonName}" : "Evolve" }.WithClass("evolve-button").WithClass("zoology-evolve");
            button.SetEnabled(can);
            if (Evolution.HasEvolved(link)) button.text = "Already evolved by another copy";
            card.Add(button);
            return card;
        }

        private static string ProgressionNodeName(bool function, string id)
        {
            var p = Progression.ProgressionManager.Instance;
            var tree = p == null ? null : function ? p.Morphology : p.Ethology;
            return tree?.Get(id)?.displayName ?? id;
        }

        private void DoEvolve(EvolutionLink link, OwnedCopy copy)
        {
            if (copy == null) return;
            Evolution.Evolve(link, copy, out var message);
            if (message != null) Message?.Invoke(message);
            if (context == copy) context = null; // that copy is now the new species
            selected = link.to;
            Refresh();
        }
    }
}
