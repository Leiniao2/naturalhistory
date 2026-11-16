using System;
using System.Collections.Generic;
using NaturalHistory.Data;

namespace NaturalHistory.World
{
    // Where a species can live: a group has to find its food on its own tile or one of the six
    // around it (species.json "diet", "prey" and "hosts").
    //  - plant, fungus, plankton and detritus eaters need a tile whose type fits (their habitats),
    //    since that is where their food grows: a zebra can't go into the desert or tundra
    //  - hunters need a group of their prey on the tile or next to it
    //  - omnivores manage with either
    //  - scavengers need some other animals on the tile or next to it
    //  - parasites need their host on the same tile
    public static class FoodWeb
    {
        public enum FoodSource { Forage, Prey, ForageOrPrey, Carrion, Host }

        // In "prey": insects, worms, plankton, small fish and the like, which the map doesn't show
        // as groups but which live all over the hunter's habitat.
        public const string SmallAnimals = "Small animals";

        public static FoodSource SourceOf(SpeciesDefinition def)
        {
            switch (def.diet)
            {
                case "Carnivore": return HasToken(def.prey, SmallAnimals) ? FoodSource.ForageOrPrey : FoodSource.Prey;
                case "Omnivore":  return FoodSource.ForageOrPrey;
                case "Scavenger": return FoodSource.Carrion;
                case "Parasite":  return FoodSource.Host;
                default:          return FoodSource.Forage; // herbivores, filter feeders, detritivores, plants
            }
        }

        // Placement order, so food is on the map before whatever eats it: foragers, then hunters
        // (small before big, so a hunter's prey is usually placed by the time it is), scavengers, parasites.
        public static int Stage(SpeciesDefinition def) => SourceOf(def) switch
        {
            FoodSource.Forage       => 0,
            FoodSource.ForageOrPrey => 1,
            FoodSource.Prey         => 2,
            FoodSource.Carrion      => 3,
            _                       => 4,
        };

        // Whether a group of `def` (`self`, or null for one not placed yet) would find food on `cell`.
        public static bool HasFood(SpeciesDefinition def, HexCell cell, SpeciesColonies colonies, ColonyGroup self)
        {
            if (def == null || cell == null) return false;
            if (colonies == null) return true;
            return SourceOf(def) switch
            {
                FoodSource.Forage       => SpeciesColonies.FitsHabitat(def, cell),
                FoodSource.ForageOrPrey => SpeciesColonies.FitsHabitat(def, cell) || AnyNear(cell, colonies, self, other => IsPrey(def, other)),
                FoodSource.Prey         => AnyNear(cell, colonies, self, other => IsPrey(def, other)),
                FoodSource.Carrion      => AnyNear(cell, colonies, self, IsAnimal),
                FoodSource.Host         => System.Linq.Enumerable.Any(colonies.GroupsAt(cell), g => IsHost(def, g, self)),
                _                       => true,
            };
        }

        // Listed prey (species ids or groups). With none listed, any smaller animal.
        public static bool IsPrey(SpeciesDefinition hunter, SpeciesDefinition other)
        {
            if (other == null || other.id == hunter.id || !IsAnimal(other)) return false;
            bool listed = false;
            if (hunter.prey != null)
                foreach (var p in hunter.prey)
                {
                    if (Same(p, SmallAnimals)) continue;
                    listed = true;
                    if (Matches(p, other)) return true;
                }
            return !listed && other.sizeCm < hunter.sizeCm;
        }

        private static bool IsHost(SpeciesDefinition parasite, ColonyGroup group, ColonyGroup self)
        {
            if (group == null || group == self || parasite.hosts == null) return false;
            foreach (var h in parasite.hosts)
                if (Matches(h, group.Definition)) return true;
            return false;
        }

        private static bool AnyNear(HexCell cell, SpeciesColonies colonies, ColonyGroup self, Func<SpeciesDefinition, bool> wanted)
        {
            // Any group on the tile or next door, whatever niche it holds
            foreach (var g in colonies.GroupsAt(cell)) if (Wanted(g, self, wanted)) return true;
            var grid = HexGrid.Instance;
            if (grid == null) return false;
            foreach (var n in grid.GetNeighbors(cell))
                foreach (var g in colonies.GroupsAt(n)) if (Wanted(g, self, wanted)) return true;
            return false;
        }

        private static bool Wanted(ColonyGroup group, ColonyGroup self, Func<SpeciesDefinition, bool> wanted) =>
            group != null && group != self && group.Definition != null && wanted(group.Definition);

        private static bool IsAnimal(SpeciesDefinition def) => def.kingdom is "Animalia" or "Protista";

        private static bool Matches(string token, SpeciesDefinition def) => Same(token, def.id) || Same(token, def.group);

        private static bool HasToken(List<string> list, string token) => list != null && list.Exists(t => Same(t, token));

        private static bool Same(string a, string b) => string.Equals(a, b, StringComparison.OrdinalIgnoreCase);
    }
}
