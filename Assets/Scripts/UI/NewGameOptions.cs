using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // The world settings on the New Game screen: map size, how much of the world is land, which
    // period it starts in, how many turns the game lasts (five lengths; "Fast" is the base table)
    // and the difficulty. Edits GameOptions.Next, which PlayerManager.StartNewGame applies.
    public class NewGameOptions
    {
        private readonly VisualElement box;
        private readonly List<Button> sizeButtons = new(), landButtons = new(), lengthButtons = new(), difficultyButtons = new();
        private readonly Label sizeNote, landNote, lengthNote, startNote, difficultyNote;
        private DropdownField startField;
        private readonly List<string> ageIds = new();

        public NewGameOptions(VisualElement root)
        {
            box = root.Q("setup-options");
            if (box == null) return;
            sizeNote       = new Label().WithClass("setup-option-note");
            landNote       = new Label().WithClass("setup-option-note");
            lengthNote     = new Label().WithClass("setup-option-note");
            startNote      = new Label().WithClass("setup-option-note");
            difficultyNote = new Label().WithClass("setup-option-note");
            box.Add(Row("Map size", GameOptions.MapSizeNames, sizeButtons, i => Change((ref GameSettings n) => n.mapSize = GameOptions.MapSizeNames[i]), sizeNote));
            box.Add(Row("Land area", GameOptions.LandNames, landButtons, i => Change((ref GameSettings n) => n.landTier = i), landNote));
            box.Add(StartRow());
            box.Add(Row("Game length", GameOptions.LengthNames, lengthButtons, i => Change((ref GameSettings n) => n.lengthTier = i), lengthNote));
            box.Add(Row("Difficulty", GameOptions.DifficultyNames, difficultyButtons, i => Change((ref GameSettings n) => n.difficulty = GameOptions.DifficultyNames[i]), difficultyNote));
            Refresh();
        }

        // Raised after any setting changes (the player list follows the map size)
        public event System.Action Changed;

        private delegate void Edit(ref GameSettings settings);
        private void Change(Edit edit)
        {
            var n = GameOptions.Next;
            edit(ref n);
            GameOptions.Next = n;
            Refresh();
            Changed?.Invoke();
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
                Changed?.Invoke();
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
            int size = GameOptions.MapSizeTier(next), difficulty = GameOptions.DifficultyTier(next);
            for (int i = 0; i < sizeButtons.Count; i++) sizeButtons[i].EnableInClassList("selected", i == size);
            for (int i = 0; i < difficultyButtons.Count; i++) difficultyButtons[i].EnableInClassList("selected", i == difficulty);
            var dims = GameOptions.MapSizes[size];
            sizeNote.text = Loc.F("{0} × {1} tiles, best for up to {2} players", dims.x, dims.y, GameOptions.MapPlayers[size]);
            difficultyNote.text = Loc.F("Start with {0}% of the usual EP and earn {1}% each turn; rival and wild animals hit yours {2}% as hard",
                Mathf.RoundToInt(GameOptions.StartPointShares[difficulty] * 100f), Mathf.RoundToInt(GameOptions.IncomeShares[difficulty] * 100f),
                Mathf.RoundToInt(GameOptions.FoeDamageShares[difficulty] * 100f));
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
