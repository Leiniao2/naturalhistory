using System;
using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;
using NaturalHistory.Evolution;
using UnityEngine;

namespace NaturalHistory.World
{
    // The slots an animal group can hold on a tile. Which ones a tile has depends on the layer and
    // on whether the tile is land or water; a niche holds one group, and groups in different niches
    // share the tile.
    //  Surface: land tiles have Microbe, Herbivore, Carnivore and Scavenger, plus Pollinator from the
    //           Cretaceous on, where flowering plants grow; water tiles have the Sea surface
    //  Under:   land tiles have Underground; water tiles have Plankton, Filter feeder, Predator and
    //           Benthic, plus Grazer from the Jurassic on, where large seaweeds grow
    //  Sky:     mountain tiles have the Summit; other tiles none
    public enum Niche
    {
        Microbe,      // land animals < 1 cm
        Herbivore,
        Carnivore,    // hunters, and parasites that live on their host
        Scavenger,    // carrion and detritus eaters
        Pollinator,   // nectar feeders, on tiles with flowering plants (Cretaceous on)
        SeaSurface,   // floating on the water: ducks, pelicans, Portuguese man o' war
        Underground,  // in the soil under land
        Plankton,     // water animals < 1 cm
        FilterFeeder,
        Predator,
        Benthic,      // living on the sea floor or lakebed
        Grazer,       // seaweed eaters, on tiles with large seaweeds (Jurassic on)
        Summit,       // mountain tops
    }

    // Which layer the map shows (see UnderView)
    public enum MapLayer { Surface, Under, Sky }

    public static class Niches
    {
        public static readonly Niche[] All = (Niche[])Enum.GetValues(typeof(Niche));

        // Species groups that live in the soil
        private static readonly HashSet<string> SoilDwellers = new(StringComparer.OrdinalIgnoreCase) { "Annelid", "Early bilaterian" };

        // Sea animals that live on the seafloor rather than in open water (trilobites, lobopodians,
        // the Ediacaran biota)
        private static readonly HashSet<string> SeafloorDwellers = new(StringComparer.OrdinalIgnoreCase)
        {
            "Trilobite", "Arthropod", "Lobopodian", "Proarticulate", "Stem mollusc", "Rangeomorph", "Trilobozoan", "Tubular animal",
            "Parvancorinomorph", "King crab", "Spiny lobster", "Horseshoe crab", "Prawn",
        };

        private const float MicrobeCm = 1f;

        // The niche a species takes on a tile (on its usual kind of tile when `cell` is null)
        public static Niche Of(SpeciesDefinition def, HexCell cell)
        {
            if (def == null) return Niche.Herbivore;
            bool water = cell != null ? cell.IsWater : LivesOnlyInWater(def);
            if (cell != null && cell.IsMountain) return Niche.Summit;
            var style = StyleOf(def);
            if (water)
            {
                if (style == ColonyStyle.Float || (IsFlyer(def) && style != ColonyStyle.Swim)) return Niche.SeaSurface; // on the water, or flying over it
                if (def.sizeCm < MicrobeCm) return Niche.Plankton;
                if (def.diet == "Filter feeder") return Niche.FilterFeeder;
                if (MainDiet(def) == Niche.Herbivore && GrazersOn(cell)) return Niche.Grazer;
                if (OnSeabed(def) || SoilDwellers.Contains(def.group ?? "") || MainDiet(def) is Niche.Scavenger or Niche.Herbivore) return Niche.Benthic;
                return Niche.Predator;
            }
            if (SoilDwellers.Contains(def.group ?? "")) return Niche.Underground;
            if (def.sizeCm < MicrobeCm) return Niche.Microbe;
            if (IsPollinator(def) && PollinatorsOn(cell)) return Niche.Pollinator;
            return MainDiet(def);
        }

        // Herbivore, Carnivore or Scavenger: what the species mostly lives on. Omnivores say so in
        // species.json "mainDiet"; parasites count as hunters; filter feeders on land (flamingos)
        // strain small animals.
        public static Niche MainDiet(SpeciesDefinition def)
        {
            var diet = def.diet == "Omnivore" && !string.IsNullOrEmpty(def.mainDiet) ? def.mainDiet : def.diet;
            return diet switch
            {
                "Herbivore" or "Omnivore" => Niche.Herbivore,
                "Scavenger" or "Detritivore" => Niche.Scavenger,
                _ => Niche.Carnivore,
            };
        }

