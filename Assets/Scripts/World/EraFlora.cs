using NaturalHistory.Core;

namespace NaturalHistory.World
{
    // How the land looked in each geological period. WorldGenerator gives every cell a climate
    // biome (HexCell.Biome: what a cell with that climate grows today). This maps it onto the ground
    // cover and plants of a period, following the fossil record:
    //   Cambrian        no land plants: bare rock, microbial mats on damp flats
    //   Ordovician      liverworts and mosses by the water (ice caps late in the period)
    //   Silurian        Cooksonia and other small vascular plants on wet lowlands
    //   Devonian        low plant cover inland, the first forests (Archaeopteris, Wattieza)
    //   Carboniferous   lycopsid coal swamps; ferns and horsetails, no grass yet; southern ice
    //   Permian         Glossopteris, early conifers, cycads and seed ferns
    //   Triassic        conifers, cycads, ginkgoes, ferns
    //   Jurassic        Araucaria and redwoods, tree ferns, prairies of giant ferns
    //   Cretaceous      flowering plants spread among the conifers and ferns
    //   Paleogene       warm broadleaf and palm forests; herbs and early grasses, no grassland
    //   Neogene         grasslands, savanna and tundra appear: the modern biomes
    //   Quaternary      modern biomes, ice ages
    public static class EraFlora
    {
        // Large ice sheets: the end-Ordovician (Hirnantian) glaciation, the Late Paleozoic Ice Age
        // and the late Cenozoic. The Paleogene only gets Antarctic ice at its very end.
        static bool HasIceSheets(GeologicalAge age) => age is GeologicalAge.Ordovician or GeologicalAge.Carboniferous or
            GeologicalAge.Permian or GeologicalAge.Neogene or GeologicalAge.Quaternary;

        public static TerrainKind TerrainFor(HexCell cell, GeologicalAge age)
        {
            var biome = cell.Biome;
            float m   = cell.Moisture;
            switch (biome)
            {
                case TerrainKind.SaltWater:
                case TerrainKind.FreshWater:
                case TerrainKind.Mountain:
                case TerrainKind.Desert:
                    return biome;

                case TerrainKind.IceSheet:
                    if (cell.Elevation >= WorldGenerator.MountainElevation)
                        return HasIceSheets(age) ? TerrainKind.IceSheet : TerrainKind.Mountain;
                    if (HasIceSheets(age)) return TerrainKind.IceSheet;
                    return age switch
                    {
                        <= GeologicalAge.Devonian  => TerrainKind.Barren,
                        <= GeologicalAge.Cretaceous => TerrainKind.FernPrairie, // Mesozoic polar forests and fern meadows
                        _                          => TerrainKind.Tundra,
                    };

                case TerrainKind.Hill:
                    return age switch
                    {
                        <= GeologicalAge.Silurian => TerrainKind.Barren,
                        GeologicalAge.Devonian    => TerrainKind.Mossland,
                        _                         => TerrainKind.Hill,
                    };

                case TerrainKind.Wetland:
                    return age switch
                    {
                        GeologicalAge.Cambrian      => TerrainKind.MicrobialMat,
                        <= GeologicalAge.Silurian   => TerrainKind.Mossland,
                        GeologicalAge.Carboniferous => TerrainKind.CoalSwamp,
                        _                           => TerrainKind.Wetland,
                    };

                case TerrainKind.Rainforest:
                    return age switch
                    {
                        GeologicalAge.Cambrian      => TerrainKind.MicrobialMat,
                        <= GeologicalAge.Devonian   => TerrainKind.Mossland,
                        GeologicalAge.Carboniferous => TerrainKind.CoalSwamp,
                        _                           => TerrainKind.Rainforest,
                    };

                case TerrainKind.Plain:
                    return age switch
                    {
                        GeologicalAge.Cambrian     => m > 0.8f ? TerrainKind.MicrobialMat : TerrainKind.Barren,
                        GeologicalAge.Ordovician   => m > 0.75f ? TerrainKind.Mossland : TerrainKind.Barren,
                        GeologicalAge.Silurian     => m > 0.6f ? TerrainKind.Mossland : TerrainKind.Barren,
                        GeologicalAge.Devonian     => TerrainKind.Mossland,
                        <= GeologicalAge.Cretaceous => TerrainKind.FernPrairie,
                        _                          => TerrainKind.Plain,
                    };

                // Grasslands only spread in the Neogene; before that dry and cold lowland is fern
                // country, and before land plants just rock.
                case TerrainKind.Savanna:
                case TerrainKind.Steppe:
                case TerrainKind.Tundra:
                    return age switch
                    {
                        <= GeologicalAge.Silurian   => TerrainKind.Barren,
                        GeologicalAge.Devonian      => biome == TerrainKind.Tundra ? TerrainKind.Mossland : TerrainKind.Barren,
                        <= GeologicalAge.Cretaceous => TerrainKind.FernPrairie,
                        GeologicalAge.Paleogene     => TerrainKind.Plain,
                        _                           => biome,
                    };
            }
            return biome;
        }

        // Forests need the Devonian; the Carboniferous turns swamp woods into dense coal forest.
        public static TerrainFeature FeatureFor(HexCell cell, TerrainKind terrain, GeologicalAge age)
        {
            var feature = cell.BiomeFeature;
            switch (feature)
            {
                case TerrainFeature.BroadleafForest:
                case TerrainFeature.ConiferForest:
                case TerrainFeature.Jungle:
                    if (age < GeologicalAge.Devonian) return TerrainFeature.None;
                    if (terrain == TerrainKind.CoalSwamp) return TerrainFeature.Jungle;
                    return feature;
            }
            return feature;
        }

