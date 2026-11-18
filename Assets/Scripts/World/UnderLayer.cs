using System;
using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.Data;

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

    // Which layer the map shows: the sky, the surface, or the layer under sea level
    public static class UnderView
    {
        public static MapLayer Layer { get; private set; } = MapLayer.Surface;
        public static bool On  => Layer == MapLayer.Under;
        public static bool Sky => Layer == MapLayer.Sky;
        public static event Action Changed;

        // Life goes ashore from the Cambrian: before it (the Ediacaran) there is nothing on land or in
        // the air, and only the layer under sea level can be shown
        public static bool SurfaceOpen
        {
            get
            {
                var grid = HexGrid.Instance;
                var age = grid != null && grid.IsGenerated ? grid.DisplayedAge
                        : AgeManager.Instance != null ? AgeManager.Instance.CurrentAge : GeologicalAge.Quaternary;
                return age >= GeologicalAge.Cambrian;
            }
        }
        private static bool wasOpen = true;

        // Re-applies the Ediacaran lock after the map shows another period
        public static void Refresh()
        {
            bool open = SurfaceOpen;
            if (open != wasOpen) { wasOpen = open; Changed?.Invoke(); }
            Set(Layer);
        }

        public static void Set(MapLayer layer)
        {
            if (!SurfaceOpen) layer = MapLayer.Under;
            if (layer == Layer) return;
            Layer = layer;
            Focus.Reset();
            Changed?.Invoke();
        }

        public static void Set(bool under) => Set(under ? MapLayer.Under : MapLayer.Surface);
        public static void Toggle()    => Set(On  ? MapLayer.Surface : MapLayer.Under);
        public static void ToggleSky() => Set(Sky ? MapLayer.Surface : MapLayer.Sky);

        // Whether a group belongs to a layer: its niche is there, or it visits it (see Niches tags)
        //  Surface: land tiles show their niches; water tiles the sea surface and the air-breathers coming up
        //  Under:   land tiles show the underground and the burrowers going down; water tiles their niches
        //  Sky:     fliers everywhere, and the summits
        public static bool InLayer(ColonyGroup g, MapLayer layer)
        {
            if (g == null || g.Definition == null || g.Cell == null) return false;
            var def = g.Definition;
            var home = Niches.LayerOf(g.Niche);
            return layer switch
            {
                MapLayer.Surface => home == MapLayer.Surface || (g.Cell.IsWater && Niches.IsSurfacer(def)),
                MapLayer.Under   => home == MapLayer.Under || (!g.Cell.IsWater && Niches.IsBurrower(def)),
                _                => home == MapLayer.Sky || Niches.IsFlyer(def),
            };
        }

        // Whether a group is drawn (and clickable) now: every group of the layer in sight
        // (FogOfWar), except on the selected tile, which shows one at a time (see Focus)
        public static bool Shows(ColonyGroup g)
        {
            if (!InLayer(g, Layer) || !FogOfWar.Reveals(g)) return false;
            return g.Cell != CellSelector.Selected || Focus.Current(g.Cell) == g;
        }

        // The selected tile shows its groups of the current layer one at a time, biggest first,
        // microbes and plankton last; Tab (or clicking the tile again) moves to the next.
        public static class Focus
        {
            private static HexCell cell;
            private static int index;
            public static int Version { get; private set; }

            public static List<ColonyGroup> Ordered(HexCell at)
            {
                var list = new List<ColonyGroup>();
                var colonies = SpeciesColonies.Instance;
                if (at == null || colonies == null) return list;
                foreach (var g in colonies.GroupsAt(at)) if (InLayer(g, Layer) && FogOfWar.Reveals(g)) list.Add(g);
                // the human player's own groups first, so a click on the tile picks yours
                static bool Mine(ColonyGroup g) => g.Owner != null && g.Owner.IsHuman;
                list.Sort((a, b) => Mine(a) != Mine(b) ? Mine(b).CompareTo(Mine(a))
                                  : Niches.IsTiny(a.Niche) != Niches.IsTiny(b.Niche) ? Niches.IsTiny(a.Niche).CompareTo(Niches.IsTiny(b.Niche))
                                  : b.Definition.sizeCm.CompareTo(a.Definition.sizeCm));
                return list;
            }

            public static ColonyGroup Current(HexCell at)
            {
                if (at != cell) { cell = at; index = 0; }
                var list = Ordered(at);
                return list.Count == 0 ? null : list[index % list.Count];
            }

            public static void Next(HexCell at)
            {
                if (at != cell) { cell = at; index = 0; }
                else index++;
                Version++;
            }

            public static void Show(ColonyGroup g)
            {
                if (g == null) return;
                var list = Ordered(g.Cell);
                int i = list.IndexOf(g);
                if (i < 0) return;
                cell = g.Cell; index = i; Version++;
            }

            public static void Reset() { cell = null; index = 0; Version++; }
        }

        // Underground animals can't enter, settle in or pass through solid bedrock
        public static bool Blocks(UnderKind kind) => kind == UnderKind.Bedrock;

        // Whether the layer below a tile is a bed of water (seabed, deep seabed, lakebed) rather than rock or caves
        public static bool IsWaterBed(UnderKind kind) => kind is UnderKind.Seabed or UnderKind.DeepSeabed or UnderKind.Lakebed;

        // Whether a soil or seabed species can live below this tile: not in solid bedrock, and
        // seabed dwellers only under water: on a seabed or lakebed, or in a sea cave (not in the
        // rock below the land, or a buried headland's rock under the sea)
        public static bool FitsBelow(SpeciesDefinition def, HexCell cell) =>
            (!Niches.InSoil(def) && !Niches.OnSeabed(def)) ||
            (!Blocks(cell.Under) && (!Niches.OnSeabed(def) || IsWaterBed(cell.Under) || (cell.IsWater && cell.Under == UnderKind.Cave)));

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
