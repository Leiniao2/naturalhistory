using UnityEngine;

namespace NaturalHistory.World
{
    public enum TerrainCategory { Land, Water }

    public enum TerrainKind
    {
        // Water
        SaltWater,
        FreshWater,
        // Land
        Plain,
        Hill,
        Mountain,
        Desert,
        Wetland,
        Tundra,
        IceSheet,
        // Added later; appended so existing assets keep their serialized values
        Savanna,
        Rainforest,
        Steppe,
        // Ground cover of earlier periods (see EraFlora): what the climate biomes looked like
        // before grasses, flowering plants or any land plants at all
        Barren,       // bare rock and regolith, before land plants
        MicrobialMat, // damp flats crusted with microbial mats and stromatolites
        Mossland,     // mosses, liverworts and the first small vascular plants
        FernPrairie,  // open ground covered in ferns and horsetails, before grasses
        CoalSwamp     // Carboniferous peat swamp
    }

    // Overlay on top of a cell's terrain (Civ-style). Chosen by WorldGenerator from climate.
    public enum TerrainFeature
    {
        None,
        BroadleafForest,
        ConiferForest,
        Jungle,   // dense tropical canopy on rainforest / hot wetland
        Reef,     // coral in warm shallow water
        Oasis,    // pond and palms in the desert
        Volcano,  // replaces the peaks on a few mountains
        Geothermal, // hot springs, geysers and fumaroles on lowland near volcanoes
        // Landforms (HexGrid.PlaceLandforms)
        Mesa,         // flat-topped table of layered rock in dry country
        Canyon,       // a gorge cut in terraces through a dry plateau
        Fjord,        // a narrow arm of the sea between sheer highland walls (cold coasts)
        WhiteCliffs,  // chalk cliffs on the coast (from the Cretaceous, when chalk was laid down)
        SaltLake,     // white salt pan with milky brine
        PinkSaltLake, // the same, the brine pink with salt-loving microbes
        Danxia,       // rainbow-striped sandstone hills
        Karst,        // limestone towers among pools, in warm wet country
    }

    [CreateAssetMenu(menuName = "NaturalHistory/TerrainType")]
    public class TerrainType : ScriptableObject
    {
        public TerrainKind kind;
        public TerrainCategory category;
        [Range(0f, 1f)] public float movementCost;
        public Color color = Color.white;
        public float visualHeight = 0.1f;
        public Material material; // optional override; if null, color is applied to the cell's base material
        [TextArea] public string description;

        public bool IsWater => category == TerrainCategory.Water;
        public bool IsHabitable => kind is TerrainKind.Plain or TerrainKind.Hill or
                                          TerrainKind.Wetland or TerrainKind.Desert or
                                          TerrainKind.Savanna or TerrainKind.Rainforest or TerrainKind.Steppe or
                                          TerrainKind.Barren or TerrainKind.MicrobialMat or TerrainKind.Mossland or
                                          TerrainKind.FernPrairie or TerrainKind.CoalSwamp or
                                          TerrainKind.FreshWater or TerrainKind.SaltWater;
    }
}
