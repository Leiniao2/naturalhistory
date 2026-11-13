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
        Steppe
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
        Volcano   // replaces the peaks on a few mountains
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
                                          TerrainKind.FreshWater or TerrainKind.SaltWater;
    }
}
