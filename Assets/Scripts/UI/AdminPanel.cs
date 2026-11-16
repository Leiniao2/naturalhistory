using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.World;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Admin tools under the top-right HUD: pick any geological period (or the present day) and the
    // game jumps to its first turn; the map, plants and climate follow. Visible in the Editor and in
    // development builds; the backquote key (`) shows or hides it. It can also set off any natural
    // phenomenon (meteor, eruption, tornado...) near the middle of the view.
    public class AdminPanel
    {
        private const string PresentDay = "Present day";

        private readonly VisualElement bar;
        private readonly DropdownField ageField;
        private readonly List<int> turns = new(); // first turn of each dropdown entry
        private readonly DropdownField phenomenon;
        private readonly Button trigger;

        public AdminPanel(VisualElement root)
        {
            bar      = root.Q("admin-bar");
            ageField = root.Q<DropdownField>("admin-age");
            ageField.RegisterValueChangedCallback(_ => OnAgePicked());

            phenomenon = new DropdownField(new List<string>(), 0) { name = "admin-phenomenon" };
            trigger    = new Button(() => NaturalEvents.Instance?.Trigger((Phenomenon)phenomenon.index)) { name = "admin-trigger" };
            bar.Add(phenomenon);
            bar.Add(trigger);
            RefreshPhenomena();
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
            // Names are filled in every time so they follow the language
            var names = new List<string>();
            turns.Clear();
            for (int i = 0; i < ages.Ages.Count; i++)
            {
                var def = ages.Ages[i];
                names.Add(Loc.F("{0}  ({1:0.#} Ma)", Loc.T(def.displayName), def.startMillionYearsAgo));
                turns.Add(ages.FirstTurnOf((GeologicalAge)i));
            }
            names.Add(Loc.T(PresentDay));
            turns.Add(ages.TotalTurns + 1);
            ageField.choices = names;
            RefreshPhenomena();
            int index = ages.IsPresentDay ? turns.Count - 1 : (int)ages.CurrentAge;
            ageField.SetValueWithoutNotify(ageField.choices[index]);
        }

        private void RefreshPhenomena()
        {
            int index = Mathf.Max(phenomenon.index, 0);
            var names = new List<string>();
            foreach (var n in NaturalEvents.Names) names.Add(Loc.T(n));
            phenomenon.choices = names;
            if (index < names.Count) phenomenon.SetValueWithoutNotify(names[index]);
            trigger.text = Loc.T("Trigger");
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
