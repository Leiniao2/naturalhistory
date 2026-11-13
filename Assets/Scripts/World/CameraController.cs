using UnityEngine;

namespace NaturalHistory.World
{
    // Attach to Main Camera.
    //   Pan:  drag with any mouse button ("grab the map"), WASD / arrow keys, or screen-edge scroll
    //   Zoom: scroll wheel
    //   Follow: keeps the followed unit (the player) centred; panning looks away, Space snaps back
    // The map wraps east–west, so the view loops around horizontally; north–south it is kept
    // inside the HexGrid's bounds.
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

        [Header("Follow")]
        [SerializeField] private float followSharpness = 8f; // higher = catches up faster
        [SerializeField] private KeyCode recenterKey   = KeyCode.Space;

        [Header("Bounds")]
        [SerializeField] private float boundsMargin = 2f; // how far past the map edge the view may go

        // True once the current/last mouse press moved far enough to be a drag.
        // CellSelector reads this so releasing a drag doesn't also click a hex.
        public static bool DraggedThisPress { get; private set; }

        public static CameraController Main { get; private set; }

        private Transform followTarget;
        private bool following;
        private bool snapToTarget;

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
            Main = this;
        }

        // Keep `target` centred from now on. snap = jump there this frame instead of gliding.
        public void Follow(Transform target, bool snap = false)
        {
            followTarget = target;
            following    = target != null;
            snapToTarget |= snap;
        }

        // Re-centre on the followed unit after the player has panned away.
        public void ResumeFollow() => following = followTarget != null;

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
            if (Main == this) Main = null;
        }

        private void Update()
        {
            HandleDrag();
            if (dragButton < 0)
            {
                HandleKeys();
                HandleEdgeScroll();
            }
            if (Input.GetKeyDown(recenterKey)) ResumeFollow();
            HandleFollow();
            HandleZoom();
            ClampAndWrap();
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
                following = false;
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
            following = false;
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

        // Glide so the followed unit sits at screen centre. Measured on the plane at the unit's
        // height, so units on high terrain are centred too, not the ground below them.
        private void HandleFollow()
        {
            if (!following || followTarget == null) return;
            var target = followTarget.position;
            var ray = cam.ScreenPointToRay(ScreenCenter);
            if (!new Plane(Vector3.up, target).Raycast(ray, out float dist)) return;

            var delta = target - ray.GetPoint(dist);
            float t = snapToTarget ? 1f : 1f - Mathf.Exp(-followSharpness * Time.deltaTime);
            snapToTarget = false;
            transform.position += new Vector3(delta.x, 0f, delta.z) * t;
        }

        // North–south: keep the view on the map. East–west: once the view is more than half a
        // map width from the map's centre, jump one map width back (the wrapped cells make that
        // invisible), then move the cells to the copy of the world nearest the view.
        private void ClampAndWrap()
        {
            var grid = HexGrid.Instance;
            if (grid == null || !grid.IsGenerated) return;
            if (!TryGroundPoint(ScreenCenter, out var center)) return;

            var rect = grid.MapRectXZ;
            float z = Mathf.Clamp(center.z, rect.yMin - boundsMargin, rect.yMax + boundsMargin);
            float wrap = grid.WrapWidth;
            float x = center.x - Mathf.Round((center.x - rect.center.x) / wrap) * wrap;
            transform.position += new Vector3(x - center.x, 0f, z - center.z);
            dragGrabPoint.x += x - center.x; // a drag in progress keeps holding the same spot
            grid.RecenterWrap(x);
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
