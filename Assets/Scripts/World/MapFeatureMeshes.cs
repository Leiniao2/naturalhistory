using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace NaturalHistory.World
{
    // Low-poly, flat-shaded props that sit on a hex tile's top face: mountain peaks and forest stands.
    // Colors are baked into vertex colors so all props share one material (MapFeature shader).
    // Meshes are centred on the tile (y = 0 is the top face) and stay inside the hex's inner radius.
    public static partial class MapFeatureMeshes
    {
        static readonly Color Rock   = new(0.46f, 0.42f, 0.38f);
        static readonly Color Snow   = new(0.94f, 0.96f, 0.99f);
        static readonly Color Bark      = new(0.36f, 0.25f, 0.16f);
        static readonly Color Leaf      = new(0.30f, 0.52f, 0.20f);
        static readonly Color LeafLight = new(0.48f, 0.66f, 0.26f);
        static readonly Color Needle    = new(0.10f, 0.29f, 0.18f);
        static readonly Color NeedleTip = new(0.22f, 0.45f, 0.26f);
        static readonly Color Shrub     = new(0.24f, 0.40f, 0.17f);

        // What a mountain tile needs to build its piece of a range (see CreateMassif).
        public struct MassifSite
        {
            public float Apothem;       // tile centre to cell edge; the piece covers the whole cell
            public float BaseY;         // world height of the tile top (rock strata line up across tiles)
            public bool[] Joined;       // per edge (60e + 30° clockwise from +Z): the neighbour is mountain too
            public Color Rock;          // rock tint here…
            public Color[] EdgeRock;    // …and where each edge is crossed (shared with the neighbour)
            public float Snow;          // snow line as a fraction of the massif height from the top
            public float[] EdgeSnow;
            public bool Green;          // grassy foot and conifers on the lower slopes
            public System.Func<Vector2, float> GroundAt; // tile surface at a local point, relative to the tile top
            public System.Func<Vector2, float> Relief;   // 0..1 ruggedness, continuous over the whole map
            public System.Func<Vector2, float> Detail;   // 0..1 smooth small-scale noise for colour variation, also map-wide
        }

        // Tallest a summit gets above its tile, × cell size
        public const float MassifHeight = 1.15f;

        // One tile's piece of a continuous mountain surface. Height comes from map-wide relief noise
        // (ridges, valleys, peaks) times a mask that is 1 toward neighbouring mountain tiles and falls
        // to the ground toward every other neighbour. Everything at a shared edge depends only on
        // world position and values both tiles agree on, so neighbouring pieces meet seamlessly and a
        // range reads as one massif rather than a grid of separate peaks.
        public static Mesh CreateMassif(System.Random rng, float size, MassifSite site)
        {
            const int n = 20; // lattice steps along each edge of the hex (6 n² triangles)
            var b = new Builder();
            float maxH = MassifHeight * size;
            var corners = new Vector2[6];
            var normals = new Vector2[6];
            for (int i = 0; i < 6; i++)
            {
                float a = 60f * i * Mathf.Deg2Rad, e = (60f * i + 30f) * Mathf.Deg2Rad;
                corners[i] = new Vector2(Mathf.Sin(a), Mathf.Cos(a)) * (site.Apothem / 0.8660254f);
                normals[i] = new Vector2(Mathf.Sin(e), Mathf.Cos(e));
            }

            float EdgeDistance(int e, Vector2 p) => site.Apothem - Vector2.Dot(p, normals[e]);
            float Mask(Vector2 p)
            {
                float m = 1f;
                for (int e = 0; e < 6; e++)
                    if (!site.Joined[e]) m *= Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(EdgeDistance(e, p) / site.Apothem));
                if (m >= 1f) return 1f;
                // The foot ends along an irregular line (map-wide noise, so neighbours agree) rather
                // than tracing the hex outline
                float t = 0.35f * site.Detail(p);
                return Mathf.Clamp01((m - t) / (1f - t));
            }
            // Below the tile surface where the mask is 0, so the massif's edge hides under the ground
            Vector3 Point(Vector2 p)
            {
                float m = Mask(p);
                float y = site.GroundAt(p) + m * maxH * (0.22f + 0.78f * site.Relief(p)) - 0.02f * size * (1f - m);
                return new Vector3(p.x, y, p.y);
            }
            // Snow line and rock tint: this tile's, easing to the shared edge value near each edge
            (float snow, Color rock) Local(Vector2 p)
            {
                int near = 0; float best = float.MaxValue;
                for (int e = 0; e < 6; e++) { float d = EdgeDistance(e, p); if (d < best) { best = d; near = e; } }
                float w = 1f - Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(best / (0.5f * site.Apothem)));
                return (Mathf.Lerp(site.Snow, site.EdgeSnow[near], w), Color.Lerp(site.Rock, site.EdgeRock[near], w));
            }

            float band = maxH * 0.12f;
            void Face(Vector3 p0, Vector3 p1, Vector3 p2)
            {
                var c   = (p0 + p1 + p2) / 3f;
                var at  = new Vector2(c.x, c.z);
                float rel = c.y - site.GroundAt(at);
                if (rel < -0.01f * size) return; // sunk under the tile surface: never seen
                var below = c + Vector3.down * size;
                float up  = FaceUp(p0, p1, p2, below);
                var (snow, rockTint) = Local(at);
                // Variation follows smooth map-wide noise rather than a random value per triangle,
                // so neighbouring facets differ only by their lighting and the surface doesn't speckle
                float detail = site.Detail(at);
                float snowY  = maxH * (1f - snow) + maxH * 0.12f * (detail - 0.5f);
                float shade  = 0.94f + 0.12f * detail;
                Color color;
                if (rel > snowY && (up > 0.45f || rel > snowY + 0.4f * (maxH - snowY)))
                    color = Snow * (0.97f + 0.03f * detail);
                else if (site.Green && rel < (0.1f + 0.08f * detail) * maxH && up > 0.55f)
                    color = Foothill * shade;
                else
                {
                    // Strata: soft bands by world height, wavering with the detail noise
                    float strata = Mathf.Repeat((c.y + site.BaseY) / band + detail * 0.8f, 2f);
                    var rock = Color.Lerp(Rock, RockDark, Mathf.SmoothStep(0f, 1f, Mathf.Abs(strata - 1f))) * rockTint;
                    color = rock * shade * Mathf.Lerp(0.8f, 1.05f, up); // steep faces a touch darker
                }
                b.AddTri(p0, p1, p2, color, below);
            }

            // Each of the 6 triangles (centre, corner i, corner i+1) is cut into a lattice; points on
            // the hex outline are the same in both neighbouring tiles.
            var grid = new Vector3[n + 1, n + 1];
            for (int i = 0; i < 6; i++)
            {
                var ca = corners[i]; var cb = corners[(i + 1) % 6];
                for (int u = 0; u <= n; u++)
                for (int v = 0; v <= n - u; v++)
                    grid[u, v] = Point((ca * u + cb * v) / n);
                for (int u = 0; u < n; u++)
                for (int v = 0; v < n - u; v++)
                {
                    Face(grid[u, v], grid[u + 1, v], grid[u, v + 1]);
                    if (u + v + 2 <= n) Face(grid[u + 1, v], grid[u + 1, v + 1], grid[u, v + 1]);
                }
            }

            // Boulders and (where green) conifers on the lower slopes
            foreach (var p in Scatter(rng, rng.Next(14, 22), site.Apothem * 0.95f, 0.07f * size, new List<Vector2>()))
            {
                float m = Mask(p);
                if (m < 0.04f || m > 0.45f) continue;
                var at = Point(p);
                var (snow, rockTint) = Local(p);
                if (site.Green && rng.NextDouble() < 0.7)
                    AddConifer(b, rng, at - Vector3.up * 0.01f * size, size * Range(rng, 0.28f, 0.4f));
                else if (rng.NextDouble() < 0.5)
                    AddRock(b, rng, at, size * Range(rng, 0.03f, 0.055f), snow >= 0.65f ? Snow * 0.85f : Rock * rockTint);
            }
            return b.ToMesh("Massif");
        }

        // Sea stacks: pillars of bedded rock left standing off a cliffed coast as the sea cuts it
        // back, with a grassy cap and fallen blocks round the foot. toLand points (local XZ) at the
        // cliff; they stand in the near half of the sea tile.
        public static Mesh CreateSeaStacks(System.Random rng, float size, Vector2 toLand, float apothem)
        {
            var b    = new Builder();
            var dir  = toLand.normalized;
            var side = new Vector2(dir.y, -dir.x);
            int count = rng.Next(1, 4);
            for (int i = 0; i < count; i++)
            {
                var at = dir * apothem * Range(rng, 0.3f, 0.55f) // clear of the headlands, which reach about a third of the way out
                        + side * apothem * Range(rng, -0.4f, 0.4f);
                float r = size * Range(rng, 0.05f, 0.09f) * (i == 0 ? 1f : 0.75f);
                float h = size * Range(rng, 0.25f, 0.5f) * (i == 0 ? 1f : Range(rng, 0.4f, 0.8f));
                AddStack(b, rng, new Vector3(at.x, -0.03f, at.y), r, h);
            }
            return b.ToMesh("SeaStacks");
        }

        static void AddStack(Builder b, System.Random rng, Vector3 foot, float radius, float height)
        {
            const int sides = 7, bands = 5;
            var angles = new float[sides];
            float rot = Range(rng, 0f, Mathf.PI * 2f);
            for (int i = 0; i < sides; i++) angles[i] = rot + (i + Range(rng, -0.25f, 0.25f)) * Mathf.PI * 2f / sides;
            var lean = new Vector3(Range(rng, -1f, 1f), 0f, Range(rng, -1f, 1f)) * 0.08f * height;
            var inside = foot + Vector3.up * height * 0.5f;

            Vector3[] RingAt(float t)
            {
                // Wider foot (talus), a waist where the waves notch it, near-vertical above
                float rad = radius * (t < 0.12f ? Mathf.Lerp(1.35f, 0.9f, t / 0.12f) : Mathf.Lerp(1f, 0.8f, t));
                var c = foot + Vector3.up * height * t + lean * t;
                var ring = new Vector3[sides];
                for (int i = 0; i < sides; i++)
                {
                    float r = rad * Range(rng, 0.88f, 1.1f);
                    ring[i] = c + new Vector3(Mathf.Sin(angles[i]) * r, 0f, Mathf.Cos(angles[i]) * r);
                }
                return ring;
            }

            var lower = RingAt(0f);
            for (int k = 1; k <= bands; k++)
            {
                float t   = k / (float)bands;
                var upper = RingAt(t);
                var color = (k % 2 == 0 ? Rock : RockDark * 1.15f) * (k == 1 ? 0.8f : 1f); // bedding; dark, wet base
                for (int i = 0; i < sides; i++)
                {
                    int j = (i + 1) % sides;
                    b.AddQuad(lower[i], lower[j], upper[j], upper[i], Shade(rng, color, 0.05f), inside);
                }
                lower = upper;
            }
            var top = foot + Vector3.up * height * 1.03f + lean;
            for (int i = 0; i < sides; i++)
                b.AddTri(lower[i], lower[(i + 1) % sides], top, Shade(rng, Foothill, 0.06f), inside); // grassy cap

            for (int i = rng.Next(1, 4); i > 0; i--)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                var at  = foot + new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a)) * radius * Range(rng, 1.4f, 2.2f) + Vector3.up * 0.03f;
                AddRock(b, rng, at, radius * Range(rng, 0.25f, 0.45f), RockDark);
            }
        }

        // A stand of detailed trees with shrubs between the trunks. Trees near the middle are
        // taller, so the canopy reads as one domed clump from the strategy camera.
        public static Mesh CreateForest(System.Random rng, float size, bool conifer)
        {
            var b = new Builder { Foliage = true }; // plants: rough, speckled leaf clumps
            float spread = 0.5f * size;
            var trees = Scatter(rng, conifer ? rng.Next(6, 10) : rng.Next(4, 7), spread,
                                (conifer ? 0.2f : 0.27f) * size, new List<Vector2>());
            foreach (var p in trees)
            {
                var root = new Vector3(p.x, 0f, p.y);
                float s  = size * Range(rng, 0.85f, 1.1f) * Mathf.Lerp(1.1f, 0.8f, p.magnitude / spread);
                if (conifer) AddConifer(b, rng, root, s);
                else         AddBroadleaf(b, rng, root, s);
            }

            foreach (var p in Scatter(rng, rng.Next(3, 7), 0.62f * size, 0.1f * size, trees))
            {
                float r = size * Range(rng, 0.04f, 0.07f);
                AddBlob(b, rng, new Vector3(p.x, 0.25f * r, p.y), r, 0.7f, 0, Shade(rng, Shrub));
            }
            return b.ToMesh(conifer ? "ConiferForest" : "BroadleafForest");
        }

        // Up to `count` points in a disc, each at least minGap from the others and from `taken`.
        static List<Vector2> Scatter(System.Random rng, int count, float radius, float minGap, List<Vector2> taken)
        {
            var placed = new List<Vector2>();
            float gapSq = minGap * minGap;
            for (int tries = 0; tries < count * 12 && placed.Count < count; tries++)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                float d = Mathf.Sqrt((float)rng.NextDouble()) * radius; // sqrt → uniform over the disc
                var p = new Vector2(Mathf.Sin(a) * d, Mathf.Cos(a) * d);
                if (placed.Exists(q => (q - p).sqrMagnitude < gapSq) || taken.Exists(q => (q - p).sqrMagnitude < gapSq)) continue;
                placed.Add(p);
            }
            return placed;
        }

        // ---- Features: jungle, reef, oasis, volcano ----

        static readonly Color JungleDark  = new(0.07f, 0.28f, 0.10f);
        static readonly Color JungleLight = new(0.20f, 0.48f, 0.16f);
        static readonly Color PalmLeaf    = new(0.26f, 0.52f, 0.18f);
        static readonly Color PalmTrunk   = new(0.48f, 0.38f, 0.24f);
        static readonly Color Lava        = new(1.30f, 0.50f, 0.10f); // >1: stays bright under shading
        static readonly Color Basalt      = new(0.24f, 0.21f, 0.20f);
        static readonly Color PondWater   = new(0.20f, 0.48f, 0.66f);
        static readonly Color[] CoralColors =
        {
            new(0.95f, 0.45f, 0.55f), new(0.98f, 0.62f, 0.30f), new(0.70f, 0.42f, 0.85f),
            new(0.98f, 0.85f, 0.35f), new(0.35f, 0.80f, 0.75f),
        };

        // Packed canopy of large, dark leaf clumps at mixed heights, with emergent palms above.
        public static Mesh CreateJungle(System.Random rng, float size)
        {
            var b = new Builder { Foliage = true }; // plants: rough, speckled leaf clumps
            foreach (var p in Scatter(rng, rng.Next(9, 13), 0.58f * size, 0.15f * size, new List<Vector2>()))
            {
                var root  = new Vector3(p.x, 0f, p.y);
                float h   = size * Range(rng, 0.18f, 0.34f);
                var color = Color.Lerp(JungleDark, JungleLight, Range(rng, 0f, 1f));
                AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * h, 0.025f * size, 0.018f * size, Shade(rng, Bark));
                AddBlob(b, rng, root + Vector3.up * (h + 0.05f * size), Range(rng, 0.12f, 0.17f) * size, 0.7f, 1, color);
            }
            for (int i = rng.Next(1, 3); i > 0; i--)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f), d = Range(rng, 0f, 0.35f) * size;
                AddPalm(b, rng, new Vector3(Mathf.Sin(a) * d, 0f, Mathf.Cos(a) * d), size * Range(rng, 1.1f, 1.3f));
            }
            return b.ToMesh("Jungle");
        }

        // Clusters of round and branching coral just breaking the water surface.
        public static Mesh CreateReef(System.Random rng, float size)
        {
            var b = new Builder();
            foreach (var p in Scatter(rng, rng.Next(7, 12), 0.6f * size, 0.12f * size, new List<Vector2>()))
            {
                var color = Shade(rng, CoralColors[rng.Next(CoralColors.Length)]);
                float r   = size * Range(rng, 0.05f, 0.09f);
                var root  = new Vector3(p.x, -0.02f, p.y);
                if (rng.NextDouble() < 0.6)
                    AddBlob(b, rng, root + Vector3.up * r * 0.3f, r, 0.55f, 0, color);
                else
                    for (int k = rng.Next(3, 6); k > 0; k--)
                    {
                        var tip = root + new Vector3(Range(rng, -1f, 1f) * r, Range(rng, 1.2f, 2.2f) * r, Range(rng, -1f, 1f) * r);
                        AddLimb(b, root, tip, 0.25f * r, 0.12f * r, color);
                    }
            }
            return b.ToMesh("Reef");
        }

        // Small pond ringed by palms and shrubs.
        static readonly Color WetSand = new(0.42f, 0.33f, 0.22f);

        // The water of an oasis: an irregular pool outlined by a thin band of dark wet sand
        // (before land plants, a band of olive microbial crust).
        static void AddOasisShore(Builder b, System.Random rng, Vector3 center, float radius, float size, bool green)
        {
            const int sides = 20;
            float rot = Range(rng, 0f, Mathf.PI * 2f), seed = Range(rng, 0f, 50f);
            float Shore(int i)
            {
                float a = rot + i * Mathf.PI * 2f / sides;
                return radius * (0.82f + 0.3f * Mathf.PerlinNoise(seed + Mathf.Cos(a) * 1.6f, seed + Mathf.Sin(a) * 1.6f));
            }
            Vector3 At(int i, float r, float y)
            {
                float a = rot + i * Mathf.PI * 2f / sides;
                return center + new Vector3(Mathf.Sin(a) * r, y, Mathf.Cos(a) * r);
            }
            var below = center - Vector3.up;
            float rimWidth = 0.025f * size;
            for (int i = 0; i < sides; i++)
            {
                int j = (i + 1) % sides;
                float ri = Shore(i), rj = Shore(j);
                b.AddTri(center, At(i, ri, 0f), At(j, rj, 0f), PondWater, below);
                b.AddQuad(At(i, ri, 0.001f), At(i, ri + rimWidth, 0.001f), At(j, rj + rimWidth, 0.001f), At(j, rj, 0.001f),
                          green ? WetSand : MatOlive, below);
            }
        }

        public static Mesh CreateOasis(System.Random rng, float size)
        {
            var b = new Builder { Foliage = true }; // plants: rough, speckled leaf clumps
            var center = new Vector3(Range(rng, -0.06f, 0.06f) * size, 0.004f, Range(rng, -0.06f, 0.06f) * size);
            AddOasisShore(b, rng, center, 0.24f * size, size, green: true);

            int palms   = rng.Next(2, 4);
            float angle = Range(rng, 0f, 360f);
            for (int i = 0; i < palms; i++, angle += 360f / palms + Range(rng, -40f, 40f))
            {
                float a = angle * Mathf.Deg2Rad, d = Range(rng, 0.32f, 0.42f) * size;
                AddPalm(b, rng, center + new Vector3(Mathf.Sin(a) * d, -0.004f, Mathf.Cos(a) * d), size * Range(rng, 0.85f, 1.05f));
            }
            for (int i = rng.Next(2, 4); i > 0; i--)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f), d = Range(rng, 0.3f, 0.5f) * size, r = size * Range(rng, 0.04f, 0.06f);
                AddBlob(b, rng, new Vector3(Mathf.Sin(a) * d, 0.25f * r, Mathf.Cos(a) * d), r, 0.7f, 0, Shade(rng, Shrub));
            }
            return b.ToMesh("Oasis");
        }

        // One lumpy smoke puff of radius 1 (VolcanoSmoke scales, tints and moves them).
        public static Mesh CreateSmokePuff(System.Random rng)
        {
            var b = new Builder();
            AddBlob(b, rng, Vector3.zero, 1f, 0.85f, 1, Smoke * 1.25f);
            return b.ToMesh("SmokePuff");
        }

        // Ribbon of lava lying in the gully along spoke `i`, from the rim down to ring `endRing`.
        // Its edge points sit on the neighbouring ring edges (lifted a hair) so it hugs the slope.
        static void AddLavaStream(Builder b, System.Random rng, Vector3[,] g, int i, int rings, int endRing, float size, Vector3 below)
        {
            int sides = g.GetLength(1);
            int prev  = (i + sides - 1) % sides, next = (i + 1) % sides;
            var lift  = Vector3.up * 0.006f * size;
            Vector3 left = default, right = default;
            for (int k = rings; k >= endRing; k--)
            {
                float t = k / (float)rings;
                float w = size * Mathf.Lerp(0.035f, 0.014f, t) * Range(rng, 0.8f, 1.2f); // spreads out downhill
                var c   = g[k, i];
                var l   = Vector3.Lerp(c, g[k, prev], Mathf.Clamp01(w / Vector3.Distance(c, g[k, prev]))) + lift;
                var r   = Vector3.Lerp(c, g[k, next], Mathf.Clamp01(w / Vector3.Distance(c, g[k, next]))) + lift;
                if (k < rings)
                {
                    var color = Color.Lerp(LavaCool, Lava, Mathf.InverseLerp(endRing, rings, k + 0.5f));
                    b.AddQuad(left, right, r, l, color * Range(rng, 0.9f, 1.1f), below);
                }
                left = l; right = r;
            }
        }

        // Slightly curved trunk topped by drooping fronds.
        static void AddPalm(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h   = s * Range(rng, 0.42f, 0.55f);
            var lean  = new Vector3(Range(rng, -1f, 1f), 0f, Range(rng, -1f, 1f)).normalized * 0.12f * h;
            var mid   = root + Vector3.up * 0.55f * h + lean * 0.35f;
            var crown = root + Vector3.up * h + lean;
            AddLimb(b, root - Vector3.up * 0.01f, mid, 0.018f * s, 0.014f * s, PalmTrunk);
            AddLimb(b, mid, crown, 0.014f * s, 0.011f * s, PalmTrunk * 1.1f);

            int fronds  = rng.Next(6, 9);
            float start = Range(rng, 0f, 360f);
            var color   = Shade(rng, L(PalmLeaf));
            for (int i = 0; i < fronds; i++)
            {
                float a  = (start + i * 360f / fronds + Range(rng, -12f, 12f)) * Mathf.Deg2Rad;
                var dir  = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a));
                var side = Vector3.Cross(Vector3.up, dir) * 0.035f * s;
                float len = Range(rng, 0.17f, 0.22f) * s;
                var bend = crown + dir * len * 0.55f + Vector3.up * 0.03f * s;
                var tip  = crown + dir * len - Vector3.up * Range(rng, 0.06f, 0.1f) * s;
                var below = crown - Vector3.up * 0.2f * s; // fronds face up
                b.AddTri(crown, bend + side, bend - side, color, below);
                b.AddTri(bend + side, tip, bend - side, color * 0.9f, below);
            }
        }

        // ---- Small per-terrain details: break up the look of plain tiles ----

        static readonly Color Grass      = new(0.32f, 0.55f, 0.20f);
        static readonly Color DryGrass   = new(0.78f, 0.66f, 0.32f);
        static readonly Color SteppeGrass = new(0.58f, 0.60f, 0.34f);
        static readonly Color Reed       = new(0.42f, 0.50f, 0.22f);
        static readonly Color LilyPad    = new(0.22f, 0.52f, 0.24f);
        static readonly Color Sandstone  = new(0.76f, 0.58f, 0.40f);
        static readonly Color Sand       = new(0.86f, 0.74f, 0.50f);
        static readonly Color Lichen     = new(0.55f, 0.56f, 0.48f);
        static readonly Color TundraShrub = new(0.40f, 0.36f, 0.22f);
        static readonly Color Ice        = new(0.80f, 0.92f, 1.00f);
        static readonly Color[] FlowerColors =
        {
            new(0.98f, 0.95f, 0.85f), new(0.98f, 0.85f, 0.30f), new(0.75f, 0.50f, 0.90f), new(0.95f, 0.45f, 0.45f),
        };

        // Scattered small props for a terrain tile, or null if the terrain has none.
        public static Mesh CreateDetail(System.Random rng, float size, TerrainKind kind)
        {
            var b = new Builder { Foliage = true }; // plants: rough, speckled leaf clumps
            var taken = new List<Vector2>();
            List<Vector2> Spots(int min, int max, float gap)
            {
                var spots = Scatter(rng, rng.Next(min, max + 1), 0.62f * size, gap * size, taken);
                taken.AddRange(spots);
                return spots;
            }
            Vector3 At(Vector2 p) => new(p.x, 0f, p.y);

            switch (kind)
            {
                case TerrainKind.Plain:
                    foreach (var p in Spots(5, 9, 0.1f)) AddTuft(b, rng, At(p), size, Grass);
                    foreach (var p in Spots(0, 4, 0.06f))
                        AddBlob(b, rng, At(p) + Vector3.up * 0.02f * size, 0.018f * size, 1f, 0, FlowerColors[rng.Next(FlowerColors.Length)]);
                    break;
                case TerrainKind.Savanna:
                    foreach (var p in Spots(0, 2, 0.3f)) AddAcacia(b, rng, At(p), size);
                    foreach (var p in Spots(4, 7, 0.1f)) AddTuft(b, rng, At(p), size * 1.2f, DryGrass);
                    break;
                case TerrainKind.Steppe:
                    foreach (var p in Spots(6, 10, 0.1f)) AddTuft(b, rng, At(p), size, SteppeGrass);
                    foreach (var p in Spots(0, 2, 0.12f)) AddRock(b, rng, At(p), size * 0.03f, Lichen);
                    break;
                case TerrainKind.Desert:
                    // dunes only now and then, one at a time and low: the sand texture carries the desert
                    if (rng.NextDouble() < 0.25)
                        foreach (var p in Spots(1, 1, 0.3f))
                            AddDune(b, rng, At(p), Range(rng, 0.22f, 0.36f) * size, Range(rng, 0.02f, 0.045f) * size, Shade(rng, Sand, 0.06f));
                    if (rng.NextDouble() < 0.15)
                        foreach (var p in Spots(1, 1, 0.3f))
                            AddButte(b, rng, At(p), Range(rng, 0.07f, 0.12f) * size, Range(rng, 0.1f, 0.2f) * size);
                    foreach (var p in Spots(0, 3, 0.12f)) AddRock(b, rng, At(p), size * Range(rng, 0.03f, 0.06f), Sandstone);
                    break;
                case TerrainKind.Hill:
                    foreach (var p in Spots(2, 4, 0.15f)) AddRock(b, rng, At(p), size * Range(rng, 0.04f, 0.07f), Rock);
                    foreach (var p in Spots(2, 5, 0.1f)) AddTuft(b, rng, At(p), size, Grass);
                    break;
                case TerrainKind.Wetland:
                    foreach (var p in Spots(3, 5, 0.12f)) AddReeds(b, rng, At(p), size);
                    foreach (var p in Spots(1, 3, 0.08f))
                    {
                        var c = At(p) + Vector3.up * 0.004f;
                        var rim = Ring(rng, c, 0.03f * size, 6, 0.15f);
                        for (int i = 0; i < rim.Length; i++) b.AddTri(c, rim[i], rim[(i + 1) % rim.Length], LilyPad, c - Vector3.up);
                    }
                    break;
                case TerrainKind.Tundra:
                    foreach (var p in Spots(2, 4, 0.12f))
                        AddBlob(b, rng, At(p) + Vector3.up * 0.01f * size, 0.04f * size, 0.6f, 0, Shade(rng, TundraShrub));
                    foreach (var p in Spots(1, 2, 0.12f)) AddRock(b, rng, At(p), size * 0.04f, Lichen);
                    break;
                case TerrainKind.IceSheet:
                    foreach (var p in Spots(2, 4, 0.15f)) AddRock(b, rng, At(p), size * Range(rng, 0.04f, 0.08f), Ice);
                    break;
                case TerrainKind.Rainforest:
                    foreach (var p in Spots(4, 6, 0.12f))
                        AddBlob(b, rng, At(p) + Vector3.up * 0.02f * size, 0.06f * size, 0.7f, 0, Color.Lerp(JungleDark, JungleLight, Range(rng, 0.3f, 1f)));
                    break;
                default:
                    return null;
            }
            return b.ToMesh($"{kind}Detail");
        }

        // Crescent dune: a curved crest with a long, gentle windward face and a short, steep (shaded)
        // slip face, tapering to nothing at both horns.
        static void AddDune(Builder b, System.Random rng, Vector3 center, float length, float height, Color color)
        {
            const int segs = 8;
            float yaw  = Range(rng, 0f, Mathf.PI * 2f);
            var along  = new Vector3(Mathf.Sin(yaw), 0f, Mathf.Cos(yaw));
            var across = new Vector3(along.z, 0f, -along.x);
            float bend = Range(rng, -0.35f, 0.35f) * length;
            var foot = new Vector3[segs + 1]; var crest = new Vector3[segs + 1];
            var wind = new Vector3[segs + 1]; var slip  = new Vector3[segs + 1];
            for (int i = 0; i <= segs; i++)
            {
                float u   = i / (float)segs * 2f - 1f;
                float hgt = height * (1f - u * u);
                foot[i]  = center + along * (u * length * 0.5f) + across * (bend * (1f - u * u)) - Vector3.up * 0.005f;
                crest[i] = foot[i] + Vector3.up * hgt;
                wind[i]  = foot[i] - across * hgt * 3f;
                slip[i]  = foot[i] + across * hgt * 1.2f;
            }
            for (int i = 0; i < segs; i++)
            {
                var inside = (foot[i] + foot[i + 1]) * 0.5f + Vector3.up * 0.3f * (crest[i].y + crest[i + 1].y - foot[i].y - foot[i + 1].y) * 0.5f;
                b.AddQuad(wind[i], wind[i + 1], crest[i + 1], crest[i], color * 1.06f, inside);
                b.AddQuad(crest[i], crest[i + 1], slip[i + 1], slip[i], color * 0.8f, inside);
            }
        }

        // Flat-topped sandstone butte: banded strata stepping in toward the top, with talus at the foot.
        static void AddButte(Builder b, System.Random rng, Vector3 center, float radius, float height)
        {
            int sides  = rng.Next(6, 9);
            var inside = center + Vector3.up * height * 0.5f;
            var lower  = Ring(rng, center - Vector3.up * 0.01f, radius, sides, 0.2f);
            const int bands = 3;
            for (int k = 0; k < bands; k++)
            {
                float shrink = Range(rng, 0.88f, 0.96f);
                float y      = height * (k + 1) / bands;
                var upper    = new Vector3[sides];
                for (int i = 0; i < sides; i++)
                {
                    var off  = (lower[i] - center) * shrink;
                    upper[i] = center + new Vector3(off.x, y, off.z);
                }
                var band = Shade(rng, k % 2 == 0 ? Sandstone : Sandstone * new Color(0.95f, 0.78f, 0.68f), 0.05f);
                for (int i = 0; i < sides; i++)
                    b.AddQuad(lower[i], lower[(i + 1) % sides], upper[(i + 1) % sides], upper[i], band, inside);
                lower = upper;
            }
            var top = center + Vector3.up * height;
            for (int i = 0; i < sides; i++)
                b.AddTri(lower[i], lower[(i + 1) % sides], top, Sandstone * 1.08f, inside);
            for (int i = rng.Next(2, 5); i > 0; i--)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                var at  = center + new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a)) * radius * Range(rng, 1f, 1.3f);
                AddRock(b, rng, at, radius * Range(rng, 0.15f, 0.3f), Sandstone);
            }
        }

        // A few thin blades fanning out from one spot.
        static void AddTuft(Builder b, System.Random rng, Vector3 root, float size, Color color)
        {
            color = Shade(rng, color);
            for (int i = rng.Next(3, 5); i > 0; i--)
            {
                var tip = root + new Vector3(Range(rng, -0.025f, 0.025f), Range(rng, 0.05f, 0.08f), Range(rng, -0.025f, 0.025f)) * size;
                AddLimb(b, root, tip, 0.008f * size, 0.001f * size, color);
            }
        }

        static void AddReeds(Builder b, System.Random rng, Vector3 root, float size)
        {
            for (int i = rng.Next(4, 7); i > 0; i--)
            {
                var foot = root + new Vector3(Range(rng, -0.03f, 0.03f), 0f, Range(rng, -0.03f, 0.03f)) * size;
                var tip  = foot + new Vector3(Range(rng, -0.015f, 0.015f), Range(rng, 0.1f, 0.16f), Range(rng, -0.015f, 0.015f)) * size;
                AddLimb(b, foot, tip, 0.006f * size, 0.002f * size, Shade(rng, L(Reed)));
            }
        }

        // Angular, half-buried stone (low-detail blob with strong jitter).
        static void AddRock(Builder b, System.Random rng, Vector3 root, float radius, Color color) =>
            AddBlob(b, rng, root + Vector3.up * radius * 0.2f, radius, Range(rng, 0.5f, 0.8f), 0, Shade(rng, color), angular: true);

        // Thin trunk under a wide, flat crown.
        static void AddAcacia(Builder b, System.Random rng, Vector3 root, float size)
        {
            float h  = size * Range(rng, 0.22f, 0.3f);
            var top  = root + new Vector3(Range(rng, -0.03f, 0.03f) * size, h, Range(rng, -0.03f, 0.03f) * size);
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.016f * size, 0.01f * size, Shade(rng, Bark));
            AddBlob(b, rng, top + Vector3.up * 0.02f * size, Range(rng, 0.13f, 0.17f) * size, 0.28f, 1, Shade(rng, L(new Color(0.36f, 0.48f, 0.20f))));
        }

        static readonly Color RockDark = new(0.36f, 0.33f, 0.31f);
        static readonly Color Foothill = new(0.38f, 0.40f, 0.27f);
        static readonly Color Ash      = new(0.43f, 0.39f, 0.35f);
        static readonly Color LavaCool = new(0.75f, 0.16f, 0.05f);
        static readonly Color Smoke    = new(0.62f, 0.60f, 0.58f);

        // Radial grid for cone-like landforms: ring 0 is the base (sunk slightly into the tile),
        // ring `rings` has topRadius. Height follows t^profile (profile > 1 → concave slopes).
        // Each spoke gets a radius multiplier (smoothed with its neighbours) so the slope forms
        // spurs (> 1) and gullies (< 1) that fade out toward the top.
        static Vector3[,] ConeGrid(System.Random rng, Vector3 center, float radius, float height, float topRadius,
                                   int sides, int rings, float ridge, float jitter, float profile, out float[] spokes)
        {
            // Ridges and gullies are set on at most 16 spokes and eased between them, so a finer grid
            // gets smoother slopes, not finer ridges; the per-point jitter shrinks the same way.
            int coarse = Mathf.Min(sides, 16);
            var raw = new float[coarse];
            for (int i = 0; i < coarse; i++) raw[i] = Range(rng, -1f, 1f);
            var ridges = new float[coarse];
            for (int i = 0; i < coarse; i++)
                ridges[i] = 0.5f * raw[i] + 0.25f * (raw[(i + coarse - 1) % coarse] + raw[(i + 1) % coarse]);
            spokes = new float[sides];
            for (int i = 0; i < sides; i++)
            {
                float at = i * coarse / (float)sides;
                int c0   = (int)at;
                float f  = 0.5f - 0.5f * Mathf.Cos((at - c0) * Mathf.PI);
                spokes[i] = 1f + ridge * Mathf.Lerp(ridges[c0], ridges[(c0 + 1) % coarse], f);
            }
            jitter *= coarse / (float)sides;

            float rot = Range(rng, 0f, Mathf.PI * 2f);
            var g = new Vector3[rings + 1, sides];
            for (int k = 0; k <= rings; k++)
            {
                float t   = k / (float)rings;
                float rad = Mathf.Lerp(radius, topRadius, t);
                float y   = k == 0 ? -0.01f : height * Mathf.Pow(t, profile);
                for (int i = 0; i < sides; i++)
                {
                    float a  = rot + i * Mathf.PI * 2f / sides;
                    float r  = rad * Mathf.Lerp(spokes[i], 1f, t * t) * Range(rng, 1f - jitter, 1f + jitter);
                    float yy = k == 0 ? y : y + height * Range(rng, -jitter, jitter) * 0.5f;
                    g[k, i] = center + new Vector3(Mathf.Sin(a) * r, yy, Mathf.Cos(a) * r);
                }
            }
            return g;
        }

        // Y component of the triangle's unit normal, oriented away from `inside`.
        static float FaceUp(Vector3 a, Vector3 b, Vector3 c, Vector3 inside)
        {
            var n = Vector3.Cross(b - a, c - a);
            if (Vector3.Dot(n, (a + b + c) / 3f - inside) < 0f) n = -n;
            return n.normalized.y;
        }

        // Tapered trunk under 4–6 stacked tiers of drooping boughs, dark at the bottom and lighter
        // toward the tip, finished with a spike.
        static void AddConifer(Builder b, System.Random rng, Vector3 root, float s, Color? needle = null, Color? needleTip = null)
        {
            var tipColor = L(needleTip ?? NeedleTip);
            float h  = s * Range(rng, 0.55f, 0.75f);
            var lean = new Vector3(Range(rng, -0.03f, 0.03f), 0f, Range(rng, -0.03f, 0.03f)) * h;
            AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * 0.85f * h + lean, 0.03f * s, 0.01f * s, Shade(rng, Bark));

            int tiers = rng.Next(4, 7);
            var dark  = Shade(rng, L(needle ?? Needle), 0.08f);
            for (int i = 0; i < tiers; i++)
            {
                float t      = i / (float)(tiers - 1);
                var center   = root + Vector3.up * Mathf.Lerp(0.16f, 0.7f, t) * h + lean * t;
                float radius = Mathf.Lerp(0.17f, 0.06f, t) * s * Range(rng, 0.9f, 1.1f);
                AddBoughTier(b, rng, center, radius, Mathf.Lerp(0.28f, 0.2f, t) * h, Color.Lerp(dark, tipColor, t * 0.8f));
            }
            AddCone(b, rng, root + Vector3.up * 0.86f * h + lean, 0.025f * s, 0.14f * h, tipColor);
        }

        // One skirt of boughs: a cone whose rim alternates between drooping tips and tucked-in notches.
        static void AddBoughTier(Builder b, System.Random rng, Vector3 center, float radius, float height, Color color)
        {
            int points = 2 * rng.Next(7, 10);
            float rot  = Range(rng, 0f, 360f);
            var apex   = center + new Vector3(Range(rng, -0.05f, 0.05f) * radius, height, Range(rng, -0.05f, 0.05f) * radius);
            var hub    = center + Vector3.up * 0.1f * height; // underside meets the trunk here
            var inside = center + Vector3.up * 0.3f * height;

            var rim = new Vector3[points];
            for (int i = 0; i < points; i++)
            {
                float a  = (rot + i * 360f / points) * Mathf.Deg2Rad;
                bool tip = i % 2 == 0;
                float r  = radius * (tip ? Range(rng, 0.9f, 1.1f) : Range(rng, 0.62f, 0.72f));
                float y  = tip ? -height * Range(rng, 0.18f, 0.3f) : 0f;
                rim[i] = center + new Vector3(Mathf.Sin(a) * r, y, Mathf.Cos(a) * r);
            }
            for (int i = 0; i < points; i++)
            {
                var p0 = rim[i];
                var p1 = rim[(i + 1) % points];
                b.AddTri(p0, p1, apex, color * Range(rng, 0.92f, 1.08f), inside, ao: 0.35f);
                b.AddTri(p0, p1, hub, color * 0.6f, inside);
            }
        }

        // Trunk that forks into 2–3 branches, each ending in a leaf clump, with a larger clump on top.
        static void AddBroadleaf(Builder b, System.Random rng, Vector3 root, float s, Color? leafDark = null, Color? leafLight = null)
        {
            float h  = s * Range(rng, 0.5f, 0.66f);
            var bark = Shade(rng, Bark);
            var leaf = L(Color.Lerp(leafDark ?? Leaf, leafLight ?? LeafLight, Range(rng, 0f, 0.45f)));
            var top  = root + new Vector3(Range(rng, -0.04f, 0.04f) * h, 0.5f * h, Range(rng, -0.04f, 0.04f) * h);
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.035f * s, 0.02f * s, bark);

            int branches = rng.Next(2, 4);
            float angle  = Range(rng, 0f, 360f);
            for (int i = 0; i < branches; i++, angle += 360f / branches + Range(rng, -30f, 30f))
            {
                float a  = angle * Mathf.Deg2Rad;
                var fork = Vector3.Lerp(root, top, Range(rng, 0.6f, 0.9f));
                var tip  = fork + new Vector3(Mathf.Sin(a) * 0.2f * h, Range(rng, 0.18f, 0.28f) * h, Mathf.Cos(a) * 0.2f * h);
                AddLimb(b, fork, tip, 0.016f * s, 0.008f * s, bark);
                AddBlob(b, rng, tip + Vector3.up * 0.04f * h, Range(rng, 0.1f, 0.13f) * s, 0.82f, 1, leaf * Range(rng, 0.88f, 1f));
            }
            AddBlob(b, rng, top + Vector3.up * 0.32f * h, Range(rng, 0.14f, 0.17f) * s, 0.82f, 1, leaf * 1.06f);
        }

        // Six-sided tapered prism from `from` to `to`, for trunks and branches (ends stay hidden).
        // With fineDetail, a smooth-shaded ten-sided tube instead.
        // Leaf clump between a smooth ball and a faceted rock: an uneven sphere with a few soft lobes,
        // shaded half-smooth (each corner's normal is part facet, part sphere), its colour varying
        // corner to corner (lit tops light, undersides dark, speckle, the odd sun-bleached or deep
        // blue-green patch) and a few short leafy tips on the upper side.
        static void FoliageBlob(Builder b, System.Random rng, Vector3 center, float radius, float squash, int detail, Color color)
        {
            int det = radius < smallBlobRadius ? 0 : Mathf.Clamp(detail, 1, 1);
            var (dirs, faces) = Icosphere(det);
            var lobes = new Vector3[3];
            for (int k = 0; k < 3; k++) lobes[k] = new Vector3(Range(rng, -1f, 1f), Range(rng, -0.2f, 1f), Range(rng, -1f, 1f)).normalized;
            var pts = new Vector3[dirs.Length];
            var nrm = new Vector3[dirs.Length];
            var col = new Color[dirs.Length];
            float sq = Mathf.Max(squash, 0.15f);
            var bleached = new Color(1.1f, 1.06f, 0.82f);
            var deep     = new Color(0.82f, 0.92f, 0.9f);
            for (int i = 0; i < dirs.Length; i++)
            {
                float bump = 0.93f;
                foreach (var l in lobes) { float d = Mathf.Max(0f, Vector3.Dot(dirs[i], l)); bump += 0.16f * d * d; }
                var p = dirs[i] * radius * bump * Range(rng, 0.88f, 1.1f);
                p.y *= squash;
                pts[i] = center + p;
                var sphereN = new Vector3(dirs[i].x, dirs[i].y / sq, dirs[i].z).normalized;
                nrm[i] = sphereN;
                double r = rng.NextDouble();
                var c = color * Mathf.Lerp(0.8f, 1.12f, 0.5f + 0.5f * sphereN.y) * Range(rng, 0.9f, 1.1f);
                if (r < 0.1) c *= bleached; else if (r < 0.2) c *= deep;
                col[i] = c * (1f - 0.3f * (0.5f - 0.5f * sphereN.y)); // self-shadowed underside
            }
            for (int f = 0; f < faces.Length; f += 3)
            {
                int i0 = faces[f], i1 = faces[f + 1], i2 = faces[f + 2];
                var p0 = pts[i0]; var p1 = pts[i1]; var p2 = pts[i2];
                var fn = Vector3.Cross(p1 - p0, p2 - p0);
                var mid = (p0 + p1 + p2) / 3f;
                if (Vector3.Dot(fn, mid - center) < 0f) fn = -fn;
                fn.Normalize();
                // half facet, half sphere: soft edges that still catch the light differently
                b.AddSmoothTri(p0, p1, p2,
                               Vector3.Lerp(fn, nrm[i0], 0.55f).normalized, Vector3.Lerp(fn, nrm[i1], 0.55f).normalized, Vector3.Lerp(fn, nrm[i2], 0.55f).normalized,
                               col[i0], col[i1], col[i2], center);
                // now and then a short leafy tip on the sunlit side
                if (fn.y > 0.3f && rng.NextDouble() < 0.08)
                {
                    var tip = mid + (fn + new Vector3(Range(rng, -0.25f, 0.25f), 0.15f, Range(rng, -0.25f, 0.25f))) * radius * Range(rng, 0.1f, 0.18f);
                    var tc  = (col[i0] + col[i1] + col[i2]) / 3f * 1.05f;
                    var inside = mid - fn * radius;
                    b.AddTri(p0, p1, tip, tc, inside);
                    b.AddTri(p1, p2, tip, tc * 0.96f, inside);
                    b.AddTri(p2, p0, tip, tc * 0.92f, inside);
                }
            }
        }

        // 0..1 from a position, the same every time (bark mottling without an rng)
        static float Hash01(Vector3 p)
        {
            unchecked
            {
                int h = Mathf.RoundToInt(p.x * 1000f) * 73856093 ^ Mathf.RoundToInt(p.y * 1000f) * 19349663 ^ Mathf.RoundToInt(p.z * 1000f) * 83492791;
                return (h & 0xFFFF) / 65535f;
            }
        }

        static void AddLimb(Builder b, Vector3 from, Vector3 to, float r0, float r1, Color color)
        {
            int sides  = fineDetail ? 10 : 6;
            var axis   = (to - from).normalized;
            var u      = Vector3.Cross(axis, Mathf.Abs(axis.y) < 0.99f ? Vector3.up : Vector3.right).normalized;
            var v      = Vector3.Cross(axis, u);
            var inside = (from + to) * 0.5f;
            for (int i = 0; i < sides; i++)
            {
                float a0 = Mathf.PI * 2f * i / sides, a1 = Mathf.PI * 2f * (i + 1) / sides;
                var d0 = u * Mathf.Cos(a0) + v * Mathf.Sin(a0);
                var d1 = u * Mathf.Cos(a1) + v * Mathf.Sin(a1);
                // plants: each face of the bark its own shade, so trunks look rough rather than painted
                var c = b.Foliage ? color * (0.82f + 0.3f * Hash01(from + d0 * r0 + to)) : color;
                if (!fineDetail) { b.AddQuad(from + d0 * r0, from + d1 * r0, to + d1 * r1, to + d0 * r1, c, inside); continue; }
                b.AddSmoothTri(from + d0 * r0, from + d1 * r0, to + d1 * r1, d0, d1, d1, c, c, c, inside);
                b.AddSmoothTri(from + d0 * r0, to + d1 * r1, to + d0 * r1, d0, d1, d0, c, c, c, inside);
            }
        }

        // Lumpy ball: an icosphere (detail 0 = 20 faces, 1 = 80) with jittered vertices, squashed
        // vertically. Downward faces are darkened so leaf clumps look self-shadowed.
        // A lumpy, smooth-shaded ball (leaf clumps, cushions, puffs): the corners are jittered for
        // an irregular outline, but the normals stay those of the smooth ellipsoid, so it reads as a
        // soft rounded mass instead of a faceted stone. Darker underneath (cheap self-shadowing),
        // with the colour varying gently over the surface.
        // `angular` (stones) keeps the asked-for detail even with fineDetail.
        static void AddBlob(Builder b, System.Random rng, Vector3 center, float radius, float squash, int detail, Color color, bool angular = false)
        {
            if (b.Foliage && !angular) { FoliageBlob(b, rng, center, radius, squash, detail, color); return; }
            if (fineDetail && !angular) detail = radius >= fineBlobRadius ? 2 : 1;
            else
            {
                if (radius < smallBlobRadius) detail = 0;
                detail = Mathf.Min(detail, maxBlobDetail);
            }
            var (dirs, faces) = Icosphere(detail);
            var pts = new Vector3[dirs.Length];
            var nrm = new Vector3[dirs.Length];
            var col = new Color[dirs.Length];
            float sq = Mathf.Max(squash, 0.15f);
            for (int i = 0; i < dirs.Length; i++)
            {
                var d = dirs[i] * radius * Range(rng, 0.82f, 1.12f);
                d.y *= squash;
                pts[i] = center + d;
                var n = new Vector3(dirs[i].x, dirs[i].y / sq, dirs[i].z).normalized;
                nrm[i] = n;
                col[i] = color * Range(rng, 0.93f, 1.07f) * (1f - 0.45f * (0.5f - 0.5f * n.y));
            }
            for (int f = 0; f < faces.Length; f += 3)
            {
                int i0 = faces[f], i1 = faces[f + 1], i2 = faces[f + 2];
                b.AddSmoothTri(pts[i0], pts[i1], pts[i2], nrm[i0], nrm[i1], nrm[i2], col[i0], col[i1], col[i2], center);
            }
        }

        static readonly (Vector3[] dirs, int[] faces)[] icospheres = new (Vector3[], int[])[3];

        // Unit icosphere subdivided `detail` times; built once and cached.
        static (Vector3[] dirs, int[] faces) Icosphere(int detail)
        {
            if (icospheres[detail].dirs != null) return icospheres[detail];

            float t  = (1f + Mathf.Sqrt(5f)) / 2f;
            var dirs = new List<Vector3>
            {
                new(-1, t, 0), new(1, t, 0), new(-1, -t, 0), new(1, -t, 0),
                new(0, -1, t), new(0, 1, t), new(0, -1, -t), new(0, 1, -t),
                new(t, 0, -1), new(t, 0, 1), new(-t, 0, -1), new(-t, 0, 1),
            };
            var faces = new List<int>
            {
                0, 11, 5,  0, 5, 1,  0, 1, 7,  0, 7, 10,  0, 10, 11,
                1, 5, 9,  5, 11, 4,  11, 10, 2,  10, 7, 6,  7, 1, 8,
                3, 9, 4,  3, 4, 2,  3, 2, 6,  3, 6, 8,  3, 8, 9,
                4, 9, 5,  2, 4, 11,  6, 2, 10,  8, 6, 7,  9, 8, 1,
            };
            for (int level = 0; level < detail; level++)
            {
                var midpoints = new Dictionary<(int, int), int>();
                int Mid(int a, int c)
                {
                    var key = a < c ? (a, c) : (c, a);
                    if (!midpoints.TryGetValue(key, out int m))
                    {
                        m = dirs.Count;
                        dirs.Add((dirs[a] + dirs[c]) * 0.5f);
                        midpoints[key] = m;
                    }
                    return m;
                }
                var next = new List<int>();
                for (int f = 0; f < faces.Count; f += 3)
                {
                    int a = faces[f], c = faces[f + 1], e = faces[f + 2];
                    int ac = Mid(a, c), ce = Mid(c, e), ea = Mid(e, a);
                    next.AddRange(new[] { a, ac, ea,  c, ce, ac,  e, ea, ce,  ac, ce, ea });
                }
                faces = next;
            }
            for (int i = 0; i < dirs.Count; i++) dirs[i] = dirs[i].normalized;
            return icospheres[detail] = (dirs.ToArray(), faces.ToArray());
        }

        static void AddCone(Builder b, System.Random rng, Vector3 baseCenter, float radius, float height, Color color)
        {
            const int sides = 7;
            var apex = baseCenter + Vector3.up * height;
            var ring = Ring(rng, baseCenter, radius, sides, 0.1f);
            for (int i = 0; i < sides; i++)
                b.AddTri(ring[i], ring[(i + 1) % sides], apex, color * Range(rng, 0.92f, 1.05f), baseCenter);
        }

        // Points around center with random overall rotation and per-point radius jitter.
        static Vector3[] Ring(System.Random rng, Vector3 center, float radius, int sides, float jitter)
        {
            var ring = new Vector3[sides];
            float rot = Range(rng, 0f, 360f);
            for (int i = 0; i < sides; i++)
            {
                float a = (rot + i * 360f / sides) * Mathf.Deg2Rad;
                float r = radius * Range(rng, 1f - jitter, 1f + jitter);
                ring[i] = center + new Vector3(Mathf.Sin(a) * r, 0f, Mathf.Cos(a) * r);
            }
            return ring;
        }

        static Color Shade(System.Random rng, Color c, float amount = 0.1f) => c * Range(rng, 1f - amount, 1f + amount);

        static float Range(System.Random rng, float min, float max) => min + (float)rng.NextDouble() * (max - min);

        // Flat-shaded mesh builder: every triangle gets its own vertices and face normal.
        sealed class Builder
        {
            // Building plants: leaf clumps come out lumpy, faceted and speckled (FoliageBlob), and
            // trunks and branches mottled, instead of smooth balls and plain sticks
            public bool Foliage;

            readonly List<Vector3> verts   = new();
            readonly List<Vector3> normals = new();
            readonly List<Color>   colors  = new();
            readonly List<int>     tris    = new();

            // Winding is fixed up so the face points away from `inside` (a point within the solid).
            // ao > 0 darkens the face the more it points downward (cheap self-shadowing).
            public void AddTri(Vector3 a, Vector3 b, Vector3 c, Color color, Vector3 inside, float ao = 0f)
            {
                var n = Vector3.Cross(b - a, c - a);
                if (Vector3.Dot(n, (a + b + c) / 3f - inside) < 0f) { (b, c) = (c, b); n = -n; }
                n.Normalize();
                if (ao > 0f) color *= 1f - ao * (0.5f - 0.5f * n.y);

                int i = verts.Count;
                verts.Add(a); verts.Add(b); verts.Add(c);
                for (int k = 0; k < 3; k++) { normals.Add(n); colors.Add(color); }
                tris.Add(i); tris.Add(i + 1); tris.Add(i + 2);
            }

            // Like AddTri, with a normal and colour per corner, so neighbouring triangles that share
            // corner normals shade as one smooth surface (leaf clumps).
            public void AddSmoothTri(Vector3 a, Vector3 b, Vector3 c, Vector3 na, Vector3 nb, Vector3 nc,
                                     Color ca, Color cb, Color cc, Vector3 inside)
            {
                var n = Vector3.Cross(b - a, c - a);
                if (Vector3.Dot(n, (a + b + c) / 3f - inside) < 0f) { (b, c) = (c, b); (nb, nc) = (nc, nb); (cb, cc) = (cc, cb); }
                int i = verts.Count;
                verts.Add(a); verts.Add(b); verts.Add(c);
                normals.Add(na); normals.Add(nb); normals.Add(nc);
                colors.Add(ca); colors.Add(cb); colors.Add(cc);
                tris.Add(i); tris.Add(i + 1); tris.Add(i + 2);
            }

            // a, b, c, d in order around the quad's edge
            public void AddQuad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Color color, Vector3 inside)
            {
                AddTri(a, b, c, color, inside);
                AddTri(a, c, d, color, inside);
            }

            public int VertexCount => verts.Count;

            // Read back what has been added (plant decorations find the leaf surfaces this way)
            public Vector3 Vertex(int i) => verts[i];
            public Vector3 Normal(int i) => normals[i];
            public Color VertexColor(int i) => colors[i];

            // How much a vertex bends in the wind (MapFeature.shader ApplyWind, mesh uv channel 3)
            readonly Dictionary<int, float> flex = new();
            public void SetFlex(int i, float amount) => flex[i] = amount;
            // Banded rock (MapFeature.shader BandColor): band coordinate and palette (1 Danxia, 2 strata)
            readonly Dictionary<int, Vector2> band = new();
            public void SetBand(int i, float coord, float palette) => band[i] = new Vector2(coord, palette);
            public void SetVertexColor(int i, Color c) => colors[i] = c;

            // Lowers every vertex added since `from` that lies below `below` by `amount`: stretches a
            // plant's trunk base down so it still meets the ground where a tile's rim slopes away.
            public void SinkBase(int from, float below, float amount)
            {
                for (int i = from; i < verts.Count; i++)
                    if (verts[i].y < below) verts[i] -= Vector3.up * amount;
            }

            public Mesh ToMesh(string name)
            {
                var mesh = new Mesh { name = name };
                if (verts.Count > 65535) mesh.indexFormat = IndexFormat.UInt32;
                mesh.SetVertices(verts);
                mesh.SetNormals(normals);
                mesh.SetColors(colors);
                // Both channels are written whenever either is used: a mesh missing one can read the
                // other's data in the shader on some GPUs (Metal), so banded rock would bend in the
                // wind (band coordinates read as flex) or plants would take on band colours.
                if (flex.Count > 0 || band.Count > 0)
                {
                    var uv3 = new Vector2[verts.Count];
                    foreach (var (i, amount) in flex) uv3[i] = new Vector2(amount, 0f);
                    mesh.SetUVs(3, uv3);
                    var uv2 = new Vector2[verts.Count];
                    foreach (var (i, value) in band) uv2[i] = value;
                    mesh.SetUVs(2, uv2);
                }
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateBounds();
                return mesh;
            }
        }
    }
}
