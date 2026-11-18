using System;
using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // A row of tabs along the top of the Functions, Behaviors and Evolution Tree panels, one per
    // species of yours (painting and name): shows whose trees are open, and a click switches to
    // another of your species.
    public class SpeciesTabs
    {
        private readonly VisualElement row;
        private readonly List<string> shown = new();

        public event Action<string> Picked;

        public SpeciesTabs(VisualElement row)
        {
            this.row = row;
            Loc.Changed += () => shown.Clear(); // names in the new language on the next Refresh
        }

        // current: the species to light up (null for none, e.g. browsing a species that isn't yours)
        public void Refresh(string current)
        {
            var species = EvolutionManager.Instance?.HumanSpecies.ToList() ?? new List<string>();
            if (!species.SequenceEqual(shown) || row.childCount != species.Count) Rebuild(species);
            foreach (var tab in row.Children())
                tab.EnableInClassList("selected", (string)tab.userData == current);
        }

        private void Rebuild(List<string> species)
        {
            shown.Clear();
            shown.AddRange(species);
            row.Clear();
            foreach (var id in species)
            {
                var def = GameDataLoader.GetSpecies(id);
                if (def == null) continue;
                var captured = id;
                var tab = new Button(() => Picked?.Invoke(captured)) { userData = id }.WithClass("species-tab");
                var pic = new VisualElement { pickingMode = PickingMode.Ignore }.WithClass("species-tab-portrait");
                var painting = SpeciesPortraits.Painting(def);
                if (painting != null) pic.style.backgroundImage = Background.FromTexture2D(painting);
                else if (SpeciesPortraits.Get(def) is UnityEngine.RenderTexture rt) pic.style.backgroundImage = Background.FromRenderTexture(rt);
                tab.Add(pic);
                tab.Add(new Label(Loc.T(def.commonName)) { pickingMode = PickingMode.Ignore }.WithClass("species-tab-name"));
                row.Add(tab);
            }
        }
    }
}
