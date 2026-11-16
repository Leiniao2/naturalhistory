using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.Editor
{
    // The menus' PanelSettings as an asset (Resources/UI/NHPanelSettings), created here if missing.
    // Only a PanelSettings made in the editor gets the ICU data UI Toolkit's text shaping needs; one
    // created at runtime has none, and in a build every label then fails to draw (GameMenus loads this).
    public static class PanelSettingsAsset
    {
        public const string Path = "Assets/Resources/UI/NHPanelSettings.asset";

        [InitializeOnLoadMethod]
        private static void OnLoad() => EditorApplication.delayCall += () => Ensure();

        public static PanelSettings Ensure()
        {
            var existing = AssetDatabase.LoadAssetAtPath<PanelSettings>(Path);
            if (existing != null) return existing;
            var settings = ScriptableObject.CreateInstance<PanelSettings>();
            settings.themeStyleSheet     = AssetDatabase.LoadAssetAtPath<ThemeStyleSheet>("Assets/Resources/UI/NHRuntimeTheme.tss");
            settings.scaleMode           = PanelScaleMode.ScaleWithScreenSize;
            settings.referenceResolution = new Vector2Int(1920, 1080);
            settings.match               = 0.5f;
            AssetDatabase.CreateAsset(settings, Path);
            AssetDatabase.SaveAssets();
            Debug.Log($"[PanelSettingsAsset] Created {Path}");
            return settings;
        }
    }
}
