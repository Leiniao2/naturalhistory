using UnityEngine;

namespace NaturalHistory.Players
{
    // A banner in the player's two colours with their name above it, planted on their start cell.
    // It is a child of the cell, so it follows the east–west wrap and goes away when the map regenerates.
    public class PlayerMarker : MonoBehaviour
    {
        public static PlayerMarker Create(Player player, Transform cell, Vector3 localSurface)
        {
            var go = new GameObject($"Banner {player.Name}");
            go.transform.SetParent(cell, false);
            go.transform.localPosition = localSurface + new Vector3(0.18f, 0f, 0.12f); // off-centre, next to colonies and props
            var marker = go.AddComponent<PlayerMarker>();
            marker.Build(player);
            return marker;
        }

        private void Build(Player player)
        {
            const float poleHeight = 0.8f;
            AddPart(PrimitiveType.Cylinder, new Vector3(0f, poleHeight * 0.5f, 0f), new Vector3(0.035f, poleHeight * 0.5f, 0.035f), new Color(0.25f, 0.2f, 0.15f));
            // Flag: primary over secondary
            AddPart(PrimitiveType.Cube, new Vector3(0.2f, poleHeight - 0.07f, 0f), new Vector3(0.36f, 0.14f, 0.02f), player.Primary);
            AddPart(PrimitiveType.Cube, new Vector3(0.2f, poleHeight - 0.21f, 0f), new Vector3(0.36f, 0.14f, 0.02f), player.Secondary);
            CreateLabel(transform, player.Name, player.Primary, poleHeight + 0.2f);
        }

        private void AddPart(PrimitiveType type, Vector3 position, Vector3 scale, Color color)
        {
            var part = GameObject.CreatePrimitive(type);
            Destroy(part.GetComponent<Collider>()); // clicks go through to the hex
            part.transform.SetParent(transform, false);
            part.transform.localPosition = position;
            part.transform.localScale = scale;
            part.GetComponent<MeshRenderer>().material.color = color;
        }

        // World-space name tag, also used above the player's own unit
        public static TextMesh CreateLabel(Transform parent, string text, Color color, float height)
        {
            var go = new GameObject("Name");
            go.transform.SetParent(parent, false);
            go.transform.localPosition = Vector3.up * height;
            var mesh = go.AddComponent<TextMesh>();
            mesh.font          = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            mesh.text          = text;
            mesh.fontSize      = 48;
            mesh.characterSize = 0.03f;
            mesh.anchor        = TextAnchor.LowerCenter;
            mesh.alignment     = TextAlignment.Center;
            mesh.color         = Color.Lerp(color, Color.white, 0.55f);
            go.GetComponent<MeshRenderer>().sharedMaterial = mesh.font.material;
            go.AddComponent<FaceCamera>();
            return mesh;
        }
    }

    // Keeps a label turned toward the camera
    public class FaceCamera : MonoBehaviour
    {
        private void LateUpdate()
        {
            var cam = Camera.main;
            if (cam != null) transform.rotation = cam.transform.rotation;
        }
    }
}
