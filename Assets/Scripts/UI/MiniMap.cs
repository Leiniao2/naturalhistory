using System.Collections.Generic;
using NaturalHistory.Territory;
using NaturalHistory.World;
using UnityEngine;
using UnityEngine.UIElements;

namespace NaturalHistory.UI
{
    // Bottom-left overview of the whole map: every hex in its terrain colour (or the layer below
    // in the Underground view), territory edged in its owner's colour, and the camera's view as a
    // frame. Click or drag on it to move the camera there.
    public class MiniMap
    {
        private const int   CellPixels = 12;     // texture pixels between hex centres in a row
        private const float RowPixels  = CellPixels * 0.8660254f;
        private const float MaxWidth   = 300f;   // panel pixels
        private const float MaxHeight  = 300f;

        private readonly VisualElement map;
        private readonly VisualElement view;     // the camera frame, drawn over the map
        private Texture2D texture;
        private bool dirty = true;
        private bool dragging;
        private readonly Vector2[] viewCorners = new Vector2[4]; // camera frame, in texture pixels
        private bool viewValid;

        private static HexGrid Grid => HexGrid.Instance;

        public MiniMap(VisualElement root)
        {
            map = root.Q("minimap");
            if (map == null) return;

            view = new VisualElement { pickingMode = PickingMode.Ignore };
            view.AddToClassList("minimap-view");
            view.generateVisualContent += DrawView;
            map.Add(view);

            map.RegisterCallback<PointerDownEvent>(e => { dragging = true; map.CapturePointer(e.pointerId); JumpTo(e.localPosition); e.StopPropagation(); });
            map.RegisterCallback<PointerMoveEvent>(e => { if (dragging) JumpTo(e.localPosition); });
            map.RegisterCallback<PointerUpEvent>(e => { dragging = false; map.ReleasePointer(e.pointerId); });

            if (Grid != null)
            {
                Grid.Generated      += MarkDirty;
                Grid.TerrainChanged += MarkDirty;
            }
            UnderView.Changed += MarkDirty;
        }

        public void Dispose()
        {
            if (Grid != null)
            {
                Grid.Generated      -= MarkDirty;
                Grid.TerrainChanged -= MarkDirty;
            }
            UnderView.Changed -= MarkDirty;
            if (territory != null) territory.TerritoryChanged -= MarkDirty;
            if (texture != null) Object.Destroy(texture);
        }

        private TerritoryManager territory;
        private void MarkDirty() => dirty = true;

        // Called every frame by GameMenus
        public void Update()
        {
            if (map == null || Grid == null || !Grid.IsGenerated) return;
            if (territory == null && TerritoryManager.Instance != null)
            {
                territory = TerritoryManager.Instance;
                territory.TerritoryChanged += MarkDirty;
                dirty = true;
            }
            if (dirty) { Redraw(); dirty = false; }
            UpdateView();
        }

        // ---------- Map image ----------

        private int TexWidth  => Grid.Width * CellPixels;
        private int TexHeight => Mathf.CeilToInt((Grid.Height - 1) * RowPixels + CellPixels);

        private void Redraw()
        {
            int w = TexWidth, h = TexHeight;
            if (texture == null || texture.width != w || texture.height != h)
            {
                if (texture != null) Object.Destroy(texture);
                texture = new Texture2D(w, h, TextureFormat.RGBA32, false)
                {
                    filterMode = FilterMode.Bilinear,
                    wrapMode   = TextureWrapMode.Clamp,
                    name       = "MiniMap",
                };
                // Keep the map's shape, within the panel's maximum size
                float scale = Mathf.Min(MaxWidth / w, MaxHeight / h);
                map.style.width  = w * scale;
                map.style.height = h * scale;
                map.style.backgroundImage = new StyleBackground(texture);
            }

            int cols = Grid.Width, rows = Grid.Height;
            var colors = new Color[cols, rows];
            var owners = new Players.Player[cols, rows];
            for (int r = 0; r < rows; r++)
            for (int c = 0; c < cols; c++)
            {
                var cell = Grid.GetCell(c, r);
                colors[c, r] = CellColor(cell);
                owners[c, r] = territory != null ? territory.OwnerOf(cell) : null;
            }

            // Each pixel takes the nearest hex centre, which draws the hexes' true shapes. Where
            // the two nearest centres are almost equally close, the pixel is on an edge: drawn in
            // the owner's colour if it is a border of their territory.
            var pixels = new Color32[w * h];
            for (int y = 0; y < h; y++)
            {
                // Texture row 0 is the bottom, like map row 0 (south)
                int baseRow = Mathf.Clamp(Mathf.FloorToInt((y - CellPixels * 0.5f) / RowPixels), 0, rows - 1);
                for (int x = 0; x < w; x++)
                {
                    float best = float.MaxValue, second = float.MaxValue;
                    int bc = 0, br = 0, sc = 0, sr = 0;
                    for (int r = Mathf.Max(0, baseRow - 1); r <= Mathf.Min(rows - 1, baseRow + 2); r++)
                    {
                        float cy = CellPixels * 0.5f + r * RowPixels;
                        float shift = (r & 1) * CellPixels * 0.5f;
                        int approx = Mathf.FloorToInt((x - shift) / CellPixels);
                        for (int c = approx - 1; c <= approx + 1; c++)
                        {
                            float cx = CellPixels * 0.5f + c * CellPixels + shift;
                            float dx = x + 0.5f - cx, dy = y + 0.5f - cy;
                            float d = dx * dx + dy * dy;
                            int wc = ((c % cols) + cols) % cols; // the map wraps east–west
                            if (d < best)        { second = best; sc = bc; sr = br; best = d; bc = wc; br = r; }
                            else if (d < second) { second = d; sc = wc; sr = r; }
                        }
                    }

                    var color = colors[bc, br];
                    var owner = owners[bc, br];
                    if (owner != null)
                    {
                        color = Color.Lerp(color, owner.Primary, 0.25f);
                        bool edge = Mathf.Sqrt(second) - Mathf.Sqrt(best) < 2.2f;
                        if (edge && owners[sc, sr] != owner) color = owner.Primary;
                    }
                    pixels[y * w + x] = color;
                }
            }
            texture.SetPixels32(pixels);
            texture.Apply(false);
        }

