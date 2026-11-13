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
        private readonly VisualElement overlay, list;
        private readonly Label title, ageName, range, description, events, environment;
        private readonly List<VisualElement> rows = new();
        private int selectedIndex;

        private static readonly Dictionary<string, Color> EraColors = new()
        {
            ["Paleozoic"] = new Color(0.36f, 0.60f, 0.62f),
            ["Mesozoic"]  = new Color(0.40f, 0.66f, 0.36f),
            ["Cenozoic"]  = new Color(0.90f, 0.75f, 0.30f),
        };

        public bool IsOpen => !overlay.ClassListContains("hidden");

        public AgePanel(VisualElement root)
        {
            overlay     = root.Q("age-overlay");
            list        = root.Q("age-list");
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
            if (rows.Count == 0) BuildList();
            title.text = newAge ? $"A new period begins: the {ages.CurrentAgeData.displayName}" : "Geologic Time";
            selectedIndex = (int)ages.CurrentAge;
            overlay.RemoveFromClassList("hidden");
            Refresh();
        }

        public void Close() => overlay.AddToClassList("hidden");

        public void Refresh()
        {
            var ages = AgeManager.Instance;
            if (ages == null || rows.Count == 0) return;
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
            for (int i = 0; i < ages.Count; i++)
            {
                var def = ages[i];
                var row = new VisualElement().WithClass("age-row");
                row.style.borderLeftColor = EraColors.TryGetValue(def.era ?? "", out var c) ? c : Color.gray;
                row.Add(new Label(def.displayName) { pickingMode = PickingMode.Ignore }.WithClass("age-row-name"));
                row.Add(new Label($"{def.era} · {def.startMillionYearsAgo:0.#}–{def.endMillionYearsAgo:0.#} Ma") { pickingMode = PickingMode.Ignore }
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
            ageName.text = def.displayName;
            var span = def.startMillionYearsAgo - def.endMillionYearsAgo;
            var r = $"{def.era} Era · {def.startMillionYearsAgo:0.##} – {def.endMillionYearsAgo:0.##} million years ago ({span:0.#} My) · {def.turns} turns";
            if (isCurrent) r += $"\nNow: {ages.MillionYearsAgo:0.0} Ma, turn {ages.TurnInAge} of {ages.TurnsInAge} in this period";
            range.text = r;
            description.text = def.description;
            events.text = def.keyEvents != null ? string.Join("\n", def.keyEvents.Select(e => "• " + e)) : "";

            // Reconstructed global averages at the start of the period (climate_history.json)
            var start = ClimateSystem.SampleHistory(def.startMillionYearsAgo);
            var env = def.environmentalConditions;
            var lines = new List<string>();
            if (env != null)
            {
                lines.Add($"Climate: {env.globalTemp}");
                lines.Add($"Sea level: {env.seaLevel}");
                lines.Add($"Oxygen: {env.oxygenLevel}");
                lines.Add($"Continents: {env.landCoverage}");
            }
            if (!string.IsNullOrEmpty(def.vegetation)) lines.Add($"Plants: {def.vegetation}");
            lines.Add($"At the start: ~{start.TemperatureC:0} °C global mean · CO2 ~{start.Co2Ppm:0} ppm · O2 ~{start.O2Percent:0.#}% · sea level {start.SeaLevelM:+0;-0;0} m");
            environment.text = string.Join("\n", lines);
        }
    }
}
