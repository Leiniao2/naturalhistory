using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // A health bar over every group that has lost HP, the way strategy games show wounded units:
    // green above half, yellow down to a fifth, red below that. Only for groups the player can see
    // (in the layer on view, out of the fog of war); full-health groups show none. Drawn over
    // everything (Shaders/MoveOverlay), facing the camera, keeping a readable size as it zooms.
    public class HealthBars : MonoBehaviour
    {
        private static readonly Color Green  = new(0.30f, 0.85f, 0.30f, 1f);
        private static readonly Color Yellow = new(0.95f, 0.80f, 0.20f, 1f);
        private static readonly Color Red    = new(0.92f, 0.22f, 0.18f, 1f);
        private static readonly Color Back   = new(0.05f, 0.05f, 0.05f, 0.85f);

        private sealed class Bar
        {
            public GameObject go;
            public Mesh mesh;
            public float shown = -1f; // the fraction the mesh was built for
        }

        private readonly Dictionary<ColonyGroup, Bar> bars = new();
        private readonly Stack<Bar> spare = new();
        private readonly List<ColonyGroup> gone = new();
        private Material material;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<HealthBars>() != null) return;
            new GameObject("HealthBars").AddComponent<HealthBars>();
        }

        public static Color ColorFor(float fraction) => fraction > 0.5f ? Green : fraction > 0.2f ? Yellow : Red;

        private void Awake()
        {
            var shader = Resources.Load<Shader>("Shaders/MoveOverlay");
            material = new Material(shader != null ? shader : Shader.Find("Sprites/Default")) { name = "HealthBar" };
        }

        private void LateUpdate()
        {
            var colonies = SpeciesColonies.Instance;
            var cam = Camera.main;
            gone.Clear();
            foreach (var g in bars.Keys) gone.Add(g);
            if (colonies != null && cam != null)
                foreach (var g in colonies.Groups)
                {
                    if (!Wounded(g) || !Seen(g, out var top)) continue;
                    gone.Remove(g);
                    if (!bars.TryGetValue(g, out var bar)) bars[g] = bar = Take();
                    float fraction = Mathf.Clamp01(g.Hp / g.MaxHp);
                    if (!Mathf.Approximately(bar.shown, fraction)) Build(bar, fraction);
                    float size = Mathf.Clamp(Vector3.Distance(cam.transform.position, top) * 0.035f, 0.22f, 1.1f);
                    bar.go.transform.SetPositionAndRotation(top + Vector3.up * size * 0.25f, cam.transform.rotation);
                    bar.go.transform.localScale = Vector3.one * size;
                    bar.go.SetActive(true);
                }
            foreach (var g in gone) { Release(bars[g]); bars.Remove(g); }
        }

        private static bool Wounded(ColonyGroup g) => g != null && g.Definition != null && g.MaxHp > 0 && g.Hp > 0f && g.Hp < g.MaxHp - 0.01f;

        // Shown on the map, and where: just above its tallest member
        private static bool Seen(ColonyGroup g, out Vector3 top)
        {
            top = default;
            if (!UnderView.Shows(g)) return false; // in the layer on view, out of the fog
            bool any = false;
            Bounds b = default;
            foreach (var m in g.Members)
            {
                var r = m.renderer;
                if (r == null || !r.enabled || !r.gameObject.activeInHierarchy) continue;
                if (!any) { b = r.bounds; any = true; } else b.Encapsulate(r.bounds);
            }
            if (!any) return false;
            top = new Vector3(b.center.x, b.max.y, b.center.z);
            return true;
        }

        // A bar one unit wide (scaled by `size`): a dark back with a coloured fill from the left
        private static void Build(Bar bar, float fraction)
        {
            bar.shown = fraction;
            const float w = 1f, h = 0.16f, pad = 0.03f;
            float fill = (w - 2 * pad) * fraction;
            var color = ColorFor(fraction);
            var v = new[]
            {
                new Vector3(-w / 2, -h / 2), new Vector3(w / 2, -h / 2), new Vector3(w / 2, h / 2), new Vector3(-w / 2, h / 2),
                new Vector3(-w / 2 + pad, -h / 2 + pad, -0.001f), new Vector3(-w / 2 + pad + fill, -h / 2 + pad, -0.001f),
                new Vector3(-w / 2 + pad + fill, h / 2 - pad, -0.001f), new Vector3(-w / 2 + pad, h / 2 - pad, -0.001f),
            };
            bar.mesh.Clear();
            bar.mesh.vertices = v;
            bar.mesh.colors = new[] { Back, Back, Back, Back, color, color, color, color };
            bar.mesh.triangles = new[] { 0, 2, 1, 0, 3, 2, 4, 6, 5, 4, 7, 6 };
            bar.mesh.RecalculateBounds();
        }

        private Bar Take()
        {
            if (spare.Count > 0) return spare.Pop();
            var go = new GameObject("HealthBar");
            go.transform.SetParent(transform, false);
            var mesh = new Mesh { name = "HealthBar" };
            mesh.MarkDynamic();
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterial = material;
            r.sortingOrder = 5;
            r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            r.receiveShadows = false;
            return new Bar { go = go, mesh = mesh };
        }

        private void Release(Bar bar)
        {
            bar.go.SetActive(false);
            bar.shown = -1f;
            spare.Push(bar);
        }
    }
}
