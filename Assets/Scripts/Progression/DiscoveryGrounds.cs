using System.Collections.Generic;
using NaturalHistory.Core;
using NaturalHistory.World;

namespace NaturalHistory.Progression
{
    // The kinds of ground a discovery card can be about (Discoveries): their names and a short
    // introduction each (English here; translations in Localization).
    public static class Grounds
    {
        public static readonly Dictionary<TerrainKind, (string name, string text)> Terrains = new()
        {
            [TerrainKind.MicrobialMat] = ("Microbial mats", "Damp flats crusted with layers of microbes that trap sediment and build stromatolites: the oldest ecosystems on Earth, making oxygen for billions of years."),
            [TerrainKind.Mossland]     = ("Mossland", "Mosses, liverworts and the first small vascular plants: the green film that first covered the land and began to make soil."),
            [TerrainKind.FernPrairie]  = ("Fern prairie", "Open country covered in ferns and horsetails, the meadows of the world long before grasses evolved."),
            [TerrainKind.Rainforest]   = ("Rainforest", "Warm, wet forest with layer upon layer of life: the richest habitat on land, home to most land species."),
            [TerrainKind.Desert]       = ("Desert", "Dry country where little rain falls: its life saves water, shelters by day and comes out at night."),
            [TerrainKind.Wetland]      = ("Wetland", "Swamps and marshes between land and water, where many of the first land animals and plants took hold."),
            [TerrainKind.Savanna]      = ("Savanna", "Warm grassland dotted with trees, grazed by great herds and hunted by their predators."),
            [TerrainKind.Steppe]       = ("Steppe", "Cool, dry grassland stretching to the horizon, where speed and endurance pay."),
            [TerrainKind.Tundra]       = ("Tundra", "Cold treeless land frozen for much of the year, with a brief, busy summer."),
            [TerrainKind.IceSheet]     = ("Ice sheet", "A dome of ice kilometres thick; little lives on it, but its cold edges feed rich seas."),
        };

        public static readonly Dictionary<TerrainFeature, (string name, string text)> Features = new()
        {
            [TerrainFeature.Reef]         = ("Reef", "Built by living things over countless generations: stromatolites, sponges, then corals. Reefs shelter a crowd of sea life."),
            [TerrainFeature.Oasis]        = ("Oasis", "Water in the desert: a pond fed from underground, a refuge every desert animal knows."),
            [TerrainFeature.Volcano]      = ("Volcano", "Molten rock breaking through the crust; its ash and lava destroy, then make some of the most fertile ground there is."),
            [TerrainFeature.Geothermal]   = ("Geothermal field", "Hot springs, geysers and steaming vents where heat-loving microbes paint the ground in bright colours."),
            [TerrainFeature.Mesa]         = ("Mesa", "A flat-topped table of layered rock left standing as the land around it wore away."),
            [TerrainFeature.Canyon]       = ("Canyon", "A deep gorge cut by a river through layer after layer of rock, a record of millions of years."),
            [TerrainFeature.WhiteCliffs]  = ("White cliffs", "Chalk cliffs made of the skeletons of countless tiny sea algae that lived in Cretaceous seas."),
            [TerrainFeature.SaltLake]     = ("Salt lake", "A lake with no outlet, where the water evaporates and leaves a white crust of salt."),
            [TerrainFeature.PinkSaltLake] = ("Pink salt lake", "A salt lake coloured pink by salt-loving microbes and algae thriving where little else can."),
            [TerrainFeature.Danxia]       = ("Danxia (rainbow hills)", "Hills of red sandstone striped in many colours, laid down in ancient deserts and lakes."),
            [TerrainFeature.Karst]        = ("Karst towers", "Limestone towers and caves dissolved by rain over millions of years, full of hidden waters."),
            [TerrainFeature.Jungle]       = ("Jungle", "A dense tropical canopy so thick that little light reaches the ground."),
            [TerrainFeature.BroadleafForest] = ("Broadleaf forest", "A forest of leafy trees that shade and feed a great web of life beneath them."),
            [TerrainFeature.ConiferForest]   = ("Conifer forest", "Evergreen cone-bearing trees, the oldest kind of forest still standing today."),
        };

        public static readonly Dictionary<UnderFeature, (string name, string text)> UnderFeatures = new()
        {
            [UnderFeature.Volcano]    = ("Underwater volcano", "A seamount rising from the sea floor; its slopes gather sea life and its eruptions remake the sea bed."),
            [UnderFeature.Vents]      = ("Hydrothermal vents", "Black smokers pouring out hot, mineral-rich water: in the dark, whole communities live on chemical energy instead of sunlight, perhaps as the first life did."),
            [UnderFeature.Geothermal] = ("Shallow hydrothermal field", "White smokers, gas seeps and sulphur on a shallow sea floor, covered in bacterial mats."),
        };

        public static Discoveries.Discovery Card(TerrainKind kind) => Make(Terrains[kind]);
        public static Discoveries.Discovery Card(TerrainFeature f)  => Make(Features[f]);
        public static Discoveries.Discovery Card(UnderFeature f)    => Make(UnderFeatures[f]);

        public static Discoveries.Discovery StromatoliteCard() => Make(("Stromatolite sea floor",
            "Domes and mounds built layer by layer by microbial mats, the first reefs and for most of Earth's history its most common sign of life."));

        private static Discoveries.Discovery Make((string name, string text) g) => new() { title = Loc.T(g.name), text = Loc.T(g.text) };
    }
}
