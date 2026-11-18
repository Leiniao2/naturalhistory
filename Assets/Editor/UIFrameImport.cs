using UnityEditor;

namespace NaturalHistory.Editor
{
    // Menu frame textures (Resources/UI/Frames, made by tools/ui/make_frames.py) are 9-sliced by
    // GameMenusStyle.uss: keep their thin brass lines crisp — no compression, clamped edges.
    public class UIFrameImport : AssetPostprocessor
    {
        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith("Assets/Resources/UI/Frames/")) return;
            var importer = (TextureImporter)assetImporter;
            importer.textureType         = TextureImporterType.Default;
            importer.textureCompression  = TextureImporterCompression.Uncompressed;
            importer.alphaIsTransparency = true;
            importer.wrapMode            = UnityEngine.TextureWrapMode.Clamp;
            importer.npotScale           = TextureImporterNPOTScale.None;
            importer.mipmapEnabled       = true;
        }
    }
}
