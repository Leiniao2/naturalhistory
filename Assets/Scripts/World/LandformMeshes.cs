using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Landform tiles: mesas, canyons, white chalk cliffs, salt lakes and Danxia rainbow
    // hills (karst: KarstMeshes.cs). Most are a height field over the hex (a triangular lattice, flat-shaded and
    // painted by height and slope) raised above the tile's own ground; where it stands above the
    // ground at the hex rim, a wall drops down to the ground (or the sea). Built per tile (unique),
    // so they follow its slopes.
    public static partial class MapFeatureMeshes
    {
        static readonly Color MesaCap     = Muted(new Color(0.46f, 0.30f, 0.22f));
        static readonly Color RedRock     = Muted(new Color(0.66f, 0.34f, 0.22f));
        static readonly Color OrangeRock  = Muted(new Color(0.78f, 0.50f, 0.30f));
        static readonly Color CreamRock   = Muted(new Color(0.84f, 0.74f, 0.58f));
        static readonly Color Scree       = Muted(new Color(0.74f, 0.52f, 0.36f));
        static readonly Color ChalkWhite  = new(0.93f, 0.92f, 0.87f);
        static readonly Color Flint       = new(0.62f, 0.62f, 0.60f);
        static readonly Color Downland    = new(0.44f, 0.56f, 0.28f);
        static readonly Color SaltWhite   = new(0.93f, 0.92f, 0.90f);
        static readonly Color BrinePink   = new(0.90f, 0.52f, 0.62f);
        static readonly Color BrineTeal   = new(0.42f, 0.72f, 0.74f);
        static readonly Color GorgeRiver  = new(0.26f, 0.50f, 0.56f);
        static readonly Color[] DanxiaBands = System.Array.ConvertAll(new Color[]
        {
            new(0.74f, 0.30f, 0.22f), new(0.86f, 0.56f, 0.30f), new(0.90f, 0.80f, 0.56f), new(0.82f, 0.46f, 0.40f),
            new(0.92f, 0.70f, 0.36f), new(0.62f, 0.36f, 0.40f), new(0.80f, 0.40f, 0.26f), new(0.88f, 0.86f, 0.70f),
        }, c => Muted(c));

        // Red-rock landforms (Danxia, mesas, canyons) were too saturated: their colours are pulled
        // this far toward grey of the same brightness
        const float RockMuting = 0.4f;
        static Color Muted(Color c)
        {
            float grey = c.r * 0.3f + c.g * 0.59f + c.b * 0.11f;
            return Color.Lerp(c, new Color(grey, grey, grey, c.a), RockMuting);
        }

        // Height field over the hex. height(p) is metres above the ground at p; ground(p) the
        // tile's surface height; paint(point, height above ground, normal) the facet's colour.
        // wallBottom(p) is how far down rim walls go (defaults to the ground).
        // band(vertex, height above ground) gives a vertex's band coordinate for facets that paint
        // returns with alpha 0 (their rgb is then only shading): the shader colours them per pixel,
        // so stripes follow smooth lines instead of the triangles. bandPalette: 1 Danxia, 2 strata.
        static void AddHeightField(Builder b, float size, int n, System.Func<Vector2, float> height, System.Func<Vector2, float> ground,
                                   System.Func<Vector3, float, Vector3, Color> paint, System.Func<Vector2, float> wallBottom = null,
                                   System.Func<Vector3, float, float> band = null, float bandPalette = 0f)
        {
            SetBandPalettes();
            float R = size * 0.985f;
            var e1 = new Vector2(0f, 1f) * R / n;
            var e2 = new Vector2(0.8660254f, 0.5f) * R / n;
            int span = 2 * n + 1;
            var pos = new Vector3[span, span];
            var hgt = new float[span, span];
            bool In(int i, int j) => Mathf.Abs(i) <= n && Mathf.Abs(j) <= n && Mathf.Abs(i + j) <= n;
            for (int i = -n; i <= n; i++)
            for (int j = -n; j <= n; j++)
            {
                if (!In(i, j)) continue;
                var p = e1 * i + e2 * j;
                float h = Mathf.Max(0f, height(p));
                hgt[i + n, j + n] = h;
                pos[i + n, j + n] = new Vector3(p.x, ground(p) + h, p.y);
            }
            void Tri(int ai, int aj, int bi, int bj, int ci, int cj)
            {
                float ha = hgt[ai + n, aj + n], hb = hgt[bi + n, bj + n], hc = hgt[ci + n, cj + n];
                float flat = 0.004f * size; // the foot of the landform: let the shared ground show instead
                if (ha < flat && hb < flat && hc < flat) return; // the tile's own ground shows
                Vector3 a = pos[ai + n, aj + n], bb = pos[bi + n, bj + n], c = pos[ci + n, cj + n];
                var m = (a + bb + c) / 3f;
                var nrm = Vector3.Cross(bb - a, c - a).normalized;
                if (nrm.y < 0f) nrm = -nrm;
                var col = paint(m, (ha + hb + hc) / 3f, nrm);
                bool banded = band != null && col.a < 0.5f;
                col.a = 1f;
                b.AddTri(a, bb, c, col, m - nrm);
                if (banded)
                    for (int v = b.VertexCount - 3; v < b.VertexCount; v++)
                    {
                        var p = b.Vertex(v);
                        b.SetBand(v, band(p, p.y - ground(new Vector2(p.x, p.z))), bandPalette);
                    }
            }
            for (int i = -n; i < n; i++)
            for (int j = -n; j < n; j++)
            {
                if (In(i, j) && In(i + 1, j) && In(i, j + 1)) Tri(i, j, i + 1, j, i, j + 1);
                if (In(i + 1, j) && In(i + 1, j + 1) && In(i, j + 1)) Tri(i + 1, j, i + 1, j + 1, i, j + 1);
            }
            // walls round the rim wherever the field stands above the ground
            var rim = new List<(int, int)>();
            for (int k = 0; k < 6; k++)
            {
                // walk the rim edge by edge: corners at n·e1, n·e2, n·(e2 - e1), -n·e1, -n·e2, n·(e1 - e2)
                (int, int) c0 = Corner(k, n), c1 = Corner(k + 1, n);
                for (int s = 0; s < n; s++)
                    rim.Add((c0.Item1 + (c1.Item1 - c0.Item1) * s / n, c0.Item2 + (c1.Item2 - c0.Item2) * s / n));
            }
            for (int k = 0; k < rim.Count; k++)
            {
                var (ai, aj) = rim[k];
                var (bi, bj) = rim[(k + 1) % rim.Count];
                float ha = hgt[ai + n, aj + n], hb = hgt[bi + n, bj + n];
                if (ha < 1e-4f && hb < 1e-4f) continue;
                Vector3 a = pos[ai + n, aj + n], c = pos[bi + n, bj + n];
                var pa = new Vector2(a.x, a.z); var pc = new Vector2(c.x, c.z);
                float ya = (wallBottom ?? ground)(pa) - 0.02f * size, yc = (wallBottom ?? ground)(pc) - 0.02f * size;
                var da = new Vector3(a.x, ya, a.z); var dc = new Vector3(c.x, yc, c.z);
                var mid = (a + c + da + dc) / 4f;
                var outward = new Vector3(mid.x, 0f, mid.z).normalized;
                b.AddQuad(a, c, dc, da, paint(mid, (ha + hb) * 0.25f, outward), mid - outward);
            }
        }

        static (int, int) Corner(int k, int n) => (k % 6) switch
        {
            0 => (n, 0), 1 => (0, n), 2 => (-n, n), 3 => (-n, 0), 4 => (0, -n), _ => (n, -n),
        };

        static float Hash01(float x, float y, float seed) => Mathf.PerlinNoise(x * 3.1f + seed, y * 3.1f - seed * 0.7f);

        // Smooth 0..1 step that is flat on both sides (terrace risers)
        static float Terrace(float s, int steps)
        {
            s = Mathf.Clamp01(s) * steps;
            int k = Mathf.Min((int)s, steps - 1);
            float f = s - k;
            return (k + Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.4f, 1f, f))) / steps; // a softer riser
        }

        // Band palettes for MapFeature.shader (Danxia: A, sedimentary strata: B). Set on every build
        // (cheap) so they survive a domain reload.
        static readonly Color[] StrataBands = { RedRock, OrangeRock, CreamRock, OrangeRock, RedRock * 0.9f };
        static void SetBandPalettes()
        {
            static Vector4[] Pad(Color[] c) { var v = new Vector4[8]; for (int i = 0; i < 8; i++) v[i] = c[Mathf.Min(i, c.Length - 1)]; return v; }
            Shader.SetGlobalVectorArray("_NHBandsA", Pad(DanxiaBands));
            Shader.SetGlobalVectorArray("_NHBandsB", Pad(StrataBands));
            Shader.SetGlobalVector("_NHBandCounts", new Vector4(DanxiaBands.Length, StrataBands.Length, 0f, 0f));
        }

        // Shading-only colour for a banded facet (alpha 0 = take the band colour per pixel)
        static Color Banded(float shade) => new(shade, shade, shade, 0f);

        // Band coordinate of sedimentary strata at a point: by height, with a little wobble
        static float StrataBand(Vector3 p, float size, float wobbleScale) =>
            p.y / size * 28f + Mathf.PerlinNoise(p.x * wobbleScale, p.z * wobbleScale) * 0.5f;

        // Banded sedimentary rock, by height: red, orange and cream layers
        static Color Strata(float y, float size, float seed, float wobble)
        {
            float band = y / size * 28f + wobble;
            int k = Mathf.FloorToInt(band);
            var palette = new[] { RedRock, OrangeRock, CreamRock, OrangeRock, RedRock * 0.9f };
            return palette[((k % palette.Length) + palette.Length) % palette.Length];
        }

        // ---- Mesa: a flat-topped table of layered rock with sheer walls, a talus apron and a
        //      smaller butte beside it

        public static Mesh CreateMesa(System.Random rng, float size, System.Func<Vector2, float> ground)
        {
            var b = new Builder();
            float seed = Range(rng, 0f, 100f);
            float H = size * Range(rng, 0.2f, 0.28f);
            float R = size * Range(rng, 0.36f, 0.44f);
            var c2 = new Vector2(Mathf.Sin(seed), Mathf.Cos(seed)) * size * 0.55f;
            float R2 = size * 0.11f, H2 = H * Range(rng, 0.75f, 0.95f);
            float Table(Vector2 p, Vector2 c, float r, float h)
            {
                var d = p - c;
                float a = Mathf.Atan2(d.x, d.y);
                float edge = r * (1f + 0.16f * (Mathf.PerlinNoise(seed + Mathf.Cos(a) * 1.6f, seed + Mathf.Sin(a) * 1.6f) - 0.5f) * 2f);
                float dist = d.magnitude;
                float wall = 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(edge - 0.02f * size, edge + 0.035f * size, dist));
                float talus = 0.3f * Mathf.Clamp01(1f - (dist - edge) / (0.2f * size));
                return h * Mathf.Max(wall, dist > edge ? talus * talus : 0f);
            }
            float Height(Vector2 p) => Mathf.Max(Table(p, Vector2.zero, R, H), Table(p, c2, R2, H2)) * RimFade(p, size);
            AddHeightField(b, size, 22, Height, ground, (m, h, nrm) =>
            {
                if (nrm.y > 0.85f && h > H * 0.8f) return Shade(rng, MesaCap, 0.05f);           // the cap rock
                if (nrm.y > 0.6f) return Shade(rng, Scree, 0.06f);                               // talus
                return Banded(Range(rng, 0.96f, 1.04f)); // layered walls, per pixel
            }, band: (p, h) => StrataBand(p, size, 4f), bandPalette: 2f);
            return b.ToMesh("Mesa");
        }

        // fades a field out toward the hex rim, so it meets the neighbours at ground level
        static float RimFade(Vector2 p, float size)
        {
            float a = size * 0.8660254f;
            float d = 0f;
            for (int e = 0; e < 3; e++)
            {
                float ang = (60f * e + 30f) * Mathf.Deg2Rad;
                d = Mathf.Max(d, Mathf.Abs(p.x * Mathf.Sin(ang) + p.y * Mathf.Cos(ang)));
            }
            // settles into the ground well before the tile's edge, so the neighbours' ground runs on
            // to its foot without a seam
            return 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(a * 0.62f, a * 0.92f, d));
        }

        // ---- Canyon: a layered plateau cut by a gorge that steps down in cliff bands to the river
        //      at the bottom. riverLines: the tile's river channels (HexGrid.RiverCenterlines), so the
        //      gorge follows the river the map draws and it runs on into the neighbouring tiles'
        //      rivers; the water itself is the river system's. Without them, a dry gorge crosses
        //      the tile from one edge to another.

        public static Mesh CreateCanyon(System.Random rng, float size, System.Func<Vector2, float> ground,
                                        IReadOnlyList<List<Vector2>> riverLines = null, float riverHalfWidth = 0f)
        {
            var b = new Builder();
            float seed = Range(rng, 0f, 100f);
            float a = size * 0.8660254f;
            var lines = new List<List<Vector2>>();
            if (riverLines != null) foreach (var l in riverLines) if (l != null && l.Count >= 2) lines.Add(l);
            if (lines.Count == 0)
            {
                int eIn = rng.Next(6), eOut = (eIn + 3 + rng.Next(-1, 2) + 6) % 6;
                Vector2 Edge(int e) { float ang = (60f * e + 30f) * Mathf.Deg2Rad; return new Vector2(Mathf.Sin(ang), Mathf.Cos(ang)) * a * 1.02f; }
                var p0 = Edge(eIn); var p1 = Edge(eOut);
                var sd = new Vector2((p1 - p0).y, -(p1 - p0).x).normalized;
                float wig = Range(rng, 0.12f, 0.2f) * size, phase = Range(rng, 0f, 6f);
                var line = new List<Vector2>();
                for (int k = 0; k <= 24; k++)
                {
                    float t = k / 24f;
                    line.Add(Vector2.Lerp(p0, p1, t) + sd * Mathf.Sin(t * Mathf.PI * 2.2f + phase) * wig * Mathf.Sin(t * Mathf.PI));
                }
                lines.Add(line);
            }
            float Dist(Vector2 p)
            {
                float best = float.MaxValue;
                foreach (var line in lines)
                for (int k = 0; k + 1 < line.Count; k++)
                {
                    var ab = line[k + 1] - line[k];
                    float t = ab.sqrMagnitude > 1e-10f ? Mathf.Clamp01(Vector2.Dot(p - line[k], ab) / ab.sqrMagnitude) : 0f;
                    best = Mathf.Min(best, (p - (line[k] + ab * t)).magnitude);
                }
                return best;
            }

            float H     = size * Range(rng, 0.24f, 0.32f);
            float floor = Mathf.Max(0.045f * size, riverHalfWidth * 1.8f); // the gorge floor holds the river with a little beach
            float reach = Range(rng, 0.26f, 0.34f) * size;                 // how far the gorge opens out at the top
            // Jagged rims and side gullies: noise in the distance to the river (a fine ridged part
            // cuts gullies into the walls)
            float Rough(Vector2 p)
            {
                float n1 = Mathf.PerlinNoise(seed + p.x / size * 4.5f, seed + p.y / size * 4.5f) - 0.5f;
                float n2 = 1f - Mathf.Abs(Mathf.PerlinNoise(seed * 1.7f + p.x / size * 13f, seed * 0.6f + p.y / size * 13f) * 2f - 1f);
                return n1 * 0.08f * size - n2 * n2 * 0.035f * size;
            }
            // The plateau steps down in cliff bands toward the gorge and, round the tile's edge, to the
            // land outside, instead of melting into a dome
            float Height(Vector2 p)
            {
                float d     = Dist(p) + Rough(p);
                float gorge = Mathf.Clamp01((d - floor) / reach);
                float rim   = RimFade(p, size);
                return H * Terrace(Mathf.Min(gorge, rim), 3);
            }
            AddHeightField(b, size, 54, Height, ground, (m, h, nrm) =>
            {
                if (nrm.y > 0.85f && h > H * 0.9f) return Shade(rng, Scree * 0.95f, 0.05f);   // the rim and plateau top
                if (nrm.y > 0.8f) return Shade(rng, Scree, 0.06f);                            // terrace treads
                return Banded(Range(rng, 0.94f, 1.05f));                                      // layered walls, per pixel
            }, band: (p, h) => StrataBand(p, size, 3f), bandPalette: 2f);

            // Fallen rock at the feet of the cliffs, and a few dry shrubs on the plateau and ledges
            Vector3 On(Vector2 p) => new(p.x, ground(p) + Height(p), p.y);
            for (int i = 0; i < 40; i++)
            {
                var p = new Vector2(Range(rng, -a, a), Range(rng, -a, a));
                float d = Dist(p);
                if (d < floor * 1.05f || d > floor + reach * 1.1f || RimFade(p, size) < 0.5f) continue;
                AddRock(b, rng, On(p), size * Range(rng, 0.01f, 0.024f), Scree * Range(rng, 0.75f, 0.95f));
            }
            for (int i = 0; i < 24; i++)
            {
                var p = new Vector2(Range(rng, -a, a), Range(rng, -a, a));
                if (Dist(p) < floor + reach * 0.5f || RimFade(p, size) < 0.6f || rng.NextDouble() < 0.5) continue;
                AddBlob(b, rng, On(p) + Vector3.up * 0.006f * size, size * Range(rng, 0.012f, 0.022f), 0.7f, 0, Shade(rng, DryShrub, 0.1f));
            }

            // a dry gorge (no river given) still has its stream at the bottom
            if (riverLines == null || riverLines.Count == 0)
                foreach (var line in lines)
                for (int k = 0; k + 1 < line.Count; k++)
                {
                    Vector2 q0 = line[k], q1 = line[k + 1];
                    var sd = new Vector2((q1 - q0).y, -(q1 - q0).x).normalized * 0.028f * size;
                    Vector3 V(Vector2 q) => new(q.x, ground(q) + 0.004f * size, q.y);
                    b.AddQuad(V(q0 + sd), V(q1 + sd), V(q1 - sd), V(q0 - sd), Shade(rng, GorgeRiver, 0.04f), V((q0 + q1) * 0.5f) - Vector3.up);
                }
            return b.ToMesh("Canyon");
        }

        static readonly Color DryShrub = new(0.42f, 0.44f, 0.26f);

        // ---- White cliffs: chalk downland rising toward the sea and ending in sheer white walls
        //      banded with flint, with fallen chalk blocks in the surf

        public static Mesh CreateWhiteCliffs(System.Random rng, float size, bool[] seaEdges, float seaY, System.Func<Vector2, float> ground)
        {
            var b = new Builder();
            float a = size * 0.8660254f;
            float H = size * Range(rng, 0.12f, 0.18f);
            float seed = Range(rng, 0f, 100f);
            float Height(Vector2 p)
            {
                float m = 0f;
                for (int e = 0; e < 6; e++)
                {
                    if (!seaEdges[e]) continue;
                    float ang = (60f * e + 30f) * Mathf.Deg2Rad;
                    float de = a - (p.x * Mathf.Sin(ang) + p.y * Mathf.Cos(ang));
                    m = Mathf.Max(m, 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.05f * a, 0.6f * a, de)));
                }
                return H * m * (0.85f + 0.3f * Mathf.PerlinNoise(seed + p.x / size * 3f, seed + p.y / size * 3f));
            }
            AddHeightField(b, size, 20, Height, ground, (m, h, nrm) =>
            {
                if (nrm.y > 0.6f) return Shade(rng, Downland, 0.07f);                                 // grassy downs on top
                bool flint = Mathf.Repeat(m.y / size * 40f, 1f) < 0.12f;
                return Shade(rng, flint ? Flint : ChalkWhite, 0.03f);
            }, p => seaEdges[Mathf.FloorToInt(Mathf.Repeat(Mathf.Atan2(p.x, p.y) * Mathf.Rad2Deg, 360f) / 60f) % 6] ? seaY : ground(p)); // sheer to the sea, flush inland
            // fallen chalk blocks at the foot
            for (int e = 0; e < 6; e++)
            {
                if (!seaEdges[e]) continue;
                float ang = (60f * e + 30f) * Mathf.Deg2Rad;
                var dir = new Vector3(Mathf.Sin(ang), 0f, Mathf.Cos(ang));
                var along = Vector3.Cross(Vector3.up, dir);
                for (int i = rng.Next(2, 5); i > 0; i--)
                    AddRock(b, rng, dir * a * Range(rng, 1.02f, 1.1f) + along * Range(rng, -0.4f, 0.4f) * size + Vector3.up * seaY,
                            size * Range(rng, 0.02f, 0.045f), ChalkWhite * 0.95f);
            }
            return b.ToMesh("WhiteCliffs");
        }

        // ---- Salt lake: a glaring white salt pan crazed into polygons, a shallow pool of brine in
        //      the middle (pink with salt-loving microbes, or milky turquoise) and crusted islets

        public static Mesh CreateSaltLake(System.Random rng, float size, bool pink, System.Func<Vector2, float> ground)
        {
            var b = new Builder();
            float a = size * 0.8660254f;
            Vector3 On(Vector2 p, float lift) => new(p.x, ground(p) + lift * size, p.y);
            // (the salt pan round it is the tile's ground: the SaltFlat surface, see HexGrid.SetGroundLook)
            // the brine pool, its shore shading from salt-white into the brine so it has no hard rim
            var brine = pink ? BrinePink : BrineTeal;
            var mid = On(new Vector2(Range(rng, -0.08f, 0.08f), Range(rng, -0.08f, 0.08f)) * size, 0.003f);
            float rot = Range(rng, 0f, 360f), seed = Range(rng, 0f, 100f);
            const int steps = 9, sides = 28;
            for (int k = 0; k < steps; k++)
            {
                float t = k / (float)(steps - 1);                       // 0 at the shore, 1 in the middle
                float r = size * Mathf.Lerp(0.4f, 0.12f, t);
                var col = t < 0.3f ? Color.Lerp(SaltWhite * 0.97f, brine, t / 0.3f)
                                   : Color.Lerp(brine, brine * (pink ? new Color(0.92f, 0.8f, 0.88f) : new Color(0.82f, 0.92f, 0.95f)), (t - 0.3f) / 0.7f);
                var c = mid + Vector3.up * 0.0006f * size * k;
                for (int i = 0; i < sides; i++)
                {
                    float a0 = (rot + i * 360f / sides) * Mathf.Deg2Rad, a1 = (rot + (i + 1) * 360f / sides) * Mathf.Deg2Rad;
                    float w0 = 1f + 0.18f * (Mathf.PerlinNoise(seed + Mathf.Cos(a0) * 1.5f, seed + Mathf.Sin(a0) * 1.5f) - 0.5f);
                    float w1 = 1f + 0.18f * (Mathf.PerlinNoise(seed + Mathf.Cos(a1) * 1.5f, seed + Mathf.Sin(a1) * 1.5f) - 0.5f);
                    b.AddTri(c, c + new Vector3(Mathf.Sin(a0), 0f, Mathf.Cos(a0)) * r * w0, c + new Vector3(Mathf.Sin(a1), 0f, Mathf.Cos(a1)) * r * w1,
                             col, c - Vector3.up);
                }
            }
            // salt islets and crust ridges in the pool
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                float ang = Range(rng, 0f, Mathf.PI * 2f), d = Range(rng, 0.05f, 0.28f) * size;
                AddBlob(b, rng, mid + new Vector3(Mathf.Sin(ang) * d, 0.002f * size, Mathf.Cos(ang) * d), size * Range(rng, 0.012f, 0.03f), 0.25f, 0, SaltWhite);
            }
            return b.ToMesh(pink ? "PinkSaltLake" : "SaltLake");
        }

        // ---- Danxia: rounded ridges of sandstone striped in bands of red, orange, cream and
        //      lilac, the stripes tilted with the beds (Zhangye's rainbow mountains)

        public static Mesh CreateDanxia(System.Random rng, float size, System.Func<Vector2, float> ground)
        {
            var b = new Builder();
            float seed = Range(rng, 0f, 100f);
            float dirA = Range(rng, 0f, Mathf.PI);
            var along = new Vector2(Mathf.Sin(dirA), Mathf.Cos(dirA));
            var across = new Vector2(along.y, -along.x);
            int ridges = rng.Next(4, 7);
            var offsets = new float[ridges]; var heights = new float[ridges]; var widths = new float[ridges];
            for (int i = 0; i < ridges; i++)
            {
                offsets[i] = Mathf.Lerp(-0.62f, 0.62f, (i + Range(rng, 0.2f, 0.8f)) / ridges) * size;
                heights[i] = size * Range(rng, 0.1f, 0.2f);
                widths[i]  = size * Range(rng, 0.1f, 0.15f);
            }
            float Height(Vector2 p)
            {
                float x = Vector2.Dot(p, across), y = Vector2.Dot(p, along);
                float h = 0f;
                for (int i = 0; i < ridges; i++)
                {
                    float off = offsets[i] + Mathf.Sin(y / size * 4f + i * 1.7f + seed) * 0.05f * size;
                    float d = (x - off) / widths[i];
                    float crest = heights[i] * (0.75f + 0.25f * Mathf.Sin(y / size * 6f + i));
                    h = Mathf.Max(h, crest * Mathf.Exp(-d * d * 1.6f));
                }
                return h * RimFade(p, size);
            }
            float tilt = Range(rng, -0.35f, 0.35f);
            // stripes follow the tilted beds; coloured per pixel by the shader (BandColor), so their
            // edges are smooth curves over the ridges rather than following the triangles
            AddHeightField(b, size, 32, Height, ground, (m, h, nrm) => Banded(Range(rng, 0.97f, 1.03f) * Mathf.Lerp(0.88f, 1.04f, nrm.y)),
                band: (p, h) => (h + Vector2.Dot(new Vector2(p.x, p.z), along) * tilt) / size * 34f + Mathf.PerlinNoise(p.x * 3f, p.z * 3f) * 0.8f,
                bandPalette: 1f);
            return b.ToMesh("Danxia");
        }
    }
}
