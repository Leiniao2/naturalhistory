using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Every species of the game (species.json), from the pause menu or the Evolution Tree, sorted by
    // period: the periods down the left (each with the species alive in it, and All), then that
    // period's species, oldest first, with a search box over names; the entry on the right shows the
    // species' painting (SpeciesPortraits.Painting), names, period, group, diet, size and habitats,
    // its description, and the species it evolves from and into (click one to go there). A button
    // opens the Evolution Tree from the species.
    public class EncyclopediaPanel
    {
        private readonly VisualElement overlay, painting, relatives;
        private readonly ScrollView periods;
        private int period = -1; // GeologicalAge shown, -1 = all; the game's current period when first opened
        private bool openedOnce;
        private bool periodsCollapsed; // the period column folded to a thin strip, for a wider list
        private readonly ListView list;
        private readonly TextField search;
        private readonly Label count, nameLabel, scientificLabel, statsLabel, descriptionLabel;
        private readonly List<SpeciesDefinition> shown = new();
        private List<SpeciesDefinition> all;
        private SpeciesDefinition current;

        public event Action<string> OpenTree; // the Evolution Tree from this species

        public bool IsOpen => !overlay.ClassListContains("hidden");

        public EncyclopediaPanel(VisualElement root)
        {
            overlay          = root.Q("encyclopedia-overlay");
            painting         = root.Q("encyclopedia-painting");
            relatives        = root.Q("encyclopedia-relatives");
            periods          = root.Q<ScrollView>("encyclopedia-periods");
            list             = root.Q<ListView>("encyclopedia-list");
            search           = root.Q<TextField>("encyclopedia-search");
            count            = root.Q<Label>("encyclopedia-count");
            nameLabel        = root.Q<Label>("encyclopedia-name");
            scientificLabel  = root.Q<Label>("encyclopedia-scientific");
            statsLabel       = root.Q<Label>("encyclopedia-stats");
            descriptionLabel = root.Q<Label>("encyclopedia-description");

            root.Q<Button>("encyclopedia-close-button").clicked += Close;
            root.Q<Button>("encyclopedia-tree-button").clicked += () => { if (current != null) OpenTree?.Invoke(current.id); };

            list.fixedItemHeight = 58f;
            list.selectionType   = SelectionType.Single;
            list.itemsSource     = shown;
            list.makeItem        = MakeRow;
            list.bindItem        = BindRow;
            list.selectionChanged += picked =>
            {
                var def = picked.OfType<SpeciesDefinition>().FirstOrDefault();
                if (def != null && def != current) Show(def);
            };
            search.RegisterValueChangedCallback(_ => Filter());
            Loc.Changed += () => { all = null; if (IsOpen) { Filter(); Show(current); } };
        }

        // speciesId: the entry to show, else the last one (or the first species)
        public void Open(string speciesId = null)
        {
            search.textEdition.placeholder = Loc.T("Search");
            overlay.RemoveFromClassList("hidden");
            var def = speciesId != null ? GameDataLoader.GetSpecies(speciesId) : current;
            if (!openedOnce && AgeManager.Instance != null) period = (int)AgeManager.Instance.CurrentAge;
            openedOnce = true;
            if (def != null && !InPeriod(def)) period = AgeIndex(def.firstAge);
            if (def != null && !Matches(def)) search.SetValueWithoutNotify("");
            Filter();
            Select(def ?? shown.FirstOrDefault());
        }

        public void Close() => overlay.AddToClassList("hidden");

        // ---------- List ----------

        private static int AgeIndex(string age) => Enum.TryParse(age, true, out GeologicalAge a) ? (int)a : 0;

        private List<SpeciesDefinition> All => all ??= GameDataLoader.Species
            .OrderBy(s => AgeIndex(s.firstAge)).ThenBy(s => Loc.T(s.commonName), StringComparer.CurrentCultureIgnoreCase).ToList();

        private bool Matches(SpeciesDefinition def)
        {
            var q = search.value?.Trim();
            if (string.IsNullOrEmpty(q)) return true;
            return Loc.T(def.commonName).IndexOf(q, StringComparison.CurrentCultureIgnoreCase) >= 0
                || (def.commonName ?? "").IndexOf(q, StringComparison.OrdinalIgnoreCase) >= 0
                || (def.scientificName ?? "").IndexOf(q, StringComparison.OrdinalIgnoreCase) >= 0
                || Loc.T(def.group ?? "").IndexOf(q, StringComparison.CurrentCultureIgnoreCase) >= 0;
        }

        private static int LastIndex(SpeciesDefinition def) =>
            string.IsNullOrEmpty(def.lastAge) ? (int)GeologicalAge.Quaternary : AgeIndex(def.lastAge);

        // Alive in the period shown: it appears in it or before, and is not gone before it
        private static bool AliveIn(SpeciesDefinition def, int age) => AgeIndex(def.firstAge) <= age && age <= LastIndex(def);
        private bool InPeriod(SpeciesDefinition def) => period < 0 || AliveIn(def, period);

        private void Filter()
        {
            shown.Clear();
            shown.AddRange(All.Where(d => InPeriod(d) && Matches(d)));
            count.text = Loc.F("{0} species", shown.Count);
            BuildPeriods();
            list.RefreshItems();
            int i = current != null ? shown.IndexOf(current) : -1;
            if (i >= 0) list.SetSelectionWithoutNotify(new[] { i });
            else list.ClearSelection();
        }

        // A fold button, then All and one button per period with how many of its species match the
        // search. Folded, only the button is left (the list keeps the period it shows).
        private void BuildPeriods()
        {
            periods.Clear();
            periods.EnableInClassList("collapsed", periodsCollapsed);
            var fold = new Button(() => { periodsCollapsed = !periodsCollapsed; BuildPeriods(); })
                { text = periodsCollapsed ? "▶" : "◀", tooltip = Loc.T("Periods") }.WithClass("encyclopedia-period-fold");
            periods.Add(fold);
            if (periodsCollapsed) return;
            var matching = All.Where(Matches).ToList();
            AddPeriod(-1, Loc.T("All periods"), matching.Count);
            foreach (GeologicalAge age in Enum.GetValues(typeof(GeologicalAge)))
                AddPeriod((int)age, Loc.T(age.ToString()), matching.Count(d => AliveIn(d, (int)age)));
        }

        private void AddPeriod(int age, string label, int n)
        {
            var button = new Button(() => SetPeriod(age)).WithClass("encyclopedia-period");
            button.Add(new Label(label) { pickingMode = PickingMode.Ignore });
            button.Add(new Label(n.ToString()) { pickingMode = PickingMode.Ignore }.WithClass("encyclopedia-period-count"));
            button.EnableInClassList("selected", age == period);
            button.EnableInClassList("empty", n == 0);
            periods.Add(button);
        }

        private void SetPeriod(int age)
        {
            if (age == period) return;
            period = age;
            Filter();
            Select(current != null && shown.Contains(current) ? current : shown.FirstOrDefault());
        }

        private void Select(SpeciesDefinition def)
        {
            if (def == null) { Show(null); return; }
            if (!InPeriod(def)) { period = AgeIndex(def.firstAge); Filter(); }
            if (!shown.Contains(def)) { search.SetValueWithoutNotify(""); Filter(); }
            int i = shown.IndexOf(def);
            Show(def);
            list.SetSelectionWithoutNotify(new[] { i });
            list.ScrollToItem(i);
        }

        private static VisualElement MakeRow()
        {
            var row = new VisualElement().WithClass("encyclopedia-row");
            row.Add(new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("encyclopedia-thumb"));
            var text = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("encyclopedia-row-text");
            text.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("encyclopedia-row-name"));
            text.Add(new Label { pickingMode = PickingMode.Ignore }.WithClass("encyclopedia-row-age"));
            row.Add(text);
            return row;
        }

        private void BindRow(VisualElement row, int index)
        {
            if (index < 0 || index >= shown.Count) return;
            var def = shown[index];
            row.Q(className: "encyclopedia-thumb").style.backgroundImage = Picture(def);
            row.Q<Label>(className: "encyclopedia-row-name").text = Loc.T(def.commonName);
            bool yours = EvolutionManager.Instance != null && EvolutionManager.Instance.HumanOwns(def.id);
            row.Q<Label>(className: "encyclopedia-row-age").text = Span(def) + (yours ? "  ·  " + Loc.T("Yours") : "");
            row.EnableInClassList("owned", yours);
        }

        private static StyleBackground Picture(SpeciesDefinition def)
        {
            var tex = SpeciesPortraits.Painting(def);
            if (tex != null) return Background.FromTexture2D(tex);
            return SpeciesPortraits.Get(def) is UnityEngine.RenderTexture rt ? Background.FromRenderTexture(rt) : new StyleBackground(StyleKeyword.None);
        }

        private static string Span(SpeciesDefinition def) =>
            string.IsNullOrEmpty(def.lastAge) ? Loc.F("{0} – today", Loc.T(def.firstAge))
            : def.firstAge == def.lastAge ? Loc.T(def.firstAge) : $"{Loc.T(def.firstAge)} – {Loc.T(def.lastAge)}";

        // ---------- Entry ----------

        private void Show(SpeciesDefinition def)
        {
            current = def;
            relatives.Clear();
            if (def == null)
            {
                nameLabel.text = scientificLabel.text = statsLabel.text = descriptionLabel.text = "";
                painting.style.backgroundImage = new StyleBackground(StyleKeyword.None);
                return;
            }

            painting.style.backgroundImage = Picture(def);
            painting.EnableInClassList("model-only", SpeciesPortraits.Painting(def) == null);
            nameLabel.text       = Loc.T(def.commonName);
            scientificLabel.text = def.scientificName ?? "";

            var lines = new List<string> { Loc.T(def.group), Span(def) };
            if (!string.IsNullOrEmpty(def.diet)) lines.Add(Loc.F("Diet: {0}", Loc.T(def.diet)));
            lines.Add(World.Diets.Describe(def));
            if (def.sizeCm > 0f) lines.Add(Loc.F("Size: {0}", AnimalPanel.FormatSize(def.sizeCm)));
            if (def.habitats is { Count: > 0 })
                lines.Add(Loc.F("Habitats: {0}", string.Join(", ", def.habitats.Select(AnimalPanel.HabitatName))));
            var stats = World.CombatStats.Of(def);
            lines.Add(Loc.F("HP {0}  ·  Attack {1}  ·  Defense {2}  ·  Actions {3}", stats.hp, stats.attack, stats.defense, stats.moves));
            var copies = EvolutionManager.Instance?.CopiesOf(Players.PlayerManager.Instance?.Human).Count(c => c.species == def.id) ?? 0;
            if (copies > 0) lines.Add(Loc.F(copies == 1 ? "You have {0} copy" : "You have {0} copies", copies));
            var abilities = World.Abilities.Describe(def, EvolutionManager.Instance != null && EvolutionManager.Instance.HumanOwns(def.id));
            if (abilities.Length > 0) lines.Add(abilities);
            statsLabel.text       = string.Join("\n", lines);
            descriptionLabel.text = Loc.T(def.description);

            AddRelatives(Loc.T("Evolves from"), EvolutionData.To(def.id).Select(l => l.from));
            AddRelatives(Loc.T("Can evolve into"), EvolutionData.From(def.id).Select(l => l.to));
        }

        private void AddRelatives(string heading, IEnumerable<string> ids)
        {
            var defs = ids.Distinct().Select(GameDataLoader.GetSpecies).Where(d => d != null).ToList();
            if (defs.Count == 0) return;
            relatives.Add(new Label(heading).WithClass("age-section"));
            var row = new VisualElement().WithClass("encyclopedia-chips");
            foreach (var d in defs)
            {
                var target = d;
                var chip = new Button(() => Select(target)).WithClass("encyclopedia-chip");
                chip.Add(new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("encyclopedia-chip-thumb"));
                chip.Q(className: "encyclopedia-chip-thumb").style.backgroundImage = Picture(d);
                chip.Add(new Label(Loc.T(d.commonName)) { pickingMode = PickingMode.Ignore }.WithClass("encyclopedia-chip-name"));
                row.Add(chip);
            }
            relatives.Add(row);
        }
    }
}
