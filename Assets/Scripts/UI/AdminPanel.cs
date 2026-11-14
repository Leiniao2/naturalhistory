using System.Collections.Generic;
using NaturalHistory.Core;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Admin tools under the top-right HUD: pick any geological period (or the present day) and the
    // game jumps to its first turn; the map, plants and climate follow. Visible in the Editor and in
    // development builds; the backquote key (`) shows or hides it.
    public class AdminPanel
    {
        private const string PresentDay = "Present day";

        private readonly VisualElement bar;
        private readonly DropdownField ageField;
        private readonly List<int> turns = new(); // first turn of each dropdown entry

        public AdminPanel(VisualElement root)
        {
            bar      = root.Q("admin-bar");
            ageField = root.Q<DropdownField>("admin-age");
            ageField.RegisterValueChangedCallback(_ => OnAgePicked());
            bar.EnableInClassList("hidden", !Debug.isDebugBuild);
        }

        public static bool Available => Debug.isDebugBuild;

        public void Toggle()
        {
            if (Available) bar.ToggleInClassList("hidden");
        }

        // Called whenever the date changes, so the dropdown shows the current period.
        public void Refresh()
        {
            var ages = AgeManager.Instance;
            if (ages == null || ages.Ages.Count == 0) { ageField.SetEnabled(false); return; }
            ageField.SetEnabled(true);
            if (turns.Count == 0)
            {
                var names = new List<string>();
                for (int i = 0; i < ages.Ages.Count; i++)
                {
                    var def = ages.Ages[i];
                    names.Add($"{def.displayName}  ({def.startMillionYearsAgo:0.#} Ma)");
                    turns.Add(ages.FirstTurnOf((GeologicalAge)i));
                }
                names.Add(PresentDay);
                turns.Add(ages.TotalTurns + 1);
                ageField.choices = names;
            }
            int index = ages.IsPresentDay ? turns.Count - 1 : (int)ages.CurrentAge;
            ageField.SetValueWithoutNotify(ageField.choices[index]);
        }

        private void OnAgePicked()
        {
            int index = ageField.index;
            if (index < 0 || index >= turns.Count || AgeManager.Instance == null) return;
            Debug.Log($"[Admin] Jump to {ageField.value} (turn {turns[index]})");
            AgeManager.Instance.JumpToTurn(turns[index]);
        }
    }
}
