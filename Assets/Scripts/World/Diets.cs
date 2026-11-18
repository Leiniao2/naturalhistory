using System.Collections.Generic;
using System.Linq;
using NaturalHistory.Core;
using NaturalHistory.Data;

namespace NaturalHistory.World
{
    // What a species eats, in words for the animal card and the Encyclopedia, following the rules
    // FoodWeb applies (species.json "diet", "prey", "hosts"); and hunger: a group with no food on its
    // tile or next to it (FoodWeb.HasFood) loses StarveLoss of its HP each turn instead of healing,
    // and starves to death at 0 (Combat.BeginTurn).
    public static class Diets
    {
        public const float StarveLoss = 0.25f; // of the maximum HP, per turn without food

        public static bool Starving(ColonyGroup g) =>
            g != null && g.Definition != null && g.Cell != null && SpeciesColonies.Instance != null
            && !FoodWeb.HasFood(g.Definition, g.Cell, SpeciesColonies.Instance, g);

        public static string Describe(SpeciesDefinition def)
        {
            if (def == null) return "";
            var habitats = Habitats(def);
            switch (def.diet)
            {
                case "Herbivore":      return Loc.F("Eats the plants of its own tile ({0})", habitats);
                case "Filter feeder":  return Loc.F("Filters plankton and particles from the water of its tile ({0})", habitats);
                case "Detritivore":    return Loc.F("Eats dead matter and microbes on its tile ({0})", habitats);
                case "Photosynthetic": return Loc.T("Lives on sunlight");
                case "Scavenger":      return Loc.T("Eats carcasses and leftovers of any animal on its tile or next to it");
                case "Parasite":       return Loc.F("Lives on or in its host, which must share its tile: {0}", Names(def.hosts));
                case "Omnivore":       return Loc.F("Eats the plants of its own tile ({0}) or hunts: {1}", habitats, Prey(def));
                case "Carnivore":      return Loc.F("Hunts: {0}", Prey(def));
                default:               return Loc.T(def.diet ?? "");
            }
        }

        // The hunter's prey as the food web sees it
        private static string Prey(SpeciesDefinition def)
        {
            var listed = (def.prey ?? new List<string>()).Where(p => !Same(p, FoodWeb.SmallAnimals)).ToList();
            bool small = def.prey != null && def.prey.Any(p => Same(p, FoodWeb.SmallAnimals));
            var parts = new List<string>();
            if (listed.Count > 0) parts.Add(Loc.F("{0}, on its tile or next to it", Names(listed)));
            if (small) parts.Add(Loc.T("small animals not shown on the map (insects, worms, plankton…), found anywhere in its habitat"));
            if (parts.Count == 0) parts.Add(Loc.T("any smaller animal on its tile or next to it"));
            return string.Join(Loc.T("; and "), parts);
        }

        // species ids and groups, by name
        private static string Names(IEnumerable<string> tokens)
        {
            var names = (tokens ?? Enumerable.Empty<string>())
                .Select(t => GameDataLoader.GetSpecies(t) is { } s ? Loc.T(s.commonName) : Loc.T(t))
                .Distinct().ToList();
            if (names.Count == 0) return Loc.T("none");
            return names.Count > 6 ? string.Join(", ", names.Take(6)) + "…" : string.Join(", ", names);
        }

        private static string Habitats(SpeciesDefinition def) =>
            def.habitats is { Count: > 0 }
                ? string.Join(", ", def.habitats.Select(h => System.Enum.TryParse(h, out TerrainKind k) ? EraFlora.DisplayName(k) : h))
                : Loc.T("a suitable tile");

        private static bool Same(string a, string b) => string.Equals(a, b, System.StringComparison.OrdinalIgnoreCase);
    }
}
