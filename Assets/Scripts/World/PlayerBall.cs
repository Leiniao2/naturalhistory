using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Placeholder player unit: a ball that sits on a hex and hops to a neighboring hex
    // when that hex is clicked. Reachable neighbors are tinted yellow.
    public class PlayerBall : MonoBehaviour
    {
        [SerializeField] private float radius   = 0.35f;
        [SerializeField] private float moveTime = 0.25f; // seconds per hop
        [SerializeField] private float hopHeight = 0.4f;
        [SerializeField] private Color color    = new(0.9f, 0.2f, 0.15f);

        public HexCell Cell { get; private set; }

        private HexGrid grid;
        private readonly List<HexCell> moveTargets = new();
        private bool moving;
        private HexCell hopFrom; // cell being left during a hop
        private float hopT;      // 0..1 progress of the current hop

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
            CellSelector.CellClicked += OnCellClicked;
        }

        private void OnDestroy()
        {
            if (grid != null) grid.Generated -= PlaceOnStartCell;
            CellSelector.CellClicked -= OnCellClicked;
        }

        private void BuildVisual()
        {
            var sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sphere.name = "Visual";
            Destroy(sphere.GetComponent<Collider>()); // clicks should pass through to the hex below
            sphere.transform.SetParent(transform, false);
            sphere.transform.localScale = Vector3.one * radius * 2f;
            sphere.GetComponent<MeshRenderer>().material.color = color;
        }

        // Start on the land cell closest to the map center (any cell if the map is all water).
        private void PlaceOnStartCell()
        {
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
            StopAllCoroutines();
            moving = false;
            SetCell(cell);
            transform.position = StandPosition(cell);
            CameraController.Main?.Follow(transform, snap: true);
        }

        private void OnCellClicked(HexCell target)
        {
            if (moving || Cell == null || target == Cell) return;
            if (!moveTargets.Contains(target)) return;
            CameraController.Main?.ResumeFollow();
            StartCoroutine(HopTo(target));
        }

        private IEnumerator HopTo(HexCell target)
        {
            moving  = true;
            hopFrom = Cell;
            SetCell(target);
            for (hopT = 0f; hopT < 1f; hopT += Time.deltaTime / moveTime)
                yield return null;
            moving = false;
        }

        // Position is derived from the cells every frame, because map wrapping can move cells
        // (by a whole map width) at any time.
        private void LateUpdate()
        {
            if (Cell == null) return;
            if (!moving) { transform.position = StandPosition(Cell); return; }

            var from = StandPosition(hopFrom);
            var to   = StandPosition(Cell);
            // Hopping across the wrap seam: use the copy of the start cell next to the target
            if (grid != null) from.x += Mathf.Round((to.x - from.x) / grid.WrapWidth) * grid.WrapWidth;
            var p = Vector3.Lerp(from, to, hopT);
            p.y += Mathf.Sin(hopT * Mathf.PI) * hopHeight;
            transform.position = p;
        }

        private void SetCell(HexCell cell)
        {
            foreach (var c in moveTargets) c.SetMoveTarget(false);
            moveTargets.Clear();

            Cell = cell;
            moveTargets.AddRange(grid.GetNeighbors(cell).FindAll(n => !n.IsMountain)); // mountains are impassable
            foreach (var c in moveTargets) c.SetMoveTarget(true);
        }

        private Vector3 StandPosition(HexCell cell) => cell.SurfacePosition + Vector3.up * radius;
    }
}
