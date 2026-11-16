using System;
using NaturalHistory.Core;

namespace NaturalHistory.World
{
    // What lies below a tile, in the layer under sea level (see HexGrid.Under). Mostly it follows the
    // surface: rock and caves under land, seabed under the sea, lakebed under lakes. Here and there it
    // doesn't (a drowned valley under the coast, a sea cave under shallow water).
    public enum UnderKind
    {
        Rock,       // soil, bedrock and burrows
        Cave,       // caves and karst
        Seabed,     // sunlit shallow seabed
        DeepSeabed, // dark abyssal plain
        Lakebed,    // lake and river bed
        Bedrock,    // solid rock with no way through: the walls of the underground maze
    }

    public enum UnderFeature
    {
        None,
        Volcano,    // underwater volcano (seamount)
        Vents,      // hydrothermal vents ("black smokers")
        Geothermal, // shallow hydrothermal field: white smokers, gas seeps, sulphur and bacterial mats
    }

    // Which layer the map shows: the surface, or the layer under sea level
    public static class UnderView
    {
        public static bool On { get; private set; }
        public static event Action Changed;

        public static void Set(bool on)
        {
            if (on == On) return;
            On = on;
            Changed?.Invoke();
        }

        public static void Toggle() => Set(!On);

        // Whether a group is shown (and clickable) in the current view: the under view shows the
        // seabed and underground niche and the animals in the sea; the surface view everything but
        // the underground niche (swimmers are in both).
        public static bool Shows(ColonyGroup g)
        {
            if (g == null) return false;
            bool below  = g.Niche == Niche.Underground;
            bool marine = g.Cell != null && g.Cell.IsWater && g.Style is ColonyStyle.Swim or ColonyStyle.Drift;
            return On ? below || marine : !below;
        }

        // Underground animals can't enter, settle in or pass through solid bedrock
        public static bool Blocks(UnderKind kind) => kind == UnderKind.Bedrock;

        public static string Name(UnderKind kind) => Loc.T(kind switch
        {
            UnderKind.Rock       => "Underground",
            UnderKind.Cave       => "Caves",
            UnderKind.Seabed     => "Seabed",
            UnderKind.DeepSeabed => "Deep seabed",
            UnderKind.Lakebed    => "Lakebed",
            UnderKind.Bedrock    => "Solid bedrock (impassable)",
            _                    => kind.ToString(),
        });

        // A seabed or lakebed built of stromatolites is its own kind of floor (painted as one, see
        // MapFeatureMeshes.CoverOf), not a plant on it
        public static bool IsFloor(PlantDefinition plant) => plant != null && plant.form == "Stromatolite";

        public static string FloorName(HexCell cell)
        {
            if (HexGrid.Instance != null && HexGrid.Instance.ShowsStromatoliteFloor(cell))
                return Loc.T(cell.Under == UnderKind.Seabed ? "Stromatolite seabed" : "Stromatolite lakebed");
            return Name(cell.Under);
        }

        public static string Name(UnderFeature feature) => Loc.T(feature switch
        {
            UnderFeature.Volcano => "underwater volcano",
            UnderFeature.Vents   => "hydrothermal vents",
            UnderFeature.Geothermal => "shallow hydrothermal field",
            _                    => null,
        });
    }
}
