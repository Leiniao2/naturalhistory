using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Shows a selected group's MoveRange, in the manner of the Civilization games: the tiles it can
    // reach this turn are washed green and the groups it can attack red (HexCell.SetGroupTarget),
    // with a fine, soft line round the edge of the range and round each target; and, for the
    // tile under the mouse, an arrow along the path it would take, a dot at each tile it passes and
    // a badge at the end with the number of turns it takes to get there. Tiles beyond this turn's
    // reach can be pointed at too (MoveRange.FarPath, MoveOrders): the arrow goes on, paler, with a
    // gold marker where each turn ends. With nothing pointed at, a group under orders shows the
    // way it is going. Drawn over everything (Shaders/MoveOverlay), at the height of the layer on
    // view (surface, seabed, sky). When a tile is to be chosen instead (where the young of a
    // reproducing group go, SpeciesColonies.ChooseTile), each tile on offer gets a blue dashed
    // ring, turning slowly (ShowPlaces).
    public class MovePathView : MonoBehaviour
    {
        private static MovePathView instance;

        private static readonly Color OutlineColor = new(0.85f, 1f, 0.88f, 0.55f);
        private static readonly Color RingColor    = new(1f, 0.55f, 0.5f, 0.6f);
        private static readonly Color AttackColor  = new(1f, 0.30f, 0.24f, 0.95f);
        private static readonly Color PathColor    = new(1f, 1f, 1f, 0.95f);
        private static readonly Color Shadow       = new(0f, 0f, 0f, 0.45f);
        private static readonly Color FarColor     = new(0.78f, 0.88f, 1f, 0.9f);   // beyond this turn
        private static readonly Color TurnEndColor = new(1f, 0.82f, 0.3f, 1f);     // where a turn ends
        private static readonly Color PlaceColor   = new(0.32f, 0.62f, 1f, 0.95f);  // a tile on offer
        private const float Lift = 0.04f; // above the tile surface

        private MoveRange range;
        private HexCell hovered;
        private List<HexCell> farPath; // to `hovered` (or the group's order) when beyond this turn's reach
        private float builtAtX = float.NaN; // the group tile's x when the outline was built (the map wraps)
        private float radius = 1f;          // hex corner radius in world units
        private Mesh outlineMesh, pathMesh;
        private MeshRenderer outlineRenderer, pathRenderer;
        private TextMesh label;
        private Transform badge;
        private List<HexCell> places; // tiles on offer (ShowPlaces)

        public static void Show(MoveRange range)
        {
            if (instance == null) instance = new GameObject("MovePathView").AddComponent<MovePathView>();
            instance.range = range;
            instance.hovered = null;
            instance.builtAtX = float.NaN;
            instance.Refresh();
        }

        // Blue dashed rings on the tiles a player can choose among
        public static void ShowPlaces(IEnumerable<HexCell> cells)
        {
            if (instance == null) instance = new GameObject("MovePathView").AddComponent<MovePathView>();
            instance.range = null;
            instance.hovered = null;
            instance.places = new List<HexCell>(cells);
            instance.Refresh();
        }

        // Set by the UI: the map can't be pointed at now (a panel such as the trees or the
        // Encyclopedia is open, or the pointer is over the UI), so nothing under it counts as hovered
        public static System.Func<bool> MapCovered;

        // The foe's tile under the pointer, while a group's range is on show (UI/AttackPreview)
        public static HexCell HoveredTarget =>
            instance != null && instance.range != null && instance.hovered != null && instance.range.AttackFrom.ContainsKey(instance.hovered) ? instance.hovered : null;
        public static MoveRange Range => instance != null ? instance.range : null;

        public static void Hide()
        {
            if (instance == null) return;
            instance.places = null;
            instance.range = null;
            instance.hovered = null;
            instance.Refresh();
        }

        private void Awake()
        {
            var shader = Resources.Load<Shader>("Shaders/MoveOverlay");
            var material = new Material(shader != null ? shader : Shader.Find("Sprites/Default")) { name = "MoveOverlay" };
            (outlineMesh, outlineRenderer) = MakeLayer("Outline", material, 0);
            (pathMesh, pathRenderer) = MakeLayer("Path", material, 1);

            badge = MakeBadge(material).transform;
            var text = new GameObject("Steps");
            text.transform.SetParent(badge, false);
            text.transform.localPosition = new Vector3(0f, 0f, -0.01f);
            label = text.AddComponent<TextMesh>();
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            // drawn after the badge (the Overlay queue), so it isn't hidden behind it
            label.GetComponent<MeshRenderer>().sharedMaterial = new Material(label.font.material) { renderQueue = 4001 };
            label.GetComponent<MeshRenderer>().sortingOrder = 3;
            label.anchor = TextAnchor.MiddleCenter;
            label.alignment = TextAlignment.Center;
            label.fontSize = 64;
            label.characterSize = 0.06f;
            label.color = Color.white;
            badge.gameObject.SetActive(false);
        }

        private (Mesh, MeshRenderer) MakeLayer(string name, Material material, int order)
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform, false);
            var mesh = new Mesh { name = name };
            mesh.MarkDynamic();
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterial = material;
            r.sortingOrder = order;
            r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            r.receiveShadows = false;
            return (mesh, r);
        }

        // A dark disc with a light rim, facing the camera, behind the step count
        private GameObject MakeBadge(Material material)
        {
            var go = new GameObject("Badge");
            go.transform.SetParent(transform, false);
            var v = new List<Vector3>(); var c = new List<Color>(); var t = new List<int>();
            const int n = 24;
            AddDisc(v, c, t, 1f, new Color(0.95f, 0.95f, 0.95f, 0.95f), n);
            AddDisc(v, c, t, 0.82f, new Color(0.08f, 0.10f, 0.14f, 0.92f), n);
            var mesh = new Mesh { name = "Badge" };
            mesh.SetVertices(v); mesh.SetColors(c); mesh.SetTriangles(t, 0);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterial = material;
            r.sortingOrder = 2;
            return go;
        }

        private static void AddDisc(List<Vector3> v, List<Color> c, List<int> t, float r, Color color, int n)
        {
            int start = v.Count;
            v.Add(Vector3.zero); c.Add(color);
            for (int i = 0; i <= n; i++)
            {
                float a = i * Mathf.PI * 2f / n;
                v.Add(new Vector3(Mathf.Cos(a) * r, Mathf.Sin(a) * r, 0f)); c.Add(color);
                if (i > 0) { t.Add(start); t.Add(start + i + 1); t.Add(start + i); }
            }
        }

        private void LateUpdate()
        {
            if (places != null) { BuildPlaces(); return; } // the rings turn
            if (range == null) return;
            if (range.Group == null || range.Group.Cell == null || range.Group.IsBusy) { Hide(); return; }
            var cam = Camera.main;
            if (cam == null) return;

            var cell = MapCovered != null && MapCovered() ? null
                     : Physics.Raycast(cam.ScreenPointToRay(Input.mousePosition), out var hit) ? hit.collider.GetComponent<HexCell>() : null;
            if (cell == range.Group.Cell) cell = null;
            bool moved = !Mathf.Approximately(builtAtX, range.Group.Cell.transform.position.x);
            if (cell != hovered || moved) { hovered = cell; Refresh(); }

            if (badge.gameObject.activeSelf) badge.rotation = cam.transform.rotation;
        }

        // ---------- Building ----------

        private void Refresh()
        {
            outlineMesh.Clear();
            pathMesh.Clear();
            badge.gameObject.SetActive(false);
            if (places != null) { BuildPlaces(); return; }
            if (range == null || range.Group == null || range.Group.Cell == null) return;
            var start = range.Group.Cell;
            builtAtX = start.transform.position.x;
            radius = CellRadius(start);
            BuildOutline(start);
            farPath = null;
            var target = hovered ?? MoveOrders.TargetOf(range.Group);
            if (target == null) return;
            if (range.Contains(target)) BuildPath(start, target);
            else
            {
                farPath = MoveRange.FarPath(range.Group, target, SpeciesColonies.Instance);
                if (farPath != null) BuildFarPath(start, farPath);
            }
        }

        private static float CellRadius(HexCell cell)
        {
            var grid = HexGrid.Instance;
            foreach (var n in grid.GetNeighbors(cell))
                if (n != null) return Delta(cell, n).magnitude / Mathf.Sqrt(3f);
            return 1f;
        }

        // n's centre relative to c's, the short way round the east–west wrap
        private static Vector3 Delta(HexCell c, HexCell n)
        {
            var d = n.transform.position - c.transform.position;
            float wrap = HexGrid.Instance.WrapWidth;
            if (d.x > wrap * 0.5f) d.x -= wrap;
            else if (d.x < -wrap * 0.5f) d.x += wrap;
            d.y = 0f;
            return d;
        }

        // Height of the overlay on a tile, in the layer on view
        private static float Height(HexCell cell)
        {
            var grid = HexGrid.Instance;
            return UnderView.Layer switch
            {
                MapLayer.Sky   => SkyLayer.DeckHeight + 0.05f,
                MapLayer.Under => cell.transform.position.y + grid.UnderSurface(cell) + Lift,
                _              => cell.SurfacePosition.y + Lift,
            };
        }

        private void BuildOutline(HexCell start)
        {
            var grid = HexGrid.Instance;
            var region = new HashSet<HexCell>(range.Destinations) { start };
            var v = new List<Vector3>(); var c = new List<Color>(); var t = new List<int>();
            float w = radius * 0.025f; // a fine line
            foreach (var cell in region)
            {
                var neighbours = grid.GetNeighbors(cell);
                for (int k = 0; k < 6; k++)
                {
                    var dir = Direction(k);
                    HexCell across = null;
                    foreach (var n in neighbours)
                        if (n != null && Vector3.Dot(Delta(cell, n).normalized, dir) > 0.95f) { across = n; break; }
                    if (across != null && region.Contains(across)) continue;
                    AddEdge(v, c, t, cell, dir, w, OutlineColor);
                }
            }
            foreach (var target in range.AttackFrom.Keys)
                for (int k = 0; k < 6; k++)
                {
                    AddEdge(v, c, t, target, Direction(k), w, RingColor);
                }
            outlineMesh.SetVertices(v); outlineMesh.SetColors(c); outlineMesh.SetTriangles(t, 0);
            outlineMesh.RecalculateBounds();
        }

        private void BuildPlaces()
        {
            outlineMesh.Clear();
            var v = new List<Vector3>(); var c = new List<Color>(); var t = new List<int>();
            const int dashes = 12;
            float spin = Time.unscaledTime * 0.35f, step = Mathf.PI * 2f / dashes;
            foreach (var cell in places)
            {
                if (cell == null) continue;
                radius = CellRadius(cell);
                var centre = cell.transform.position; centre.y = Height(cell);
                float r = radius * 0.62f, w = radius * 0.06f;
                for (int d = 0; d < dashes; d++)
                {
                    float a0 = spin + d * step, a1 = a0 + step * 0.55f;
                    AddArc(v, c, t, centre, r, w * 2f, a0, a1, Shadow); // a dark edge, so it reads on any ground
                    AddArc(v, c, t, centre, r, w, a0, a1, PlaceColor);
                }
            }
            outlineMesh.SetVertices(v); outlineMesh.SetColors(c); outlineMesh.SetTriangles(t, 0);
            outlineMesh.RecalculateBounds();
        }

        // A flat band `width` wide along a circle of radius r, from angle a0 to a1
        private static void AddArc(List<Vector3> v, List<Color> c, List<int> t, Vector3 centre, float r, float width, float a0, float a1, Color color)
        {
            const int n = 4;
            int start = v.Count;
            for (int i = 0; i <= n; i++)
            {
                float a = Mathf.Lerp(a0, a1, i / (float)n);
                var d = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
                v.Add(centre + d * (r + width * 0.5f)); c.Add(color);
                v.Add(centre + d * (r - width * 0.5f)); c.Add(color);
                if (i > 0)
                {
                    int k = start + i * 2;
                    t.Add(k - 2); t.Add(k - 1); t.Add(k);
                    t.Add(k - 1); t.Add(k + 1); t.Add(k);
                }
            }
        }

        // Neighbour directions of a pointy-top hex: east, then every 60°
        private static Vector3 Direction(int k)
        {
            float a = k * Mathf.PI / 3f;
            return new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
        }

        // A band along the tile's edge facing `dir`, `width` wide, just inside the tile
        private void AddEdge(List<Vector3> v, List<Color> c, List<int> t, HexCell cell, Vector3 dir, float width, Color color)
        {
            var centre = cell.transform.position; centre.y = Height(cell);
            var perp = new Vector3(-dir.z, 0f, dir.x);
            float inset = radius * 0.04f; // keeps neighbouring outlines (and the groove) apart
            var mid = centre + dir * (radius * Mathf.Sqrt(3f) * 0.5f - inset);
            var a = mid + perp * (radius * 0.5f - inset * 0.58f);
            var b = mid - perp * (radius * 0.5f - inset * 0.58f);
            // the inner side's corners point at the centre, so bands meet cleanly at the corners
            var ai = a + (centre - a).normalized * width * 1.15f;
            var bi = b + (centre - b).normalized * width * 1.15f;
            int i = v.Count;
            v.Add(a); v.Add(b); v.Add(bi); v.Add(ai);
            c.Add(color); c.Add(color); c.Add(color); c.Add(color);
            t.Add(i); t.Add(i + 1); t.Add(i + 2); t.Add(i); t.Add(i + 2); t.Add(i + 3);
        }

        private void BuildPath(HexCell start, HexCell target)
        {
            bool attack = range.AttackFrom.TryGetValue(target, out var from);
            var cells = range.PathTo(attack ? from : target);
            if (attack) cells.Add(target);
            if (cells.Count == 0) return;

            // centres along the path, unwrapped from the start
            var pts = new List<Vector3>();
            var basePos = start.transform.position;
            var p = new Vector3(basePos.x, Height(start), basePos.z);
            pts.Add(p);
            var prev = start;
            var offset = Vector3.zero;
            foreach (var cell in cells)
            {
                offset += Delta(prev, cell);
                pts.Add(new Vector3(basePos.x + offset.x, Height(cell), basePos.z + offset.z));
                prev = cell;
            }
            // leave the animal itself uncovered, and stop the head short of the end tile's centre
            pts[0] = Vector3.Lerp(pts[0], pts[1], 0.3f);
            if (attack) pts[^1] = Vector3.Lerp(pts[^2], pts[^1], 0.62f);

            var v = new List<Vector3>(); var c = new List<Color>(); var t = new List<int>();
            var color = attack ? AttackColor : PathColor;
            AddArrow(v, c, t, pts, radius * 0.22f, Shadow);
            AddArrow(v, c, t, pts, radius * 0.13f, color);
            for (int i = 1; i < pts.Count - 1; i++) // a dot at each tile passed
            {
                AddFlatDisc(v, c, t, pts[i], radius * 0.13f, Shadow);
                AddFlatDisc(v, c, t, pts[i], radius * 0.09f, color);
            }
            pathMesh.SetVertices(v); pathMesh.SetColors(c); pathMesh.SetTriangles(t, 0);
            pathMesh.RecalculateBounds();

            ShowBadge(pts[^1], 1, attack ? new Color(1f, 0.75f, 0.7f) : Color.white); // within reach: this turn
        }

        // The number of turns over the end of the path
        private void ShowBadge(Vector3 at, int turns, Color color)
        {
            badge.gameObject.SetActive(true);
            badge.position = at + Vector3.up * radius * 0.45f;
            badge.localScale = Vector3.one * radius * 0.24f;
            label.text = turns.ToString();
            label.color = color;
        }

        // Beyond this turn's reach: the whole way, white as far as this turn goes and paler after,
        // a gold marker at each tile where a turn ends, and the turns it takes in the badge
        private void BuildFarPath(HexCell start, List<HexCell> cells)
        {
            var legs = new List<int>();
            int turns = MoveRange.TurnsAlong(range.Group, cells, SpeciesColonies.Instance, legs);
            if (turns < 0 || cells.Count == 0) return;

            var pts = new List<Vector3>();
            var basePos = start.transform.position;
            pts.Add(new Vector3(basePos.x, Height(start), basePos.z));
            var prev = start;
            var offset = Vector3.zero;
            foreach (var cell in cells)
            {
                offset += Delta(prev, cell);
                pts.Add(new Vector3(basePos.x + offset.x, Height(cell), basePos.z + offset.z));
                prev = cell;
            }
            pts[0] = Vector3.Lerp(pts[0], pts[1], 0.3f);

            var v = new List<Vector3>(); var c = new List<Color>(); var t = new List<int>();
            AddArrow(v, c, t, pts, radius * 0.22f, Shadow);
            int now = legs.Count > 0 ? legs[0] : 0; // tiles walked this turn
            if (now >= 1) AddArrow(v, c, t, pts.GetRange(0, now + 1), radius * 0.13f, PathColor, head: false);
            AddArrow(v, c, t, pts.GetRange(Mathf.Max(0, now), pts.Count - Mathf.Max(0, now)), radius * 0.13f, FarColor);
            var ends = new HashSet<int>(legs);
            for (int i = 1; i < pts.Count - 1; i++)
            {
                bool turnEnd = ends.Contains(i);
                AddFlatDisc(v, c, t, pts[i], radius * (turnEnd ? 0.2f : 0.13f), Shadow);
                AddFlatDisc(v, c, t, pts[i], radius * (turnEnd ? 0.15f : 0.09f), turnEnd ? TurnEndColor : i <= now ? PathColor : FarColor);
            }
            pathMesh.SetVertices(v); pathMesh.SetColors(c); pathMesh.SetTriangles(t, 0);
            pathMesh.RecalculateBounds();
            ShowBadge(pts[^1], turns, turns <= 1 ? Color.white : new Color(1f, 0.88f, 0.55f));
        }

        // A ribbon along `pts`, with an arrowhead at the end unless `head` is false
        private static void AddArrow(List<Vector3> v, List<Color> c, List<int> t, List<Vector3> pts, float width, Color color, bool head = true)
        {
            if (pts.Count < 2) return;
            float headSize = width * 2.6f;
            var end = pts[^1];
            var lastDir = Flat(end - pts[^2]).normalized;
            var shaftEnd = head ? end - lastDir * headSize * 0.9f : end;
            var line = new List<Vector3>(pts) { [pts.Count - 1] = shaftEnd };

            int first = v.Count;
            for (int i = 0; i < line.Count; i++)
            {
                var dirIn  = i > 0 ? Flat(line[i] - line[i - 1]).normalized : Flat(line[1] - line[0]).normalized;
                var dirOut = i < line.Count - 1 ? Flat(line[i + 1] - line[i]).normalized : dirIn;
                var dir = (dirIn + dirOut).normalized;
                if (dir == Vector3.zero) dir = dirIn;
                var side = new Vector3(-dir.z, 0f, dir.x) * (width * 0.5f / Mathf.Max(0.5f, Vector3.Dot(dir, dirIn)));
                v.Add(line[i] + side); v.Add(line[i] - side);
                c.Add(color); c.Add(color);
                if (i > 0)
                {
                    int a = first + (i - 1) * 2;
                    t.Add(a); t.Add(a + 2); t.Add(a + 1);
                    t.Add(a + 1); t.Add(a + 2); t.Add(a + 3);
                }
            }
            if (!head) return;
            var sideHead = new Vector3(-lastDir.z, 0f, lastDir.x) * headSize * 0.62f;
            int h = v.Count;
            v.Add(shaftEnd + sideHead); v.Add(shaftEnd - sideHead); v.Add(end + lastDir * width * 0.4f);
            c.Add(color); c.Add(color); c.Add(color);
            t.Add(h); t.Add(h + 2); t.Add(h + 1);
        }

        private static void AddFlatDisc(List<Vector3> v, List<Color> c, List<int> t, Vector3 centre, float r, Color color)
        {
            const int n = 16;
            int start = v.Count;
            v.Add(centre); c.Add(color);
            for (int i = 0; i <= n; i++)
            {
                float a = i * Mathf.PI * 2f / n;
                v.Add(centre + new Vector3(Mathf.Cos(a) * r, 0f, Mathf.Sin(a) * r)); c.Add(color);
                if (i > 0) { t.Add(start); t.Add(start + i + 1); t.Add(start + i); }
            }
        }

        private static Vector3 Flat(Vector3 d) { d.y = 0f; return d; }
    }
}
