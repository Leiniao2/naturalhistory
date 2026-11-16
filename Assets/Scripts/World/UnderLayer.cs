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

        public static string Name(UnderFeature feature) => Loc.T(feature switch
        {
            UnderFeature.Volcano => "underwater volcano",
            UnderFeature.Vents   => "hydrothermal vents",
            _                    => null,
        });
    }
}
