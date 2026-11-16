using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Turbulence in the under view: faint streaks of water drifting through the water column along
    // a slowly changing current field, and slow eddies swirling round a point, more of both where
    // the water is rough (over trenches, steep slopes, vents and seamounts). Only near the camera,
    // only while the under view is on. Purely visual.
    public class UnderCurrents : MonoBehaviour
    {
        private const int   Streaks      = 70;
        private const float SpawnPerSec  = 22f;
        private const float EddyShare    = 0.28f;

        private sealed class Streak
        {
            public Transform t;
            public MeshRenderer r;
            public MeshFilter f;
            public Vector3 pos;
            public float born, life, length, speed, radius, angle, spin, alpha;
            public bool eddy, alive;
        }

        private readonly List<Streak> pool = new();
        private Material material;
        private Mesh streakMesh, eddyMesh;
        private MaterialPropertyBlock block;
        private float due;
        private System.Random rng;
        private static readonly int ColorId = Shader.PropertyToID("_Color");

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<HexGrid>() == null || FindAnyObjectByType<UnderCurrents>() != null) return;
            new GameObject("UnderCurrents").AddComponent<UnderCurrents>();
        }

        private void Start()
        {
            material = Resources.Load<Material>("Materials/FxSmoke");
            streakMesh = BuildStreakMesh();
            eddyMesh   = BuildEddyMesh();
            block = new MaterialPropertyBlock();
            rng = new System.Random(4242);
            for (int i = 0; i < Streaks; i++)
            {
                var go = new GameObject("CurrentStreak") { hideFlags = HideFlags.DontSave };
                go.transform.SetParent(transform, false);
                var f = go.AddComponent<MeshFilter>();
                f.sharedMesh = streakMesh;
                var r = go.AddComponent<MeshRenderer>();
                r.sharedMaterial = material;
                r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                r.receiveShadows = false;
                r.enabled = false;
                pool.Add(new Streak { t = go.transform, r = r, f = f });
            }
        }

        private float R(float a, float b) => a + (float)rng.NextDouble() * (b - a);

        private void Update()
        {
            var grid = HexGrid.Instance;
            bool on = UnderView.On && grid != null && grid.IsGenerated && material != null;
            if (!on)
            {
                foreach (var s in pool) if (s.alive) { s.alive = false; s.r.enabled = false; }
                return;
            }
            due += Time.deltaTime * SpawnPerSec;
            while (due >= 1f) { due -= 1f; Spawn(grid); }

            float now = Time.time;
            foreach (var s in pool)
            {
                if (!s.alive) continue;
                float age = (now - s.born) / s.life;
                if (age >= 1f) { s.alive = false; s.r.enabled = false; continue; }
                float fade = Mathf.Sin(Mathf.PI * age);
                if (s.eddy)
                {
                    // a swirl turning in place, drifting slowly with the current
                    s.angle += s.spin * Time.deltaTime;
                    s.pos += Flow(s.pos) * s.speed * 0.3f * Time.deltaTime;
                    s.t.SetPositionAndRotation(s.pos, Quaternion.Euler(0f, s.angle * Mathf.Rad2Deg, 0f));
                    float grow = s.radius * (0.7f + 0.3f * age);
                    s.t.localScale = new Vector3(grow * (s.spin < 0f ? -1f : 1f), 1f, grow);
                }
                else
                {
                    var dir = Flow(s.pos);
                    s.pos += dir * s.speed * Time.deltaTime;
                    s.t.SetPositionAndRotation(s.pos, Quaternion.LookRotation(dir, Vector3.up));
                    s.t.localScale = new Vector3(s.length * 0.16f, 1f, s.length * (0.7f + 0.3f * fade));
                }
                block.SetColor(ColorId, new Color(0.8f, 0.93f, 1f, s.alpha * fade));
                s.r.SetPropertyBlock(block);
            }
        }

        // The current: a smooth field of directions that turns slowly over the map and with time
        private static Vector3 Flow(Vector3 p)
        {
            float a = Mathf.PerlinNoise(p.x * 0.12f + Time.time * 0.01f, p.z * 0.12f) * Mathf.PI * 4f;
            return new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
        }

        private void Spawn(HexGrid grid)
        {
            Streak s = null;
            foreach (var p in pool) if (!p.alive) { s = p; break; }
            if (s == null || !PhenomenaUtil.CameraFocus(out var focus, out float radius)) return;

            // a random water tile in view, rough water preferred
            var at = focus + new Vector3(R(-1f, 1f), 0f, R(-1f, 1f)) * radius * 0.9f;
            var cell = CellAt(grid, at);
            if (cell == null || !cell.IsWater) return;
            float rough = Roughness(grid, cell);
            if (rng.NextDouble() > 0.35 + 0.65 * rough) return;

            float floorY = cell.transform.position.y + grid.UnderSurface(cell);
            float topY   = cell.transform.position.y + cell.SurfaceHeight;
            s.pos   = new Vector3(at.x, Mathf.Lerp(floorY, topY, R(0.15f, 0.85f)), at.z);
            s.born  = Time.time;
            s.eddy  = rng.NextDouble() < EddyShare * (0.6f + rough);
            s.life  = s.eddy ? R(4f, 7f) : R(2.5f, 5.5f);
            s.length = R(0.35f, 0.7f) * (1f + rough * 0.5f);
            s.speed = R(0.15f, 0.3f) * (1f + rough);
            s.alpha = R(0.3f, 0.45f) * (0.75f + 0.5f * rough);
            s.radius = R(0.18f, 0.38f) * (1f + rough * 0.4f);
            s.angle  = R(0f, Mathf.PI * 2f);
            s.spin   = R(1.2f, 2.4f) * (rng.NextDouble() < 0.5 ? -1f : 1f);
            s.f.sharedMesh = s.eddy ? eddyMesh : streakMesh;
            s.alive = true;
            s.r.enabled = true;
            s.t.position = s.pos;
        }

        // 0..1: how churned the water is over this tile (a steep seabed, a trench, vents, a seamount)
        private static float Roughness(HexGrid grid, HexCell cell)
        {
            float y = grid.UnderSurface(cell), steep = 0f;
            foreach (var n in grid.GetNeighbors(cell))
                if (n?.Terrain != null) steep = Mathf.Max(steep, Mathf.Abs(grid.UnderSurface(n) - y));
            float r = Mathf.InverseLerp(0.05f, 0.3f, steep);
            if (cell.UnderFeature != UnderFeature.None) r = Mathf.Max(r, 0.9f);
            return Mathf.Clamp01(r);
        }

        private static HexCell CellAt(HexGrid grid, Vector3 world)
        {
            if (!Physics.Raycast(new Ray(new Vector3(world.x, 50f, world.z), Vector3.down), out var hit, 200f)) return null;
            return hit.collider != null ? hit.collider.GetComponentInParent<HexCell>() : null;
        }

        // A soft ribbon along +Z (length 1, width 1), lying flat and seen from above or below:
        // vertex alpha fades it out at both ends and both edges
        private static Mesh BuildStreakMesh()
        {
            const int segs = 10;
            var pts = new List<Vector3>(); var alphas = new List<float>();
            for (int i = 0; i <= segs; i++)
            {
                float t = i / (float)segs, along = Mathf.Sin(Mathf.PI * t);
                for (int j = 0; j < 3; j++)
                {
                    pts.Add(new Vector3((j - 1) * 0.5f * Mathf.Lerp(0.4f, 1f, along), 0f, t - 0.5f));
                    alphas.Add(j == 1 ? along : 0f);
                }
            }
            return Ribbon("CurrentStreak", pts, alphas, segs, 3);
        }

        // Two spiral arms winding in to a centre (radius 1), brightest at the outer ends of the
        // arms and fading toward the eye and the tails: spun round Y it reads as a whirl
        private static Mesh BuildEddyMesh()
        {
            const int segs = 28;
            var pts = new List<Vector3>(); var alphas = new List<float>();
            for (int arm = 0; arm < 2; arm++)
            for (int i = 0; i <= segs; i++)
            {
                float t = i / (float)segs;                       // 0 at the centre, 1 at the arm's tip
                float a = arm * Mathf.PI + t * Mathf.PI * 2.2f;   // a little over one turn
                float r = 0.12f + 0.88f * t;
                float w = 0.05f + 0.13f * t;
                float fade = Mathf.SmoothStep(0f, 1f, t * 3f) * Mathf.SmoothStep(0f, 1f, (1f - t) * 5f);
                var dir = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
                for (int j = 0; j < 3; j++)
                {
                    pts.Add(dir * (r + (j - 1) * w * 0.5f));
                    alphas.Add(j == 1 ? fade : 0f);
                }
            }
            return Ribbon("CurrentEddy", pts, alphas, segs, 3, 2);
        }

        // Rows of `across` points, `segs + 1` rows per strip; double-sided with separate vertices
        // (normals up and down) so the soft-edge shader sees it from either side
        private static Mesh Ribbon(string name, List<Vector3> pts, List<float> alphas, int segs, int across, int strips = 1)
        {
            var v = new List<Vector3>(); var n = new List<Vector3>(); var c = new List<Color>(); var tri = new List<int>();
            for (int side = 0; side < 2; side++)
            {
                int b = v.Count;
                for (int k = 0; k < pts.Count; k++)
                {
                    v.Add(pts[k]);
                    n.Add(side == 0 ? Vector3.up : Vector3.down);
                    c.Add(new Color(1f, 1f, 1f, alphas[k]));
                }
                for (int st = 0; st < strips; st++)
                for (int i = 0; i < segs; i++)
                for (int j = 0; j < across - 1; j++)
                {
                    int a0 = b + (st * (segs + 1) + i) * across + j, a1 = a0 + 1, b0 = a0 + across, b1 = b0 + 1;
                    if (side == 0) tri.AddRange(new[] { a0, b0, b1, a0, b1, a1 });
                    else           tri.AddRange(new[] { a0, b1, b0, a0, a1, b1 });
                }
            }
            var m = new Mesh { name = name, hideFlags = HideFlags.DontSave };
            m.SetVertices(v); m.SetNormals(n); m.SetColors(c); m.SetTriangles(tri, 0);
            m.RecalculateBounds();
            return m;
        }
    }
}