        private static Color CellColor(HexCell cell)
        {
            if (cell == null || cell.Terrain == null) return Color.black;
            if (UnderView.On)
            {
                return cell.Under switch
                {
                    UnderKind.Rock       => new Color(0.45f, 0.36f, 0.27f),
                    UnderKind.Cave       => new Color(0.30f, 0.26f, 0.24f),
                    UnderKind.Seabed     => new Color(0.30f, 0.62f, 0.78f),
                    UnderKind.DeepSeabed => Color.Lerp(new Color(0.16f, 0.34f, 0.58f), new Color(0.07f, 0.16f, 0.36f), cell.Depth),
                    UnderKind.Lakebed    => new Color(0.38f, 0.64f, 0.70f),
                    UnderKind.Bedrock    => new Color(0.16f, 0.15f, 0.15f),
                    _                    => Color.gray,
                };
            }
            var color = cell.Terrain.color;
            if (cell.Terrain.kind == TerrainKind.SaltWater)
                color = Color.Lerp(color, color * 0.55f, cell.Depth); // deep sea darker
            else if (cell.IsForest || cell.Feature == TerrainFeature.Jungle)
                color *= 0.78f;
            color.a = 1f;
            return color;
        }

        // ---------- Camera frame ----------

        // Texture pixel of a world point, unwrapped (x may lie outside the texture)
        private Vector2 ToPixel(Vector3 world)
        {
            var origin = Grid.transform.position;
            float size = Grid.WrapWidth / (Mathf.Sqrt(3f) * Grid.Width);
            float col = (world.x - origin.x) / (Mathf.Sqrt(3f) * size);
            float row = (world.z - origin.z) / (1.5f * size);
            return new Vector2(CellPixels * 0.5f + col * CellPixels, CellPixels * 0.5f + row * RowPixels);
        }

        private Vector3 ToWorld(Vector2 pixel)
        {
            var origin = Grid.transform.position;
            float size = Grid.WrapWidth / (Mathf.Sqrt(3f) * Grid.Width);
            float col = (pixel.x - CellPixels * 0.5f) / CellPixels;
            float row = (pixel.y - CellPixels * 0.5f) / RowPixels;
            return new Vector3(origin.x + col * Mathf.Sqrt(3f) * size, 0f, origin.z + row * 1.5f * size);
        }

        private void UpdateView()
        {
            var cam = Camera.main;
            viewValid = false;
            if (cam == null || texture == null) return;
            var ground = new Plane(Vector3.up, Vector3.zero);
            var screen = new[] { new Vector3(0, 0), new Vector3(Screen.width, 0), new Vector3(Screen.width, Screen.height), new Vector3(0, Screen.height) };
            for (int i = 0; i < 4; i++)
            {
                var ray = cam.ScreenPointToRay(screen[i]);
                // Corners above the horizon: take a point far along the ground instead
                float dist = ground.Raycast(ray, out float d) ? Mathf.Min(d, 200f) : 200f;
                var p = ray.GetPoint(dist);
                viewCorners[i] = ToPixel(p);
            }
            viewValid = true;
            view.MarkDirtyRepaint();
        }

        // Frame in panel coordinates; drawn again one map width either side so it shows across
        // the east–west wrap
        private void DrawView(MeshGenerationContext ctx)
        {
            if (!viewValid || texture == null) return;
            float sx = map.resolvedStyle.width / texture.width;
            float sy = map.resolvedStyle.height / texture.height;
            var painter = ctx.painter2D;
            painter.strokeColor = new Color(1f, 1f, 1f, 0.9f);
            painter.lineWidth   = 1.5f;
            for (int copy = -1; copy <= 1; copy++)
            {
                painter.BeginPath();
                for (int i = 0; i < 4; i++)
                {
                    var p = viewCorners[i];
                    var panel = new Vector2((p.x + copy * texture.width) * sx, map.resolvedStyle.height - p.y * sy);
                    if (i == 0) painter.MoveTo(panel); else painter.LineTo(panel);
                }
                painter.ClosePath();
                painter.Stroke();
            }
        }

        private void JumpTo(Vector2 local)
        {
            if (texture == null || Grid == null || CameraController.Main == null) return;
            float sx = texture.width / map.resolvedStyle.width;
            float sy = texture.height / map.resolvedStyle.height;
            var pixel = new Vector2(local.x * sx, (map.resolvedStyle.height - local.y) * sy);
            CameraController.Main.CenterOn(ToWorld(pixel));
        }
    }
}
