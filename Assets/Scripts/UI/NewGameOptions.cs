using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // The game settings on the New Game screen, under the player count: how much of the world is
    // land, how many turns the game lasts (five lengths; "Fast" is the base table), and which
    // period it starts in. Edits GameOptions.Next, which PlayerManager.StartNewGame applies.
    public class NewGameOptions
    {
        private readonly VisualElement box;
        private readonly List<Button> landButtons = new(), lengthButtons = new();
        private readonly Label landNote, lengthNote, startNote;
        private DropdownField startField;
        private readonly List<string> ageIds = new();

        public NewGameOptions(VisualElement root)
        {
            box = root.Q("setup-options");
            if (box == null) return;
            landNote   = new Label().WithClass("setup-option-note");
            lengthNote = new Label().WithClass("setup-option-note");
            startNote  = new Label().WithClass("setup-option-note");
            box.Add(Row("Land area", GameOptions.LandNames, landButtons, i => { var n = GameOptions.Next; n.landTier = i; GameOptions.Next = n; Refresh(); }, landNote));
            box.Add(Row("Game length", GameOptions.LengthNames, lengthButtons, i => { var n = GameOptions.Next; n.lengthTier = i; GameOptions.Next = n; Refresh(); }, lengthNote));
            box.Add(StartRow());
            Refresh();
        }

        private VisualElement Row(string title, string[] names, List<Button> buttons, System.Action<int> pick, Label note)
        {
            var row = new VisualElement().WithClass("setup-option-row");
            row.Add(new Label(Loc.T(title)).WithClass("setup-option-label"));
            var group = new VisualElement().WithClass("setup-option-group");
            for (int i = 0; i < names.Length; i++)
            {
                int index = i;
                var b = new Button(() => pick(index)) { text = Loc.T(names[i]) }.WithClass("setup-option");
                buttons.Add(b);
                group.Add(b);
            }
            row.Add(group);
            row.Add(note);
            return row;
        }

        private VisualElement StartRow()
        {
            var row = new VisualElement().WithClass("setup-option-row");
            row.Add(new Label(Loc.T("Starting period")).WithClass("setup-option-label"));
            if (GameDataLoader.Ages == null) GameDataLoader.Initialize();
            var names = new List<string>();
            foreach (var a in GameDataLoader.Ages) { ageIds.Add(a.id); names.Add($"{Loc.T(a.displayName)}  ({a.startMillionYearsAgo:0.#} Ma)"); }
            startField = new DropdownField(names, Mathf.Max(0, ageIds.IndexOf(GameOptions.Next.startAge))).WithClass("setup-option-dropdown");
            startField.RegisterValueChangedCallback(_ =>
            {
                var n = GameOptions.Next;
                n.startAge = ageIds[Mathf.Max(0, startField.index)];
                GameOptions.Next = n;
                Refresh();
            });
            row.Add(startField);
            row.Add(startNote);
            return row;
        }

        // Highlights the current choices and explains them
        public void Refresh()
        {
            if (box == null) return;
            var next = GameOptions.Next;
            for (int i = 0; i < landButtons.Count; i++) landButtons[i].EnableInClassList("selected", i == next.landTier);
            for (int i = 0; i < lengthButtons.Count; i++) lengthButtons[i].EnableInClassList("selected", i == next.lengthTier);
            landNote.text = Loc.F("{0:0} % of the world is land today", GameOptions.LandShares[next.landTier] * 100f);

            int turns = 0, turnsFromStart = 0;
            bool counting = false;
            foreach (var a in GameDataLoader.Ages)
            {
                int t = Mathf.Max(1, Mathf.RoundToInt(a.turns * GameOptions.LengthFactors[next.lengthTier]));
                counting |= a.id == next.startAge;
                turns += t;
                if (counting) turnsFromStart += t;
            }
            lengthNote.text = Loc.F("{0} turns to the present day ({1} in all)", turnsFromStart, turns);

            bool sea = System.Enum.TryParse(next.startAge, out GeologicalAge age) && GameOptions.StartsUnderSea(age);
            startNote.text = Loc.T(sea ? "Life is still all in the sea: you begin on the seabed, in the layer under sea level"
                                       : "You begin on the surface");
            if (startField != null) startField.SetValueWithoutNotify(startField.choices[Mathf.Max(0, ageIds.IndexOf(next.startAge))]);
        }
    }
}
