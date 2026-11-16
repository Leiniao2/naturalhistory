using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace NaturalHistory.World
{
    // Shared base of the natural-phenomenon effects (meteors, eruptions, storms, waves...). Every
    // effect is a set of parts moved, tinted and scaled by script:
    //   solid parts on the opaque map material (angular rocks, water sheets), which vanish by shrinking;
    //   Smoke parts (FxSmoke: soft, lit, see-through; alpha in the colour fades them);
    //   Glow parts (FxGlow: additive light for fire, lava, flashes and embers);
    // plus point lights and camera shake for the violent moments. An effect is a child of the tile
    // it happens on, so it follows the east-west wrap; positions are in that tile's space (x, z from
    // its centre, y up from its base).
    public abstract class PhenomenonFx : MonoBehaviour
    {
        protected struct Part
        {
            public Transform transform;
            public MeshRenderer renderer;
        }

        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static Mesh puffMesh, chunkMesh, discMesh, ballMesh;
        private static Mesh[] rockMeshes;
        private static Material material, smokeMaterial, glowMaterial;
        private readonly List<Light> lights = new();
        private MaterialPropertyBlock block;

        protected HexGrid grid;
        protected HexCell cell;
        protected float s;            // cell size
        protected System.Random rng;
        protected float duration;     // seconds; the effect destroys itself afterwards
        private float startTime;
        private readonly List<Part> parts = new();

        internal static Mesh Puff  => puffMesh  ??= MapFeatureMeshes.CreateSmokePuff(new System.Random(11));
        internal static Mesh Chunk => chunkMesh ??= CreateChunk();
        internal static Mesh Disc  => discMesh  ??= CreateDisc();

        // Puff vertex colours are a pale grey (about 0.78); multiply tints by this to get the colour asked for
        internal const float PuffBoost = 1.28f;

        // Smooth white ball of radius 1 for Smoke and Glow parts
        internal static Mesh Ball => ballMesh ??= CreateBall();

        // Angular, faceted boulders of radius ~1 (several shapes, so no two rocks match)
        internal static Mesh Rock(int i) => (rockMeshes ??= CreateRocks(8))[((i % 8) + 8) % 8];

        public void Begin(HexGrid grid, HexCell cell, float duration, int seed)
        {
            this.grid     = grid;
            this.cell     = cell;
            this.duration = duration;
            s         = grid.WrapWidth / (Mathf.Sqrt(3f) * Mathf.Max(1, grid.Width));
            rng       = new System.Random(seed);
            block     = new MaterialPropertyBlock();
            material      ??= Resources.Load<Material>("Materials/MapFeatures");
            smokeMaterial ??= Resources.Load<Material>("Materials/FxSmoke");
            glowMaterial  ??= Resources.Load<Material>("Materials/FxGlow");
            startTime = Time.time;
            Build();
            Animate(0f, 0f);
            HideIfUnderground();
        }

        protected abstract void Build();

        // u = 0..1 through the effect, t = seconds since it began
        protected abstract void Animate(float u, float t);

        protected virtual void End() { }

        // Whether it shows in the Underground view too (earthquakes shake the rock below as well).
        // Most happen on the surface only, so they keep playing out but are hidden while the view is on.
        protected virtual bool ShowsUnderground => false;
        private bool Hidden => UnderView.On && !ShowsUnderground;

        private void HideIfUnderground()
        {
            if (!Hidden) return;
            foreach (var p in parts) if (p.renderer != null) p.renderer.enabled = false;
        }

        private void Update()
        {
            if (grid == null) return;
            float t = Time.time - startTime;
            if (t >= duration)
            {
                End();
                Destroy(gameObject);
                return;
            }
            Animate(t / duration, t);
            HideIfUnderground();
        }

        protected float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);

        protected Part AddPart(Mesh mesh, string name = "Part") => AddPart(mesh, material, name);

        private Part AddPart(Mesh mesh, Material mat, string name)
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterial    = mat != null ? mat : material;
            mr.shadowCastingMode = ShadowCastingMode.Off;
            mr.receiveShadows    = false;
            var part = new Part { transform = go.transform, renderer = mr };
            parts.Add(part);
            return part;
        }

        protected Part[] AddParts(Mesh mesh, int count, string name = "Part")
        {
            var list = new Part[count];
            for (int i = 0; i < count; i++) list[i] = AddPart(mesh, name);
            return list;
        }

        // Soft, see-through smoke / dust / spray puffs; the colour's alpha is their opacity
        protected Part[] AddSmoke(int count, string name = "Smoke")
        {
            var list = new Part[count];
            for (int i = 0; i < count; i++) list[i] = AddPart(Ball, smokeMaterial, name);
            return list;
        }

        // Additive glow (fire, lava, flashes); the colour's alpha scales the brightness
        protected Part[] AddGlow(int count, string name = "Glow")
        {
            var list = new Part[count];
            for (int i = 0; i < count; i++) list[i] = AddPart(Ball, glowMaterial, name);
            return list;
        }

        // Solid angular rocks, each a different shape
        protected Part[] AddRocks(int count, string name = "Rock")
        {
            var list = new Part[count];
            for (int i = 0; i < count; i++) list[i] = AddPart(Rock(rng.Next(8)), material, name);
            return list;
        }

        // A point light that lights up the map around the effect (flashes, lava, fire)
        protected Light AddLight(Color color, float range)
        {
            var go = new GameObject("Light");
            go.transform.SetParent(transform, false);
            var light = go.AddComponent<Light>();
            light.type      = LightType.Point;
            light.color     = color;
            light.range     = range * s;
            light.intensity = 0f;
            light.shadows   = LightShadows.None;
            lights.Add(light);
            return light;
        }

        protected static void SetLight(Light light, Vector3 position, float intensity)
        {
            light.transform.localPosition = position;
            light.intensity = Mathf.Max(0f, intensity);
            light.enabled   = intensity > 0.01f;
        }

        // Shakes the camera (strength in cells at the source; fades with distance from the view)
        protected void Shake(Vector3 local, float strength, float seconds) =>
            CameraShake.Add(transform.TransformPoint(local), strength * s * 0.05f, seconds);

        // Places a part; a size of (nearly) zero hides it.
        protected void Show(Part p, Vector3 position, Vector3 scale, Color color, Quaternion rotation)
        {
            bool visible = scale.x > 1e-4f && scale.y > 1e-4f && scale.z > 1e-4f;
            p.renderer.enabled = visible;
            if (!visible) return;
            p.transform.localPosition = position;
            p.transform.localRotation = rotation;
            p.transform.localScale    = scale;
            block.SetColor(ColorId, color);
            p.renderer.SetPropertyBlock(block);
        }

        protected void Show(Part p, Vector3 position, float size, Color color) =>
            Show(p, position, Vector3.one * size, color, Quaternion.identity);

        // Smoke / glow part with an opacity (alpha); fully transparent hides it
        protected void Show(Part p, Vector3 position, float size, Color color, float alpha)
        {
            color.a = Mathf.Clamp01(alpha);
            Show(p, position, color.a > 0.004f ? Vector3.one * size : Vector3.zero, color, Quaternion.identity);
        }

        protected void Show(Part p, Vector3 position, Vector3 scale, Color color, float alpha, Quaternion rotation)
        {
            color.a = Mathf.Clamp01(alpha);
            Show(p, position, color.a > 0.004f ? scale : Vector3.zero, color, rotation);
        }

        protected static void Hide(Part p) => p.renderer.enabled = false;

        // Ground height (local y) under a point given in this tile's space; continuous across tiles.
        protected float Ground(Vector3 local) => grid.GroundHeight(cell, local);
        protected Vector3 OnGround(Vector3 local, float lift = 0f) => new(local.x, Ground(local) + lift, local.z);

        // Offset from this tile's centre to another tile's centre (across the wrap seam if need be).
        protected Vector3 Toward(HexCell other) => PhenomenaUtil.Offset(grid, cell, other);

        // 0 → 1 over [a, b] with smooth ends
        protected static float Ramp(float x, float a, float b) => Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(a, b, x));

        // Rises over the first `fadeIn`, holds, and falls over the last `fadeOut` of u
        protected static float Envelope(float u, float fadeIn, float fadeOut) =>
            Ramp(u, 0f, fadeIn) * (1f - Ramp(u, 1f - fadeOut, 1f));

        private static Mesh CreateBall()
        {
            var mesh = new Mesh { name = "FxBall" };
            // icosphere, 2 subdivisions, shared vertices so normals are smooth
            float t = (1f + Mathf.Sqrt(5f)) / 2f;
            var v = new List<Vector3>
            {
                new(-1, t, 0), new(1, t, 0), new(-1, -t, 0), new(1, -t, 0), new(0, -1, t), new(0, 1, t),
                new(0, -1, -t), new(0, 1, -t), new(t, 0, -1), new(t, 0, 1), new(-t, 0, -1), new(-t, 0, 1),
            };
            for (int i = 0; i < v.Count; i++) v[i] = v[i].normalized;
            var f = new List<int>
            {
                0, 11, 5, 0, 5, 1, 0, 1, 7, 0, 7, 10, 0, 10, 11, 1, 5, 9, 5, 11, 4, 11, 10, 2, 10, 7, 6, 7, 1, 8,
                3, 9, 4, 3, 4, 2, 3, 2, 6, 3, 6, 8, 3, 8, 9, 4, 9, 5, 2, 4, 11, 6, 2, 10, 8, 6, 7, 9, 8, 1,
            };
            for (int level = 0; level < 2; level++)
            {
                var mid = new Dictionary<long, int>();
                int Mid(int a, int b)
                {
                    long key = a < b ? ((long)a << 32) | (uint)b : ((long)b << 32) | (uint)a;
                    if (mid.TryGetValue(key, out int m)) return m;
                    v.Add(((v[a] + v[b]) * 0.5f).normalized);
                    return mid[key] = v.Count - 1;
                }
                var next = new List<int>();
                for (int i = 0; i < f.Count; i += 3)
                {
                    int a = f[i], b = f[i + 1], c = f[i + 2];
                    int ab = Mid(a, b), bc = Mid(b, c), ca = Mid(c, a);
                    next.AddRange(new[] { a, ab, ca, b, bc, ab, c, ca, bc, ab, bc, ca });
                }
                f = next;
            }
            for (int i = 0; i < f.Count; i += 3) // face outward
            {
                Vector3 a = v[f[i]], b = v[f[i + 1]], c = v[f[i + 2]];
                if (Vector3.Dot(Vector3.Cross(b - a, c - a), a + b + c) < 0f) (f[i + 1], f[i + 2]) = (f[i + 2], f[i + 1]);
            }
            mesh.SetVertices(v);
            mesh.SetNormals(v);
            mesh.SetTriangles(f, 0);
            var colors = new Color[v.Count];
            for (int i = 0; i < colors.Length; i++) colors[i] = Color.white;
            mesh.colors = colors;
            mesh.RecalculateBounds();
            return mesh;
        }

        // Boulders: an icosahedron pulled into an irregular, flattened or elongated block (strong
        // per-corner jitter), flat shaded with a slightly different shade per facet so the faces read
        private static Mesh[] CreateRocks(int count)
        {
            var rnd = new System.Random(1234);
            float R(float a, float b) => a + (float)rnd.NextDouble() * (b - a);
            float t = (1f + Mathf.Sqrt(5f)) / 2f;
            Vector3[] baseV =
            {
                new(-1, t, 0), new(1, t, 0), new(-1, -t, 0), new(1, -t, 0), new(0, -1, t), new(0, 1, t),
                new(0, -1, -t), new(0, 1, -t), new(t, 0, -1), new(t, 0, 1), new(-t, 0, -1), new(-t, 0, 1),
            };
            int[] f =
            {
                0, 11, 5, 0, 5, 1, 0, 1, 7, 0, 7, 10, 0, 10, 11, 1, 5, 9, 5, 11, 4, 11, 10, 2, 10, 7, 6, 7, 1, 8,
                3, 9, 4, 3, 4, 2, 3, 2, 6, 3, 6, 8, 3, 8, 9, 4, 9, 5, 2, 4, 11, 6, 2, 10, 8, 6, 7, 9, 8, 1,
            };
            var meshes = new Mesh[count];
            for (int m = 0; m < count; m++)
            {
                var stretch = new Vector3(R(0.8f, 1.25f), R(0.55f, 0.9f), R(0.8f, 1.35f));
                var v = new Vector3[baseV.Length];
                for (int i = 0; i < v.Length; i++)
                    v[i] = Vector3.Scale(baseV[i].normalized * R(0.6f, 1.2f), stretch);
                // knock a couple of corners flat so it reads as a broken block, not a pebble
                for (int k = 0; k < 2; k++) { int i = rnd.Next(v.Length); v[i] *= 0.55f; }
                var verts  = new List<Vector3>();
                var colors = new List<Color>();
                var tris   = new List<int>();
                for (int i = 0; i < f.Length; i += 3)
                {
                    Vector3 a = v[f[i]], b = v[f[i + 1]], c = v[f[i + 2]];
                    if (Vector3.Dot(Vector3.Cross(b - a, c - a), a + b + c) < 0f) (b, c) = (c, b);
                    float shade = R(0.82f, 1.08f);
                    var col = new Color(shade, shade, shade);
                    verts.Add(a); verts.Add(b); verts.Add(c);
                    colors.Add(col); colors.Add(col); colors.Add(col);
                    tris.Add(i); tris.Add(i + 1); tris.Add(i + 2);
                }
                var mesh = new Mesh { name = $"PhenomenonRock{m}" };
                mesh.SetVertices(verts);
                mesh.SetColors(colors);
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateNormals();
                mesh.RecalculateBounds();
                meshes[m] = mesh;
            }
            return meshes;
        }

        // Low-poly boulder of radius ~1 with white vertex colours (tinted per part)
        private static Mesh CreateChunk()
        {
            var mesh = new Mesh { name = "PhenomenonChunk" };
            float t = (1f + Mathf.Sqrt(5f)) / 2f;
            var v = new List<Vector3>
            {
                new(-1, t, 0), new(1, t, 0), new(-1, -t, 0), new(1, -t, 0),
                new(0, -1, t), new(0, 1, t), new(0, -1, -t), new(0, 1, -t),
                new(t, 0, -1), new(t, 0, 1), new(-t, 0, -1), new(-t, 0, 1),
            };
            int[] f =
            {
                0, 11, 5, 0, 5, 1, 0, 1, 7, 0, 7, 10, 0, 10, 11, 1, 5, 9, 5, 11, 4, 11, 10, 2, 10, 7, 6, 7, 1, 8,
                3, 9, 4, 3, 4, 2, 3, 2, 6, 3, 6, 8, 3, 8, 9, 4, 9, 5, 2, 4, 11, 6, 2, 10, 8, 6, 7, 9, 8, 1,
            };
            // lumpy: fixed per-vertex radii so every boulder shares one irregular mesh
            float[] lump = { 1.0f, 0.85f, 0.95f, 1.1f, 0.9f, 1.05f, 0.8f, 1.0f, 1.1f, 0.9f, 0.95f, 1.05f };
            for (int i = 0; i < v.Count; i++) v[i] = v[i].normalized * lump[i];
            // flat shaded: own vertices per face
            var verts = new List<Vector3>();
            var tris  = new List<int>();
            for (int i = 0; i < f.Length; i += 3)
            {
                Vector3 a = v[f[i]], b = v[f[i + 1]], c = v[f[i + 2]];
                if (Vector3.Dot(Vector3.Cross(b - a, c - a), a + b + c) < 0f) (b, c) = (c, b); // face outward
                verts.Add(a); verts.Add(b); verts.Add(c);
                tris.Add(i); tris.Add(i + 1); tris.Add(i + 2);
            }
            mesh.SetVertices(verts);
            mesh.SetTriangles(tris, 0);
            var colors = new Color[verts.Count];
            for (int i = 0; i < colors.Length; i++) colors[i] = Color.white;
            mesh.colors = colors;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        // Flat pointy-top hexagon of radius 1 at y = 0, facing up (water sheets for floods, surges)
        private static Mesh CreateDisc()
        {
            var mesh  = new Mesh { name = "PhenomenonDisc" };
            var verts = new Vector3[7];
            verts[0] = Vector3.zero;
            for (int i = 0; i < 6; i++)
            {
                float a = Mathf.Deg2Rad * 60f * i;
                verts[1 + i] = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a));
            }
            var tris = new int[18];
            for (int i = 0; i < 6; i++) { tris[3 * i] = 0; tris[3 * i + 1] = 1 + i; tris[3 * i + 2] = 1 + (i + 1) % 6; }
            mesh.vertices = verts;
            mesh.triangles = tris;
            var colors = new Color[7];
            for (int i = 0; i < 7; i++) colors[i] = Color.white;
            mesh.colors = colors;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }
    }

    public static class PhenomenaUtil
    {
        public const int CliffElevation = 5; // coastal land this high meets the sea in a cliff (as in HexGrid)

        public static float CellSize(HexGrid grid) => grid.WrapWidth / (Mathf.Sqrt(3f) * Mathf.Max(1, grid.Width));

        public static Vector3 Offset(HexGrid grid, HexCell from, HexCell to)
        {
            var d = to.transform.localPosition - from.transform.localPosition;
            d.x -= Mathf.Round(d.x / grid.WrapWidth) * grid.WrapWidth;
            d.y = 0f;
            return d;
        }

        // Neighbour across each edge (edge e faces 60e + 30 degrees clockwise from +Z); null off the map.
        public static HexCell[] EdgeNeighbors(HexGrid grid, HexCell cell)
        {
            var result = new HexCell[6];
            foreach (var n in grid.GetNeighbors(cell))
            {
                var d = Offset(grid, cell, n);
                float angle = Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;
                result[((Mathf.RoundToInt((angle - 30f) / 60f) % 6) + 6) % 6] = n;
            }
            return result;
        }

        public static Vector3 EdgeDirection(int edge)
        {
            float a = Mathf.Deg2Rad * (60f * edge + 30f);
            return new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a));
        }

        public static bool IsLand(HexCell c) => c != null && c.Terrain != null && !c.IsWater;
        public static bool IsSea(HexCell c)  => c != null && c.Terrain != null && c.Terrain.kind == TerrainKind.SaltWater;

        // Where the camera looks, on the map plane (world space); false without a camera.
        public static bool CameraFocus(out Vector3 point, out float viewRadius)
        {
            point = default;
            viewRadius = 0f;
            var cam = Camera.main;
            if (cam == null) return false;
            var ray = cam.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0f));
            if (!new Plane(Vector3.up, Vector3.zero).Raycast(ray, out float dist)) return false;
            point = ray.GetPoint(dist);
            viewRadius = Mathf.Clamp(cam.transform.position.y * 1.1f, 3f, 16f);
            return true;
        }
    }
}
