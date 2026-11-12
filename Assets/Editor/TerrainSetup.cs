using UnityEngine;
using UnityEditor;
using NaturalHistory.World;

namespace NaturalHistory.Editor
{
    public static class TerrainSetup
    {
        static readonly (TerrainKind kind, TerrainCategory cat, Color color, float height)[] Definitions =
        {
            (TerrainKind.SaltWater,  TerrainCategory.Water, new Color(0.10f, 0.28f, 0.65f), 0.00f),
            (TerrainKind.FreshWater, TerrainCategory.Water, new Color(0.20f, 0.50f, 0.80f), 0.04f),
            (TerrainKind.Plain,      TerrainCategory.Land,  new Color(0.35f, 0.62f, 0.22f), 0.08f),
            (TerrainKind.Hill,       TerrainCategory.Land,  new Color(0.52f, 0.52f, 0.20f), 0.25f),
            (TerrainKind.Mountain,   TerrainCategory.Land,  new Color(0.48f, 0.46f, 0.44f), 0.55f),
            (TerrainKind.Desert,     TerrainCategory.Land,  new Color(0.82f, 0.72f, 0.35f), 0.06f),
            (TerrainKind.Wetland,    TerrainCategory.Land,  new Color(0.18f, 0.48f, 0.38f), 0.05f),
            (TerrainKind.Tundra,     TerrainCategory.Land,  new Color(0.68f, 0.78f, 0.76f), 0.15f),
            (TerrainKind.IceSheet,   TerrainCategory.Land,  new Color(0.88f, 0.93f, 0.98f), 0.38f),
        };

        [MenuItem("NaturalHistory/Setup Terrain Materials")]
        public static void SetupTerrainMaterials()
        {
            EnsureFolder("Assets/Resources/Terrains");

            foreach (var (kind, cat, color, height) in Definitions)
            {
                var assetPath = $"Assets/Resources/Terrains/{kind}.asset";
                var terrain = AssetDatabase.LoadAssetAtPath<TerrainType>(assetPath);
                if (terrain == null)
                {
                    terrain = ScriptableObject.CreateInstance<TerrainType>();
                    AssetDatabase.CreateAsset(terrain, assetPath);
                }
                terrain.kind         = kind;
                terrain.category     = cat;
                terrain.movementCost = 1f;
                terrain.color        = color;
                terrain.visualHeight = height;
                terrain.material     = null;
                EditorUtility.SetDirty(terrain);
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[TerrainSetup] Terrain assets updated for all 9 TerrainKinds.");
        }

        static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            var parts  = path.Split('/');
            var parent = parts[0];
            for (int i = 1; i < parts.Length; i++)
            {
                var full = parent + "/" + parts[i];
                if (!AssetDatabase.IsValidFolder(full))
                    AssetDatabase.CreateFolder(parent, parts[i]);
                parent = full;
            }
        }
    }
}
