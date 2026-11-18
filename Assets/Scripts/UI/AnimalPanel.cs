using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.World;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Right side, above the tile panel: the animals on the selected tile in the current layer. One
    // card at a time — portrait, names, period, diet, size, niche, owner, description — with a tab
    // per group along its top edge when the tile holds more than one, biggest first. The card is
    // the animal the tile shows (UnderView.Focus): Tab, clicking the tile again or a tab moves on.
    public class AnimalPanel
    {
        private readonly VisualElement panel, tabs, portrait;
        private readonly Label nameLabel, metaLabel, statsLabel, descriptionLabel;

        private HexCell shownCell;
        private readonly List<ColonyGroup> shownGroups = new();
        private ColonyGroup current, followed;
        private bool dirty = true;

        public AnimalPanel(VisualElement root)
        {
            panel            = root.Q("animal-panel");
            tabs             = root.Q("animal-tabs");
            portrait         = root.Q("animal-portrait");
            nameLabel        = root.Q<Label>("animal-name");
            metaLabel        = root.Q<Label>("animal-meta");
            statsLabel       = root.Q<Label>("animal-stats");
            descriptionLabel = root.Q<Label>("animal-description");
            Loc.Changed += () => dirty = true;
        }

        // Polled every frame: follows CellSelector's selection and the groups on that tile
        public void Update()
        {
            var cell     = CellSelector.Selected;
            var colonies = SpeciesColonies.Instance;
            var groups   = cell != null && colonies != null ? UnderView.Focus.Ordered(cell) : new List<ColonyGroup>();

            bool changed = cell != shownCell || !groups.SequenceEqual(shownGroups);
            if (changed)
            {
                shownCell = cell;
                shownGroups.Clear();
                shownGroups.AddRange(groups);
                if (!shownGroups.Contains(current)) current = null;
                RebuildTabs();
                dirty = true;
            }
            // the animal the tile shows on the map takes the card
            var focused = cell != null ? UnderView.Focus.Current(cell) : null;
            if (focused != followed)
            {
                followed = focused;
                if (focused != null && focused != current) { current = focused; dirty = true; }
            }
            if (current == null && shownGroups.Count > 0) { current = shownGroups[0]; dirty = true; }

            panel.EnableInClassList("hidden", current == null);
            if (current == null || !dirty) return;
            dirty = false;
            Show(current);
        }

        private void RebuildTabs()
        {
            tabs.Clear();
            tabs.EnableInClassList("hidden", shownGroups.Count < 2);
            panel.EnableInClassList("tabbed", shownGroups.Count >= 2);
            if (shownGroups.Count < 2) return;
            foreach (var g in shownGroups)
            {
                var group = g;
                var tab = new Button(() => { UnderView.Focus.Show(group); current = group; dirty = true; }) { text = Loc.T(g.Definition.commonName) };
                tab.AddToClassList("animal-tab");
                tab.userData = group;
                tabs.Add(tab);
            }
        }

        private void Show(ColonyGroup g)
        {
            foreach (var tab in tabs.Children())
                tab.EnableInClassList("selected", ReferenceEquals(tab.userData, g));

            var def = g.Definition;
            var tex = SpeciesPortraits.Get(def);
            portrait.style.backgroundImage = tex is UnityEngine.RenderTexture rt ? Background.FromRenderTexture(rt) : new StyleBackground(StyleKeyword.None);
            nameLabel.text = Loc.T(def.commonName);

            var span = string.IsNullOrEmpty(def.lastAge) ? Loc.F("{0} – today", Loc.T(def.firstAge))
                     : def.firstAge == def.lastAge ? Loc.T(def.firstAge) : $"{Loc.T(def.firstAge)} – {Loc.T(def.lastAge)}";
            metaLabel.text = $"{def.scientificName}\n{Loc.T(def.group)}  ·  {span}";

            var owner = g.Owner == null ? Loc.T("Wild") : g.Owner.IsHuman ? Loc.T("Yours") : g.Owner.Name;
            var lines = new List<string>
            {
                Loc.F("Niche: {0}", Niches.Name(g.Niche)),
                Loc.F("Owner: {0}", owner),
            };
            if (!string.IsNullOrEmpty(def.diet)) lines.Add(Loc.F("Diet: {0}", Loc.T(def.diet)));
            if (def.sizeCm > 0f) lines.Add(Loc.F("Size: {0}", FormatSize(def.sizeCm)));
            if (def.habitats != null && def.habitats.Count > 0)
                lines.Add(Loc.F("Habitats: {0}", string.Join(", ", def.habitats.Select(h => HabitatName(h)))));
            statsLabel.text = string.Join("\n", lines);
            descriptionLabel.text = Loc.T(def.description);
        }

        // Habitat entries are TerrainKind names; shown the way the tile panel names terrain
        internal static string HabitatName(string habitat) =>
            System.Enum.TryParse(habitat, out TerrainKind kind) ? EraFlora.DisplayName(kind) : habitat;

        internal static string FormatSize(float cm) => cm switch
        {
            >= 100f => Loc.F("{0:0.#} m", cm / 100f),
            >= 1f   => Loc.F("{0:0.#} cm", cm),
            _       => Loc.F("{0:0.##} mm", cm * 10f),
        };
    }
}
