using System;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.World
{
    // Left-click selects a hex (the tile panel, ClimateHud, shows what it is)
    public class CellSelector : MonoBehaviour
    {
        public static HexCell Selected { get; private set; }

        // Fired on every left-click that lands on a hex
        public static event Action<HexCell> CellClicked;

        private Camera cam;

        private void Awake()
        {
            cam = GetComponent<Camera>() ?? Camera.main;
        }

        private void Update()
        {
            // Act on release so a left-drag that pans the camera doesn't also click a hex
            if (!Input.GetMouseButtonUp(0) || CameraController.DraggedThisPress) return;

            var ray = cam.ScreenPointToRay(Input.mousePosition);
            var cell = Physics.Raycast(ray, out var hit) ? hit.collider.GetComponent<HexCell>() : null;
            Select(cell);
            if (cell != null) CellClicked?.Invoke(cell);
        }

        private static void Select(HexCell cell)
        {
            if (Selected == cell) return;
            if (Selected != null) Selected.SetHighlight(false);
            Selected = cell;
            if (Selected != null) Selected.SetHighlight(true);
        }
    }
}
