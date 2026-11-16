using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Karst tiles, in six forms picked by the country they stand in:
    //   tower forest (fenglin, Guilin): tall lone towers out of a flat green valley, a river
    //     winding between them, now and then a natural arch
    //   peak cluster (fengcong): steep cones rising from one shared forested pedestal, with sinkhole
    //     pools in the hollows between them
    //   stone forest (Shilin, Tsingy): crowds of thin grey blades and pinnacles
    //   haystack hills (Chocolate Hills, mogotes): rounded grassy domes, brown where it is drier
    //   tiankeng / cenote: a forested limestone plateau broken by a great collapse pit, jungle or
    //     blue water at its bottom
    //   drowned towers (Ha Long Bay): towers rising sheer out of the sea, undercut at the waterline
    // Towers are fluted, undercut at the foot and stepped into ledges; their bare rock is streaked
    // black and ochre where water runs down it, and every ledge and top carries jungle.
    public static partial class MapFeatureMeshes
    {
        static readonly Color Limestone     = new(0.66f, 0.66f, 0.62f);
        static readonly Color LimestonePale = new(0.80f, 0.79f, 0.74f);
        static readonly Color KarstStain    = new(0.24f, 0.25f, 0.27f);
        static readonly Color KarstOchre    = new(0.72f, 0.55f, 0.38f);
        static readonly Color[] KarstJungle =
        {
            new(0.20f, 0.40f, 0.16f), new(0.26f, 0.46f, 0.18f), new(0.15f, 0.32f, 0.14f), new(0.33f, 0.50f, 0.22f),
        };
        static readonly Color HillGrass = new(0.46f, 0.58f, 0.26f);
        static readonly Color HillBrown = new(0.54f, 0.41f, 0.24f);
        static readonly Color CenoteBlue = new(0.16f, 0.60f, 0.66f);

        enum KarstForm { TowerForest, PeakCluster, StoneForest, Haystacks, Sinkhole, Drowned }

        // atSea: a shallow sea tile (its surface at y = 0, ground the sea floor). moisture 0..1.
        public static Mesh CreateKarst(System.Random rng, float size, System.Func<Vector2, float> ground, bool atSea = false, float moisture = 0.7f)
        {
            var b = new Builder();
            var form = atSea ? KarstForm.Drowned : PickKarstForm(rng, moisture);
            switch (form)
            {
                case KarstForm.TowerForest: AddTowerForest(b, rng, size, ground); break;
                case KarstForm.PeakCluster: AddPeakCluster(b, rng, size, ground); break;
                case KarstForm.StoneForest: AddStoneForest(b, rng, size, ground); break;
                case KarstForm.Haystacks:   AddHaystacks(b, rng, size, ground, moisture); break;
                case KarstForm.Sinkhole:    AddSinkhole(b, rng, size, ground); break;
                default:                    AddDrownedTowers(b, rng, size, ground); break;
            }
            return b.ToMesh("Karst" + form);
        }

        static KarstForm PickKarstForm(System.Random rng, float moisture)
        {
            // wet country: towers, cones and great pits under jungle; drier: grassy domes and bare stone forests
            float[] w = moisture > 0.68f ? new[] { 0.34f, 0.28f, 0.1f, 0.06f, 0.22f } : new[] { 0.2f, 0.12f, 0.26f, 0.32f, 0.1f };
            float r = (float)rng.NextDouble(), sum = 0f;
            for (int i = 0; i < w.Length; i++) { sum += w[i]; if (r < sum) return (KarstForm)i; }
            return KarstForm.TowerForest;
        }

        // ---- Towers

        sealed class Spire
        {
            public float radius, height;
            public float notch = 0.12f, notchAt = 0.05f; // undercut (fraction of radius) and where (0..1 up the tower)
            public float taper = 0.7f;                   // radius at the top / at the foot, before the top rounds over
            public float dome = 0.3f;                    // share of the height that rounds over into the top
            public bool sharp;                           // ends in a point instead of a dome
            public int flutes = 7; public float flute = 0.08f; // vertical solution grooves
            public int ledges = 2;                       // steps where the tower narrows: jungle grows on them
            public float lean = 0.05f, stretch = 1f;     // lean (fraction of the height), blade-like elongation
            public float cover = 0.55f;                  // faces flatter than this (normal.y) are green
            public float stains = 1f;
            public float jungle = 1f;                    // how many leaf clumps sit on ledges and top
            public Color rock = Limestone;
            public int sides = 18, rings = 16;
        }

        static float Sq(float x) => x * x;

        // Lowest ground under a footprint, so a tower never floats on a slope
        static float FootY(System.Func<Vector2, float> ground, Vector2 at, float r)
        {
            float y = ground(at);
            for (int i = 0; i < 6; i++) y = Mathf.Min(y, ground(at + new Vector2(Mathf.Sin(i * 1.0472f), Mathf.Cos(i * 1.0472f)) * r));
            return y;
        }

        static void AddSpire(Builder b, System.Random rng, float size, Vector2 at, float footY, Spire s)
        {
            int S = s.sides, K = s.rings;
            float seed = Range(rng, 0f, 100f);
            float leanA = Range(rng, 0f, Mathf.PI * 2f), stretchA = Range(rng, 0f, Mathf.PI);
            var leanDir = new Vector3(Mathf.Sin(leanA), 0f, Mathf.Cos(leanA));
            var axis = new Vector2(Mathf.Sin(stretchA), Mathf.Cos(stretchA));

            // ledges: the ring just above each is pulled down level with the one below, so the step is
            // a flat shelf, and everything above it is narrower
            var ledgeRing = new HashSet<int>();
            for (int l = 0; l < s.ledges; l++) ledgeRing.Add(Mathf.Clamp(Mathf.RoundToInt(Range(rng, 0.25f, 0.75f) * K), 2, K - 3));
            var ty = new float[K + 1];
            var narrow = new float[K + 1];
            float n = 1f;
            for (int k = 0; k <= K; k++)
            {
                bool shelf = ledgeRing.Contains(k);
                if (shelf) n *= Range(rng, 0.8f, 0.88f);
                narrow[k] = n;
                ty[k] = shelf ? ty[k - 1] + 0.15f / K : k / (float)K;
            }

            float Profile(float t, int k)
            {
                float body  = Mathf.Lerp(1f, s.taper, t);
                float notch = 1f - s.notch * Mathf.Exp(-Sq((t - s.notchAt) / 0.06f));
                float cap = 1f, d0 = 1f - s.dome;
                if (t > d0)
                {
                    float u = (t - d0) / s.dome;
                    cap = s.sharp ? 1f - u : Mathf.Sqrt(Mathf.Max(0f, 1f - u * u));
                }
                return body * notch * narrow[k] * Mathf.Max(cap, 0.05f);
            }

            var g = new Vector3[K + 1, S];
            var mid = new Vector3[K + 1];
            for (int k = 0; k <= K; k++)
            {
                float t = ty[k];
                mid[k] = new Vector3(at.x, footY + t * s.height, at.y) + leanDir * s.lean * s.height * t * t;
                float prof = Profile(t, k);
                float twist = Mathf.PerlinNoise(seed, t * 2f) * 2f;
                for (int i = 0; i < S; i++)
                {
                    float a = i * Mathf.PI * 2f / S;
                    var dir = new Vector2(Mathf.Sin(a), Mathf.Cos(a));
                    dir += axis * Vector2.Dot(dir, axis) * (s.stretch - 1f);
                    float wob = 1f + 0.36f * (Mathf.PerlinNoise(seed + Mathf.Cos(a) * 1.3f + t * 0.9f, seed + Mathf.Sin(a) * 1.3f) - 0.5f);
                    float fl  = 1f - s.flute * Mathf.Pow(0.5f + 0.5f * Mathf.Cos(a * s.flutes + twist), 3f);
                    float rr  = s.radius * prof * wob * fl;
                    float jy  = k > 0 && k < K && !ledgeRing.Contains(k) ? Range(rng, -0.3f, 0.3f) * s.height / K : 0f;
                    g[k, i] = mid[k] + new Vector3(dir.x, 0f, dir.y) * rr + Vector3.up * jy;
                }
            }
            for (int i = 0; i < S; i++) g[0, i].y -= 0.02f * size; // sunk into the ground

            Color Green() => Shade(rng, KarstJungle[rng.Next(KarstJungle.Length)], 0.08f);
            Color Rock(int i, float t)
            {
                float streak = Mathf.PerlinNoise(seed + i * 0.83f, t * 1.3f + seed * 0.3f);
                var c = Color.Lerp(s.rock, LimestonePale, Mathf.PerlinNoise(seed * 0.5f + i * 0.4f, t * 3f) * 0.55f);
                if (streak > 0.6f) c = Color.Lerp(c, KarstStain, Mathf.InverseLerp(0.6f, 0.85f, streak) * 0.75f * s.stains);
                else if (streak < 0.32f) c = Color.Lerp(c, KarstOchre, Mathf.InverseLerp(0.32f, 0.1f, streak) * 0.55f * s.stains);
                if (t < s.notchAt + 0.05f) c *= 0.8f; // wet and shaded in the undercut
                return c * Range(rng, 0.95f, 1.05f);
            }

            var spots = new List<(Vector3 p, Vector3 n)>();
            for (int k = 0; k < K; k++)
            for (int i = 0; i < S; i++)
            {
                int j = (i + 1) % S;
                Vector3 p0 = g[k, i], p1 = g[k, j], p2 = g[k + 1, j], p3 = g[k + 1, i];
                var inside = (mid[k] + mid[k + 1]) * 0.5f;
                var c = (p0 + p1 + p2 + p3) * 0.25f;
                var nrm = Vector3.Cross(p1 - p0, p3 - p0).normalized;
                if (Vector3.Dot(nrm, c - inside) < 0f) nrm = -nrm;
                float t = (ty[k] + ty[k + 1]) * 0.5f;
                bool top   = t > 1f - s.dome * 0.55f && nrm.y > 0.25f && !s.sharp;
                bool vines = nrm.y > -0.1f && t > 0.15f && Mathf.PerlinNoise(seed * 1.7f + i * 1.9f, t * 5f) > 0.74f;
                bool green = nrm.y > s.cover || top || (vines && s.cover < 0.8f);
                var col = green ? Green() * (vines && !top && nrm.y <= s.cover ? 0.8f : 1f) : Rock(i, t);
                b.AddTri(p0, p1, p2, col, inside, 0.4f);
                b.AddTri(p0, p2, p3, col, inside, 0.4f);
                if (green && nrm.y > 0.3f) spots.Add((c, nrm));
            }
            // close the top
            var apex = mid[K] + Vector3.up * (s.sharp ? 0.02f : 0.004f) * s.height;
            var capCol = s.sharp ? Rock(0, 1f) : Green();
            for (int i = 0; i < S; i++) b.AddTri(g[K, i], g[K, (i + 1) % S], apex, capCol, mid[K] - Vector3.up * 0.01f * s.height);

            // leaf clumps on the shelves and the top
            if (s.jungle <= 0f) return;
            int clumps = Mathf.RoundToInt(Mathf.Min(spots.Count, (6 + s.height / size * 30f) * s.jungle));
            for (int c = 0; c < clumps; c++)
            {
                var (p, nr) = spots[rng.Next(spots.Count)];
                float r = s.radius * Range(rng, 0.18f, 0.32f);
                AddBlob(b, rng, p + nr * r * 0.4f, r, 0.75f, 1, Green());
            }
            if (!s.sharp)
                for (int c = rng.Next(2, 5); c > 0; c--)
                {
                    var p = mid[K] + new Vector3(Range(rng, -1f, 1f), 0f, Range(rng, -1f, 1f)) * s.radius * s.taper * 0.4f;
                    AddBlob(b, rng, p, s.radius * Range(rng, 0.25f, 0.4f), 0.7f, 1, Green());
                }
        }

        // A natural arch from a to b (feet on the ground), its opening `height` high
        static void AddArch(Builder b, System.Random rng, float size, Vector3 a, Vector3 c, float height)
        {
            const int segs = 18;
            float width = size * Range(rng, 0.045f, 0.06f), thick = size * Range(rng, 0.03f, 0.04f);
            var span = c - a;
            var side = Vector3.Cross(Vector3.up, span).normalized;
            float seed = Range(rng, 0f, 100f);
            var rings = new Vector3[segs + 1, 4];
            var mids = new Vector3[segs + 1];
            for (int k = 0; k <= segs; k++)
            {
                float u = k / (float)segs, arc = Mathf.Sin(u * Mathf.PI);
                var m = a + span * u + Vector3.up * (height * arc);
                var tangent = (span + Vector3.up * (height * Mathf.PI * Mathf.Cos(u * Mathf.PI))).normalized;
                var outward = Vector3.Cross(tangent, side).normalized;
                if (outward.y < 0f) outward = -outward;
                float th = thick * (1f + 1.3f * (1f - arc)) * (0.85f + 0.3f * Mathf.PerlinNoise(seed, u * 4f));
                float w  = width * (1f + 0.6f * (1f - arc));
                if (k == 0 || k == segs) m -= Vector3.up * 0.03f * size; // the feet run into the ground
                mids[k] = m + outward * th * 0.5f;
                rings[k, 0] = m - side * w * 0.5f;
                rings[k, 1] = m + side * w * 0.5f;
                rings[k, 2] = m + side * w * 0.5f + outward * th;
                rings[k, 3] = m - side * w * 0.5f + outward * th;
            }
            for (int k = 0; k < segs; k++)
            for (int e = 0; e < 4; e++)
            {
                int f = (e + 1) % 4;
                Vector3 p0 = rings[k, e], p1 = rings[k, f], p2 = rings[k + 1, f], p3 = rings[k + 1, e];
                var inside = (mids[k] + mids[k + 1]) * 0.5f;
                var nrm = Vector3.Cross(p1 - p0, p3 - p0).normalized;
                if (Vector3.Dot(nrm, (p0 + p2) * 0.5f - inside) < 0f) nrm = -nrm;
                float streak = Mathf.PerlinNoise(seed + k * 0.6f, e * 1.3f);
                var col = nrm.y > 0.55f ? Shade(rng, KarstJungle[rng.Next(KarstJungle.Length)], 0.08f)
                        : Color.Lerp(Limestone, streak > 0.6f ? KarstStain : LimestonePale, Mathf.Abs(streak - 0.5f)) * Range(rng, 0.95f, 1.05f);
                b.AddTri(p0, p1, p2, col, inside, 0.4f);
                b.AddTri(p0, p2, p3, col, inside, 0.4f);
            }
            for (int k = 3; k < segs - 2; k += 3) // shrubs on the crest
                AddBlob(b, rng, mids[k] + Vector3.up * thick * 0.6f, thick * Range(rng, 0.5f, 0.8f), 0.7f, 1, Shade(rng, KarstJungle[rng.Next(KarstJungle.Length)], 0.08f));
        }

        // A smooth rounded hill (haystacks, islets)
        static void AddDome(Builder b, System.Random rng, float size, Vector2 at, float footY, float r, float h, Color low, Color high)
        {
            const int S = 18, K = 8;
            float seed = Range(rng, 0f, 100f);
            var g = new Vector3[K + 1, S];
            var center = new Vector3(at.x, footY, at.y);
            for (int k = 0; k <= K; k++)
            {
                float th = k / (float)K * Mathf.PI * 0.5f;
                float u = Mathf.Cos(th), y = h * Mathf.Pow(Mathf.Sin(th), 1.4f);
                for (int i = 0; i < S; i++)
                {
                    float a = i * Mathf.PI * 2f / S;
                    float wob = 1f + 0.18f * (Mathf.PerlinNoise(seed + Mathf.Cos(a) * 1.2f, seed + Mathf.Sin(a) * 1.2f + k * 0.15f) - 0.5f);
                    g[k, i] = center + new Vector3(Mathf.Sin(a) * u * r * wob, k == 0 ? -0.015f * size : y, Mathf.Cos(a) * u * r * wob);
                }
            }
            var apex = center + Vector3.up * h;
            Vector3 N(int k, int i)
            {
                if (k >= K) return Vector3.up;
                var across = g[k, (i + 1) % S] - g[k, (i + S - 1) % S];
                var up = g[Mathf.Min(k + 1, K), i] - g[Mathf.Max(k - 1, 0), i];
                var n = Vector3.Cross(up, across).normalized;
                return n.y < 0f ? -n : n;
            }
            Color C(int k) => Color.Lerp(low, high, k / (float)K) * (0.97f + 0.06f * Mathf.PerlinNoise(seed + k, seed));
            var inside = center + Vector3.up * h * 0.3f;
            for (int k = 0; k < K; k++)
            for (int i = 0; i < S; i++)
            {
                int j = (i + 1) % S;
                b.AddSmoothTri(g[k, i], g[k, j], g[k + 1, j], N(k, i), N(k, j), N(k + 1, j), C(k), C(k), C(k + 1), inside);
                b.AddSmoothTri(g[k, i], g[k + 1, j], g[k + 1, i], N(k, i), N(k + 1, j), N(k + 1, i), C(k), C(k + 1), C(k + 1), inside);
            }
            for (int i = 0; i < S; i++)
                b.AddSmoothTri(g[K, i], g[K, (i + 1) % S], apex, N(K - 1, i), N(K - 1, (i + 1) % S), Vector3.up, C(K), C(K), C(K), inside);
        }

        static Color JungleClump(System.Random rng) => Shade(rng, KarstJungle[rng.Next(KarstJungle.Length)], 0.08f);

        static List<Vector2> EdgeToEdge(System.Random rng, float size, int points)
        {
            float a = size * 0.8660254f;
            int eIn = rng.Next(6), eOut = (eIn + 3 + rng.Next(-1, 2) + 6) % 6;
            Vector2 Edge(int e) { float ang = (60f * e + 30f) * Mathf.Deg2Rad; return new Vector2(Mathf.Sin(ang), Mathf.Cos(ang)) * a * 1.02f; }
            var p0 = Edge(eIn); var p1 = Edge(eOut);
            var side = new Vector2((p1 - p0).y, -(p1 - p0).x).normalized;
            float wig = Range(rng, 0.1f, 0.18f) * size, phase = Range(rng, 0f, 6f);
            var line = new List<Vector2>();
            for (int k = 0; k <= points; k++)
            {
                float t = k / (float)points;
                line.Add(Vector2.Lerp(p0, p1, t) + side * Mathf.Sin(t * Mathf.PI * 2.4f + phase) * wig * Mathf.Sin(t * Mathf.PI));
            }
            return line;
        }

        static float DistToLine(List<Vector2> line, Vector2 p)
        {
            float best = float.MaxValue;
            for (int k = 0; k + 1 < line.Count; k++)
            {
                var ab = line[k + 1] - line[k];
                float t = Mathf.Clamp01(Vector2.Dot(p - line[k], ab) / ab.sqrMagnitude);
                best = Mathf.Min(best, (p - (line[k] + ab * t)).magnitude);
            }
            return best;
        }

        // ---- Tower forest: lone towers out of a green valley floor, a river winding through

        static void AddTowerForest(Builder b, System.Random rng, float size, System.Func<Vector2, float> ground)
        {
            float a = size * 0.8660254f;
            var river = EdgeToEdge(rng, size, 28);
            var towers = new List<(Vector2 p, float r)>();
            foreach (var p in HexScatter(rng, rng.Next(5, 9), a * 0.72f, 0.2f * size, new List<Vector2>()))
            {
                float r = size * Range(rng, 0.06f, 0.1f);
                if (DistToLine(river, p) < r + 0.05f * size) continue;
                towers.Add((p, r));
                AddSpire(b, rng, size, p, FootY(ground, p, r), new Spire
                {
                    radius = r, height = size * Range(rng, 0.24f, 0.46f), taper = Range(rng, 0.6f, 0.85f), dome = Range(rng, 0.2f, 0.35f),
                    notch = Range(rng, 0.08f, 0.18f), ledges = rng.Next(1, 4), lean = Range(rng, 0f, 0.08f),
                    flutes = rng.Next(5, 9), flute = Range(rng, 0.05f, 0.12f), cover = Range(rng, 0.5f, 0.62f),
                });
            }
            // now and then a natural arch (Moon Hill)
            if (rng.NextDouble() < 0.3)
                foreach (var p in HexScatter(rng, 1, a * 0.55f, 0.24f * size, towers.ConvertAll(t => t.p)))
                {
                    float ang = Range(rng, 0f, Mathf.PI), half = size * Range(rng, 0.07f, 0.1f);
                    var d = new Vector2(Mathf.Sin(ang), Mathf.Cos(ang)) * half;
                    if (DistToLine(river, p) < half + 0.05f * size) break;
                    Vector3 On(Vector2 q) => new(q.x, ground(q), q.y);
                    AddArch(b, rng, size, On(p - d), On(p + d), size * Range(rng, 0.1f, 0.16f));
                    towers.Add((p, half));
                }
            bool Clear(Vector2 q, float pad)
            {
                foreach (var (p, r) in towers) if ((q - p).magnitude < r * 1.15f + pad) return false;
                return DistToLine(river, q) > 0.045f * size + pad;
            }
            // the river
            for (int k = 0; k + 1 < river.Count; k++)
            {
                Vector2 q0 = river[k], q1 = river[k + 1];
                var sd = new Vector2((q1 - q0).y, -(q1 - q0).x).normalized * 0.03f * size;
                Vector3 V(Vector2 q) => new(q.x, ground(q) + 0.004f * size, q.y);
                b.AddQuad(V(q0 + sd), V(q1 + sd), V(q1 - sd), V(q0 - sd), Shade(rng, GorgeRiver, 0.04f), V((q0 + q1) * 0.5f) - Vector3.up);
            }
            // trees along the banks and round the tower feet
            for (int i = 0; i < 14; i++)
            {
                var q = river[rng.Next(river.Count)] + new Vector2(Range(rng, -1f, 1f), Range(rng, -1f, 1f)).normalized * 0.06f * size;
                if (!InHex(q, a * 0.9f) || !Clear(q, 0f)) continue;
                AddBlob(b, rng, new Vector3(q.x, ground(q) + 0.02f * size, q.y), size * Range(rng, 0.018f, 0.03f), 0.85f, 1, JungleClump(rng));
            }
            foreach (var (p, r) in towers)
                for (int i = rng.Next(2, 4); i > 0; i--)
                {
                    float ang = Range(rng, 0f, Mathf.PI * 2f);
                    var q = p + new Vector2(Mathf.Sin(ang), Mathf.Cos(ang)) * r * Range(rng, 1.05f, 1.3f);
                    AddBlob(b, rng, new Vector3(q.x, ground(q) + 0.012f * size, q.y), size * Range(rng, 0.02f, 0.032f), 0.8f, 1, JungleClump(rng));
                }
        }

        static bool InHex(Vector2 p, float apothem)
        {
            for (int e = 0; e < 3; e++)
            {
                float ang = (60f * e + 30f) * Mathf.Deg2Rad;
                if (Mathf.Abs(p.x * Mathf.Sin(ang) + p.y * Mathf.Cos(ang)) > apothem) return false;
            }
            return true;
        }

        // ---- Peak cluster: steep cones on one forested pedestal, pools in the hollows between

        static void AddPeakCluster(Builder b, System.Random rng, float size, System.Func<Vector2, float> ground)
        {
            float a = size * 0.8660254f, seed = Range(rng, 0f, 100f);
            var peaks = HexScatter(rng, rng.Next(5, 9), a * 0.6f, 0.17f * size, new List<Vector2>());
            var radii = peaks.ConvertAll(_ => size * Range(rng, 0.08f, 0.12f));
            var hollows = HexScatter(rng, rng.Next(1, 4), a * 0.5f, 0.1f * size, peaks);
            float Hp = size * Range(rng, 0.05f, 0.08f);
            float Pedestal(Vector2 p)
            {
                float m = 0f;
                for (int i = 0; i < peaks.Count; i++)
                    m = Mathf.Max(m, Mathf.Clamp01(1f - ((p - peaks[i]).magnitude - radii[i]) / (0.16f * size)));
                float h = Hp * Mathf.SmoothStep(0f, 1f, m) * (0.85f + 0.3f * Mathf.PerlinNoise(seed + p.x / size * 5f, seed + p.y / size * 5f));
                foreach (var q in hollows) h -= Hp * 1.4f * Mathf.Exp(-Sq((p - q).magnitude / (0.07f * size))); // sinkholes
                return Mathf.Max(0f, h) * RimFade(p, size);
            }
            AddHeightField(b, size, 30, Pedestal, ground, (m, h, nrm) =>
                nrm.y > 0.72f ? JungleClump(rng) : Color.Lerp(Limestone, KarstStain, Mathf.PerlinNoise(m.x * 9f, m.z * 9f) * 0.5f) * Range(rng, 0.95f, 1.05f));
            for (int i = 0; i < peaks.Count; i++)
            {
                var p = peaks[i];
                float foot = FootY(p2 => ground(p2) + Pedestal(p2), p, radii[i] * 0.8f);
                AddSpire(b, rng, size, p, foot, new Spire
                {
                    radius = radii[i], height = size * Range(rng, 0.18f, 0.32f), taper = Range(rng, 0.25f, 0.4f), dome = Range(rng, 0.35f, 0.5f),
                    notch = 0f, ledges = rng.Next(0, 2), lean = Range(rng, 0f, 0.06f), flutes = rng.Next(4, 7), flute = Range(rng, 0.06f, 0.12f),
                    cover = Range(rng, 0.42f, 0.52f), jungle = 1.3f,
                });
            }
            foreach (var q in hollows)
                AddPond(b, rng, new Vector3(q.x, ground(q) + Pedestal(q) + 0.004f * size, q.y), size * Range(rng, 0.035f, 0.055f), Shade(rng, GorgeRiver, 0.05f));
        }

        // ---- Stone forest: crowds of thin grey blades and pinnacles

        static void AddStoneForest(Builder b, System.Random rng, float size, System.Func<Vector2, float> ground)
        {
            float a = size * 0.8660254f;
            var groves = HexScatter(rng, rng.Next(3, 6), a * 0.55f, 0.22f * size, new List<Vector2>());
            var taken = new List<Vector2>();
            bool fine = rng.NextDouble() < 0.5; // Tsingy: finer, sharper, denser
            foreach (var g in groves)
            {
                float spread = size * Range(rng, 0.11f, 0.17f);
                for (int i = rng.Next(12, 20); i > 0; i--)
                {
                    var p = g + new Vector2(Range(rng, -1f, 1f), Range(rng, -1f, 1f)) * spread;
                    if (!InHex(p, a * 0.82f) || taken.Exists(q => (q - p).sqrMagnitude < Sq(0.028f * size))) continue;
                    taken.Add(p);
                    float centre = 1f - Mathf.Clamp01((p - g).magnitude / spread) * 0.5f;
                    float r = size * Range(rng, 0.016f, 0.032f) * (fine ? 0.8f : 1f);
                    AddSpire(b, rng, size, p, FootY(ground, p, r), new Spire
                    {
                        radius = r, height = size * Range(rng, 0.07f, 0.2f) * centre, sharp = true, dome = Range(rng, 0.3f, 0.5f),
                        taper = Range(rng, 0.45f, 0.7f), notch = Range(rng, 0.05f, 0.15f), ledges = 0, lean = Range(rng, 0f, 0.1f),
                        flutes = rng.Next(3, 6), flute = Range(rng, 0.15f, 0.28f), stretch = Range(rng, 1.2f, 2f),
                        cover = 0.9f, stains = 1.2f, jungle = 0f, rock = fine ? Limestone * 0.9f : LimestonePale * 0.95f,
                        sides = 9, rings = 7,
                    });
                }
            }
            // shrubs and grass tussocks between
            foreach (var p in HexScatter(rng, 18, a * 0.85f, 0.04f * size, taken))
                AddBlob(b, rng, new Vector3(p.x, ground(p) + 0.006f * size, p.y), size * Range(rng, 0.012f, 0.025f), 0.6f, 1, Shade(rng, rng.NextDouble() < 0.5 ? HillGrass : KarstJungle[1], 0.1f));
        }

        // ---- Haystack hills: rounded grassy domes, brown where it is drier

        static void AddHaystacks(Builder b, System.Random rng, float size, System.Func<Vector2, float> ground, float moisture)
        {
            float a = size * 0.8660254f;
            var grass = Color.Lerp(HillBrown, HillGrass, Mathf.InverseLerp(0.4f, 0.75f, moisture));
            var spots = HexScatter(rng, rng.Next(7, 13), a * 0.74f, 0.15f * size, new List<Vector2>());
            foreach (var p in spots)
            {
                float r = size * Range(rng, 0.07f, 0.1f);
                var low = Shade(rng, Color.Lerp(grass, HillGrass * 0.8f, 0.4f), 0.05f);
                AddDome(b, rng, size, p, FootY(ground, p, r), r, r * Range(rng, 0.9f, 1.3f), low, Shade(rng, grass, 0.05f));
            }
            // forest in the flats between the hills
            foreach (var p in HexScatter(rng, 22, a * 0.88f, 0.04f * size, spots.ConvertAll(s => s)))
            {
                bool nearHill = spots.Exists(s => (s - p).magnitude < 0.12f * size);
                if (!nearHill && rng.NextDouble() < 0.5) continue;
                AddBlob(b, rng, new Vector3(p.x, ground(p) + 0.015f * size, p.y), size * Range(rng, 0.018f, 0.03f), 0.85f, 1, JungleClump(rng));
            }
        }

        // ---- Tiankeng / cenote: a forested plateau broken by a great collapse pit

        static void AddSinkhole(Builder b, System.Random rng, float size, System.Func<Vector2, float> ground)
        {
            float a = size * 0.8660254f, seed = Range(rng, 0f, 100f);
            var pit = new Vector2(Range(rng, -0.08f, 0.08f), Range(rng, -0.08f, 0.08f)) * size;
            float pr = size * Range(rng, 0.2f, 0.26f), H = size * Range(rng, 0.11f, 0.15f);
            float Edge(Vector2 p)
            {
                var d = p - pit;
                float ang = Mathf.Atan2(d.x, d.y);
                return pr * (1f + 0.2f * (Mathf.PerlinNoise(seed + Mathf.Cos(ang) * 1.4f, seed + Mathf.Sin(ang) * 1.4f) - 0.5f));
            }
            float Plateau(Vector2 p)
            {
                float e = Edge(p), d = (p - pit).magnitude;
                float wall = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(e - 0.012f * size, e + 0.02f * size, d));
                float bumps = 0.85f + 0.3f * Mathf.PerlinNoise(seed + p.x / size * 4f, seed + p.y / size * 4f);
                return H * wall * bumps * RimFade(p, size);
            }
            AddHeightField(b, size, 40, Plateau, ground, (m, h, nrm) =>
            {
                if (nrm.y > 0.66f) return JungleClump(rng);
                var d = new Vector2(m.x, m.z) - pit;
                float streak = Mathf.PerlinNoise(seed + Mathf.Atan2(d.x, d.y) * 5f, 0.5f);
                var c = Color.Lerp(Limestone, LimestonePale, Mathf.PerlinNoise(m.x * 12f, m.y * 30f) * 0.6f);
                if (streak > 0.58f) c = Color.Lerp(c, KarstStain, (streak - 0.58f) * 2.5f);
                else if (streak < 0.35f) c = Color.Lerp(c, KarstOchre, (0.35f - streak) * 2f);
                if (h < H * 0.35f) c *= 0.75f; // the shadowed depths
                return c * Range(rng, 0.95f, 1.05f);
            });
            bool cenote = rng.NextDouble() < 0.5;
            var floor = new Vector3(pit.x, ground(pit), pit.y);
            if (cenote)
            {
                AddPond(b, rng, floor + Vector3.up * 0.006f * size, pr * 0.85f, CenoteBlue);
                AddPond(b, rng, floor + Vector3.up * 0.007f * size, pr * 0.45f, CenoteBlue * 0.7f); // deep blue middle
            }
            else
                for (int i = rng.Next(14, 22); i > 0; i--) // a lost forest at the bottom
                {
                    float ang = Range(rng, 0f, Mathf.PI * 2f), d = Mathf.Sqrt((float)rng.NextDouble()) * pr * 0.8f;
                    var q = pit + new Vector2(Mathf.Sin(ang), Mathf.Cos(ang)) * d;
                    AddBlob(b, rng, new Vector3(q.x, ground(q) + 0.02f * size, q.y), size * Range(rng, 0.02f, 0.035f), 0.85f, 1, JungleClump(rng));
                }
            // vines hanging over the lip
            for (int i = 0; i < 16; i++)
            {
                float ang = i / 16f * Mathf.PI * 2f + Range(rng, -0.1f, 0.1f);
                var dir = new Vector2(Mathf.Sin(ang), Mathf.Cos(ang));
                var q = pit + dir * (Edge(pit + dir * pr) + 0.025f * size);
                AddBlob(b, rng, new Vector3(q.x, ground(q) + Plateau(q), q.y), size * Range(rng, 0.016f, 0.026f), 0.8f, 1, JungleClump(rng));
            }
            // a few small towers on the plateau
            foreach (var p in HexScatter(rng, rng.Next(1, 4), a * 0.62f, 0.15f * size, new List<Vector2> { pit, pit + Vector2.up * pr * 0.7f, pit - Vector2.up * pr * 0.7f }))
            {
                if ((p - pit).magnitude < pr + 0.1f * size) continue;
                float r = size * Range(rng, 0.05f, 0.075f);
                AddSpire(b, rng, size, p, FootY(q => ground(q) + Plateau(q), p, r), new Spire
                {
                    radius = r, height = size * Range(rng, 0.12f, 0.22f), taper = Range(rng, 0.4f, 0.6f), dome = 0.4f, notch = 0.05f,
                    ledges = rng.Next(0, 2), cover = 0.5f,
                });
            }
        }

        // ---- Drowned towers: sheer towers out of a shallow sea, undercut by the waves at the waterline

        static void AddDrownedTowers(Builder b, System.Random rng, float size, System.Func<Vector2, float> ground)
        {
            float a = size * 0.8660254f;
            var spots = HexScatter(rng, rng.Next(8, 14), a * 0.8f, 0.13f * size, new List<Vector2>());
            foreach (var p in spots)
            {
                float r = size * Range(rng, 0.04f, 0.1f);
                float foot = FootY(ground, p, r);
                float above = size * Range(rng, 0.12f, 0.36f) * Mathf.Lerp(0.6f, 1.1f, r / (0.1f * size));
                float hgt = above - foot;
                if (rng.NextDouble() < 0.2) // a low wooded islet
                {
                    AddDome(b, rng, size, p, foot, r, -foot + r * 0.6f, JungleClump(rng) * 0.9f, JungleClump(rng));
                    continue;
                }
                AddSpire(b, rng, size, p, foot, new Spire
                {
                    radius = r, height = hgt, taper = Range(rng, 0.55f, 0.85f), dome = Range(rng, 0.18f, 0.3f),
                    notch = Range(rng, 0.2f, 0.3f), notchAt = Mathf.Clamp01(-foot / hgt + 0.01f), // the wave-cut notch
                    ledges = rng.Next(1, 3), lean = Range(rng, 0f, 0.06f), flutes = rng.Next(5, 9), flute = Range(rng, 0.06f, 0.12f),
                    cover = Range(rng, 0.48f, 0.6f),
                });
                if (rng.NextDouble() < 0.25) // a pocket beach at the foot
                {
                    float ang = Range(rng, 0f, Mathf.PI * 2f);
                    var q = p + new Vector2(Mathf.Sin(ang), Mathf.Cos(ang)) * r * 1.1f;
                    AddBlob(b, rng, new Vector3(q.x, 0.002f * size, q.y), r * 0.5f, 0.12f, 1, Shade(rng, Sand, 0.05f), true);
                }
            }
        }
    }
}
