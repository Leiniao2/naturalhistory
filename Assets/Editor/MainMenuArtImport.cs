using UnityEditor;

namespace NaturalHistory.Editor
{
    // The title screen's paintings (Resources/UI/MainMenu) fill the screen: full size, high-quality
    // compression, no mipmaps (they are always drawn at about their own size), clamped edges.
    public class MainMenuArtImport : AssetPostprocessor
    {
        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith("Assets/Resources/UI/MainMenu/")) return;
            var importer = (TextureImporter)assetImporter;
            importer.textureType        = TextureImporterType.Default;
            importer.maxTextureSize     = 4096;
            importer.textureCompression = TextureImporterCompression.CompressedHQ;
            importer.wrapMode           = UnityEngine.TextureWrapMode.Clamp;
            importer.npotScale          = TextureImporterNPOTScale.None;
            importer.mipmapEnabled      = false;
        }
    }
}
