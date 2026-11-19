using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Players;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Players in the top-left HUD (colour band + name), the faction panel with each faction's
    // iconic animals, and the new-game screen, in three pages (SetupPages): your realm (faction)
    // picked from one set of cards, your name and colours; the world (NewGameOptions); and the competitors: how many (up to what the map size
    // holds) and each one's realm, name and colours.
    public class PlayersPanel
    {
        private readonly VisualElement bar, factionOverlay, factionBand, factionAnimals, setupOverlay, setupList, setupYou;
        private readonly ScrollView setupRealms;
        private readonly Label factionTitle, factionSubtitle, factionDescription, realmDescription, realmAnimals;
        private readonly IntegerField setupCount; // competitors; typed or stepped with − / +
        private List<PlayerSetup> draft = new();

        public event Action NewGameStarting; // just before the new map is made
        public event Action NewGameStarted;
        public Action<Action> Loading; // runs the new game's setup behind the loading screen (GameMenus)
        public event Action SetupClosed;

        public bool FactionOpen => !factionOverlay.ClassListContains("hidden");
        public bool SetupOpen => !setupOverlay.ClassListContains("hidden");

        // The new-game screen's pages: your realm, the world, your competitors
        private const int SetupPages = 3;
        private readonly VisualElement[] pages = new VisualElement[SetupPages];
        private readonly Button[] steps = new Button[SetupPages];
        private Button nextButton, startButton;
        private int page;

        private void ShowPage(int index)
        {
            page = Mathf.Clamp(index, 0, SetupPages - 1);
            for (int i = 0; i < SetupPages; i++)
            {
                pages[i].EnableInClassList("hidden", i != page);
                steps[i].EnableInClassList("selected", i == page);
            }
            bool last = page == SetupPages - 1;
            nextButton.EnableInClassList("hidden", last);
            startButton.EnableInClassList("hidden", !last);
        }

        private static PlayerManager Manager => PlayerManager.Instance;
        private static IReadOnlyList<FactionDefinition> Factions => GameDataLoader.Factions;

        public PlayersPanel(VisualElement root)
        {
            bar                = root.Q("players-bar");
            factionOverlay     = root.Q("faction-overlay");
            factionBand        = root.Q("faction-band");
            factionAnimals     = root.Q("faction-animals");
            factionTitle       = root.Q<Label>("faction-title");
            factionSubtitle    = root.Q<Label>("faction-subtitle");
            factionDescription = root.Q<Label>("faction-description");
            setupOverlay       = root.Q("setup-overlay");
            setupList          = root.Q("setup-list");
            setupCount         = root.Q<IntegerField>("setup-count");
            setupCount.isDelayed = true; // applied on Enter or leaving the field, not at each digit
            setupCount.RegisterValueChangedCallback(e => SetCompetitors(e.newValue));
            setupRealms        = root.Q<ScrollView>("setup-realms");
            setupYou           = root.Q("setup-you");
            realmDescription   = root.Q<Label>("setup-realm-description");
            realmAnimals       = root.Q<Label>("setup-realm-animals");

            root.Q<Button>("faction-close-button").clicked += CloseFaction;
            root.Q<Button>("setup-fewer").clicked          += () => ChangeCount(-1);
            root.Q<Button>("setup-more").clicked           += () => ChangeCount(+1);
            root.Q<Button>("setup-randomize").clicked      += Randomize;
            // Back goes a page back, and from the first page back to the menu
            root.Q<Button>("setup-back-button").clicked    += () => { if (page > 0) ShowPage(page - 1); else { CloseSetup(); SetupClosed?.Invoke(); } };
            root.Q<Button>("setup-next-button").clicked    += () => ShowPage(page + 1);
            root.Q<Button>("setup-start-button").clicked   += StartGame;
            nextButton  = root.Q<Button>("setup-next-button");
            startButton = root.Q<Button>("setup-start-button");
            for (int i = 0; i < SetupPages; i++)
            {
                int captured = i;
                pages[i] = root.Q("setup-page-" + i);
                steps[i] = root.Q<Button>("setup-step-" + i);
                steps[i].clicked += () => ShowPage(captured);
            }
        }

        // ---------- HUD ----------

        public void RefreshBar()
        {
            bar.Clear();
            if (Manager == null) return;
            foreach (var player in Manager.Players)
            {
                var chip = new VisualElement().WithClass("player-chip");
                chip.EnableInClassList("human", player.IsHuman);
                chip.Add(Band(player.Primary, player.Secondary));
                chip.Add(new Label(ShownName(player)).WithClass("player-chip-name"));
                if (player.IsHuman) chip.Add(new Label(Loc.T("you")).WithClass("player-chip-tag"));
                chip.tooltip = Loc.T(player.FactionName);
                var captured = player;
                chip.RegisterCallback<ClickEvent>(_ => OpenFaction(captured));
                bar.Add(chip);
            }
        }

        // ---------- Faction ----------

        public void OpenFaction(Player player)
        {
            var faction = player.Faction;
            factionBand.Clear();
            factionBand.Add(BandHalf(player.Primary));
            factionBand.Add(BandHalf(player.Secondary));
            factionTitle.text = ShownName(player);
            factionSubtitle.text = faction == null ? "" :
                (player.Name != faction.displayName ? $"{Loc.T(faction.displayName)} · " : "") + Loc.T(faction.category)
                + " · " + Loc.T(player.IsHuman ? "You" : "AI");
            factionDescription.text = Loc.T(faction?.description ?? "");

            factionAnimals.Clear();
            if (faction != null)
            {
                foreach (var animal in faction.iconicAnimals.OrderBy(a => AgeOrder(a.age)))
                {
                    bool active = Player.IsActive(animal);
                    var row = new VisualElement().WithClass("animal-row").WithClass(active ? "active" : "inactive");
                    var header = new VisualElement().WithClass("animal-header");
                    header.Add(new Label(Loc.T(animal.name)).WithClass("animal-name"));
                    header.Add(new Label(animal.scientificName).WithClass("animal-scientific"));
                    var bonus = animal.bonusEvolutionPoints > 0 ? "  ·  " + Loc.F("+{0} EP", animal.bonusEvolutionPoints) : "";
                    var age = Loc.T(GameDataLoader.GetAge(animal.age)?.displayName ?? animal.age);
                    header.Add(new Label(Loc.F(active ? "Active since the {0}" : "Arrives in the {0}", age) + bonus).WithClass("animal-status"));
                    row.Add(header);
                    row.Add(new Label(Loc.T(animal.description)).WithClass("animal-description"));
                    factionAnimals.Add(row);
                }
            }
            factionOverlay.RemoveFromClassList("hidden");
        }

        public void CloseFaction() => factionOverlay.AddToClassList("hidden");

        // A player still called after their faction is shown with the faction's translated name
        private static string ShownName(Player player)
            => player.Faction != null && player.Name == player.Faction.displayName ? Loc.T(player.Name) : player.Name;

        private static int AgeOrder(string age) => Enum.TryParse<GeologicalAge>(age, out var a) ? (int)a : int.MaxValue;

        // ---------- New game ----------

        public void OpenSetup()
        {
            if (Manager == null || Factions == null || Factions.Count == 0) return;
            draft = Manager.CurrentSetups();
            if (draft.Count == 0) draft = PlayerManager.RandomSetup(PlayerManager.DefaultPlayerCount, new System.Random());
            RebuildSetup();
            ShowPage(0);
            setupOverlay.RemoveFromClassList("hidden");
        }

        public void CloseSetup() => setupOverlay.AddToClassList("hidden");

        private void StartGame()
        {
            CloseSetup();
            void Start()
            {
                NewGameStarting?.Invoke();
                Manager?.StartNewGame(draft);
                NewGameStarted?.Invoke();
            }
            if (Loading != null) Loading(Start);
            else Start();
        }

        // Seats the new game can have: up to PlayerManager.MaxPlayers, each with a realm of their own
        private static int MaxSeats => Mathf.Min(PlayerManager.MaxPlayers, Factions.Count);

        // The world settings changed
        public void OnOptionsChanged()
        {
            if (SetupOpen) RebuildSetup();
        }

        private void ChangeCount(int delta) => SetCompetitors(draft.Count - 1 + delta);

        // New competitors get a random realm nobody has; removing takes the last ones (seat 1, the
        // human, is never removed)
        private void SetCompetitors(int count)
        {
            int seats = Mathf.Clamp(count + 1, PlayerManager.MinPlayers, MaxSeats);
            while (draft.Count < seats)
            {
                var unused = Factions.Where(f => draft.All(s => s.faction != f.id)).ToList();
                draft.Add(PlayerSetup.For(unused[UnityEngine.Random.Range(0, unused.Count)], human: false));
            }
            while (draft.Count > seats) draft.RemoveAt(draft.Count - 1);
            RebuildSetup();
        }

        private void Randomize()
        {
            var human = draft.Count > 0 ? draft[0] : null;
            draft = PlayerManager.RandomSetup(draft.Count, new System.Random());
            // Keep a name the human typed themselves
            if (human != null && human.name != GameDataLoader.GetFaction(human.faction)?.displayName) draft[0].name = human.name;
            RebuildSetup();
        }

        private void RebuildSetup()
        {
            while (draft.Count > Mathf.Max(PlayerManager.MinPlayers, MaxSeats)) draft.RemoveAt(draft.Count - 1);
            setupCount.SetValueWithoutNotify(draft.Count - 1);
            BuildRealms();
            BuildYou();

            setupList.Clear();
            var choices = Factions.Select(f => Loc.T(f.displayName)).ToList();
            for (int i = 1; i < draft.Count; i++)
            {
                var setup = draft[i];
                var row = new VisualElement().WithClass("setup-row");

                row.Add(new Label(Loc.F("AI {0}", i)).WithClass("setup-seat"));
                row.Add(BandButton(setup));

                var dropdown = new DropdownField(choices, Mathf.Max(0, Factions.ToList().FindIndex(f => f.id == setup.faction))).WithClass("setup-faction");
                dropdown.RegisterValueChangedCallback(_ => ChangeFaction(setup, dropdown.index >= 0 && dropdown.index < Factions.Count ? Factions[dropdown.index] : null));
                row.Add(dropdown);

                row.Add(NameField(setup));
                setupList.Add(row);
            }
            if (draft.Count == 1) setupList.Add(new Label(Loc.T("No competitors: the world is yours alone.")).WithClass("setup-empty"));
        }

        // Every realm as a card, all together (not sorted into categories); yours lit, the ones a
        // competitor has marked with their seat. Picking one a competitor has swaps the two.
        private void BuildRealms()
        {
            var offset = setupRealms.scrollOffset;
            setupRealms.Clear();
            var you = draft[0];
            var cards = new VisualElement().WithClass("setup-realm-cards");
            foreach (var f in Factions)
            {
                var faction = f;
                var card = new Button(() => ChangeFaction(you, faction)).WithClass("setup-realm");
                card.EnableInClassList("selected", f.id == you.faction);
                card.tooltip = Loc.T(f.description);
                var band = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("band");
                band.Add(BandHalf(Parse(f.primaryColor)));
                band.Add(BandHalf(Parse(f.secondaryColor)));
                card.Add(band);
                card.Add(new Label(Loc.T(f.displayName)) { pickingMode = PickingMode.Ignore }.WithClass("setup-realm-name"));
                int seat = draft.FindIndex(x => x.faction == f.id);
                if (seat > 0) card.Add(new Label(Loc.F("AI {0}", seat)) { pickingMode = PickingMode.Ignore }.WithClass("setup-realm-taken"));
                cards.Add(card);
            }
            setupRealms.Add(cards);
            setupRealms.schedule.Execute(() => setupRealms.scrollOffset = offset); // once laid out again

            var mine = GameDataLoader.GetFaction(you.faction);
            realmDescription.text = mine == null ? "" : $"{Loc.T(mine.displayName)}\n{Loc.T(mine.description)}";
            realmAnimals.text = mine == null || mine.iconicAnimals.Count == 0 ? "" :
                Loc.F("Iconic animals: {0}", string.Join(", ", mine.iconicAnimals.OrderBy(x => AgeOrder(x.age))
                    .Select(x => $"{Loc.T(x.name)} ({Loc.T(GameDataLoader.GetAge(x.age)?.displayName ?? x.age)})")));
        }

        // Your colours and name, under the realm cards
        private void BuildYou()
        {
            setupYou.Clear();
            var you = draft[0];
            setupYou.Add(new Label(Loc.T("You")).WithClass("setup-seat"));
            setupYou.Add(BandButton(you));
            setupYou.Add(NameField(you));
        }

        private Button BandButton(PlayerSetup setup)
        {
            var band = new Button(() => CycleBand(setup)).WithClass("setup-band");
            band.Add(BandHalf(Parse(setup.primaryColor)));
            band.Add(BandHalf(Parse(setup.secondaryColor)));
            band.tooltip = Loc.T("Change colours");
            return band;
        }

        private static TextField NameField(PlayerSetup setup)
        {
            var name = new TextField { value = setup.name, maxLength = 24 }.WithClass("setup-name");
            name.RegisterValueChangedCallback(e => setup.name = e.newValue);
            return name;
        }

        // Picking a faction another seat has swaps the two. The name and colours follow the faction
        // unless the player changed them.
        private void ChangeFaction(PlayerSetup setup, FactionDefinition next)
        {
            if (next == null || next.id == setup.faction) return;
            var previous = GameDataLoader.GetFaction(setup.faction);
            var other = draft.FirstOrDefault(s => s != setup && s.faction == next.id);
            if (other != null && previous != null) AssignFaction(other, previous, next);
            AssignFaction(setup, next, previous);
            RebuildSetup();
        }

        private static void AssignFaction(PlayerSetup setup, FactionDefinition faction, FactionDefinition old)
        {
            if (old == null || string.IsNullOrWhiteSpace(setup.name) || setup.name == old.displayName) setup.name = faction.displayName;
            if (old == null || (setup.primaryColor == old.primaryColor && setup.secondaryColor == old.secondaryColor))
            {
                setup.primaryColor   = faction.primaryColor;
                setup.secondaryColor = faction.secondaryColor;
            }
            setup.faction = faction.id;
        }

        // Steps through every faction's band, plus each one flipped
        private void CycleBand(PlayerSetup setup)
        {
            var bands = Factions.SelectMany(f => new[] { (f.primaryColor, f.secondaryColor), (f.secondaryColor, f.primaryColor) }).ToList();
            int i = bands.FindIndex(b => Same(b.Item1, setup.primaryColor) && Same(b.Item2, setup.secondaryColor));
            (setup.primaryColor, setup.secondaryColor) = bands[(i + 1) % bands.Count];
            RebuildSetup();
        }

        private static bool Same(string a, string b) => string.Equals(a?.TrimStart('#'), b?.TrimStart('#'), StringComparison.OrdinalIgnoreCase);

        // ---------- Helpers ----------

        private static VisualElement Band(Color primary, Color secondary)
        {
            var band = new VisualElement().WithClass("band");
            band.Add(BandHalf(primary));
            band.Add(BandHalf(secondary));
            return band;
        }

        private static VisualElement BandHalf(Color color)
        {
            var half = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("band-half");
            half.style.backgroundColor = color;
            return half;
        }

        private static Color Parse(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.gray;
    }
}
