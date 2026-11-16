using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Geothermal fields. On land: ground crusted white with sinter, hot springs ringed in the
    // colours of the microbes that live at each temperature (deep blue in the scalding middle, then
    // turquoise, green, yellow and orange toward the cooler rim), a geyser on its sinter mound,
    // bubbling mud pots, fumaroles caked in yellow sulphur and a little staircase of travertine
    // terraces. On the shallow seabed: pale "white smoker" chimneys, sulphur mounds, white and
    // orange bacterial mats and pillow lava, with gas bubbling out of the seeps. GeothermalSteam
    // animates the steam (land) and bubbles (sea) from the points registered here.
    public static partial class MapFeatureMeshes
    {
        static readonly Color Sinter      = new(0.76f, 0.73f, 0.64f);
        static readonly Color RunOff      = new(0.62f, 0.42f, 0.24f);
        static readonly Color Sulphur     = new(0.86f, 0.76f, 0.30f);
        static readonly Color MudGrey     = new(0.47f, 0.44f, 0.40f);
        static readonly Color MatOrange   = new(0.74f, 0.42f, 0.20f);
        static readonly Color MatYellow   = new(0.80f, 0.70f, 0.36f);
        static readonly Color MatGreen    = new(0.46f, 0.58f, 0.40f);
        static readonly Color SpringTeal  = new(0.30f, 0.62f, 0.66f);
        static readonly Color SpringBlue  = new(0.12f, 0.38f, 0.60f);
        static readonly Color WhiteSmoker = new(0.86f, 0.84f, 0.78f);
        static readonly Color MatPale     = new(0.62f, 0.66f, 0.64f); // a sulphur-bacteria film under water
        static readonly Color PillowLava  = new(0.20f, 0.18f, 0.18f);

        // The points steam (or bubbles) rise from on each geothermal mesh; on land the first is the geyser
        static readonly Dictionary<Mesh, Vector3[]> steamVents = new();

        public static bool TryGetSteamVents(Mesh mesh, out Vector3[] points)
        {
            points = null;
            return mesh != null && steamVents.TryGetValue(mesh, out points);
        }

        static void RegisterSteam(Mesh mesh, List<Vector3> points)
        {
            if (steamVents.Count > 512)
            {
                var gone = new List<Mesh>();
                foreach (var m in steamVents.Keys) if (m == null) gone.Add(m);
                foreach (var m in gone) steamVents.Remove(m);
            }
            steamVents[mesh] = points.ToArray();
        }

        // Flat irregular patch lying on the ground (pond-like fan), `lift` above it
        static void AddGroundPatch(Builder b, System.Random rng, Vector3 centre, float radius, Color color, int sides = 10, float jitter = 0.25f)
        {
            var rim = Ring(rng, centre, radius, sides, jitter);
            for (int i = 0; i < rim.Length; i++)
                b.AddTri(centre, rim[i], rim[(i + 1) % rim.Length], Shade(rng, color, 0.04f), centre - Vector3.up);
        }

        // A hot spring: rings of colour from the cool rim to the deep, scalding middle
        static void AddHotSpring(Builder b, System.Random rng, Vector3 centre, float r)
        {
            // colour stops from the rim inward; drawn as many thin, blended rings so they shade into
            // each other instead of reading as a target
            var stops = new[] { (Sinter, 1f), (MatOrange, 0.86f), (MatYellow, 0.7f), (MatGreen, 0.58f), (SpringTeal, 0.46f), (SpringBlue, 0.2f) };
            const int steps = 14;
            float rot = Range(rng, 0f, 360f);
            for (int k = 0; k < steps; k++)
            {
                float f = Mathf.Lerp(1f, 0.2f, k / (float)(steps - 1));
                int s = 0;
                while (s < stops.Length - 2 && f < stops[s + 1].Item2) s++;
                var col = Color.Lerp(stops[s].Item1, stops[s + 1].Item1, Mathf.InverseLerp(stops[s].Item2, stops[s + 1].Item2, f));
                var c = centre + Vector3.up * (0.0004f * k * r / 0.1f);
                const int sides = 24;
                for (int i = 0; i < sides; i++)
                {
                    float a0 = (rot + i * 360f / sides) * Mathf.Deg2Rad, a1 = (rot + (i + 1) * 360f / sides) * Mathf.Deg2Rad;
                    float w0 = 1f + 0.06f * Mathf.Sin(a0 * 3f), w1 = 1f + 0.06f * Mathf.Sin(a1 * 3f);
                    b.AddTri(c, c + new Vector3(Mathf.Sin(a0), 0f, Mathf.Cos(a0)) * r * f * w0,
                                c + new Vector3(Mathf.Sin(a1), 0f, Mathf.Cos(a1)) * r * f * w1, col, c - Vector3.up);
                }
            }
        }

        // A thin, tapering streak of microbe-stained run-off from a spring across the ground
        static void AddRunOff(Builder b, System.Random rng, System.Func<Vector2, Vector3> on, Vector2 from, Vector2 dir, float length, float width)
        {
            const int segs = 6;
            var side = new Vector2(dir.y, -dir.x);
            Vector3 l0 = default, r0 = default;
            float bend = Range(rng, -0.6f, 0.6f);
            for (int k = 0; k <= segs; k++)
            {
                float t = k / (float)segs;
                var d = (dir + side * bend * t).normalized;
                var p = from + d * length * t;
                float w = width * (1f - t * 0.85f);
                var l = on(p + side * w); var r = on(p - side * w);
                if (k > 0)
                    b.AddQuad(l0, r0, r, l, Color.Lerp(MatOrange, RunOff, t) * Range(rng, 0.95f, 1.05f), (l0 + r) * 0.5f - Vector3.up);
                l0 = l; r0 = r;
            }
        }

        public static Mesh CreateGeothermalField(System.Random rng, float size, System.Func<Vector2, float> groundAt = null)
        {
            var b = new Builder();
            var steam = new List<Vector3>();
            var taken = new List<Vector2>();
            float apothem = 0.8660254f * size;
            Vector3 On(Vector2 p, float lift = 0f) => new(p.x, (groundAt != null ? groundAt(p) : 0f) + lift * size, p.y);

            // (the mineral-crusted ground itself is a tint on the tile, see HexGrid.SetGroundLook)

            // the geyser: a low sinter mound with a vent, near the middle
            var gp = new Vector2(Range(rng, -0.12f, 0.12f), Range(rng, -0.12f, 0.12f)) * size;
            taken.Add(gp);
            var gv = AddVolcanoCone(b, rng, size, new Cone
            {
                at = On(gp), radius = 0.1f * size, height = 0.045f * size, top = 0.025f * size, sides = 16, rings = 4,
                profile = 0.8f, ridge = 0.1f, jitter = 0.05f, rough = 0.4f, crater = Crater.Dry, craterDepth = 0.3f,
                craterInset = 0.5f, ash = Sinter, rock = Sinter * 0.86f, blocks = 0,
            }, null);
            steam.Add(gv);

            // hot springs
            foreach (var p in HexScatter(rng, rng.Next(2, 4), apothem * 0.7f, 0.3f * size, taken))
            {
                float r = size * Range(rng, 0.09f, 0.15f);
                AddHotSpring(b, rng, On(p, 0.003f), r);
                float ra = Range(rng, 0f, Mathf.PI * 2f);
                for (int i = rng.Next(1, 3); i > 0; i--, ra += Range(rng, 0.6f, 1.4f))
                    AddRunOff(b, rng, q => On(q, 0.0025f), p, new Vector2(Mathf.Sin(ra), Mathf.Cos(ra)), size * Range(rng, 0.12f, 0.22f), r * 0.3f);
                steam.Add(On(p, 0.01f));
                taken.Add(p);
            }

            // bubbling mud pots
            foreach (var p in HexScatter(rng, rng.Next(1, 3), apothem * 0.8f, 0.18f * size, taken))
            {
                AddGroundPatch(b, rng, On(p, 0.003f), size * Range(rng, 0.04f, 0.06f), MudGrey, 10, 0.15f);
                for (int i = rng.Next(2, 4); i > 0; i--)
                    AddBlob(b, rng, On(p + new Vector2(Range(rng, -0.025f, 0.025f), Range(rng, -0.025f, 0.025f)) * size, 0.004f),
                            size * Range(rng, 0.006f, 0.012f), 0.6f, 0, MudGrey * 1.12f);
                taken.Add(p);
            }

            // fumaroles: rock heaps caked in sulphur, steaming
            foreach (var p in HexScatter(rng, rng.Next(2, 4), apothem * 0.85f, 0.16f * size, taken))
            {
                var at = On(p);
                for (int i = rng.Next(2, 4); i > 0; i--)
                    AddRock(b, rng, at + new Vector3(Range(rng, -0.03f, 0.03f), 0f, Range(rng, -0.03f, 0.03f)) * size,
                            size * Range(rng, 0.015f, 0.03f), rng.NextDouble() < 0.6 ? Sulphur : Color.Lerp(Sulphur, Basalt, 0.5f));
                AddGroundPatch(b, rng, On(p, 0.0025f), size * 0.05f, Color.Lerp(Sulphur, Sinter, 0.4f), 14, 0.1f);
                steam.Add(On(p, 0.03f));
                taken.Add(p);
            }

            // a staircase of travertine terraces: rimmed white ledges stepping down one side, each
            // holding a shallow turquoise pool
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                var dir = new Vector2(Mathf.Sin(a), Mathf.Cos(a));
                for (int k = 0; k < 4; k++)
                {
                    var c = dir * (0.4f + 0.075f * k) * size + new Vector2(dir.y, -dir.x) * Range(rng, -0.03f, 0.03f) * size;
                    float r = size * (0.085f - 0.01f * k);
                    float y = (0.024f - 0.006f * k) * size;
                    var top = On(c) + Vector3.up * y;
                    var rim = Ring(rng, top, r, 16, 0.08f);
                    for (int i = 0; i < rim.Length; i++)
                    {
                        int j = (i + 1) % rim.Length;
                        var d0 = new Vector3(rim[i].x, On(new Vector2(rim[i].x, rim[i].z)).y - 0.005f * size, rim[i].z);
                        var d1 = new Vector3(rim[j].x, On(new Vector2(rim[j].x, rim[j].z)).y - 0.005f * size, rim[j].z);
                        b.AddQuad(rim[i], rim[j], d1, d0, Shade(rng, Sinter * 0.9f, 0.04f), top - Vector3.up * 0.1f * size); // the ledge's face
                        b.AddTri(top, rim[i], rim[j], Shade(rng, Sinter, 0.03f), top - Vector3.up);
                    }
                    AddGroundPatch(b, rng, top + Vector3.up * 0.002f * size, r * 0.78f, Color.Lerp(SpringTeal, Sinter, 0.25f), 16, 0.06f);
                }
            }

            var mesh = b.ToMesh("Geothermal");
            RegisterSteam(mesh, steam);
            return mesh;
        }

        // A shallow-water hydrothermal field on the seabed
        public static Mesh CreateShallowVents(System.Random rng, float size)
        {
            var b = new Builder();
            var seeps = new List<Vector3>();
            float apothem = 0.8660254f * size;
            var taken = new List<Vector2>();

            // bacterial mats: small, rounded, dull patches round the vents (kept apart and muted, so
            // they read as a film on the floor rather than bright white shapes)
            foreach (var p in HexScatter(rng, rng.Next(3, 6), apothem * 0.75f, 0.2f * size, new List<Vector2>()))
                AddGroundPatch(b, rng, new Vector3(p.x, 0.002f * size, p.y), size * Range(rng, 0.05f, 0.09f),
                               rng.NextDouble() < 0.4 ? Shade(rng, MatPale, 0.05f) : Color.Lerp(MatOrange, MatYellow, Range(rng, 0f, 0.6f)) * 0.85f, 14, 0.12f);

            // white smokers: short, knobbly pale chimneys
            foreach (var p in HexScatter(rng, rng.Next(3, 6), apothem * 0.6f, 0.15f * size, taken))
            {
                var root = new Vector3(p.x, 0f, p.y);
                float h = size * Range(rng, 0.08f, 0.18f);
                var prev = root - Vector3.up * 0.01f;
                int segs = rng.Next(2, 4);
                for (int k = 1; k <= segs; k++)
                {
                    float t = k / (float)segs;
                    var next = root + new Vector3(Range(rng, -0.015f, 0.015f) * size, h * t, Range(rng, -0.015f, 0.015f) * size);
                    AddLimb(b, prev, next, Mathf.Lerp(0.04f, 0.022f, t - 1f / segs) * size, Mathf.Lerp(0.04f, 0.022f, t) * size, Shade(rng, WhiteSmoker, 0.06f));
                    prev = next;
                }
                AddBlob(b, rng, prev, 0.024f * size, 0.6f, 0, Sulphur * 0.9f); // mineral crust round the mouth
                seeps.Add(prev + Vector3.up * 0.01f * size);
                taken.Add(p);
            }

            // sulphur mounds and gas seeps in the mats
            foreach (var p in HexScatter(rng, rng.Next(3, 5), apothem * 0.85f, 0.12f * size, taken))
            {
                var at = new Vector3(p.x, 0f, p.y);
                AddBlob(b, rng, at, size * Range(rng, 0.025f, 0.045f), 0.45f, 0, Shade(rng, Sulphur, 0.08f));
                seeps.Add(at + Vector3.up * 0.02f * size);
                taken.Add(p);
            }

            // pillow lava heaped at the edges
            foreach (var p in HexScatter(rng, rng.Next(5, 9), apothem * 0.95f, 0.08f * size, taken))
            {
                if (p.magnitude < apothem * 0.5f) continue;
                for (int i = rng.Next(2, 4); i > 0; i--)
                    AddBlob(b, rng, new Vector3(p.x + Range(rng, -0.03f, 0.03f) * size, 0.01f * size, p.y + Range(rng, -0.03f, 0.03f) * size),
                            size * Range(rng, 0.025f, 0.04f), 0.65f, 0, Shade(rng, PillowLava, 0.08f));
            }

            var mesh = b.ToMesh("ShallowVents");
            RegisterSteam(mesh, seeps);
            return mesh;
        }
    }
}
