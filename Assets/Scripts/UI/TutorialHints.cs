using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Evolution;
using NaturalHistory.Players;
using NaturalHistory.Progression;
using NaturalHistory.World;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Tips that guide a new player through the first turns, one card at a time in the lower left:
    // what they start with, how to select and move, end the turn, reproduce, spend Evolution Points,
    // evolve, and what wild animals, hunger and a new period mean. Each tip shows once, when what it
    // explains first happens (polled, so nothing else has to call in); "Got it" moves on, "No more
    // tips" stops them for good. Which tips were seen is kept between games (PlayerPrefs).
    public class TutorialHints : MonoBehaviour
    {
        private const string SeenKey = "hints.seen", OffKey = "hints.off";

        private sealed class Hint
        {
            public string id, title, text;
            public Func<bool> due;
        }

        private readonly List<Hint> hints = new();
        private readonly HashSet<string> seen = new();
        private VisualElement root, card;
        private Label title, body;
        private Button gotIt, noMore;
        private Hint showing;
        private bool newPeriod, selectedOnce;
        private float nextCheck;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<TutorialHints>() != null) return;
            new GameObject("TutorialHints").AddComponent<TutorialHints>();
        }

        public static bool Enabled
        {
            get => PlayerPrefs.GetInt(OffKey, 0) == 0;
            set { PlayerPrefs.SetInt(OffKey, value ? 0 : 1); PlayerPrefs.Save(); }
        }

        // Shows every tip again from the start (e.g. for a new player on the same machine)
        public static void ResetSeen() { PlayerPrefs.DeleteKey(SeenKey); PlayerPrefs.SetInt(OffKey, 0); PlayerPrefs.Save(); }

        private void Start()
        {
            foreach (var id in PlayerPrefs.GetString(SeenKey, "").Split(',', StringSplitOptions.RemoveEmptyEntries)) seen.Add(id);
            if (AgeManager.Instance != null) AgeManager.Instance.OnAgeTransition += (_, _) => newPeriod = true;
            Define();
        }

        // ---------- The tips, in the order they come up ----------

        private void Define()
        {
            Add("start", "Your first creatures",
                "You begin with three single-celled founders, one from each great branch of life, living around your habitat center. Guide them through 600 million years: spread out, compete, and evolve into the animals of later periods.",
                () => MyGroups().Any());
            Add("layers", "Layers of the map",
                "Every tile has layers: the sky, the surface, and below it the underground or the seabed. Animals live in one of them, and a layer shows only its own. Switch with the Sky, Surface and Underground buttons at the top (U and K on the keyboard) to find yours.",
                () => Seen("start") && MyGroups().Any());
            Add("select", "Select an animal",
                "Click one of your groups to select it. On a tile with several animals, click again or press Tab to pick the next one.",
                () => Seen("layers") && !selectedOnce);
            Add("move", "Moving",
                "The green tiles are where it can go this turn: each tile costs one action. Point at a tile to see the path and its cost, then click to move there. A group ringed in red can be attacked.",
                () => Selected() != null);
            Add("end-turn", "Ending the turn",
                "When your animals have used their actions, press Next Turn (or Enter). Each turn your habitat centers earn Evolution Points (EP); kills and sightings of new species earn more.",
                () => MyGroups().Any(g => g.ActionsLeft < g.Stats.moves));
            Add("reproduce", "Reproducing",
                "Select a group and press Reproduce, then pick a neighbouring tile: for 1 EP a new group is born there. More groups hold more territory and earn more.",
                () => Turn() >= 2 && Points() >= EvolutionManager.ReproduceCost);
            Add("traits", "Functions and Behaviors",
                "Spend EP in the Functions and Behaviors trees to give a species new traits. Evolving into another species needs certain traits, so look at what the species you want to become requires.",
                () => Turn() >= 3 && Points() >= 3);
            Add("evolve", "Ready to evolve",
                "One of your groups can now evolve. Press Evolve on its card, or open the Evolution Tree to see every species it can become and what each needs. Later species are stronger: their attack, defense and health grow with each period.",
                CanEvolveSomething);
            Add("wild", "Wild relatives",
                "Wild animals have appeared far away: close relatives of your species, evolved from the same ancestor. They compete with you for food and space, and some will fight.",
                () => Turn() >= 2 && WildNewcomers());
            Add("hunger", "Hunger",
                "One of your groups has no food on its tile or next to it. Each turn it goes hungry it loses a quarter of its health: move it to where it can eat.",
                () => MyGroups().Any(g => g.Definition != null && !FoodWeb.HasFood(g.Definition, g.Cell, SpeciesColonies.Instance, g)));
            Add("period", "A new period",
                "A new geological period has begun. The land, the climate and the wild animals change; your animals and territory carry on. New species can now evolve.",
                () => newPeriod);
        }

        private void Add(string id, string title, string text, Func<bool> due) =>
            hints.Add(new Hint { id = id, title = title, text = text, due = due });

        // ---------- State ----------

        private static Player Human => PlayerManager.Instance != null ? PlayerManager.Instance.Human : null;

        private static IEnumerable<ColonyGroup> MyGroups()
        {
            var colonies = SpeciesColonies.Instance;
            var human = Human;
            if (colonies == null || human == null) return Enumerable.Empty<ColonyGroup>();
            return colonies.Groups.Where(g => g != null && g.Cell != null && g.Owner != null && g.Owner.Index == human.Index);
        }

        private static ColonyGroup Selected()
        {
            var g = SpeciesColonies.Instance != null ? SpeciesColonies.Instance.Selected : null;
            return g != null && g.Owner != null && g.Owner.IsHuman ? g : null;
        }

        private static int Turn() => TurnManager.Instance != null ? TurnManager.Instance.CurrentTurn : 0;
        private static int Points() => ProgressionManager.Instance != null ? ProgressionManager.Instance.EvolutionPoints : 0;

        private static bool CanEvolveSomething()
        {
            var evolution = EvolutionManager.Instance;
            if (evolution == null) return false;
            foreach (var copy in evolution.CopiesOf(Human).ToList())
                foreach (var link in EvolutionData.From(copy.species))
                    if (evolution.CanEvolve(link, copy)) return true;
            return false;
        }

        // Wild groups of species other than the founders: born during the game (WildBirths)
        private static bool WildNewcomers()
        {
            var colonies = SpeciesColonies.Instance;
            return colonies != null && colonies.Groups.Any(g => g != null && g.Owner == null && g.Definition != null &&
                                                                 !Territory.TerritoryManager.Starters.Contains(g.Definition.id));
        }

        private bool Seen(string id) => seen.Contains(id);

        // Only during play: not over the title screen, the New Game screen or a loading screen
        private bool InPlay()
        {
            if (GameManager.Instance != null && GameManager.Instance.State != GameState.Playing) return false;
            if (root == null) return false;
            foreach (var name in new[] { "main-menu", "setup-overlay", "pause-overlay", "settings-overlay", "slots-overlay" })
            {
                var e = root.Q(name);
                if (e != null && !e.ClassListContains("hidden")) return false;
            }
            return true;
        }

        // ---------- Showing ----------

        private void Update()
        {
            if (Selected() != null) selectedOnce = true;
            if (Time.unscaledTime < nextCheck) return;
            nextCheck = Time.unscaledTime + 0.5f;
            if (root == null) Build();
            if (card == null) return;

            bool play = InPlay();
            card.style.display = play && showing != null ? DisplayStyle.Flex : DisplayStyle.None;
            if (!play || showing != null || !Enabled) return;
            foreach (var hint in hints)
            {
                if (seen.Contains(hint.id)) continue;
                bool due;
                try { due = hint.due(); } catch (Exception) { due = false; }
                if (!due) continue;
                Show(hint);
                break;
            }
            if (showing == null && newPeriod && seen.Contains("period")) newPeriod = false;
        }

        private void Show(Hint hint)
        {
            showing = hint;
            title.text = Loc.T(hint.title);
            body.text = Loc.T(hint.text);
            gotIt.text = Loc.T("Got it");
            noMore.text = Loc.T("No more tips");
            card.style.display = DisplayStyle.Flex;
        }

        private void Dismiss(bool all)
        {
            if (showing != null)
            {
                seen.Add(showing.id);
                if (showing.id == "period") newPeriod = false;
                PlayerPrefs.SetString(SeenKey, string.Join(",", seen));
                PlayerPrefs.Save();
            }
            if (all) Enabled = false;
            showing = null;
            card.style.display = DisplayStyle.None;
            nextCheck = Time.unscaledTime + 1.5f; // a pause before the next one
        }

        // The card, built in code so it needs nothing in GameMenus.uxml
        private void Build()
        {
            var doc = FindAnyObjectByType<UIDocument>();
            if (doc == null || doc.rootVisualElement == null) return;
            root = doc.rootVisualElement;

            card = new VisualElement { name = "tutorial-hint", pickingMode = PickingMode.Position };
            var s = card.style;
            s.position = Position.Absolute;
            s.left = 24; s.bottom = 150;
            s.width = 460;
            s.paddingLeft = s.paddingRight = 18; s.paddingTop = 14; s.paddingBottom = 12;
            s.backgroundColor = new Color(0.10f, 0.13f, 0.11f, 0.94f);
            s.borderTopWidth = s.borderBottomWidth = s.borderLeftWidth = s.borderRightWidth = 2;
            var gold = new Color(0.86f, 0.70f, 0.32f);
            s.borderTopColor = s.borderBottomColor = s.borderLeftColor = s.borderRightColor = gold;
            s.borderTopLeftRadius = s.borderTopRightRadius = s.borderBottomLeftRadius = s.borderBottomRightRadius = 8;
            s.display = DisplayStyle.None;

            title = new Label();
            title.style.fontSize = 22;
            title.style.unityFontStyleAndWeight = FontStyle.Bold;
            title.style.color = new Color(0.96f, 0.84f, 0.48f);
            title.style.marginBottom = 6;
            body = new Label();
            body.style.fontSize = 18;
            body.style.whiteSpace = WhiteSpace.Normal;
            body.style.color = new Color(0.92f, 0.92f, 0.86f);

            var row = new VisualElement();
            row.style.flexDirection = FlexDirection.Row;
            row.style.justifyContent = Justify.FlexEnd;
            row.style.marginTop = 12;
            noMore = new Button(() => Dismiss(true));
            gotIt = new Button(() => Dismiss(false));
            foreach (var b in new[] { noMore, gotIt })
            {
                b.style.fontSize = 17;
                b.style.height = 36;
                b.style.marginLeft = 8;
                b.style.paddingLeft = b.style.paddingRight = 14;
            }
            gotIt.style.backgroundColor = new Color(0.55f, 0.42f, 0.14f);
            gotIt.style.color = Color.white;
            row.Add(noMore);
            row.Add(gotIt);

            card.Add(title);
            card.Add(body);
            card.Add(row);
            root.Add(card);
            Loc.Changed += () => { if (showing != null) Show(showing); };
        }
    }
}