        // Player-facing name, e.g. FernPrairie → "Fern prairie"
        public static string DisplayName(TerrainKind kind) => kind switch
        {
            TerrainKind.SaltWater    => "Ocean",
            TerrainKind.FreshWater   => "Shallow water",
            TerrainKind.IceSheet     => "Ice sheet",
            TerrainKind.MicrobialMat => "Microbial mat",
            TerrainKind.FernPrairie  => "Fern prairie",
            TerrainKind.CoalSwamp    => "Coal swamp",
            _                        => kind.ToString(),
        };

        // What grows on a cell in a period, for the tile panel. Null when there is nothing to say.
        public static string FloraOf(HexCell cell, GeologicalAge age)
        {
            if (cell?.Terrain == null) return null;
            return cell.Feature switch
            {
                TerrainFeature.BroadleafForest or TerrainFeature.ConiferForest or TerrainFeature.Jungle => ForestFlora(cell.Feature, age),
                TerrainFeature.Reef  => age switch
                {
                    GeologicalAge.Cambrian    => "Stromatolites and archaeocyathid sponge reef",
                    <= GeologicalAge.Permian  => "Tabulate and rugose corals, sponges and crinoids",
                    _                         => "Coral reef",
                },
                TerrainFeature.Oasis => age < GeologicalAge.Devonian ? "Spring-fed pool ringed with microbial mats" : "Spring-fed pool with " + OasisPlants(age),
                _ => GroundFlora(cell.Terrain.kind, age),
            };
        }

        static string OasisPlants(GeologicalAge age) => age switch
        {
            GeologicalAge.Devonian      => "horsetails and mosses",
            GeologicalAge.Carboniferous => "Calamites and tree ferns",
            <= GeologicalAge.Jurassic   => "cycads and tree ferns",
            _                           => "palms",
        };

        static string ForestFlora(TerrainFeature f, GeologicalAge age)
        {
            bool conifer = f == TerrainFeature.ConiferForest, jungle = f == TerrainFeature.Jungle;
            return age switch
            {
                GeologicalAge.Devonian      => jungle ? "Wattieza forest, the first trees" : "Archaeopteris forest",
                GeologicalAge.Carboniferous => conifer ? "Cordaites forest"
                                             : jungle ? "Coal forest: Lepidodendron, Sigillaria, Calamites and tree ferns"
                                             : "Lycopsid and tree-fern forest",
                GeologicalAge.Permian       => conifer ? "Walchia conifer forest" : jungle ? "Tree ferns, cycads and Calamites" : "Glossopteris forest",
                GeologicalAge.Triassic      => conifer ? "Voltzia conifer forest" : jungle ? "Tree-fern and cycad thicket" : "Conifer, ginkgo and cycad woodland",
                GeologicalAge.Jurassic      => conifer ? "Araucaria and redwood forest" : jungle ? "Tree ferns, cycads and giant ferns" : "Araucaria, ginkgo and tree-fern forest",
                GeologicalAge.Cretaceous    => conifer ? "Redwood and cypress forest" : jungle ? "Early flowering-plant rainforest with tree ferns" : "Magnolia, laurel and conifer forest",
                GeologicalAge.Paleogene     => conifer ? "Dawn redwood forest" : jungle ? "Paratropical rainforest with palms" : "Warm broadleaf forest",
                _                           => conifer ? "Boreal conifer forest" : jungle ? "Tropical rainforest" : "Temperate broadleaf forest",
            };
        }

        static string GroundFlora(TerrainKind kind, GeologicalAge age) => kind switch
        {
            TerrainKind.Barren       => "No land plants: bare rock and regolith",
            TerrainKind.MicrobialMat => "Microbial mats and stromatolites",
            TerrainKind.Mossland     => age switch
            {
                GeologicalAge.Ordovician => "Liverworts and mosses",
                GeologicalAge.Silurian   => "Mosses and Cooksonia, the first vascular plants",
                _                        => "Mosses, Rhynia and small lycopsids",
            },
            TerrainKind.FernPrairie  => age switch
            {
                GeologicalAge.Carboniferous => "Ferns, horsetails and seed ferns",
                GeologicalAge.Permian       => "Seed ferns, horsetails and cycads",
                GeologicalAge.Triassic      => "Ferns, horsetails and cycads",
                GeologicalAge.Jurassic      => "Giant ferns and cycads",
                _                           => "Ferns, cycads and the first flowering herbs",
            },
            TerrainKind.CoalSwamp    => "Giant horsetails and lycopsids over peat",
            TerrainKind.Wetland      => age < GeologicalAge.Cretaceous ? "Horsetails and ferns" : "Reeds, sedges and water lilies",
            TerrainKind.Rainforest   => age < GeologicalAge.Paleogene ? "Ferns and cycads under a gymnosperm canopy" : "Dense tropical undergrowth",
            TerrainKind.Plain        => age == GeologicalAge.Paleogene ? "Herbs, shrubs and early grasses" : "Grasses and wildflowers",
            TerrainKind.Hill         => age < GeologicalAge.Paleogene ? "Ferns and scrub" : "Grass and scrub",
            TerrainKind.Savanna      => "Grasses and acacias",
            TerrainKind.Steppe       => "Short grasses and sagebrush",
            TerrainKind.Tundra       => "Mosses, lichens and dwarf shrubs",
            TerrainKind.Desert       => age < GeologicalAge.Devonian ? "Bare sand" : "Sparse, drought-hardy plants",
            _                        => null,
        };
    }
}
