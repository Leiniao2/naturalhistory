using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // The animal group in focus — the one picked for orders, else the one the selected tile shows
    // (UnderView.Focus) — gets a dashed ring around it, slowly turning and pulsing, drawn over
    // everything (Shaders/MoveOverlay). The camera keeps it centred: it glides there whenever the
    // focus changes or the group reaches another tile, and follows it while it walks (panning away
    // stops that until the next change, or the recenter key).
    public class FocusRing : MonoBehaviour
    {
        private const int   Dashes    = 20;
        private const float DashShare = 0.58f; // of each dash's slot; the rest is the gap
        private const float TurnSpeed = 12f;   // degrees per second
        private static readonly Color DashColor   = new(1f, 0.93f, 0.6f, 1f);
        private static readonly Color ShadowColor = new(0f, 0f, 0f, 0.5f);

        private Mesh mesh;
        private MeshRenderer meshRenderer;
        private ColonyGroup focus;
        private HexCell focusCell;
        private float builtRadius = -1f;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<FocusRing>() != null) return;
            new GameObject("FocusRing").AddComponent<FocusRing>();
        }

        private void Awake()
        {
            var shader = Resources.Load<Shader>("Shaders/MoveOverlay");
            var material = new Material(shader != null ? shader : Shader.Find("Sprites/Default")) { name = "FocusRing" };
            var ring = new GameObject("Ring");
            ring.transform.SetParent(transform, false);
            mesh = new Mesh { name = "FocusRing" };
            ring.AddComponent<MeshFilter>().sharedMesh = mesh;
            meshRenderer = ring.AddComponent<MeshRenderer>();
            meshRenderer.sharedMaterial = material;
            meshRenderer.sortingOrder = 2;
            meshRenderer.enabled = false;
        }

        private static ColonyGroup Focused()
        {
            var colonies = SpeciesColonies.Instance;
            if (colonies == null) return null;
            var g = colonies.Selected;
            if (g == null && CellSelector.Selected != null) g = UnderView.Focus.Current(CellSelector.Selected);
            return g != null && g.Cell != null && g.Members.Count > 0 && UnderView.Shows(g) ? g : null;
        }

        private void LateUpdate()
        {
            var g = Focused();
            var cam = CameraController.Main;
            if (g != focus)
            {
                focus = g;
                focusCell = g != null ? g.Cell : null;
                if (cam != null) cam.Follow(g != null ? transform : null);
            }
            else if (g != null && g.Cell != focusCell) // reached another tile: back to the middle
            {
                focusCell = g.Cell;
                cam?.ResumeFollow();
            }

            meshRenderer.enabled = g != null;
            if (g == null) return;

            // around the members wherever they are (walking between tiles too), at their feet
            var centre = Vector3.zero;
            float low = float.MaxValue;
            foreach (var m in g.Members) { var p = m.transform.position; centre += p; low = Mathf.Min(low, p.y); }
            centre /= g.Members.Count;
            float spread = 0f;
            foreach (var m in g.Members)
            {
                var d = m.transform.position - centre; d.y = 0f;
                spread = Mathf.Max(spread, d.magnitude);
            }
            float cell = HexGrid.Instance != null ? HexGrid.Instance.CellSize : 1f;
            float radius = Mathf.Clamp(spread + g.MemberSpan * cell * 0.55f + 0.04f * cell, 0.22f * cell, 0.95f * cell);
            radius = Mathf.Round(radius / (0.02f * cell)) * (0.02f * cell); // rebuild only on real changes
            if (!Mathf.Approximately(radius, builtRadius)) Build(radius, cell);

            transform.position = new Vector3(centre.x, low + 0.01f, centre.z);
            transform.rotation = Quaternion.Euler(0f, Time.time * TurnSpeed, 0f);
            float pulse = 0.75f + 0.25f * Mathf.Sin(Time.time * 3f);
            transform.localScale = Vector3.one * (0.97f + 0.03f * pulse);
        }

        // Dashes round a circle, each over a slightly wider dark one so it reads on any ground
        private void Build(float radius, float cell)
        {
            builtRadius = radius;
            var v = new List<Vector3>();
            var c = new List<Color>();
            var t = new List<int>();
            float width = 0.035f * cell;
            AddDashes(v, c, t, radius, width * 2.2f, ShadowColor, 0.04f);
            AddDashes(v, c, t, radius, width, DashColor, 0f);
            mesh.Clear();
            mesh.SetVertices(v);
            mesh.SetColors(c);
            mesh.SetTriangles(t, 0);
            mesh.RecalculateBounds();
        }

        private static void AddDashes(List<Vector3> v, List<Color> c, List<int> t, float radius, float width, Color color, float extraShare)
        {
            const int steps = 4; // per dash, so it bends with the circle
            float slot = Mathf.PI * 2f / Dashes;
            float span = slot * Mathf.Min(1f, DashShare + extraShare);
            for (int d = 0; d < Dashes; d++)
            {
                float a0 = d * slot - (span - slot * DashShare) * 0.5f;
                int first = v.Count;
                for (int s = 0; s <= steps; s++)
                {
                    float a = a0 + span * s / steps;
                    var dir = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
                    v.Add(dir * (radius - width * 0.5f)); c.Add(color);
                    v.Add(dir * (radius + width * 0.5f)); c.Add(color);
                }
                for (int s = 0; s < steps; s++)
                {
                    int i = first + s * 2;
                    t.Add(i); t.Add(i + 1); t.Add(i + 3);
                    t.Add(i); t.Add(i + 3); t.Add(i + 2);
                }
            }
        }
    }
}
