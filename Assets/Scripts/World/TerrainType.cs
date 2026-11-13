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
        IceSheet
    }

    // Overlay on top of a cell's terrain (Civ-style). Chosen by WorldGenerator from climate.
    public enum TerrainFeature
    {
        None,
        BroadleafForest,
        ConiferForest
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
                                          TerrainKind.FreshWater or TerrainKind.SaltWater;
    }
}
