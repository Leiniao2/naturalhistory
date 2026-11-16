using System.Linq;
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
        // density: how thick this tile's water-plant bed is (patchy across the map, see HexGrid.BuildUnderProps)
        public static Mesh CreateUnderDetail(System.Random rng, float size, UnderKind kind, PlantDefinition main, PlantDefinition second,
                                             IReadOnlyList<PlantDefinition> extras = null, float density = 1f, bool groundwater = false)
        {
            var b = new Builder();
            var taken = new List<Vector2>();
            float apothem = 0.8660254f * size;
            // Plants, algae and fungi (dense = true) come ~1.7× as many and a little closer
            // together, and reach slightly past the tile's edge so beds run on into the
            // neighbouring tiles instead of stopping at a bare seam.
            bool waterBed = kind is UnderKind.Seabed or UnderKind.DeepSeabed or UnderKind.Lakebed;
            List<Vector2> Spots(int min, int max, float gap, bool dense = false)
            {
                int count = rng.Next(min, max + 1);
                // Not Denser(): the old periods' density boost is for tiny early land plants; under water
                // the beds are already thick, and the boost made early seabeds needlessly heavy to draw.
                // Their plants still get the old periods' bigger size (AgeSize), so they stay visible.
                if (dense) { count = Mathf.RoundToInt(count * DenseCount * (waterBed ? WaterBedDensity * AgeWaterDensity * density : 1f)); gap *= DenseGap; }
                // spacing in step with the count, so the bed stays even from edge to edge
                if (dense && waterBed) gap /= Mathf.Sqrt(WaterBedDensity * AgeWaterDensity * density);
                var spots = HexScatter(rng, count, apothem * (dense ? 1.06f : 0.95f), gap * size, taken);
                taken.AddRange(spots);
                return spots;
            }
            Vector3 At(Vector2 p) => new(p.x, 0f, p.y);
            void AddUnderSpecies(PlantDefinition first, PlantDefinition other)
            {
                // giant Prototaxites trunks stand alone, one to three to a tile, not in clumps
                bool Giant(PlantDefinition d) => d.form == "Prototaxites";
                // fungi in caves and soil: a few clumps scattered over the floor, not a carpet
                // (the deep seabed's bacterial mats stay thick)
                List<Vector2> Many(int min, int max) => waterBed ? Spots(min, max, 0.11f, true) : Spots(Mathf.Max(1, min / 3), Mathf.Max(2, max / 3), 0.2f);
                // late periods: one cave or soil clump in five left out (AgeThin); water beds are thinned by AgeWaterDensity
                bool Keep(PlantDefinition d) => waterBed || Giant(d) || rng.NextDouble() < AgeThin;
                if (first != null)  foreach (var p in Giant(first) ? Spots(1, 3, 0.3f) : Many(6, 11)) if (Keep(first)) AddUnderPlant(b, rng, At(p), size, first, 1f);
                if (other != null) foreach (var p in Giant(other) ? Spots(1, 2, 0.3f) : Many(2, 5)) if (Keep(other)) AddUnderPlant(b, rng, At(p), size, other, 0.85f);
            }
            maxBlobDetail = 0;
            fineDetail = true;
            waterPlantScale = waterBed ? WaterPlantSize : 1f;
            stromatoliteTint = kind == UnderKind.Seabed ? SeaVeil : kind == UnderKind.Lakebed ? (groundwater ? Groundwater : LakeVeil) : Color.white;
            fineBlobRadius = 0.012f * size;
            skipPainted = waterBed; // mats, crusts and turf are in the floor texture there (CoverOf)

            switch (kind)
            {
                case UnderKind.Cave:
                    // no stalagmites, columns or crystal spikes: rounded rocks and pools keep the floor open
                    foreach (var p in Spots(3, 6, 0.14f))  AddRock(b, rng, At(p), size * Range(rng, 0.025f, 0.05f), Color.Lerp(Dripstone, CaveRock, Range(rng, 0.3f, 1f)));
                    foreach (var p in Spots(1, 2, 0.2f))   AddPond(b, rng, At(p) + Vector3.up * 0.004f, size * Range(rng, 0.07f, 0.12f), CavePool);
                    AddUnderSpecies(main, second); // cave fungi, glowing mushrooms, moulds
                    break;
                case UnderKind.Rock:
                    foreach (var p in Spots(3, 6, 0.14f)) AddRock(b, rng, At(p), size * Range(rng, 0.03f, 0.06f), Color.Lerp(Soil, CaveRock, Range(rng, 0f, 1f)));
                    foreach (var p in Spots(2, 4, 0.15f)) AddRoots(b, rng, At(p), size);
                    foreach (var p in Spots(2, 4, 0.1f))  AddPond(b, rng, At(p) + Vector3.up * 0.003f, size * Range(rng, 0.02f, 0.035f), Burrow); // burrow mouths
                    AddUnderSpecies(main, second); // soil fungi: mushrooms, truffles, mycelium, slime moulds
                    break;
                case UnderKind.DeepSeabed:
                    foreach (var p in Spots(3, 7, 0.12f)) AddRock(b, rng, At(p), size * Range(rng, 0.015f, 0.03f), Nodule); // manganese nodules
                    foreach (var p in Spots(1, 3, 0.15f)) AddRock(b, rng, At(p), size * Range(rng, 0.03f, 0.05f), SeabedStone);
                    AddUnderSpecies(main, second); // bacterial mats
                    break;
                default: // Seabed, Lakebed
                {
                    // A few big specimens of the tallest species first, then the rest around them
                    // at varied sizes, so a water tile reads as a mixed bed rather than one carpet.
                    var all = new List<PlantDefinition>();
                    if (main != null) all.Add(main);
                    if (second != null) all.Add(second);
                    if (extras != null) all.AddRange(extras);
                    if (all.Count > 0)
                    {
                        var hero = all.OrderByDescending(UnderStature).First();
                        foreach (var p in Spots(1, 3, 0.22f, true)) AddUnderPlant(b, rng, At(p), size, hero, Range(rng, 1.7f, 2.4f));
                    }
                    if (main != null)
                    {
                        bool big = UnderStature(main) >= 3f;
                        foreach (var p in Spots(big ? 6 : 10, big ? 10 : 16, big ? 0.13f : 0.1f, true)) AddUnderPlant(b, rng, At(p), size, main, Range(rng, 0.8f, 1.5f));
                    }
                    if (second != null)
                        foreach (var p in Spots(4, 7, 0.1f, true)) AddUnderPlant(b, rng, At(p), size, second, Range(rng, 0.8f, 1.35f));
                    if (extras != null)
                        foreach (var extra in extras)
                            foreach (var p in Spots(2, 4, 0.1f, true)) AddUnderPlant(b, rng, At(p), size, extra, Range(rng, 0.75f, 1.3f));
                    // a few low tufts of the smallest species between them (open seabed between plants is fine)
                    if (all.Count > 0)
                    {
                        var low = all.OrderBy(UnderStature).First();
                        foreach (var p in Spots(4, 8, 0.08f, true)) AddUnderPlant(b, rng, At(p), size, low, Range(rng, 0.5f, 0.8f));
                    }
                    foreach (var p in Spots(1, 4, 0.1f)) AddRock(b, rng, At(p), size * Range(rng, 0.02f, 0.045f), SeabedStone);
                    if (kind == UnderKind.Seabed)
                        foreach (var p in Spots(1, 4, 0.06f)) AddBlob(b, rng, At(p) + Vector3.up * 0.004f, size * 0.012f, 0.45f, 0, Shade(rng, Shell));
                    break;
                }
            }
            maxBlobDetail = 1;
            fineDetail = false;
            waterPlantScale = 1f;
            stromatoliteTint = Color.white;
            skipPainted = false;
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

        // Rough height class of a water plant's form, for picking the big specimens of a tile
        static float UnderStature(PlantDefinition p) => p.size * p.form switch
        {
            "Kelp" => 5f, "Ribbon" => 4f, "Lotus" => 3f, "Whorl" => 2.6f, "Feather" => 2.2f, "Rosette" => 2.2f,
            "Fingers" => 1.8f, "Tuft" => 1.8f, "Grape" => 1.6f, "SeaLettuce" => 1.6f, "Fan" => 1.5f, "Wineglass" => 1.4f,
            "Seagrass" => 1.8f, "Charophyte" => 1.6f, _ => 1f,
        };

        // Under-layer plants and fungi: how much more of them a tile holds, how much closer they
        // stand, and how much bigger they grow than their base shapes
        const float DenseCount = 1.7f, DenseGap = 0.8f, UnderPlantScale = 1.8f;

        // How much a water plant's form sways with the swell (0 = stays still)
        static float UnderSway(string form) => form switch
        {
            "Kelp" => 1f, "Ribbon" => 1f, "Seagrass" => 0.8f, "Feather" => 0.6f,
            _ => 0f,
        };

        static float PlantHeight(Builder b, int from, Vector3 root)
        {
            float top = 0f;
            for (int i = from; i < b.VertexCount; i++) top = Mathf.Max(top, b.Vertex(i).y - root.y);
            return top;
        }
        // Seabed, deep seabed and lakebed plant beds get this share of the count (caves and soil
        // keep theirs), times the period's AgeWaterDensity (up to 2.3× from the Paleogene on).
        const float WaterBedDensity = 0.75f;
        // Seabed and lakebed plants are grown this much bigger again (same count), so the beds read
        // as tall meadows and forests; caves' and soil's fungi keep their size. Set by CreateUnderDetail.
        const float WaterPlantSize = 1.4f;
        static float waterPlantScale = 1f;

        // The light veil of water over the seabed and lakebed in the under view (HexGrid.UnderTint);
        // the 3D stromatolites take it too, so they match the stromatolite floor they stand on
        public static readonly Color SeaVeil  = new(0.8f, 0.94f, 1.14f);
        public static readonly Color LakeVeil = new(0.88f, 0.98f, 1.06f);
        public static readonly Color Groundwater = new(0.42f, 0.76f, 0.98f); // lake-blue groundwater lakes under the land (HexGrid.Plateau)
        static Color stromatoliteTint = Color.white;

        // Simple, flat water plants (microbial and bacterial mats, coralline crusts, low algal turf) are
        // painted into the floor texture of seabed, deep seabed and lakebed tiles instead of being built
        // as props: they would only be a thin carpet of geometry. Set by CreateUnderDetail.
        static bool skipPainted;
        // (coralline crusts are no longer painted, HexGrid.Under.FloorCover: they stand as props again)
        static bool Painted(string form) => form is "Mat" or "Algae";

        // Fungi, lichens and slime moulds of caves and soil are drawn this much bigger (Prototaxites
        // has its own size)
        const float FungusScale = 2f;
        static bool Fungal(string form) => form is "Mushroom" or "Toadstool" or "GlowCap" or "Inkcap" or "Funnel" or "Bracket"
            or "Puffball" or "Earthstar" or "Lattice" or "CoralFungus" or "Cup" or "Morel" or "Mycelium" or "SlimeMold"
            or "Stalks" or "Lichen" or "Truffle";

        // The floor texture a water tile gets for its plants ("BacterialMat", "MicrobialMat",
        // "Coralline", "AlgalTurf", "Stromatolite"; null = the plain floor): from its main species if that is a painted
        // form, else its second. HexGrid.Under loads Materials/Under/Under{kind}{cover}.
        // meadow: the tile lies in a meadow region (HexGrid.Under.IsMeadow) — if nothing above
        // applies, its water plants are painted into the floor as a meadow ("SeagrassMeadow",
        // "KelpBed", "SeaweedMeadow"; lakebed "WaterweedMeadow") and only a few stand as 3D plants.
        public static string CoverOf(UnderKind kind, PlantDefinition main, PlantDefinition second, bool meadow = false)
        {
            // stromatolites make the whole floor, so they win over a mat or turf
            if (kind is UnderKind.Seabed or UnderKind.Lakebed && (UnderView.IsFloor(main) || UnderView.IsFloor(second))) return "Stromatolite";
            foreach (var p in new[] { main, second })
            {
                if (p == null || !Painted(p.form)) continue;
                string cover = (p.form, kind) switch
                {
                    ("Mat", UnderKind.DeepSeabed)                 => "BacterialMat",
                    ("Mat", UnderKind.Seabed or UnderKind.Lakebed) => "MicrobialMat",
                    ("Coralline", UnderKind.Seabed)               => "Coralline",
                    ("Algae", UnderKind.Seabed or UnderKind.Lakebed) => "AlgalTurf",
                    _ => null,
                };
                if (cover != null) return cover;
            }
            if (!meadow || main == null) return null;
            if (kind == UnderKind.Lakebed) return "WaterweedMeadow";
            if (kind != UnderKind.Seabed) return null;
            return main.form switch
            {
                "Seagrass" => "SeagrassMeadow",
                "Kelp"     => "KelpBed",
                _          => "SeaweedMeadow",
            };
        }

        public static bool IsMeadowCover(string cover) => cover is "SeagrassMeadow" or "KelpBed" or "SeaweedMeadow" or "WaterweedMeadow";

        static void AddUnderPlant(Builder b, System.Random rng, Vector3 root, float size, PlantDefinition plant, float scale)
        {
            if (skipPainted && Painted(plant.form)) return; // painted into the floor instead
            // stromatolites are mostly painted into the floor (CoverOf): only one in five stands as a 3D dome
            if (plant.form == "Stromatolite" && rng.NextDouble() < 0.8) return;
            float m = plant.size * scale * UnderPlantScale * waterPlantScale * Mathf.Lerp(1f, AgeSize, 0.6f) * Range(rng, 0.8f, 1.15f);
            if (Fungal(plant.form)) m *= FungusScale; // mushrooms, brackets, moulds... were too small to see
            leafTint = plant.Tint;
            int from = b.VertexCount;
            switch (plant.form)
            {
                case "Seagrass":     AddSeagrass(b, rng, root, size * 0.09f * m); break;
                case "Kelp":         AddKelp(b, rng, root, size * 0.35f * m); break;
                case "Coralline":    AddCoralline(b, rng, root, size * 0.04f * m); break;
                case "Charophyte":   AddCharophyte(b, rng, root, size * 0.08f * m); break;
                case "Stromatolite": AddStromatolites(b, rng, root, size * 0.04f * m, stromatoliteTint); break;
                default:
                    if (!AddUnderFlora(b, rng, root, size, plant, m)) AddAlgae(b, rng, root, size * 0.035f * m); // fungi and more water plants: UnderFlora.cs
                    break;
            }
            // only tall, slender plants sway in the water (MapFeature.shader ApplySway); short ones stay still
            float sway = UnderSway(plant.form);
            if (sway > 0f && PlantHeight(b, from, root) >= 0.08f * size) MakeFlexible(b, from, root, sway, size);
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
