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
    // The evolution tree (evolution.json), shown a piece at a time since the whole tree has far too
    // many species for one view. It starts from one species (the selected animal) and shows what it
    // can evolve into and their descendants for a few generations (MaxGenerations), left to right;
    // a species further on that has descendants of its own says how many, and clicking it carries on
    // from there. Each species' descendants take a block of rows of their own, with the species
    // centred on them and a gap between neighbouring lineages, joined to it by a fork, so lineages
    // never interleave. Its ancestor sits faded on the left. A descendant that starts a new major group (a phylum, class... see Clades: insects,
    // vertebrates, mammals) is not expanded but shown as one group card; clicking that opens the tree
    // again from the group's first species. Clicking a species makes it the starting point; Back
    // returns to the previous view.
    //
    // Selecting a species shows where it comes from and, for each species it can become, the
    // requirements ticked off for your copies, with an Evolve button; its painting and description
    // are in the Encyclopedia (the button by its name, or double-click the species). Opened from the
    // HUD (browse) or from a selected animal's Evolve button: then that copy is the one that evolves.
    // A tab per species of yours along the top starts the tree from that one.
    public class ZoologyPanel
    {
        private const float ColumnWidth = 330f; // wide enough for long names (Chinese, German...)
        private const float RowHeight   = 102f;
        private const float Padding     = 24f;
        private const float NodeWidth   = 290f;
        private const float NodeHeight  = 86f;
        private const int   MaxGenerations = 3;  // generations shown after the starting species…
        private const float MaxRows        = 14f; // …fewer where the tree would grow taller than this (hubs like the choanoflagellate)
        private const float LineageGap  = 0.4f;  // extra rows between neighbouring lineages
        private const float ForkRadius  = 10f;   // rounded corners of the fork lines

        private static readonly Color LineReady   = new(0.95f, 0.80f, 0.35f);
        private static readonly Color LineUsed    = new(0.45f, 0.75f, 0.45f);
        private static readonly Color LineOther   = new(0.36f, 0.40f, 0.36f);

        // The major groups that get their own tree, by the trait tag that marks them (trait_rules.json),
        // broadest first: a species with a tag its ancestor lacks starts that group.
        private static readonly (string tag, string name)[] Clades =
        {
            ("Arthropod",     "Phylum Arthropoda"),
            ("Chelicerate",   "Subphylum Chelicerata"),
            ("Myriapod",      "Subphylum Myriapoda"),
            ("Insect",        "Class Insecta"),
            ("Mollusc",       "Phylum Mollusca"),
            ("Cephalopod",    "Class Cephalopoda"),
            ("Chordate",      "Phylum Chordata"),
            ("Vertebrate",    "Subphylum Vertebrata"),
            ("Cartilaginous", "Class Chondrichthyes"),
            ("Bony fish",     "Class Osteichthyes"),
            ("Amphibian",     "Class Amphibia"),
            ("Reptile",       "Class Reptilia"),
            ("Dinosaur",      "Superorder Dinosauria"),
            ("Bird",          "Class Aves"),
            ("Mammal",        "Class Mammalia"),
        };

        // One card of the current view: a species, or a group standing for its founders' trees
        private sealed class Node
        {
            public string key, species, clade; // clade: index into Clades as text, for group cards
            public List<string> founders;
            public bool ancestor;
            public int generation;   // after the starting species
            public int more;         // descendants not shown (the view stops here)
            public VisualElement view;
            public Vector2 position;
        }

        private readonly VisualElement overlay, canvas, linksBox;
        private readonly Label subtitle, nameLabel, metaLabel;
        private readonly SpeciesTabs speciesTabs;
        private readonly Button backButton;
        private readonly Dictionary<string, Node> nodes = new();
        private readonly List<(string from, string to, EvolutionLink link)> edges = new();
        private readonly Stack<(List<string> roots, string clade)> history = new();
        private List<string> roots = new();
        private string rootClade; // the group card that was opened, if any (shown in the subtitle)
        private VisualElement lines;
        private string selected;
        private OwnedCopy context; // the copy that evolves (from a selected animal), or null

        public event Action<string> Message;
        public event Action<string> OpenEncyclopedia; // a species' entry

        public bool IsOpen => !overlay.ClassListContains("hidden");
        private static EvolutionManager Evolution => EvolutionManager.Instance;

        public ZoologyPanel(VisualElement root)
        {
            overlay          = root.Q("zoology-overlay");
            canvas           = root.Q("zoology-canvas");
            linksBox         = root.Q("zoology-links");
            subtitle         = root.Q<Label>("zoology-subtitle");
            nameLabel        = root.Q<Label>("zoology-name");
            metaLabel        = root.Q<Label>("zoology-meta");
            backButton       = root.Q<Button>("zoology-back-button");
            backButton.clicked += Back;
            root.Q<Button>("zoology-close-button").clicked += Close;
            root.Q<Button>("zoology-encyclopedia-button").clicked += () => { if (selected != null) OpenEncyclopedia?.Invoke(selected); };
            speciesTabs = new SpeciesTabs(root.Q("zoology-species-tabs"));
            speciesTabs.Picked += id =>
            {
                Evolution?.Focus(id); // the Functions / Behaviors trees follow
                context = null;
                StartFrom(id);
            };
        }

        // start: the species to start from (e.g. from the Encyclopedia), else the copy's or yours
        public void Open(OwnedCopy copy = null, string start = null)
        {
            if (Evolution == null) return;
            context = copy;
            overlay.RemoveFromClassList("hidden");
            StartFrom(start ?? copy?.species ?? Evolution.FocusSpecies ?? Evolution.HumanSpecies.FirstOrDefault() ?? selected
                    ?? EvolutionData.Links.Select(l => l.from).FirstOrDefault(id => !EvolutionData.To(id).Any()));
        }

        private void StartFrom(string id)
        {
            selected = id;
            history.Clear();
            roots = selected != null ? new List<string> { selected } : new List<string>();
            rootClade = null;
            Build();
            Refresh();
        }

        public void Close()
        {
            overlay.AddToClassList("hidden");
            context = null;
        }

        // Start the view from other species (a clicked species, or a group's founders)
        private void Show(List<string> newRoots, string clade)
        {
            if (newRoots.Count == 0 || (clade == rootClade && newRoots.SequenceEqual(roots))) return;
            history.Push((roots, rootClade));
            roots = newRoots;
            rootClade = clade;
            selected = newRoots[0];
            Build();
            Refresh();
        }

        private void Back()
        {
            if (history.Count == 0) return;
            (roots, rootClade) = history.Pop();
            if (roots.Count > 0) selected = roots[0];
            Build();
            Refresh();
        }

        // ---------- Groups ----------

        private static HashSet<string> TagsOf(string id) => new(EvolutionData.TagsOf(GameDataLoader.GetSpecies(id)));

        // The first major group `child` belongs to and `parent` doesn't, or -1
        private static int NewClade(string parent, string child)
        {
            var had = TagsOf(parent);
            var has = TagsOf(child);
            for (int i = 0; i < Clades.Length; i++)
                if (has.Contains(Clades[i].tag) && !had.Contains(Clades[i].tag)) return i;
            return -1;
        }

        // How many species there are in the trees of these founders (them included)
        private static int CountFrom(IEnumerable<string> founders)
        {
            var seen = new HashSet<string>();
            var todo = new Stack<string>(founders);
            while (todo.Count > 0)
            {
                var id = todo.Pop();
                if (!seen.Add(id)) continue;
                foreach (var l in EvolutionData.From(id)) todo.Push(l.to);
            }
            return seen.Count;
        }

        // ---------- Layout ----------

        private void Build()
        {
            canvas.Clear();
            backButton.SetEnabled(history.Count > 0);

            // Laid out with MaxGenerations, then with one fewer each time while the tree is too tall
            // to see without dragging (down to 1: what the starting species become directly)
            List<string> parents = null;
            Dictionary<string, float> row = null;
            for (int generations = MaxGenerations; ; generations--)
            {
                nodes.Clear();
                edges.Clear();

                // the starting species, then what they become: species of their own group are expanded,
                // the first species of a new group collapse into that group's card. What the starting
                // species become directly is always shown; when that starts a new group, its own
                // descendants are the group's card after it.
                var queue = new Queue<string>();
                foreach (var id in roots.Where(id => GameDataLoader.GetSpecies(id) != null))
                {
                    if (nodes.ContainsKey(id)) continue;
                    nodes[id] = new Node { key = id, species = id };
                    queue.Enqueue(id);
                }
                while (queue.Count > 0)
                {
                    var id = queue.Dequeue();
                    bool isRoot = roots.Contains(id);
                    int founded = isRoot ? -1 : EvolutionData.To(id).Where(l => roots.Contains(l.from)).Select(l => NewClade(l.from, id)).DefaultIfEmpty(-1).Max();
                    if (founded >= 0)
                    {
                        if (!EvolutionData.From(id).Any()) continue;
                        var cardKey = $"clade:{founded}:{id}";
                        if (!nodes.TryGetValue(cardKey, out var card))
                            nodes[cardKey] = card = new Node { key = cardKey, clade = founded.ToString(), founders = new List<string>() };
                        if (!card.founders.Contains(id)) card.founders.Add(id);
                        card.generation = nodes[id].generation + 1;
                        edges.Add((id, cardKey, null));
                        continue;
                    }
                    // far enough: the rest of this lineage is a click away
                    if (nodes[id].generation >= generations)
                    {
                        nodes[id].more = CountFrom(new[] { id }) - 1;
                        continue;
                    }
                    foreach (var link in EvolutionData.From(id))
                    {
                        if (GameDataLoader.GetSpecies(link.to) == null) continue;
                        int clade = isRoot || nodes.ContainsKey(link.to) ? -1 : NewClade(id, link.to);
                        if (clade < 0)
                        {
                            if (!nodes.ContainsKey(link.to))
                            {
                                nodes[link.to] = new Node { key = link.to, species = link.to, generation = nodes[id].generation + 1 };
                                queue.Enqueue(link.to);
                            }
                            edges.Add((id, link.to, link));
                            continue;
                        }
                        var key = $"clade:{clade}:{id}";
                        if (!nodes.TryGetValue(key, out var group))
                            nodes[key] = group = new Node { key = key, clade = clade.ToString(), founders = new List<string>() };
                        if (!group.founders.Contains(link.to)) group.founders.Add(link.to);
                        if (!edges.Contains((id, key, null))) edges.Add((id, key, null));
                        group.generation = nodes[id].generation + 1;
                    }
                }

                // where the starting species come from, faded in a column on the left
                parents = roots.SelectMany(id => EvolutionData.To(id)).Select(l => l.from).Distinct()
                                   .Where(id => !nodes.ContainsKey(id) && GameDataLoader.GetSpecies(id) != null).ToList();

                // a tidy tree: leaves take the next free row, each species sits centred on its children,
                // and a lineage with descendants keeps a gap from its neighbours
                var children = new Dictionary<string, List<string>>();
                foreach (var (from, to, _) in edges)
                {
                    if (!children.TryGetValue(from, out var list)) children[from] = list = new List<string>();
                    if (!list.Contains(to)) list.Add(to);
                }
                foreach (var list in children.Values)
                    list.Sort((x, y) => SortKey(x).CompareTo(SortKey(y)));
                row = new Dictionary<string, float>();
                float next = 0f;
                bool lastWasLineage = false;
                void Place(string key)
                {
                    if (row.ContainsKey(key)) return;
                    row[key] = -1f; // being placed
                    var kids = children.TryGetValue(key, out var k) ? k.Where(c => !row.ContainsKey(c)).ToList() : new List<string>();
                    if (kids.Count == 0)
                    {
                        if (lastWasLineage) next += LineageGap;
                        row[key] = next++;
                        lastWasLineage = false;
                        return;
                    }
                    if (next > 0f) next += LineageGap; // a lineage starts: keep it apart from what's above
                    foreach (var c in kids) Place(c);
                    row[key] = (row[kids[0]] + row[kids[kids.Count - 1]]) * 0.5f;
                    lastWasLineage = true;
                }
                foreach (var id in roots) if (nodes.ContainsKey(id)) Place(id);
                if (generations <= 1 || row.Values.DefaultIfEmpty(0f).Max() <= MaxRows) break;
            }

            int shift = parents.Count > 0 ? 1 : 0;
            int maxGen = nodes.Values.Select(n => n.generation).DefaultIfEmpty(0).Max();
            float rootRow = roots.Where(row.ContainsKey).Select(r => row[r]).DefaultIfEmpty(0f).Average();
            foreach (var id in parents)
            {
                nodes[id] = new Node { key = id, species = id, ancestor = true, generation = -1 };
                row[id] = rootRow;
                foreach (var l in EvolutionData.From(id)) if (roots.Contains(l.to)) edges.Add((id, l.to, l));
            }
            foreach (var node in nodes.Values)
                node.position = new Vector2(Padding + (node.generation + shift) * ColumnWidth,
                                            Padding + (row.TryGetValue(node.key, out var r) ? Mathf.Max(0f, r) : 0f) * RowHeight);
            float rows = row.Values.DefaultIfEmpty(0f).Max();
            canvas.style.width  = Padding * 2 + (maxGen + shift) * ColumnWidth + NodeWidth;
            canvas.style.height = Padding * 2 + rows * RowHeight + NodeHeight;

            lines = new VisualElement { pickingMode = PickingMode.Ignore };
            lines.AddToClassList("tree-lines");
            lines.generateVisualContent += DrawLines;
            canvas.Add(lines);

            foreach (var node in nodes.Values)
            {
                var view = new VisualElement().WithClass("zoology-node");
                view.style.left = node.position.x;
                view.style.top  = node.position.y;
                var pic = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("species-portrait").WithClass("zoology-node-portrait");
                view.Add(pic);
                var text = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("zoology-node-text");
                view.Add(text);
                var face = GameDataLoader.GetSpecies(node.species ?? node.founders[0]);
                if (SpeciesPortraits.Get(face) is RenderTexture rt) pic.style.backgroundImage = Background.FromRenderTexture(rt);
                if (node.clade != null)
                {
                    // a group card: its name, and how many species its tree holds
                    view.AddToClassList("zoology-clade");
                    text.Add(new Label(Loc.T(Clades[int.Parse(node.clade)].name)) { pickingMode = PickingMode.Ignore }.WithClass("node-name"));
                    int n = CountFrom(node.founders);
                    text.Add(new Label(Loc.F("{0} species ▸", n)) { pickingMode = PickingMode.Ignore }.WithClass("node-cost"));
                    var founders = node.founders;
                    var clade = node.clade;
                    view.RegisterCallback<ClickEvent>(_ => Show(new List<string>(founders), clade));
                }
                else
                {
                    if (node.ancestor) view.AddToClassList("ancestor");
                    text.Add(new Label(Loc.T(face.commonName)) { pickingMode = PickingMode.Ignore }.WithClass("node-name"));
                    text.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("node-cost"));
                    if (node.more > 0) // the view stops here: its lineage goes on
                    {
                        view.AddToClassList("zoology-more");
                        text.Add(new Label(Loc.F("{0} more species ▸", node.more)) { pickingMode = PickingMode.Ignore }.WithClass("node-more"));
                    }
                    var id = node.species;
                    view.RegisterCallback<ClickEvent>(e =>
                    {
                        if (roots.Count == 1 && roots[0] == id)
                        {
                            selected = id;
                            if (e.clickCount == 2) OpenEncyclopedia?.Invoke(id); // its entry
                            else Refresh();
                        }
                        else Show(new List<string> { id }, null);
                    });
                }
                canvas.Add(view);
                node.view = view;
            }
        }

        // siblings in order of appearance, group cards last
        private (int, int, string) SortKey(string key) =>
            nodes.TryGetValue(key, out var n) && n.species != null ? (0, AgeIndex(n.species), key) : (1, 0, key);

        private static int AgeIndex(string id) =>
            Enum.TryParse(GameDataLoader.GetSpecies(id)?.firstAge, true, out GeologicalAge a) ? (int)a : 0;

        private void DrawLines(MeshGenerationContext ctx)
        {
            var p = ctx.painter2D;
            p.lineWidth = 3f;
            p.lineCap   = LineCap.Round;
            foreach (var (fromKey, toKey, link) in edges)
            {
                if (!nodes.TryGetValue(fromKey, out var a) || !nodes.TryGetValue(toKey, out var b)) continue;
                var from = a.position + new Vector2(NodeWidth, NodeHeight * 0.5f);
                var to   = b.position + new Vector2(0f, NodeHeight * 0.5f);
                p.strokeColor = link == null ? LineOther : Evolution.HasEvolved(link) ? LineUsed : ReadyFor(link) != null ? LineReady : LineOther;
                // a fork: out of the origin, along a trunk in the gap between the columns shared by
                // all its descendants, then across into each of them, with rounded corners
                float trunk = from.x + (to.x - from.x) * 0.5f;
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
            var status = context != null
                ? Loc.F("Evolving one {0}", Loc.T(GameDataLoader.GetSpecies(context.species)?.commonName))
                : Loc.F(ready == 1 ? "{0} of your species  ·  {1} evolution ready" : "{0} of your species  ·  {1} evolutions ready", owned.Count, ready);
            subtitle.text = rootClade != null ? $"{Loc.T(Clades[int.Parse(rootClade)].name)}  ·  {status}" : status;
            speciesTabs.Refresh(roots.Count == 1 ? roots[0] : null);

            foreach (var node in nodes.Values)
            {
                if (node.species == null) continue; // group cards don't change
                var id = node.species;
                bool canBecome = EvolutionData.To(id).Any(l => ReadyFor(l) != null);
                node.view.EnableInClassList("owned",    owned.Contains(id));
                node.view.EnableInClassList("ready",    canBecome);
                node.view.EnableInClassList("selected", id == selected);
                var def = GameDataLoader.GetSpecies(id);
                // a direct descendant that starts a major group says so
                int clade = node.ancestor ? -1 : EvolutionData.To(id).Where(l => roots.Contains(l.from)).Select(l => NewClade(l.from, id)).DefaultIfEmpty(-1).Max();
                var state = Loc.T(owned.Contains(id) ? "Yours" : canBecome ? "Can evolve" : def.firstAge);
                node.view.Q<Label>(className: "node-cost").text = clade >= 0 ? $"{state} · {Loc.T(Clades[clade].name)}" : state;
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
                nameLabel.text = Loc.T("Select a species");
                metaLabel.text = "";
                return;
            }

            nameLabel.text = Loc.T(def.commonName);
            var span = string.IsNullOrEmpty(def.lastAge) ? Loc.F("{0} – today", Loc.T(def.firstAge)) : def.firstAge == def.lastAge ? Loc.T(def.firstAge) : $"{Loc.T(def.firstAge)} – {Loc.T(def.lastAge)}";
            var count = Evolution.CopiesOf(Players.PlayerManager.Instance?.Human).Count(c => c.species == def.id);
            metaLabel.text = $"{def.scientificName}  ·  {Loc.T(def.group)}  ·  {span}" + (count > 0 ? "\n" + Loc.F(count == 1 ? "You have {0} copy" : "You have {0} copies", count) : "");

            var parents = EvolutionData.To(def.id).Select(l => Loc.T(GameDataLoader.GetSpecies(l.from)?.commonName ?? l.from)).ToList();
            if (parents.Count > 0) linksBox.Add(new Label(Loc.F("Evolves from: {0}", string.Join(", ", parents))).WithClass("zoology-from"));

            var outgoing = EvolutionData.From(def.id).ToList();
            if (outgoing.Count == 0) { linksBox.Add(new Label(Loc.T("No known descendants among the game's species.")).WithClass("zoology-from")); return; }
            linksBox.Add(new Label(Loc.T("Can evolve into")).WithClass("age-section"));
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
            var title = new Label(Loc.T(target?.commonName ?? link.to)).WithClass("zoology-link-name");
            title.RegisterCallback<ClickEvent>(_ => Show(new List<string> { link.to }, null));
            head.Add(title);
            card.Add(head);
            if (!string.IsNullOrEmpty(link.description)) card.Add(new Label(Loc.T(link.description)).WithClass("zoology-link-text"));

            // The copy this card is about: the one being evolved, else one of yours that is ready
            var copy = context != null ? (context.species == link.from ? context : null) : ReadyFor(link);
            foreach (var r in Evolution.Requirements(link, copy))
                card.Add(new Label((r.met ? "✓  " : "✗  ") + r.text).WithClass("zoology-req").WithClass(r.met ? "met" : "unmet"));

            var grants = link.grantFunctions.Select(id => ProgressionNodeName(true, id))
                .Concat(link.grantBehaviors.Select(id => ProgressionNodeName(false, id))).ToList();
            if (grants.Count > 0) card.Add(new Label(Loc.F("Gains on evolving: {0}", string.Join(", ", grants))).WithClass("zoology-link-text"));

            bool can = copy != null && Evolution.CanEvolve(link, copy);
            var button = new Button(() => DoEvolve(link, copy)) { text = can ? Loc.F("Evolve into {0}", Loc.T(target?.commonName)) : Loc.T("Evolve") }.WithClass("evolve-button").WithClass("zoology-evolve");
            button.SetEnabled(can);
            if (Evolution.HasEvolved(link)) button.text = Loc.T("Already evolved by another copy");
            card.Add(button);
            return card;
        }

        private static string ProgressionNodeName(bool function, string id)
        {
            var p = Progression.ProgressionManager.Instance;
            var tree = p == null ? null : function ? p.Morphology : p.Ethology;
            return Loc.T(tree?.Get(id)?.displayName ?? id);
        }

        private void DoEvolve(EvolutionLink link, OwnedCopy copy)
        {
            if (copy == null) return;
            Evolution.Evolve(link, copy, out var message);
            if (message != null) Message?.Invoke(message);
            if (context == copy) context = null; // that copy is now the new species
            Show(new List<string> { link.to }, null);
            Refresh();
        }
    }
}