        // The layer a niche belongs to
        public static MapLayer LayerOf(Niche niche) => niche switch
        {
            Niche.Underground or Niche.Plankton or Niche.FilterFeeder or Niche.Predator or Niche.Benthic or Niche.Grazer => MapLayer.Under,
            Niche.Summit => MapLayer.Sky,
            _ => MapLayer.Surface,
        };

        // The niches a tile has in a layer, in display order
        public static IEnumerable<Niche> On(HexCell cell, MapLayer layer)
        {
            if (cell == null) yield break;
            switch (layer)
            {
                case MapLayer.Surface when cell.IsWater:
                    yield return Niche.SeaSurface; break;
                case MapLayer.Surface when !cell.IsMountain:
                    yield return Niche.Microbe; yield return Niche.Herbivore; yield return Niche.Carnivore; yield return Niche.Scavenger;
                    if (PollinatorsOn(cell)) yield return Niche.Pollinator;
                    break;
                case MapLayer.Under when cell.IsWater:
                    yield return Niche.Plankton; yield return Niche.FilterFeeder; yield return Niche.Predator; yield return Niche.Benthic;
                    if (GrazersOn(cell)) yield return Niche.Grazer;
                    if (!UnderView.SurfaceOpen) yield return Niche.SeaSurface; // the surface can't be shown yet
                    break;
                case MapLayer.Under:
                    yield return Niche.Underground; break;
                case MapLayer.Sky when cell.IsMountain:
                    yield return Niche.Summit; break;
            }
        }

        // ---------- Tags: animals seen in a layer other than their niche's ----------

        // Fliers (species.json tag "Flyer", or soaring/swarming, or a good flier by its genes): shown in the sky
        public static bool IsFlyer(SpeciesDefinition def) =>
            HasTag(def, "Flyer") || StyleOf(def) is ColonyStyle.Soar or ColonyStyle.Swarm || Gene(def, "flight_capability") >= 0.4f;

        // Air-breathers of the water that come up to the surface (tag "Surfacer", or water tetrapods):
        // whales, turtles, crocodiles, otters, the platypus; flying fish by tag
        public static bool IsSurfacer(SpeciesDefinition def) =>
            HasTag(def, "Surfacer") || (LivesInWater(def) && System.Linq.Enumerable.Contains(EvolutionData.TagsOf(def), "Tetrapod") && StyleOf(def) != ColonyStyle.Float);

        // Land animals that dig or go into burrows (tag "Burrower", or by their genes): rats, ants, termites
        public static bool IsBurrower(SpeciesDefinition def) =>
            HasTag(def, "Burrower") || (!LivesOnlyInWater(def) && def.diet != "Parasite" && Gene(def, "burrowing") >= 0.5f);

        // Nectar feeders (tag "Pollinator", or by their genes): bees, butterflies, hummingbirds
        public static bool IsPollinator(SpeciesDefinition def) => HasTag(def, "Pollinator") || Gene(def, "nectar_feeding") >= 0.5f;

        // ---------- Niches that need plants ----------

        // Flowering plants (and so pollinators) from the Cretaceous on
        public static bool PollinatorsOn(HexCell cell)
        {
            if (cell == null || cell.IsWater || Age < GeologicalAge.Cretaceous) return false;
            foreach (var p in cell.Plants) if (IsFlowering(p)) return true;
            return false;
        }

        // Large seaweeds (and so grazers) from the Jurassic on
        public static bool GrazersOn(HexCell cell)
        {
            if (cell == null || !cell.IsWater || Age < GeologicalAge.Jurassic) return false;
            foreach (var p in cell.UnderPlants) if (IsSeaweed(p)) return true;
            return false;
        }

        private static readonly HashSet<string> FloweringGroups = new(StringComparer.OrdinalIgnoreCase) { "Flowering plant", "Grass", "Palm", "Sedge", "Cactus" };
        public static bool IsFlowering(PlantDefinition p) => p != null && FloweringGroups.Contains(p.group ?? "");

