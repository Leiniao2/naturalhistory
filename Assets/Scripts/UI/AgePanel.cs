using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Climate;
using NaturalHistory.Core;
using NaturalHistory.Data;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Geologic timeline: every period of the Phanerozoic on the left (past / current / future),
    // details of the selected one on the right. Opens automatically when a new period begins.
    public class AgePanel
    {
        private readonly VisualElement overlay, list, climate;
        private readonly Label title, ageName, range, description, events, environment;
        private readonly List<VisualElement> rows = new();
        private int selectedIndex;
        private string listLanguage; // the list is built again after the language changes

        private static readonly Dictionary<string, Color> EraColors = new()
        {
            ["Neoproterozoic"] = new Color(0.62f, 0.45f, 0.60f),
            ["Paleozoic"] = new Color(0.36f, 0.60f, 0.62f),
            ["Mesozoic"]  = new Color(0.40f, 0.66f, 0.36f),
            ["Cenozoic"]  = new Color(0.90f, 0.75f, 0.30f),
        };

        public bool IsOpen => !overlay.ClassListContains("hidden");

        public AgePanel(VisualElement root)
        {
            overlay     = root.Q("age-overlay");
            list        = root.Q("age-list");
            climate     = root.Q("age-climate"); // world climate now (ClimateHud fills it)
            title       = root.Q<Label>("age-panel-title");
            ageName     = root.Q<Label>("age-name");
            range       = root.Q<Label>("age-range");
            description = root.Q<Label>("age-description");
            events      = root.Q<Label>("age-events");
            environment = root.Q<Label>("age-environment");
            root.Q<Button>("age-close-button").clicked += Close;
        }

        public void Open(bool newAge = false)
        {
            var ages = AgeManager.Instance;
            if (ages == null || ages.Ages.Count == 0) return;
            if (rows.Count == 0 || listLanguage != Loc.Current) BuildList();
            title.text = newAge ? Loc.F("A new period begins: the {0}", Loc.T(ages.CurrentAgeData.displayName)) : Loc.T("Geologic Time");
            selectedIndex = (int)ages.CurrentAge;
            overlay.RemoveFromClassList("hidden");
            Refresh();
        }

        public void Close() => overlay.AddToClassList("hidden");

        public void Refresh()
        {
            var ages = AgeManager.Instance;
            if (ages == null || rows.Count == 0) return;
            if (listLanguage != Loc.Current) BuildList();
            int current = (int)ages.CurrentAge;
            for (int i = 0; i < rows.Count; i++)
            {
                rows[i].EnableInClassList("past",     i < current);
                rows[i].EnableInClassList("current",  i == current);
                rows[i].EnableInClassList("future",   i > current);
                rows[i].EnableInClassList("selected", i == selectedIndex);
            }
            ShowDetails(ages.Ages[selectedIndex], selectedIndex == current);
        }

        private void BuildList()
        {
            var ages = AgeManager.Instance.Ages;
            list.Clear();
            rows.Clear();
            listLanguage = Loc.Current;
            for (int i = 0; i < ages.Count; i++)
            {
                var def = ages[i];
                var row = new VisualElement().WithClass("age-row");
                row.style.borderLeftColor = EraColors.TryGetValue(def.era ?? "", out var c) ? c : Color.gray;
                row.Add(new Label(Loc.T(def.displayName)) { pickingMode = PickingMode.Ignore }.WithClass("age-row-name"));
                row.Add(new Label(Loc.F("{0} · {1:0.#}–{2:0.#} Ma", Loc.T(def.era), def.startMillionYearsAgo, def.endMillionYearsAgo)) { pickingMode = PickingMode.Ignore }
                    .WithClass("age-row-range"));
                int index = i;
                row.RegisterCallback<ClickEvent>(_ => { selectedIndex = index; Refresh(); });
                list.Add(row);
                rows.Add(row);
            }
        }

        private void ShowDetails(AgeDefinition def, bool isCurrent)
        {
            var ages = AgeManager.Instance;
            ageName.text = Loc.T(def.displayName);
            var span = def.startMillionYearsAgo - def.endMillionYearsAgo;
            var r = Loc.F("{0} Era · {1:0.##} – {2:0.##} million years ago ({3:0.#} My) · {4} turns",
                          Loc.T(def.era), def.startMillionYearsAgo, def.endMillionYearsAgo, span, ages.TurnsOf(selectedIndex));
            if (isCurrent) r += "\n" + Loc.F("Now: {0:0.0} Ma, turn {1} of {2} in this period", ages.MillionYearsAgo, ages.TurnInAge, ages.TurnsInAge);
            range.text = r;
            climate.EnableInClassList("hidden", !isCurrent);
            description.text = Loc.T(def.description);
            events.text = def.keyEvents != null ? string.Join("\n", def.keyEvents.Select(e => "• " + Loc.T(e))) : "";

            // Reconstructed global averages at the start of the period (climate_history.json)
            var start = ClimateSystem.SampleHistory(def.startMillionYearsAgo);
            var env = def.environmentalConditions;
            var lines = new List<string>();
            if (env != null)
            {
                lines.Add(Loc.F("Climate: {0}", Loc.T(env.globalTemp)));
                lines.Add(Loc.F("Sea level: {0}", Loc.T(env.seaLevel)));
                lines.Add(Loc.F("Oxygen: {0}", Loc.T(env.oxygenLevel)));
                lines.Add(Loc.F("Continents: {0}", Loc.T(env.landCoverage)));
            }
            if (!string.IsNullOrEmpty(def.vegetation)) lines.Add(Loc.F("Plants: {0}", Loc.T(def.vegetation)));
            lines.Add(Loc.F("At the start: ~{0:0} °C global mean · CO2 ~{1:0} ppm · O2 ~{2:0.#}% · sea level {3:+0;-0;0} m",
                            start.TemperatureC, start.Co2Ppm, start.O2Percent, start.SeaLevelM));
            environment.text = string.Join("\n", lines);
        }
    }
}
