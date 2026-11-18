using UnityEngine;

namespace NaturalHistory.World
{
    // The human player's start marker: a ball in their colours on the start hex. It stays there;
    // the player's animal groups are what move.
    public class PlayerBall : MonoBehaviour
    {
        [SerializeField] private float radius   = 0.35f;
        [SerializeField] private Color color    = new(0.9f, 0.2f, 0.15f);
        [SerializeField] private Color bandColor = new(0.95f, 0.9f, 0.8f);

        public HexCell Cell { get; private set; }

        private HexGrid grid;
        private MeshRenderer ballRenderer, bandRenderer;
        private TextMesh nameLabel;
        private string playerName;

        // Spawns a ball in any scene that has a HexGrid, so Game.unity doesn't need editing.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<PlayerBall>() != null) return;
            new GameObject("PlayerBall").AddComponent<PlayerBall>();
        }

        private void Start()
        {
            BuildVisual();
            grid = HexGrid.Instance;
            if (grid == null) { Debug.LogWarning("[PlayerBall] No HexGrid in scene."); return; }

            grid.Generated += PlaceOnStartCell;
            if (grid.IsGenerated) PlaceOnStartCell();
        }

        private void OnDestroy()
        {
            if (grid != null) grid.Generated -= PlaceOnStartCell;
        }

        private void BuildVisual()
        {
            var sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sphere.name = "Visual";
            Destroy(sphere.GetComponent<Collider>()); // clicks should pass through to the hex below
            sphere.transform.SetParent(transform, false);
            sphere.transform.localScale = Vector3.one * radius * 2f;
            ballRenderer = sphere.GetComponent<MeshRenderer>();

            // Second colour of the player's band, around the equator
            var band = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            band.name = "Band";
            Destroy(band.GetComponent<Collider>());
            band.transform.SetParent(transform, false);
            band.transform.localScale = new Vector3(radius * 2.08f, radius * 0.22f, radius * 2.08f);
            bandRenderer = band.GetComponent<MeshRenderer>();
            ApplyColors();
        }

        // The player's colour band and name (set by PlayerManager; may arrive before Start)
        public void SetColors(Color primary, Color secondary, string displayName)
        {
            color      = primary;
            bandColor  = secondary;
            playerName = displayName;
            ApplyColors();
        }

        private void ApplyColors()
        {
            if (ballRenderer == null) return;
            ballRenderer.material.color = color;
            bandRenderer.material.color = bandColor;
            if (string.IsNullOrEmpty(playerName)) return;
            if (nameLabel == null) nameLabel = Players.PlayerMarker.CreateLabel(transform, Core.Loc.T(playerName), color, radius + 0.15f);
            nameLabel.text  = Core.Loc.T(playerName); // a faction's default name is translated; a typed one stays
            nameLabel.color = Color.Lerp(color, Color.white, 0.55f);
        }

        // Start on the land cell closest to the map center (any cell if the map is all water).
        private void PlaceOnStartCell()
        {
            if (Players.PlayerManager.Instance != null) return; // it places the ball on the human player's start cell
            HexCell best = null;
            float bestDist = float.MaxValue;
            var center = new Vector2((grid.Width - 1) * 0.5f, (grid.Height - 1) * 0.5f);
            for (int r = 0; r < grid.Height; r++)
            for (int q = 0; q < grid.Width; q++)
            {
                var cell = grid.GetCell(q, r);
                if (cell == null) continue;
                float d = Vector2.Distance(new Vector2(q, r), center);
                if (cell.Terrain != null && cell.Terrain.IsWater) d += 1000f; // prefer land
                if (cell.IsMountain) d += 2000f;                               // never start inside a peak
                if (d < bestDist) { bestDist = d; best = cell; }
            }
            if (best != null) PlaceAt(best);
        }

        // Teleports the ball onto a cell (start of game, loading a save).
        public void PlaceAt(HexCell cell)
        {
            if (grid == null) grid = HexGrid.Instance; // may be called before Start
            Cell = cell;
            transform.position = StandPosition(cell);
            CameraController.Main?.Follow(transform, snap: true);
        }

        // Position is derived from the cell every frame, because map wrapping can move cells
        // (by a whole map width) at any time.
        private void LateUpdate()
        {
            if (Cell != null) transform.position = StandPosition(Cell);
        }

        private Vector3 StandPosition(HexCell cell) => cell.SurfacePosition + Vector3.up * radius;
    }
}
