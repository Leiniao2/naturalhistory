using System.Reflection;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using NaturalHistory.World;
using NaturalHistory.Core;
using NaturalHistory.Biology;

namespace NaturalHistory.Editor
{
    public static class SceneSetup
    {
        [MenuItem("NaturalHistory/Setup Game Scene")]
        public static void SetupGameScene()
        {
            if (Application.isPlaying)
            {
                Debug.LogError("[SceneSetup] Exit Play mode before running Setup Game Scene.");
                return;
            }

            EnsureFolder("Assets/Scenes");
            EnsureFolder("Assets/Prefabs");
            EnsureFolder("Assets/Resources");
            EnsureFolder("Assets/Resources/Terrains");

            // Create all terrain assets first so they have material=null and correct colors
            TerrainSetup.SetupTerrainMaterials();

            // --- TerrainType ScriptableObject (Plain, no URP material) ---
            const string terrainPath = "Assets/Resources/Terrains/Plain.asset";
            var terrain = AssetDatabase.LoadAssetAtPath<TerrainType>(terrainPath);
            if (terrain == null) { Debug.LogError("[SceneSetup] Failed to load Plain terrain asset!"); return; }

            // --- Base material for cells (built-in Unlit/Color) ---
            EnsureFolder("Assets/Materials");
            const string basMatPath = "Assets/Materials/HexBase.mat";
            AssetDatabase.DeleteAsset(basMatPath); // always rebuild with correct shader
            var baseMat = (Material)null;
            if (baseMat == null)
            {
                baseMat = FindUrpMaterial();
                if (baseMat == null) { Debug.LogError("[SceneSetup] Cannot find a URP material."); return; }
                var clone = new Material(baseMat) { name = "HexBase" };
                clone.color = Color.white;
                AssetDatabase.CreateAsset(clone, basMatPath);
                AssetDatabase.SaveAssets();
                baseMat = AssetDatabase.LoadAssetAtPath<Material>(basMatPath);
            }

            // --- HexCell prefab (plain GO — no CreatePrimitive to avoid legacy material) ---
            const string prefabPath = "Assets/Prefabs/HexCell.prefab";
            AssetDatabase.DeleteAsset(prefabPath); // always rebuild so material is fresh
            {
                var cellGO = new GameObject("HexCell");
                cellGO.AddComponent<MeshFilter>();
                var mr = cellGO.AddComponent<MeshRenderer>();
                mr.sharedMaterial = baseMat;
                cellGO.AddComponent<HexCell>();
                PrefabUtility.SaveAsPrefabAsset(cellGO, prefabPath);
                Object.DestroyImmediate(cellGO);
                AssetDatabase.SaveAssets();
                AssetDatabase.Refresh();
            }
            var existingPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            if (existingPrefab == null) { Debug.LogError("[SceneSetup] Failed to create HexCell prefab!"); return; }

            // Reload assets fresh — references go stale when NewScene unloads the current scene
            AssetDatabase.SaveAssets();
            terrain        = AssetDatabase.LoadAssetAtPath<TerrainType>(terrainPath);
            existingPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            if (terrain == null || existingPrefab == null)
            {
                Debug.LogError("[SceneSetup] Asset reload failed before scene creation.");
                return;
            }

            // --- New scene ---
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

            // --- Camera: look at grid center from above ---
            var cam = Object.FindAnyObjectByType<Camera>();
            if (cam != null)
            {
                var gridCenter = new Vector3(10f, 0f, 5f);
                cam.transform.position = gridCenter + new Vector3(0f, 20f, -10f);
                cam.transform.LookAt(gridCenter);
                cam.gameObject.AddComponent<CameraController>();
                cam.gameObject.AddComponent<CellSelector>();
                Debug.Log($"[SceneSetup] Camera set to {cam.transform.position}, looking at {gridCenter}");
            }
            else
            {
                Debug.LogWarning("[SceneSetup] No Camera found in scene!");
            }

            // --- _Managers ---
            var managersGO = new GameObject("_Managers");
            var gm = managersGO.AddComponent<GameManager>();
            var am = managersGO.AddComponent<AgeManager>();
            var tm = managersGO.AddComponent<TurnManager>();
            managersGO.AddComponent<SpeciesManager>();

            var gmSO = new SerializedObject(gm);
            gmSO.FindProperty("ageManager").objectReferenceValue = am;
            gmSO.FindProperty("turnManager").objectReferenceValue = tm;
            gmSO.ApplyModifiedProperties();

            // --- HexGrid ---
            var gridGO = new GameObject("HexGrid");
            var grid = gridGO.AddComponent<HexGrid>();

            // Use reflection to reliably set private [SerializeField] fields
            var flags = BindingFlags.NonPublic | BindingFlags.Instance;
            var gridType = typeof(HexGrid);
            var cellPrefabComp = existingPrefab.GetComponent<HexCell>();
            gridType.GetField("cellPrefab", flags)?.SetValue(grid, cellPrefabComp);
            gridType.GetField("defaultTerrain", flags)?.SetValue(grid, terrain);
            EditorUtility.SetDirty(grid);
            Debug.Log($"[SceneSetup] HexGrid refs — cellPrefab={cellPrefabComp != null}, defaultTerrain={terrain != null}");

            // --- Save scene ---
            EditorSceneManager.SaveScene(scene, "Assets/Scenes/Game.unity");

            // --- Build Settings ---
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene("Assets/Scenes/Game.unity", true)
            };

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("[SceneSetup] Done! Press Play to see the hex grid.");
        }

        private static Material FindUrpMaterial()
        {
            // Built-in renderer — Standard shader gives per-face lighting so 3D height is visible.
            var shader = Shader.Find("Standard");
            if (shader == null) { Debug.LogError("[SceneSetup] Cannot find Standard shader!"); return null; }
            var mat = new Material(shader) { color = Color.white };
            mat.SetFloat("_Glossiness", 0.05f);
            mat.SetFloat("_Metallic",   0f);
            return mat;
        }

        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            var parts = path.Split('/');
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
