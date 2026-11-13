using System;
using UnityEngine;

namespace NaturalHistory.World
{
    public class CellSelector : MonoBehaviour
    {
        public static HexCell Selected { get; private set; }

        // Fired on every left-click that lands on a hex
        public static event Action<HexCell> CellClicked;

        private Camera cam;
        private GUIStyle boxStyle;

        private void Awake()
        {
            cam = GetComponent<Camera>() ?? Camera.main;
        }

        private void Update()
        {
            if (!Input.GetMouseButtonDown(0)) return;

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

        private void OnGUI()
        {
            if (Selected == null) return;

            boxStyle ??= new GUIStyle(GUI.skin.box)
            {
                fontSize  = 15,
                alignment = TextAnchor.UpperLeft,
                padding   = new RectOffset(10, 10, 8, 8),
            };
            boxStyle.normal.textColor = Color.white;

            var terrain = Selected.Terrain;
            var text = $"Terrain:  {terrain?.kind}\nCategory: {terrain?.category}\nCoords:   {Selected.Coordinates}";
            GUI.Box(new Rect(10, 10, 230, 72), text, boxStyle);
        }
    }
}
