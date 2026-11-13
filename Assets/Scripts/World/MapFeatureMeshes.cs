using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace NaturalHistory.World
{
    // Low-poly, flat-shaded props that sit on a hex tile's top face: mountain peaks and forest stands.
    // Colors are baked into vertex colors so all props share one material (MapFeature shader).
    // Meshes are centred on the tile (y = 0 is the top face) and stay inside the hex's inner radius.
    public static class MapFeatureMeshes
    {
        static readonly Color Rock   = new(0.46f, 0.42f, 0.38f);
        static readonly Color Snow   = new(0.94f, 0.96f, 0.99f);
        static readonly Color Bark      = new(0.36f, 0.25f, 0.16f);
        static readonly Color Leaf      = new(0.30f, 0.52f, 0.20f);
        static readonly Color LeafLight = new(0.48f, 0.66f, 0.26f);
        static readonly Color Needle    = new(0.10f, 0.29f, 0.18f);
        static readonly Color NeedleTip = new(0.22f, 0.45f, 0.26f);
        static readonly Color Shrub     = new(0.24f, 0.40f, 0.17f);

        // One large ridged peak plus 0–3 smaller ones, boulders around the foot and, where allowed,
        // a few pines. snowLine = fraction of the main peak's height (from the top) where snow can
        // lie; it only sticks to gentle faces, so cliffs stay bare rock. heightScale stretches the
        // whole massif; rockTint recolours the stone (e.g. red sandstone, blue-grey granite).
        public static Mesh CreateMountain(System.Random rng, float size, float snowLine, float heightScale, Color rockTint, bool allowTrees)
        {
            var b = new Builder();
            bool icy         = snowLine >= 0.65f;
            float mainHeight = size * Range(rng, 0.95f, 1.25f) * heightScale;
            float snowY      = mainHeight * (1f - snowLine);

            var mainCenter = new Vector3(Range(rng, -0.08f, 0.08f), 0f, Range(rng, -0.08f, 0.08f)) * size;
            AddPeak(b, rng, mainCenter, size * Range(rng, 0.4f, 0.5f), mainHeight, snowY, allowTrees, rockTint);

            int extra   = rng.Next(0, 4);
            float angle = Range(rng, 0f, 360f);
            for (int i = 0; i < extra; i++, angle += Range(rng, 90f, 160f))
            {
                float a = angle * Mathf.Deg2Rad;
                float d = size * Range(rng, 0.28f, 0.38f);
                var center = new Vector3(Mathf.Sin(a) * d, 0f, Mathf.Cos(a) * d);
                // Occasionally a near-twin summit, so some massifs read as a ridge rather than one cone
                float rel = rng.NextDouble() < 0.2 ? Range(rng, 0.75f, 0.9f) : Range(rng, 0.4f, 0.65f);
                AddPeak(b, rng, center, size * Range(rng, 0.22f, 0.32f), mainHeight * rel, snowY, allowTrees, rockTint);
            }

            foreach (var p in Scatter(rng, rng.Next(2, 7), 0.68f * size, 0.08f * size, new List<Vector2>()))
            {
                if (p.magnitude < 0.5f * size) continue; // only around the foot, not buried in the slope
                AddRock(b, rng, new Vector3(p.x, 0f, p.y), size * Range(rng, 0.03f, 0.055f), icy ? Snow * 0.85f : Rock * rockTint);
            }
            if (allowTrees && rng.NextDouble() < 0.75)
            {
                foreach (var p in Scatter(rng, rng.Next(3, 8), 0.66f * size, 0.08f * size, new List<Vector2>()))
                    if (p.magnitude > 0.5f * size)
                        AddConifer(b, rng, new Vector3(p.x, 0f, p.y), size * Range(rng, 0.3f, 0.42f));
            }
            return b.ToMesh("MountainPeaks");
        }

        // A stand of detailed trees with shrubs between the trunks. Trees near the middle are
        // taller, so the canopy reads as one domed clump from the strategy camera.
        public static Mesh CreateForest(System.Random rng, float size, bool conifer)
        {
            var b = new Builder();
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
            var b = new Builder();
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
        public static Mesh CreateOasis(System.Random rng, float size)
        {
            var b = new Builder();
            var center = new Vector3(Range(rng, -0.06f, 0.06f) * size, 0.004f, Range(rng, -0.06f, 0.06f) * size);
            var rim = Ring(rng, center, 0.24f * size, 10, 0.2f);
            for (int i = 0; i < rim.Length; i++)
                b.AddTri(center, rim[i], rim[(i + 1) % rim.Length], PondWater, center - Vector3.up);

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

        // Concave stratovolcano: gullied ash slopes turning to basalt near the top, a crater with a
        // lava lake, lava streams down the deepest gullies, a small side cone and a smoke plume.
        public static Mesh CreateVolcano(System.Random rng, float size, float heightScale)
        {
            const int sides = 16, rings = 6;
            var b = new Builder();
            float h    = size * Range(rng, 0.8f, 1.0f) * heightScale;
            var below  = Vector3.down * h;
            var g      = ConeGrid(rng, Vector3.zero, 0.58f * size, h, 0.15f * size, sides, rings, 0.22f, 0.05f, 1.7f, out var spokes);

            for (int k = 0; k < rings; k++)
            {
                float t   = (k + 0.5f) / rings;
                var slope = t < 0.25f ? Ash : Color.Lerp(Ash, Basalt, Mathf.InverseLerp(0.25f, 0.7f, t));
                for (int i = 0; i < sides; i++)
                {
                    int j = (i + 1) % sides;
                    b.AddQuad(g[k, i], g[k, j], g[k + 1, j], g[k + 1, i], Shade(rng, slope, 0.08f), below);
                }
            }

            // Crater: inner wall down to a lava lake. The wall faces inward, so "inside" is beyond the rim.
            float rimY = 0f;
            for (int i = 0; i < sides; i++) rimY += g[rings, i].y / sides;
            float lavaY  = rimY - 0.12f * h;
            var lavaRing = new Vector3[sides];
            for (int i = 0; i < sides; i++)
                lavaRing[i] = new Vector3(g[rings, i].x * 0.6f, lavaY, g[rings, i].z * 0.6f);
            for (int i = 0; i < sides; i++)
            {
                int j = (i + 1) % sides;
                var outside = (g[rings, i] + g[rings, j]) * 0.5f;
                outside = new Vector3(outside.x * 3f, lavaY, outside.z * 3f);
                b.AddQuad(g[rings, i], g[rings, j], lavaRing[j], lavaRing[i], Shade(rng, Basalt * 0.7f, 0.08f), outside);
                b.AddTri(Vector3.up * lavaY, lavaRing[i], lavaRing[j], Lava * Range(rng, 0.85f, 1.1f), Vector3.up * (lavaY - 1f));
            }

            // Lava streams follow the two deepest gullies from the rim partway down the slope.
            var order = new List<int>();
            for (int i = 0; i < sides; i++) order.Add(i);
            order.Sort((x, y) => spokes[x].CompareTo(spokes[y]));
            int streams = rng.Next(1, 3);
            for (int n = 0; n < streams; n++)
                AddLavaStream(b, rng, g, order[n * (sides / 2)], rings, rng.Next(1, 3), size, below);

            // Parasitic cone on a flank away from the lava
            {
                int i   = order[sides - 1];
                var dir = new Vector3(g[0, i].x, 0f, g[0, i].z).normalized;
                var c   = dir * 0.42f * size + Vector3.up * h * Mathf.Pow(0.25f, 1.7f);
                var cg  = ConeGrid(rng, c, 0.12f * size, 0.13f * size, 0.04f * size, 8, 2, 0.1f, 0.06f, 1.2f, out _);
                var cb  = c + Vector3.down * size;
                for (int k = 0; k < 2; k++)
                for (int s0 = 0; s0 < 8; s0++)
                {
                    int s1 = (s0 + 1) % 8;
                    b.AddQuad(cg[k, s0], cg[k, s1], cg[k + 1, s1], cg[k + 1, s0], Shade(rng, Basalt, 0.08f), cb);
                }
                var top = c + Vector3.up * 0.1f * size;
                for (int s0 = 0; s0 < 8; s0++)
                    b.AddTri(cg[2, s0], cg[2, (s0 + 1) % 8], top, Basalt * 0.55f, top + Vector3.up);
            }

            foreach (var p in Scatter(rng, rng.Next(3, 6), 0.7f * size, 0.08f * size, new List<Vector2>()))
                if (p.magnitude > 0.55f * size)
                    AddRock(b, rng, new Vector3(p.x, 0f, p.y), size * Range(rng, 0.03f, 0.05f), Basalt);

            // Smoke plume drifting with the wind, puffs growing and paling as they rise
            var drift = new Vector3(Range(rng, -1f, 1f), 0f, Range(rng, -1f, 1f)).normalized * 0.05f * size;
            for (int n = 0; n < 4; n++)
            {
                var c = Vector3.up * (rimY + (0.1f + 0.11f * n) * size) + drift * n * n * 0.6f;
                AddBlob(b, rng, c, (0.06f + 0.03f * n) * size, 0.8f, 1, Color.Lerp(Smoke * 0.6f, Smoke * 1.2f, n / 3f));
            }
            return b.ToMesh("Volcano");
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
            var color   = Shade(rng, PalmLeaf);
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
            var b = new Builder();
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
                    foreach (var p in Spots(1, 3, 0.3f))
                        AddDune(b, rng, At(p), Range(rng, 0.25f, 0.45f) * size, Range(rng, 0.035f, 0.08f) * size, Shade(rng, Sand, 0.06f));
                    if (rng.NextDouble() < 0.3)
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
                AddLimb(b, foot, tip, 0.006f * size, 0.002f * size, Shade(rng, Reed));
            }
        }

        // Angular, half-buried stone (low-detail blob with strong jitter).
        static void AddRock(Builder b, System.Random rng, Vector3 root, float radius, Color color) =>
            AddBlob(b, rng, root + Vector3.up * radius * 0.2f, radius, Range(rng, 0.5f, 0.8f), 0, Shade(rng, color));

        // Thin trunk under a wide, flat crown.
        static void AddAcacia(Builder b, System.Random rng, Vector3 root, float size)
        {
            float h  = size * Range(rng, 0.22f, 0.3f);
            var top  = root + new Vector3(Range(rng, -0.03f, 0.03f) * size, h, Range(rng, -0.03f, 0.03f) * size);
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.016f * size, 0.01f * size, Shade(rng, Bark));
            AddBlob(b, rng, top + Vector3.up * 0.02f * size, Range(rng, 0.13f, 0.17f) * size, 0.28f, 1, Shade(rng, new Color(0.36f, 0.48f, 0.20f)));
        }

        static readonly Color RockDark = new(0.36f, 0.33f, 0.31f);
        static readonly Color Foothill = new(0.38f, 0.40f, 0.27f);
        static readonly Color Ash      = new(0.43f, 0.39f, 0.35f);
        static readonly Color LavaCool = new(0.75f, 0.16f, 0.05f);
        static readonly Color Smoke    = new(0.62f, 0.60f, 0.58f);

        // Ridged peak on a radial grid: spurs and gullies, concave slopes and a craggy summit.
        // Faces are coloured by height and slope: green-brown foot, banded rock strata, and snow
        // above a ragged snow line on faces gentle enough to hold it.
        static void AddPeak(Builder b, System.Random rng, Vector3 center, float radius, float height, float snowY, bool vegetatedFoot, Color rockTint)
        {
            const int rings = 5;
            int sides = rng.Next(9, 14);
            var g = ConeGrid(rng, center, radius, height * 0.93f, radius * 0.1f, sides, rings,
                             Range(rng, 0.2f, 0.5f), Range(rng, 0.05f, 0.11f), Range(rng, 1.1f, 1.6f), out _);
            var apex   = center + new Vector3(Range(rng, -0.06f, 0.06f) * radius, height, Range(rng, -0.06f, 0.06f) * radius);
            var below  = center + Vector3.down * height; // every face of a radial height field points away from here
            float band = height * Range(rng, 0.1f, 0.14f);

            Color FaceColor(Vector3 a, Vector3 c, Vector3 d)
            {
                float y  = (a.y + c.y + d.y) / 3f;
                float up = FaceUp(a, c, d, below);
                float snowAt = snowY + height * Range(rng, -0.06f, 0.06f);
                if (y > snowAt && (up > 0.45f || y > snowAt + 0.4f * (height - snowAt)))
                    return Shade(rng, Snow, 0.04f);
                if (vegetatedFoot && y < height * 0.14f && up > 0.4f)
                    return Shade(rng, Foothill, 0.08f);
                var rock = (Mathf.FloorToInt(y / band) % 2 == 0 ? Rock : RockDark) * rockTint;
                return Shade(rng, rock, 0.07f) * Mathf.Lerp(0.85f, 1.05f, up); // cliffs a touch darker
            }

            for (int k = 0; k < rings; k++)
            for (int i = 0; i < sides; i++)
            {
                int j = (i + 1) % sides;
                var p0 = g[k, i]; var p1 = g[k, j]; var p2 = g[k + 1, j]; var p3 = g[k + 1, i];
                b.AddTri(p0, p1, p2, FaceColor(p0, p1, p2), below);
                b.AddTri(p0, p2, p3, FaceColor(p0, p2, p3), below);
            }
            for (int i = 0; i < sides; i++)
            {
                var p0 = g[rings, i]; var p1 = g[rings, (i + 1) % sides];
                b.AddTri(p0, p1, apex, FaceColor(p0, p1, apex), below);
            }
        }

        // Radial grid for cone-like landforms: ring 0 is the base (sunk slightly into the tile),
        // ring `rings` has topRadius. Height follows t^profile (profile > 1 → concave slopes).
        // Each spoke gets a radius multiplier (smoothed with its neighbours) so the slope forms
        // spurs (> 1) and gullies (< 1) that fade out toward the top.
        static Vector3[,] ConeGrid(System.Random rng, Vector3 center, float radius, float height, float topRadius,
                                   int sides, int rings, float ridge, float jitter, float profile, out float[] spokes)
        {
            var raw = new float[sides];
            for (int i = 0; i < sides; i++) raw[i] = Range(rng, -1f, 1f);
            spokes = new float[sides];
            for (int i = 0; i < sides; i++)
                spokes[i] = 1f + ridge * (0.5f * raw[i] + 0.25f * (raw[(i + sides - 1) % sides] + raw[(i + 1) % sides]));

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
        static void AddConifer(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h  = s * Range(rng, 0.55f, 0.75f);
            var lean = new Vector3(Range(rng, -0.03f, 0.03f), 0f, Range(rng, -0.03f, 0.03f)) * h;
            AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * 0.85f * h + lean, 0.03f * s, 0.01f * s, Shade(rng, Bark));

            int tiers = rng.Next(4, 7);
            var dark  = Shade(rng, Needle, 0.08f);
            for (int i = 0; i < tiers; i++)
            {
                float t      = i / (float)(tiers - 1);
                var center   = root + Vector3.up * Mathf.Lerp(0.16f, 0.7f, t) * h + lean * t;
                float radius = Mathf.Lerp(0.17f, 0.06f, t) * s * Range(rng, 0.9f, 1.1f);
                AddBoughTier(b, rng, center, radius, Mathf.Lerp(0.28f, 0.2f, t) * h, Color.Lerp(dark, NeedleTip, t * 0.8f));
            }
            AddCone(b, rng, root + Vector3.up * 0.86f * h + lean, 0.025f * s, 0.14f * h, NeedleTip);
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
        static void AddBroadleaf(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h  = s * Range(rng, 0.5f, 0.66f);
            var bark = Shade(rng, Bark);
            var leaf = Color.Lerp(Leaf, LeafLight, Range(rng, 0f, 0.45f));
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
        static void AddLimb(Builder b, Vector3 from, Vector3 to, float r0, float r1, Color color)
        {
            const int sides = 6;
            var axis   = (to - from).normalized;
            var u      = Vector3.Cross(axis, Mathf.Abs(axis.y) < 0.99f ? Vector3.up : Vector3.right).normalized;
            var v      = Vector3.Cross(axis, u);
            var inside = (from + to) * 0.5f;
            for (int i = 0; i < sides; i++)
            {
                float a0 = Mathf.PI * 2f * i / sides, a1 = Mathf.PI * 2f * (i + 1) / sides;
                var d0 = u * Mathf.Cos(a0) + v * Mathf.Sin(a0);
                var d1 = u * Mathf.Cos(a1) + v * Mathf.Sin(a1);
                b.AddQuad(from + d0 * r0, from + d1 * r0, to + d1 * r1, to + d0 * r1, color, inside);
            }
        }

        // Lumpy ball: an icosphere (detail 0 = 20 faces, 1 = 80) with jittered vertices, squashed
        // vertically. Downward faces are darkened so leaf clumps look self-shadowed.
        static void AddBlob(Builder b, System.Random rng, Vector3 center, float radius, float squash, int detail, Color color)
        {
            var (dirs, faces) = Icosphere(detail);
            var pts = new Vector3[dirs.Length];
            for (int i = 0; i < dirs.Length; i++)
            {
                var d = dirs[i] * radius * Range(rng, 0.82f, 1.12f);
                d.y *= squash;
                pts[i] = center + d;
            }
            for (int f = 0; f < faces.Length; f += 3)
                b.AddTri(pts[faces[f]], pts[faces[f + 1]], pts[faces[f + 2]], color * Range(rng, 0.93f, 1.07f), center, ao: 0.45f);
        }

        static readonly (Vector3[] dirs, int[] faces)[] icospheres = new (Vector3[], int[])[2];

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

            // a, b, c, d in order around the quad's edge
            public void AddQuad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Color color, Vector3 inside)
            {
                AddTri(a, b, c, color, inside);
                AddTri(a, c, d, color, inside);
            }

            public Mesh ToMesh(string name)
            {
                var mesh = new Mesh { name = name };
                if (verts.Count > 65535) mesh.indexFormat = IndexFormat.UInt32;
                mesh.SetVertices(verts);
                mesh.SetNormals(normals);
                mesh.SetColors(colors);
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateBounds();
                return mesh;
            }
        }
    }
}
