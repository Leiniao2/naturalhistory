using UnityEngine;

namespace NaturalHistory.World
{
    // Draws the fog of war (FogOfWar) over the map camera's image: each pixel's ground point from
    // the depth buffer, the tile under it, and that tile's state from the fog texture: cloud over
    // unexplored tiles, dimmed colours where nothing is in sight. One pass after everything else
    // (water, clouds, overlays), so every shader is covered without changes of its own.
    [RequireComponent(typeof(Camera))]
    public class FogOfWarEffect : MonoBehaviour
    {
        private static readonly int CornersId = Shader.PropertyToID("_FrustumCorners");

        private Camera cam;
        private Material material;

        // Adds the pass to the map camera while the fog is on; it does nothing while it is off
        public static void Ensure(bool on)
        {
            var main = CameraController.Main != null ? CameraController.Main.GetComponent<Camera>() : Camera.main;
            if (main == null) return;
            var effect = main.GetComponent<FogOfWarEffect>();
            if (effect == null && on) effect = main.gameObject.AddComponent<FogOfWarEffect>();
            if (effect != null) effect.enabled = on;
        }

        private void OnEnable()
        {
            cam = GetComponent<Camera>();
            cam.depthTextureMode |= DepthTextureMode.Depth;
            if (material == null)
            {
                var shader = Resources.Load<Shader>("Shaders/FogOfWar");
                if (shader == null || !shader.isSupported) { Debug.LogWarning("[FogOfWar] Missing or unsupported Shaders/FogOfWar"); enabled = false; return; }
                material = new Material(shader) { name = "FogOfWar", hideFlags = HideFlags.HideAndDontSave };
            }
        }

        private void OnDestroy()
        {
            if (material != null) Destroy(material);
        }

        private void OnRenderImage(RenderTexture source, RenderTexture destination)
        {
            if (material == null || cam == null) { Graphics.Blit(source, destination); return; }
            // World-space rays to the frustum corners at one unit of view depth: bottom-left,
            // bottom-right, top-left, top-right
            var corners = new Vector3[4];
            cam.CalculateFrustumCorners(new Rect(0, 0, 1, 1), 1f, Camera.MonoOrStereoscopicEye.Mono, corners);
            var m = Matrix4x4.identity;
            m.SetRow(0, cam.transform.TransformVector(corners[0]));
            m.SetRow(1, cam.transform.TransformVector(corners[3]));
            m.SetRow(2, cam.transform.TransformVector(corners[1]));
            m.SetRow(3, cam.transform.TransformVector(corners[2]));
            material.SetMatrix(CornersId, m);
            Graphics.Blit(source, destination, material);
        }
    }
}
