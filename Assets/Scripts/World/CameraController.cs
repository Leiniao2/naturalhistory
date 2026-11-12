using UnityEngine;

namespace NaturalHistory.World
{
    // Attach to Main Camera. Pan with middle-mouse drag or edge scroll; zoom with scroll wheel.
    public class CameraController : MonoBehaviour
    {
        [Header("Pan")]
        [SerializeField] private float panSpeed       = 0.3f;
        [SerializeField] private float edgeScrollSize = 20f; // pixels from edge to trigger scroll

        [Header("Zoom")]
        [SerializeField] private float zoomSpeed = 4f;
        [SerializeField] private float minHeight = 4f;
        [SerializeField] private float maxHeight = 40f;

        [Header("Bounds (world XZ)")]
        [SerializeField] private float minX = -5f;
        [SerializeField] private float maxX = 30f;
        [SerializeField] private float minZ = -5f;
        [SerializeField] private float maxZ = 20f;

        private bool isDragging;
        private Vector3 dragOrigin;

        private void Update()
        {
            HandlePan();
            HandleZoom();
            ClampPosition();
        }

        private void HandlePan()
        {
            var delta = Vector3.zero;

            // Middle-mouse drag
            if (Input.GetMouseButtonDown(2))
            {
                isDragging = true;
                dragOrigin = Input.mousePosition;
            }
            if (Input.GetMouseButtonUp(2)) isDragging = false;

            if (isDragging)
            {
                var diff = Input.mousePosition - dragOrigin;
                dragOrigin = Input.mousePosition;
                delta -= new Vector3(diff.x, 0f, diff.y) * panSpeed * 0.05f;
            }

            // Edge scrolling
            var mp = Input.mousePosition;
            if (mp.x < edgeScrollSize)  delta.x -= panSpeed * Time.deltaTime * 10f;
            if (mp.x > Screen.width  - edgeScrollSize) delta.x += panSpeed * Time.deltaTime * 10f;
            if (mp.y < edgeScrollSize)  delta.z -= panSpeed * Time.deltaTime * 10f;
            if (mp.y > Screen.height - edgeScrollSize) delta.z += panSpeed * Time.deltaTime * 10f;

            transform.position += delta;
        }

        private void HandleZoom()
        {
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) < 0.001f) return;

            var pos = transform.position;
            pos.y -= scroll * zoomSpeed * 10f;
            pos.y  = Mathf.Clamp(pos.y, minHeight, maxHeight);
            transform.position = pos;
        }

        private void ClampPosition()
        {
            var pos = transform.position;
            pos.x = Mathf.Clamp(pos.x, minX, maxX);
            pos.z = Mathf.Clamp(pos.z, minZ, maxZ);
            transform.position = pos;
        }
    }
}
