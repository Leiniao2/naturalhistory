using System;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Progression;
using NaturalHistory.World;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Bottom-centre card for the selected animal group of the human player: portrait, species,
    // and its actions: open the species' Functions / Behaviors trees, reproduce, evolve (opens the
    // Evolution Tree panel on this copy).
    public class UnitPanel
    {
        private readonly VisualElement panel, portrait;
        private readonly Label nameLabel, detailLabel;
        private readonly Button reproduceButton, evolveButton, skipButton, restButton;
        private readonly Label restTip;

        public OwnedCopy Copy { get; private set; }

        public event Action<ProgressionTree> OpenTree;
        public event Action<OwnedCopy> OpenEvolve;
        public event Action<string> Message;

        private static EvolutionManager Evolution => EvolutionManager.Instance;

        public UnitPanel(VisualElement root)
        {
            panel           = root.Q("unit-panel");
            portrait        = root.Q("unit-portrait");
            nameLabel       = root.Q<Label>("unit-name");
            detailLabel     = root.Q<Label>("unit-detail");
            reproduceButton = root.Q<Button>("unit-reproduce");
            evolveButton    = root.Q<Button>("unit-evolve");
            skipButton      = root.Q<Button>("unit-skip");

            root.Q<Button>("unit-functions").clicked += () => ShowTree(ProgressionManager.Instance?.Morphology);
            root.Q<Button>("unit-behaviors").clicked += () => ShowTree(ProgressionManager.Instance?.Ethology);
            // in the trees' colours, glowing while this animal's species has something to acquire or become
            bool Focused() => Copy != null && ProgressionManager.Instance?.Species?.id == Copy.species;
            ThemedButtons.Apply(root.Q<Button>("unit-functions"), ThemedButtons.Theme.Functions, () => Focused() && ThemedButtons.TraitsReady(ProgressionManager.Instance.Morphology));
            ThemedButtons.Apply(root.Q<Button>("unit-behaviors"), ThemedButtons.Theme.Behaviors, () => Focused() && ThemedButtons.TraitsReady(ProgressionManager.Instance.Ethology));
            ThemedButtons.Apply(root.Q<Button>("unit-evolve"), ThemedButtons.Theme.Evolution, () => Copy != null && ThemedButtons.EvolutionReady(new[] { Copy }));
            UiIcons.Decorate(root.Q<Button>("unit-reproduce"), UiIcons.Reproduce);
            reproduceButton.clicked += OnReproduce;
            evolveButton.clicked    += () => { if (Copy != null) OpenEvolve?.Invoke(Copy); };
            skipButton.clicked      += () => { if (Copy?.group != null) UnitCycle.Instance?.Skip(Copy.group); };
            // Station: stay put until given an order, which is the only way to heal
            // (ColonyGroup.Stationed, BeginTurn); clicked again, it is ready for orders again
            restButton = new Button(() =>
            {
                var g = Copy?.group;
                if (g == null) return;
                g.Stationed = !g.Stationed;
                if (g.Stationed)
                {
                    Message?.Invoke(Loc.F("Stationed: heals {0}% HP each turn it stays", Mathf.RoundToInt(HealShare(g) * 100f)));
                    UnitCycle.Instance?.Skip(g); // on to the next animal awaiting orders
                }
                Refresh();
            }) { name = "unit-station" };
            restButton.AddToClassList("unit-button");
            skipButton.parent.Insert(skipButton.parent.IndexOf(skipButton) + 1, restButton);
            // what staying does, under the pointer (UI Toolkit's own tooltips only show in the Editor)
            restTip = new Label { pickingMode = PickingMode.Ignore };
            restTip.AddToClassList("zoology-tip");
            restTip.AddToClassList("hidden");
            root.Add(restTip);
            restButton.RegisterCallback<PointerEnterEvent>(e =>
            {
                var g = Copy?.group;
                if (g == null) return;
                restTip.text = g.Stationed
                    ? Loc.T("Stationed. Click to give it orders again (any order also ends it).")
                    : Loc.F("Stay here until ordered: only stationed animals heal, {0}% of their HP each turn (from the turn after they last acted).", Mathf.RoundToInt(HealShare(g) * 100f));
                restTip.RemoveFromClassList("hidden");
                restTip.BringToFront();
                PlaceTip(root, e.position);
            });
            restButton.RegisterCallback<PointerMoveEvent>(e => PlaceTip(root, e.position));
            restButton.RegisterCallback<PointerLeaveEvent>(_ => restTip.AddToClassList("hidden"));
        }

        // Polled every frame: follows the group selected on the map
        public void Update()
        {
            var group = SpeciesColonies.Instance != null ? SpeciesColonies.Instance.Selected : null;
            var copy  = group != null && group.Owner != null && group.Owner.IsHuman && Evolution != null ? Evolution.CopyOf(group) : null;
            if (copy != Copy)
            {
                Copy = copy;
                panel.EnableInClassList("hidden", copy == null);
                if (copy != null) Evolution.Focus(copy.species); // the trees follow the selected animal
            }
            if (Copy != null) Refresh();
        }

        private void Refresh()
        {
            var def = GameDataLoader.GetSpecies(Copy.species);
            if (def == null) return;
            var tex = SpeciesPortraits.Get(def);
            portrait.style.backgroundImage = tex is UnityEngine.RenderTexture rt ? Background.FromRenderTexture(rt) : new StyleBackground(StyleKeyword.None);
            nameLabel.text = Loc.T(def.commonName);

            var mine  = Evolution.CopiesOf(Copy.group.Owner).Where(c => c.species == Copy.species).ToList();
            int wait  = Evolution.TurnsUntilReproduce(Copy);
            int ready = EvolutionData.From(Copy.species).Count(l => Evolution.CanEvolve(l, Copy));
            int total = EvolutionData.From(Copy.species).Count();
            var breed = Copy.JustBorn ? Loc.T("New this turn: it can act from the next turn")
                      : wait > 0 ? Loc.F(wait == 1 ? "reproduce in {0} turn" : "reproduce in {0} turns", wait)
                      : Loc.T(Evolution.ReproduceCell(Copy) == null ? "no room to reproduce" : "can reproduce");
            var evolve = total == 0 ? Loc.T("no known descendants")
                       : ready > 0 ? Loc.F(ready == 1 ? "{0} evolution ready" : "{0} evolutions ready", ready)
                       : Loc.F(total == 1 ? "{0} possible evolution" : "{0} possible evolutions", total);
            var copies = Loc.F(mine.Count == 1 ? "{0} copy" : "{0} copies", mine.Count);
            var g = Copy.group;
            var combat = Loc.F("HP {0}/{1}  ·  Attack {2}  ·  Defense {3}  ·  Actions {4}/{5}",
                Mathf.CeilToInt(g.Hp), g.MaxHp, g.Stats.attack, g.Stats.defense, g.ActionsLeft, g.MaxActions);
            if (Diets.Starving(g)) combat += "\n" + Loc.F("No food on its tile or next to it: loses {0}% HP a turn", Mathf.RoundToInt(Diets.StarveLoss * 100f));
            var status = Abilities.Status(g);
            if (status.Length > 0) combat += "\n" + status;
            var abilities = string.Join(", ", Abilities.Of(def).Select(a =>
                Loc.T(a.name) + (Abilities.Unlocked(def, a) ? "" : " " + Loc.T("(locked)"))));
            detailLabel.text = $"{def.scientificName}  ·  {copies}\n{combat}\n{breed}  ·  {evolve}"
                             + (abilities.Length > 0 ? "\n" + Loc.F("Abilities: {0}", abilities) : "");

            reproduceButton.SetEnabled(wait == 0 && (Copy.group.HasActions() || Evolution.BreedsFree(Copy)) && Evolution.ReproduceCell(Copy) != null && Evolution.CanAffordReproduce(Copy));
            evolveButton.EnableInClassList("ready", ready > 0);
            evolveButton.SetEnabled(total > 0);
            skipButton.SetEnabled(UnitCycle.Instance != null && UnitCycle.Instance.Awaits(Copy.group));
            var group = Copy.group;
            // Station / its undoing, for your own groups
            restButton.style.display = group.Owner != null && group.Owner.IsHuman ? DisplayStyle.Flex : DisplayStyle.None;
            restButton.text = group.Stationed ? Loc.T("Stationed") : Loc.T("Station");
            restButton.EnableInClassList("selected", group.Stationed);
        }

        // The tip above the pointer, kept inside the screen
        private void PlaceTip(VisualElement root, Vector2 pointer)
        {
            var area = root.worldBound;
            var size = restTip.layout.size;
            float x = pointer.x + 16f, y = pointer.y - (float.IsNaN(size.y) ? 40f : size.y) - 12f;
            if (!float.IsNaN(size.x) && x + size.x > area.xMax - 8f) x = pointer.x - size.x - 16f;
            restTip.style.left = x - area.xMin;
            restTip.style.top  = Mathf.Max(0f, y - area.yMin);
        }

        private static float HealShare(ColonyGroup g) =>
            ColonyGroup.HealPerTurn * (Abilities.Has(g, Abilities.Regeneration) ? 2f : 1f);

        private void ShowTree(ProgressionTree tree)
        {
            if (Copy == null || tree == null) return;
            Evolution.Focus(Copy.species);
            OpenTree?.Invoke(tree);
        }

        // The young go where the player says: the free neighbouring tiles are marked, and clicking
        // one of them places them there (any other click cancels)
        private void OnReproduce()
        {
            if (Copy == null || SpeciesColonies.Instance == null) return;
            var copy  = Copy;
            var cells = Evolution.ReproduceCells(copy);
            if (cells.Count == 0 || Evolution.TurnsUntilReproduce(copy) > 0)
            {
                Evolution.Reproduce(copy, out var why); // says why not
                if (why != null) Message?.Invoke(why);
                return;
            }
            SpeciesColonies.Instance.ChooseTile(cells, cell =>
            {
                Evolution.Reproduce(copy, out var message, cell);
                if (message != null) Message?.Invoke(message);
            });
            Message?.Invoke(Loc.T("Click a marked tile to place the young"));
        }
    }
}
