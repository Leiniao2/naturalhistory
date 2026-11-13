using UnityEngine;

namespace NaturalHistory.World
{
    // Attach to Main Camera.
    //   Pan:  drag with any mouse button ("grab the map"), WASD / arrow keys, or screen-edge scroll
    //   Zoom: scroll wheel
    // The point the camera looks at is kept inside the HexGrid's bounds, whatever the map size.
    public class CameraController : MonoBehaviour
    {
        [Header("Pan")]
        [SerializeField] private float keyPanSpeed    = 1.2f; // map units per second, per unit of camera height
        [SerializeField] private bool  edgeScroll     = true;
        [SerializeField] private float edgeScrollSize = 20f;  // pixels from edge to trigger scroll
        [SerializeField] private float dragThreshold  = 6f;   // pixels moved before a press counts as a drag

        [Header("Zoom")]
        [SerializeField] private float zoomSpeed = 4f;
        [SerializeField] private float minHeight = 4f;
        [SerializeField] private float maxHeight = 70f;

        [Header("Bounds")]
        [SerializeField] private float boundsMargin = 2f; // how far past the map edge the view may go

        // True once the current/last mouse press moved far enough to be a drag.
        // CellSelector reads this so releasing a drag doesn't also click a hex.
        public static bool DraggedThisPress { get; private set; }

        private Camera cam;
        private Plane ground = new(Vector3.up, Vector3.zero);
        private int dragButton = -1;
        private Vector3 pressScreenPos;
        private Vector3 dragGrabPoint;
        private bool hasGrabPoint;

        private void Awake()
        {
            cam = GetComponent<Camera>();
            if (cam == null) cam = Camera.main;
        }

        private void Start()
        {
            var grid = HexGrid.Instance;
            if (grid == null) return;
            grid.Generated += FocusMapCenter;
            if (grid.IsGenerated) FocusMapCenter();
        }

        private void OnDestroy()
        {
            if (HexGrid.Instance != null) HexGrid.Instance.Generated -= FocusMapCenter;
        }

        private void Update()
        {
            HandleDrag();
            if (dragButton < 0)
            {
                HandleKeys();
                HandleEdgeScroll();
            }
            HandleZoom();
            ClampToMap();
        }

        private void HandleDrag()
        {
            if (dragButton < 0)
            {
                for (int b = 0; b <= 2; b++)
                {
                    if (!Input.GetMouseButtonDown(b)) continue;
                    dragButton       = b;
                    DraggedThisPress = false;
                    pressScreenPos   = Input.mousePosition;
                    hasGrabPoint     = TryGroundPoint(Input.mousePosition, out dragGrabPoint);
                    break;
                }
                if (dragButton < 0) return;
            }

            if (!DraggedThisPress && (Input.mousePosition - pressScreenPos).magnitude > dragThreshold)
                DraggedThisPress = true;

            // Keep the ground point grabbed at press time under the cursor.
            if (DraggedThisPress && hasGrabPoint && TryGroundPoint(Input.mousePosition, out var current))
            {
                var delta = dragGrabPoint - current;
                transform.position += new Vector3(delta.x, 0f, delta.z);
            }

            if (Input.GetMouseButtonUp(dragButton)) dragButton = -1;
        }

        private void HandleKeys()
        {
            var input = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"));
            if (input.sqrMagnitude < 0.01f) return;
            Pan(input.normalized * keyPanSpeed * transform.position.y * Time.deltaTime);
        }

        private void HandleEdgeScroll()
        {
            if (!edgeScroll || !Application.isFocused) return;
            var mp = Input.mousePosition;
            // Ignore the cursor when it's outside the window (e.g. elsewhere in the Unity editor)
            if (mp.x < 0 || mp.y < 0 || mp.x > Screen.width || mp.y > Screen.height) return;

            var dir = Vector2.zero;
            if (mp.x < edgeScrollSize)                 dir.x -= 1f;
            if (mp.x > Screen.width - edgeScrollSize)  dir.x += 1f;
            if (mp.y < edgeScrollSize)                 dir.y -= 1f;
            if (mp.y > Screen.height - edgeScrollSize) dir.y += 1f;
            if (dir != Vector2.zero)
                Pan(dir.normalized * keyPanSpeed * transform.position.y * Time.deltaTime);
        }

        // Move in screen-aligned directions on the ground plane (x = right, y = forward).
        private void Pan(Vector2 amount)
        {
            var right   = Vector3.ProjectOnPlane(transform.right,   Vector3.up).normalized;
            var forward = Vector3.ProjectOnPlane(transform.forward, Vector3.up).normalized;
            transform.position += right * amount.x + forward * amount.y;
        }

        // Zoom along the view direction so the point at screen center stays put.
        private void HandleZoom()
        {
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) < 0.001f) return;

            var fwd = transform.forward;
            if (fwd.y > -0.01f) return; // camera isn't looking down
            float targetY = Mathf.Clamp(transform.position.y - scroll * zoomSpeed * 10f, minHeight, maxHeight);
            float distance = (transform.position.y - targetY) / -fwd.y;
            transform.position += fwd * distance;
        }

        private void ClampToMap()
        {
            var grid = HexGrid.Instance;
            if (grid == null || !grid.IsGenerated) return;
            if (!TryGroundPoint(ScreenCenter, out var center)) return;

            var rect = grid.MapRectXZ;
            float x = Mathf.Clamp(center.x, rect.xMin - boundsMargin, rect.xMax + boundsMargin);
            float z = Mathf.Clamp(center.z, rect.yMin - boundsMargin, rect.yMax + boundsMargin);
            transform.position += new Vector3(x - center.x, 0f, z - center.z);
        }

        private void FocusMapCenter()
        {
            if (!TryGroundPoint(ScreenCenter, out var center)) return;
            var target = HexGrid.Instance.MapRectXZ.center;
            transform.position += new Vector3(target.x - center.x, 0f, target.y - center.z);
        }

        private static Vector3 ScreenCenter => new(Screen.width * 0.5f, Screen.height * 0.5f, 0f);

        private bool TryGroundPoint(Vector3 screenPos, out Vector3 point)
        {
            var ray = cam.ScreenPointToRay(screenPos);
            if (ground.Raycast(ray, out float dist)) { point = ray.GetPoint(dist); return true; }
            point = default;
            return false;
        }
    }
}
