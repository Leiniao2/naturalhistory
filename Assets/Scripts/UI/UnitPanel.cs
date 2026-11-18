using System;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using NaturalHistory.Progression;
using NaturalHistory.World;
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
        private readonly Button reproduceButton, evolveButton;

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

            root.Q<Button>("unit-functions").clicked += () => ShowTree(ProgressionManager.Instance?.Morphology);
            root.Q<Button>("unit-behaviors").clicked += () => ShowTree(ProgressionManager.Instance?.Ethology);
            reproduceButton.clicked += OnReproduce;
            evolveButton.clicked    += () => { if (Copy != null) OpenEvolve?.Invoke(Copy); };
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
            detailLabel.text = $"{def.scientificName}  ·  {copies}\n{breed}  ·  {evolve}";

            reproduceButton.SetEnabled(wait == 0 && Evolution.ReproduceCell(Copy) != null);
            evolveButton.EnableInClassList("ready", ready > 0);
            evolveButton.SetEnabled(total > 0);
        }

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
