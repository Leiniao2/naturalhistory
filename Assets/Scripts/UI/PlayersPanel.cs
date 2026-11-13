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
    // iconic animals, and the new-game screen where players pick count, faction, name and colours.
    public class PlayersPanel
    {
        private readonly VisualElement bar, factionOverlay, factionBand, factionAnimals, setupOverlay, setupList;
        private readonly Label factionTitle, factionSubtitle, factionDescription, setupCount;
        private List<PlayerSetup> draft = new();

        public event Action NewGameStarted;
        public event Action SetupClosed;

        public bool FactionOpen => !factionOverlay.ClassListContains("hidden");
        public bool SetupOpen => !setupOverlay.ClassListContains("hidden");

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
            setupCount         = root.Q<Label>("setup-count");

            root.Q<Button>("faction-close-button").clicked += CloseFaction;
            root.Q<Button>("setup-fewer").clicked          += () => ChangeCount(-1);
            root.Q<Button>("setup-more").clicked           += () => ChangeCount(+1);
            root.Q<Button>("setup-randomize").clicked      += Randomize;
            root.Q<Button>("setup-back-button").clicked    += () => { CloseSetup(); SetupClosed?.Invoke(); };
            root.Q<Button>("setup-start-button").clicked   += StartGame;
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
                chip.Add(new Label(player.Name).WithClass("player-chip-name"));
                if (player.IsHuman) chip.Add(new Label("you").WithClass("player-chip-tag"));
                chip.tooltip = player.FactionName;
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
            factionTitle.text = player.Name;
            factionSubtitle.text = faction == null ? "" :
                (player.Name != faction.displayName ? $"{faction.displayName} · " : "") + faction.category + (player.IsHuman ? " · You" : " · AI");
            factionDescription.text = faction?.description ?? "";

            factionAnimals.Clear();
            if (faction != null)
            {
                foreach (var animal in faction.iconicAnimals.OrderBy(a => AgeOrder(a.age)))
                {
                    bool active = Player.IsActive(animal);
                    var row = new VisualElement().WithClass("animal-row").WithClass(active ? "active" : "inactive");
                    var header = new VisualElement().WithClass("animal-header");
                    header.Add(new Label(animal.name).WithClass("animal-name"));
                    header.Add(new Label(animal.scientificName).WithClass("animal-scientific"));
                    var bonus = animal.bonusEvolutionPoints > 0 ? $"  ·  +{animal.bonusEvolutionPoints} EP" : "";
                    header.Add(new Label((active ? $"Active since the {animal.age}" : $"Arrives in the {animal.age}") + bonus).WithClass("animal-status"));
                    row.Add(header);
                    row.Add(new Label(animal.description).WithClass("animal-description"));
                    factionAnimals.Add(row);
                }
            }
            factionOverlay.RemoveFromClassList("hidden");
        }

        public void CloseFaction() => factionOverlay.AddToClassList("hidden");

        private static int AgeOrder(string age) => Enum.TryParse<GeologicalAge>(age, out var a) ? (int)a : int.MaxValue;

        // ---------- New game ----------

        public void OpenSetup()
        {
            if (Manager == null || Factions == null || Factions.Count == 0) return;
            draft = Manager.CurrentSetups();
            if (draft.Count == 0) draft = PlayerManager.RandomSetup(PlayerManager.DefaultPlayerCount, new System.Random());
            RebuildSetup();
            setupOverlay.RemoveFromClassList("hidden");
        }

        public void CloseSetup() => setupOverlay.AddToClassList("hidden");

        private void StartGame()
        {
            CloseSetup();
            Manager?.StartNewGame(draft);
            NewGameStarted?.Invoke();
        }

        private void ChangeCount(int delta)
        {
            int max = Mathf.Min(PlayerManager.MaxPlayers, Factions.Count);
            if (delta > 0 && draft.Count < max)
            {
                var unused = Factions.Where(f => draft.All(s => s.faction != f.id)).ToList();
                draft.Add(PlayerSetup.For(unused[UnityEngine.Random.Range(0, unused.Count)], human: false));
            }
            else if (delta < 0 && draft.Count > PlayerManager.MinPlayers)
            {
                draft.RemoveAt(draft.Count - 1); // seat 1 (the human) is never removed
            }
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
            setupCount.text = draft.Count.ToString();
            setupList.Clear();
            var choices = Factions.Select(f => f.displayName).ToList();

            for (int i = 0; i < draft.Count; i++)
            {
                var setup = draft[i];
                var faction = GameDataLoader.GetFaction(setup.faction);
                var row = new VisualElement().WithClass("setup-row");

                row.Add(new Label(setup.human ? "You" : $"AI {i}").WithClass("setup-seat"));

                var band = new Button(() => CycleBand(setup)).WithClass("setup-band");
                band.Add(BandHalf(Parse(setup.primaryColor)));
                band.Add(BandHalf(Parse(setup.secondaryColor)));
                band.tooltip = "Change colours";
                row.Add(band);

                var dropdown = new DropdownField(choices, Mathf.Max(0, Factions.ToList().FindIndex(f => f.id == setup.faction))).WithClass("setup-faction");
                dropdown.RegisterValueChangedCallback(e => ChangeFaction(setup, Factions.FirstOrDefault(f => f.displayName == e.newValue)));
                row.Add(dropdown);

                var name = new TextField { value = setup.name, maxLength = 24 }.WithClass("setup-name");
                name.RegisterValueChangedCallback(e => setup.name = e.newValue);
                row.Add(name);

                row.Add(new Label(faction?.category ?? "").WithClass("setup-category"));
                setupList.Add(row);
            }
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