        // Medium and large algae: not crusts, mats, stromatolites or calcified microbes
        private static readonly HashSet<string> SeaweedForms = new(StringComparer.OrdinalIgnoreCase)
            { "Algae", "Kelp", "SeaLettuce", "Ribbon", "Fan", "Feather", "Grape", "Bubble", "Fingers", "Tuft", "Whorl", "Rosette", "Wineglass", "Cushion" };
        public static bool IsSeaweed(PlantDefinition p) =>
            p != null && p.group != null && p.group.IndexOf("alga", StringComparison.OrdinalIgnoreCase) >= 0 && SeaweedForms.Contains(p.form ?? "");

        private static GeologicalAge Age => HexGrid.Instance != null ? HexGrid.Instance.DisplayedAge : GeologicalAge.Quaternary;

        // ---------- Helpers ----------

        // Sessile and bottom-living animals of the water (sponges, corals, urchins, trilobites…):
        // they live on the seabed or lakebed, not in caves or rock
        public static bool OnSeabed(SpeciesDefinition def)
        {
            if (def == null || !LivesOnlyInWater(def)) return false;
            return StyleOf(def) == ColonyStyle.Fixed || SoilDwellers.Contains(def.group ?? "") || SeafloorDwellers.Contains(def.group ?? "");
        }

        // Soil animals under land: they can't get into solid bedrock
        public static bool InSoil(SpeciesDefinition def) => def != null && SoilDwellers.Contains(def.group ?? "") && !LivesOnlyInWater(def);

        public static bool LivesOnlyInWater(SpeciesDefinition def)
        {
            if (def.habitats == null || def.habitats.Count == 0) return false;
            foreach (var h in def.habitats)
                if (h != nameof(TerrainKind.SaltWater) && h != nameof(TerrainKind.FreshWater)) return false;
            return true;
        }

        private static bool LivesInWater(SpeciesDefinition def) =>
            def.habitats != null && (def.habitats.Contains(nameof(TerrainKind.SaltWater)) || def.habitats.Contains(nameof(TerrainKind.FreshWater)));

        private static ColonyStyle StyleOf(SpeciesDefinition def) =>
            Enum.TryParse(def.mapStyle, true, out ColonyStyle style) ? style : ColonyStyle.Drift;

        private static bool HasTag(SpeciesDefinition def, string tag) =>
            def.tags != null && def.tags.Exists(t => string.Equals(t, tag, StringComparison.OrdinalIgnoreCase));

        private static float Gene(SpeciesDefinition def, string gene)
        {
            if (def.genes != null) foreach (var g in def.genes) if (g.gene == gene) return g.expression;
            return 0f;
        }

        // Each niche's spot on a tile (offset from the centre, in cells), so groups sharing a tile
        // stand apart; big animals keep near the middle.
        public static Vector3 Spot(Niche niche) => niche switch
        {
            Niche.Microbe or Niche.Plankton     => new Vector3(-0.30f, 0f,  0.20f),
            Niche.Herbivore or Niche.FilterFeeder => new Vector3( 0.30f, 0f,  0.20f),
            Niche.Carnivore or Niche.Predator   => new Vector3(-0.22f, 0f, -0.26f),
            Niche.Scavenger or Niche.Benthic    => new Vector3( 0.12f, 0f, -0.12f),
            Niche.Pollinator or Niche.Grazer    => new Vector3( 0.05f, 0f,  0.38f),
            _                                   => Vector3.zero,
        };

        public static string Name(Niche niche) => Loc.T(niche switch
        {
            Niche.Microbe      => "Microbes (<1 cm)",
            Niche.Herbivore    => "Herbivores",
            Niche.Carnivore    => "Carnivores",
            Niche.Scavenger    => "Scavengers",
            Niche.Pollinator   => "Pollinators",
            Niche.SeaSurface   => "Sea surface",
            Niche.Underground  => "Underground",
            Niche.Plankton     => "Plankton (<1 cm)",
            Niche.FilterFeeder => "Filter feeders",
            Niche.Predator     => "Predators",
            Niche.Benthic      => "Bottom dwellers",
            Niche.Grazer       => "Grazers",
            Niche.Summit       => "Summit",
            _                  => niche.ToString(),
        });

        // Microbes and plankton: hidden on a selected tile unless they are all it has
        public static bool IsTiny(Niche niche) => niche is Niche.Microbe or Niche.Plankton;
    }
}
