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
        }

        private void OnCellClicked(HexCell target)
        {
            if (moving || Cell == null || target == Cell) return;
            if (!moveTargets.Contains(target)) return;
            StartCoroutine(HopTo(target));
        }

        private IEnumerator HopTo(HexCell target)
        {
            moving = true;
            var from = transform.position;
            var to   = StandPosition(target);
            SetCell(target);

            for (float t = 0f; t < 1f; t += Time.deltaTime / moveTime)
            {
                var p = Vector3.Lerp(from, to, t);
                p.y += Mathf.Sin(t * Mathf.PI) * hopHeight;
                transform.position = p;
                yield return null;
            }
            transform.position = to;
            moving = false;
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
