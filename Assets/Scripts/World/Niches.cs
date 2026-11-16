using System;
using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.World
{
    // The slots an animal group can hold on a tile. Every tile, land or water, has one of each:
    // five in the open (by way of life and body size) and one below it: underground on land,
    // underwater on the seabed for water tiles. A niche holds one group; groups in different niches
    // share the tile.
    public enum Niche
    {
        Aerial,      // fliers above the tile
        Micro,       // < 1 mm
        Small,       // 1 mm – 10 cm
        Medium,      // 10 cm – 1 m
        Large,       // > 1 m
        Underground, // burrowers in the soil; on water tiles: life fixed to or buried in the seabed
    }

    public static class Niches
    {
        public static readonly Niche[] All = (Niche[])Enum.GetValues(typeof(Niche));

        // Species groups that live in the soil
        private static readonly HashSet<string> Burrowers = new(StringComparer.OrdinalIgnoreCase) { "Annelid", "Early bilaterian" };

        // Sea animals that live on the seafloor rather than in open water (trilobites, lobopodians,
        // the Ediacaran biota): they take the seabed niche
        private static readonly HashSet<string> SeafloorDwellers = new(StringComparer.OrdinalIgnoreCase)
        {
            "Trilobite", "Arthropod", "Lobopodian", "Proarticulate", "Stem mollusc", "Rangeomorph", "Trilobozoan", "Tubular animal",
            "Parvancorinomorph",
        };

        // Which niche a species takes: burrowers and seabed-fixed life go below, fliers above, the
        // rest by body length (species.json sizeCm).
        public static Niche Of(SpeciesDefinition def)
        {
            if (def == null) return Niche.Small;
            if (def.group != null && Burrowers.Contains(def.group)) return Niche.Underground;
            Enum.TryParse(def.mapStyle, true, out ColonyStyle style);
            if (style == ColonyStyle.Fixed && LivesOnlyInWater(def)) return Niche.Underground; // corals, sponges, anemones, urchins
            if (def.group != null && SeafloorDwellers.Contains(def.group) && LivesOnlyInWater(def)) return Niche.Underground;
            if (style is ColonyStyle.Soar or ColonyStyle.Swarm) return Niche.Aerial;
            float cm = def.sizeCm;
            if (cm < 0.1f) return Niche.Micro;
            if (cm < 10f)  return Niche.Small;
            if (cm < 100f) return Niche.Medium;
            return Niche.Large;
        }

        private static bool LivesOnlyInWater(SpeciesDefinition def)
        {
            if (def.habitats == null || def.habitats.Count == 0) return false;
            foreach (var h in def.habitats)
                if (h != nameof(TerrainKind.SaltWater) && h != nameof(TerrainKind.FreshWater)) return false;
            return true;
        }

        // Each niche's spot on a tile (offset from the centre, in cells), so groups sharing a tile
        // stand apart. Fliers circle overhead anyway; big animals keep near the middle.
        public static Vector3 Spot(Niche niche) => niche switch
        {
            Niche.Micro       => new Vector3(-0.30f, 0f,  0.20f),
            Niche.Small       => new Vector3( 0.30f, 0f,  0.20f),
            Niche.Medium      => new Vector3(-0.22f, 0f, -0.26f),
            Niche.Large       => new Vector3( 0.12f, 0f, -0.12f),
            Niche.Underground => new Vector3( 0.05f, 0f,  0.38f),
            _                 => Vector3.zero,
        };

        // Player-facing name; the lower layer depends on the tile
        public static string Name(Niche niche, HexCell cell) => Loc.T(niche switch
        {
            Niche.Aerial      => "Aerial",
            Niche.Micro       => "Micro (<1 mm)",
            Niche.Small       => "Small (1 mm–10 cm)",
            Niche.Medium      => "Medium (10 cm–1 m)",
            Niche.Large       => "Large (>1 m)",
            Niche.Underground => cell != null && cell.IsWater ? "Underwater (seabed)" : "Underground",
            _                 => niche.ToString(),
        });
    }
}
