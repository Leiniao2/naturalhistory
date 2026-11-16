using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Props for the layer under sea level (HexGrid.Under): cave formations, soil and burrows, seabed
    // with its water plants (plants.json layer "under"), underwater volcanoes and hydrothermal vents.
    public static partial class MapFeatureMeshes
    {
        static readonly Color CaveRock    = new(0.42f, 0.44f, 0.48f);
        static readonly Color Dripstone   = new(0.78f, 0.72f, 0.62f);
        static readonly Color CavePool    = new(0.10f, 0.22f, 0.30f);
        static readonly Color Crystal     = new(0.80f, 0.86f, 0.95f);
        static readonly Color Soil        = new(0.40f, 0.30f, 0.22f);
        static readonly Color Root        = new(0.48f, 0.38f, 0.28f);
        static readonly Color Burrow      = new(0.12f, 0.09f, 0.07f);
        static readonly Color SeabedStone = new(0.50f, 0.52f, 0.50f);
        static readonly Color Shell       = new(0.92f, 0.86f, 0.76f);
        static readonly Color Nodule      = new(0.16f, 0.15f, 0.16f);
        static readonly Color Chimney     = new(0.16f, 0.14f, 0.14f);
        static readonly Color VentGlow    = new(1.20f, 0.55f, 0.20f);
        static readonly Color TubeWorm    = new(0.92f, 0.90f, 0.85f);
        static readonly Color WormPlume   = new(0.95f, 0.15f, 0.15f);
        static readonly Color Seagrass    = new(0.30f, 0.55f, 0.25f);
        static readonly Color KelpBrown   = new(0.50f, 0.42f, 0.18f);
        static readonly Color AlgaeGreen  = new(0.35f, 0.58f, 0.25f);
        static readonly Color CorallinePink = new(0.85f, 0.55f, 0.62f);
        static readonly Color Charophyte  = new(0.40f, 0.58f, 0.30f);

        // The tile's ground in the under layer: formations for caves and soil, water plants (main and
        // second species, may be null) with stones and shells for seabed and lakebed. Fills the hex.
        public static Mesh CreateUnderDetail(System.Random rng, float size, UnderKind kind, PlantDefinition main, PlantDefinition second)
        {
            var b = new Builder();
            var taken = new List<Vector2>();
            float apothem = 0.8660254f * size;
            List<Vector2> Spots(int min, int max, float gap)
            {
                var spots = HexScatter(rng, rng.Next(min, max + 1), apothem * 0.95f, gap * size, taken);
                taken.AddRange(spots);
                return spots;
            }
            Vector3 At(Vector2 p) => new(p.x, 0f, p.y);
            maxBlobDetail = 0;

            switch (kind)
            {
                case UnderKind.Cave:
                    foreach (var p in Spots(6, 11, 0.12f)) AddStalagmite(b, rng, At(p), size * Range(rng, 0.1f, 0.3f));
                    foreach (var p in Spots(1, 3, 0.2f))   AddDripColumn(b, rng, At(p), size * Range(rng, 0.3f, 0.45f));
                    foreach (var p in Spots(1, 2, 0.2f))   AddPond(b, rng, At(p) + Vector3.up * 0.004f, size * Range(rng, 0.07f, 0.12f), CavePool);
                    if (rng.NextDouble() < 0.4)
                        foreach (var p in Spots(2, 4, 0.08f)) AddCone(b, rng, At(p), size * 0.02f, size * Range(rng, 0.05f, 0.09f), Shade(rng, Crystal));
                    break;
                case UnderKind.Rock:
                    foreach (var p in Spots(3, 6, 0.14f)) AddRock(b, rng, At(p), size * Range(rng, 0.03f, 0.06f), Color.Lerp(Soil, CaveRock, Range(rng, 0f, 1f)));
                    foreach (var p in Spots(2, 4, 0.15f)) AddRoots(b, rng, At(p), size);
                    foreach (var p in Spots(2, 4, 0.1f))  AddPond(b, rng, At(p) + Vector3.up * 0.003f, size * Range(rng, 0.02f, 0.035f), Burrow); // burrow mouths
                    break;
                case UnderKind.DeepSeabed:
                    foreach (var p in Spots(3, 7, 0.12f)) AddRock(b, rng, At(p), size * Range(rng, 0.015f, 0.03f), Nodule); // manganese nodules
                    foreach (var p in Spots(1, 3, 0.15f)) AddRock(b, rng, At(p), size * Range(rng, 0.03f, 0.05f), SeabedStone);
                    break;
                default: // Seabed, Lakebed
                    if (main != null)
                    {
                        bool big = main.form == "Kelp";
                        foreach (var p in Spots(big ? 7 : 12, big ? 12 : 20, big ? 0.13f : 0.09f)) AddUnderPlant(b, rng, At(p), size, main, 1f);
                    }
                    if (second != null)
                        foreach (var p in Spots(3, 7, 0.1f)) AddUnderPlant(b, rng, At(p), size, second, 0.85f);
                    foreach (var p in Spots(1, 4, 0.1f)) AddRock(b, rng, At(p), size * Range(rng, 0.02f, 0.045f), SeabedStone);
                    if (kind == UnderKind.Seabed)
                        foreach (var p in Spots(1, 4, 0.06f)) AddBlob(b, rng, At(p) + Vector3.up * 0.004f, size * 0.012f, 0.45f, 0, Shade(rng, Shell));
                    break;
            }
            maxBlobDetail = 1;
            return b.ToMesh($"Under_{kind}_{main?.id}_{second?.id}");
        }

        // A field of hydrothermal vents: chimneys glowing at the top, ringed by tube worms
        public static Mesh CreateVents(System.Random rng, float size)
        {
            var b = new Builder();
            float apothem = 0.8660254f * size;
            var chimneys = HexScatter(rng, rng.Next(3, 6), apothem * 0.6f, 0.18f * size, new List<Vector2>());
            foreach (var p in chimneys)
            {
                var root = new Vector3(p.x, 0f, p.y);
                float h  = size * Range(rng, 0.18f, 0.4f);
                var prev = root - Vector3.up * 0.01f;
                int segs = rng.Next(3, 5);
                for (int k = 1; k <= segs; k++)
                {
                    float t = k / (float)segs;
                    var next = root + new Vector3(Range(rng, -0.02f, 0.02f) * size, h * t, Range(rng, -0.02f, 0.02f) * size);
                    AddLimb(b, prev, next, Mathf.Lerp(0.05f, 0.025f, t - 1f / segs) * size, Mathf.Lerp(0.05f, 0.025f, t) * size, Shade(rng, Chimney, 0.06f));
                    prev = next;
                }
                AddBlob(b, rng, prev, 0.03f * size, 0.6f, 0, VentGlow); // the hot vent mouth
                for (int i = rng.Next(4, 8); i > 0; i--)
                {
                    float a = Range(rng, 0f, Mathf.PI * 2f), d = Range(rng, 0.06f, 0.11f) * size;
                    var foot = root + new Vector3(Mathf.Sin(a) * d, 0f, Mathf.Cos(a) * d);
                    var tip  = foot + Vector3.up * Range(rng, 0.04f, 0.08f) * size;
                    AddLimb(b, foot, tip, 0.006f * size, 0.005f * size, TubeWorm);
                    AddBlob(b, rng, tip, 0.008f * size, 1f, 0, WormPlume);
                }
            }
            foreach (var p in HexScatter(rng, rng.Next(3, 6), apothem * 0.9f, 0.1f * size, chimneys))
                AddRock(b, rng, new Vector3(p.x, 0f, p.y), size * Range(rng, 0.02f, 0.04f), Nodule);
            return b.ToMesh("Vents");
        }

        static void AddUnderPlant(Builder b, System.Random rng, Vector3 root, float size, PlantDefinition plant, float scale)
        {
            float m = plant.size * scale * Range(rng, 0.8f, 1.15f);
            leafTint = plant.Tint;
            switch (plant.form)
            {
                case "Seagrass":     AddSeagrass(b, rng, root, size * 0.09f * m); break;
                case "Kelp":         AddKelp(b, rng, root, size * 0.35f * m); break;
                case "Coralline":    AddCoralline(b, rng, root, size * 0.04f * m); break;
                case "Charophyte":   AddCharophyte(b, rng, root, size * 0.08f * m); break;
                case "Stromatolite": AddStromatolites(b, rng, root, size * 0.04f * m); break;
                default:             AddAlgae(b, rng, root, size * 0.035f * m); break;
            }
            leafTint = Color.white;
        }

        // Meadow of thin, slightly curving blades
        static void AddSeagrass(Builder b, System.Random rng, Vector3 root, float h)
        {
            var color = Shade(rng, L(Seagrass));
            for (int i = rng.Next(8, 14); i > 0; i--)
            {
                var foot = root + new Vector3(Range(rng, -0.5f, 0.5f), 0f, Range(rng, -0.5f, 0.5f)) * h;
                var lean = new Vector3(Range(rng, -0.3f, 0.3f), 0f, Range(rng, -0.3f, 0.3f)) * h;
                var mid  = foot + Vector3.up * 0.55f * h + lean * 0.4f;
                var tip  = foot + Vector3.up * Range(rng, 0.8f, 1.1f) * h + lean;
                AddLimb(b, foot, mid, 0.04f * h, 0.035f * h, color);
                AddLimb(b, mid, tip, 0.035f * h, 0.005f * h, color * 1.06f);
            }
        }

        // Kelp: a few tall, swaying stipes with blades along them and a float at the top
        static void AddKelp(Builder b, System.Random rng, Vector3 root, float h)
        {
            for (int i = rng.Next(2, 5); i > 0; i--)
            {
                var foot  = root + new Vector3(Range(rng, -0.08f, 0.08f), 0f, Range(rng, -0.08f, 0.08f)) * h;
                var color = Shade(rng, L(KelpBrown));
                float phase = Range(rng, 0f, Mathf.PI * 2f);
                var dir   = new Vector3(Mathf.Sin(phase), 0f, Mathf.Cos(phase));
                var prev  = foot;
                int segs  = 5;
                for (int k = 1; k <= segs; k++)
                {
                    float t = k / (float)segs;
                    var p = foot + Vector3.up * h * t * Range(rng, 0.85f, 1.05f) + dir * Mathf.Sin(t * 3f + phase) * 0.08f * h;
                    AddLimb(b, prev, p, 0.012f * h, 0.01f * h, color);
                    if (k > 1) AddBlob(b, rng, p + dir * 0.03f * h, 0.05f * h, 0.3f, 0, color * 1.08f); // blade
                    prev = p;
                }
                AddBlob(b, rng, prev, 0.025f * h, 1f, 0, color * 1.15f); // gas float
            }
        }

        // Turf of seaweed: low lumps with a few short fronds
        static void AddAlgae(Builder b, System.Random rng, Vector3 root, float r)
        {
            var color = Shade(rng, L(AlgaeGreen));
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                var at = root + new Vector3(Range(rng, -1f, 1f), 0f, Range(rng, -1f, 1f)) * r;
                AddBlob(b, rng, at + Vector3.up * 0.3f * r, r * Range(rng, 0.5f, 0.9f), 0.6f, 0, color * Range(rng, 0.9f, 1.1f));
            }
            AddFrondRosette(b, rng, root, rng.Next(3, 6), r * 2.2f, r * 1.5f, r * 0.3f, r * 0.5f, color * 0.95f);
        }

        // Pink, knobbly crusts of coralline algae (or calcimicrobes)
        static void AddCoralline(Builder b, System.Random rng, Vector3 root, float r)
        {
            var color = Shade(rng, L(CorallinePink));
            for (int i = rng.Next(3, 7); i > 0; i--)
            {
                var at = root + new Vector3(Range(rng, -1.2f, 1.2f), 0f, Range(rng, -1.2f, 1.2f)) * r;
                AddBlob(b, rng, at, r * Range(rng, 0.4f, 0.8f), 0.45f, 0, color * Range(rng, 0.9f, 1.1f));
            }
        }

        // Stonewort: little jointed stems with whorls of branchlets
        static void AddCharophyte(Builder b, System.Random rng, Vector3 root, float h)
        {
            var color = Shade(rng, L(Charophyte));
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                var foot = root + new Vector3(Range(rng, -0.4f, 0.4f), 0f, Range(rng, -0.4f, 0.4f)) * h;
                var prev = foot;
                for (int k = 1; k <= 3; k++)
                {
                    var p = foot + Vector3.up * h * k / 3f;
                    AddLimb(b, prev, p, 0.03f * h, 0.025f * h, color);
                    for (int w = 0; w < 5; w++)
                    {
                        float a = w * Mathf.PI * 2f / 5f + k;
                        AddLimb(b, p, p + new Vector3(Mathf.Sin(a) * 0.25f, 0.12f, Mathf.Cos(a) * 0.25f) * h, 0.012f * h, 0.004f * h, color * 1.05f);
                    }
                    prev = p;
                }
            }
        }

        // Dripstone rising from the cave floor
        static void AddStalagmite(Builder b, System.Random rng, Vector3 root, float h)
        {
            var c = Color.Lerp(Dripstone, CaveRock, Range(rng, 0f, 0.6f));
            AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * h * 0.6f, 0.12f * h, 0.07f * h, Shade(rng, c, 0.05f));
            AddCone(b, rng, root + Vector3.up * h * 0.58f, 0.07f * h, h * 0.42f, Shade(rng, c * 1.05f, 0.05f));
        }

        // Where a stalactite and stalagmite met: a column, thick at both ends
        static void AddDripColumn(Builder b, System.Random rng, Vector3 root, float h)
        {
            var c = Shade(rng, Dripstone, 0.06f);
            AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * h * 0.5f, 0.11f * h, 0.05f * h, c);
            AddLimb(b, root + Vector3.up * h * 0.5f, root + Vector3.up * h, 0.05f * h, 0.12f * h, c * 0.95f);
        }

        // Roots reaching down from the surface, poking out of the soil
        static void AddRoots(Builder b, System.Random rng, Vector3 root, float size)
        {
            var color = Shade(rng, Root);
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                var dir = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a));
                var mid = root + dir * 0.05f * size + Vector3.up * 0.03f * size;
                var end = root + dir * Range(rng, 0.09f, 0.15f) * size - Vector3.up * 0.01f;
                AddLimb(b, root - Vector3.up * 0.01f, mid, 0.008f * size, 0.006f * size, color);
                AddLimb(b, mid, end, 0.006f * size, 0.002f * size, color);
            }
        }
    }
}
