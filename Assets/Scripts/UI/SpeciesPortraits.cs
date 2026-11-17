using System.Collections.Generic;
using NaturalHistory.Data;
using UnityEngine;

namespace NaturalHistory.UI
{
    // Portrait images of species for the UI, rendered once from their map model (species.json
    // "model") into a small texture: front three-quarter view, lit by the scene's sun, transparent
    // background. Species without a model get null.
    public static class SpeciesPortraits
    {
        private const int Size  = 256;
        private const int Layer = 31; // only the portrait camera draws this layer, far below the map

        private static readonly Dictionary<string, RenderTexture> cache = new();
        private static Camera camera;
        private static Material material;

        public static Texture Get(SpeciesDefinition species)
        {
            if (species == null || string.IsNullOrEmpty(species.model)) return null;
            if (cache.TryGetValue(species.id, out var cached) && cached != null) return cached;

            var prefab = Resources.Load<GameObject>(species.model);
            if (prefab == null) return null;
            if (material == null) material = Resources.Load<Material>("Materials/MapFeatures");

            var model = Object.Instantiate(prefab, new Vector3(0f, -1000f, 0f), Quaternion.identity);
            model.hideFlags = HideFlags.HideAndDontSave;
            var renderers = model.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) { Object.DestroyImmediate(model); return null; }
            var bounds = renderers[0].bounds;
            foreach (var r in renderers)
            {
                r.gameObject.layer = Layer;
                if (material != null) r.sharedMaterial = material; // vertex-coloured, like on the map
                var filter = r.GetComponent<MeshFilter>();
                var block = new MaterialPropertyBlock();
                block.SetVector(World.AnimalFur.FurId, World.AnimalFur.Of(species, filter != null ? filter.sharedMesh : null));
                r.SetPropertyBlock(block);
                bounds.Encapsulate(r.bounds);
            }

            var cam = PortraitCamera();
            float radius = Mathf.Max(bounds.extents.magnitude, 0.001f);
            var dir = new Vector3(0.75f, 0.45f, 1f).normalized; // models face +Z: look at them from the front-right
            cam.transform.position = bounds.center + dir * (radius / Mathf.Sin(cam.fieldOfView * 0.5f * Mathf.Deg2Rad)) * 1.05f;
            cam.transform.LookAt(bounds.center);
            cam.nearClipPlane = radius * 0.05f;
            cam.farClipPlane  = radius * 10f;

            var texture = new RenderTexture(Size, Size, 16, RenderTextureFormat.ARGB32) { antiAliasing = 4, name = $"Portrait_{species.id}" };
            cam.targetTexture = texture;
            cam.Render();
            cam.targetTexture = null;
            Object.DestroyImmediate(model);

            cache[species.id] = texture;
            return texture;
        }

        private static Camera PortraitCamera()
        {
            if (camera != null) return camera;
            var go = new GameObject("PortraitCamera") { hideFlags = HideFlags.HideAndDontSave };
            camera = go.AddComponent<Camera>();
            camera.enabled         = false; // renders only when asked
            camera.cullingMask     = 1 << Layer;
            camera.clearFlags      = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0f, 0f, 0f, 0f);
            camera.fieldOfView     = 30f;
            return camera;
        }
    }
}
