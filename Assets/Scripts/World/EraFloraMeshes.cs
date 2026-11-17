using System.Collections.Generic;
using NaturalHistory.Core;
using UnityEngine;

namespace NaturalHistory.World
{
    // Period-specific plants for the map props (see EraFlora for which terrain each period has).
    // Same low-poly, vertex-coloured style as the rest of MapFeatureMeshes. From the Paleogene on,
    // forests, reefs and oases use the modern meshes.
    public static partial class MapFeatureMeshes
    {
        static readonly Color FernGreen      = new(0.25f, 0.50f, 0.20f);
        static readonly Color FernDark       = new(0.14f, 0.34f, 0.16f);
        static readonly Color FernLight      = new(0.45f, 0.62f, 0.26f);
        static readonly Color FernTrunk      = new(0.26f, 0.19f, 0.13f);
        static readonly Color CycadTrunk     = new(0.44f, 0.34f, 0.22f);
        static readonly Color CycadLeaf      = new(0.16f, 0.36f, 0.15f);
        static readonly Color CycadCone      = new(0.70f, 0.45f, 0.18f);
        static readonly Color LycopsidBark   = new(0.36f, 0.38f, 0.28f);
        static readonly Color LycopsidLeaf   = new(0.20f, 0.40f, 0.16f);
        static readonly Color CalamitesStem  = new(0.40f, 0.48f, 0.24f);
        static readonly Color Horsetail      = new(0.38f, 0.52f, 0.22f);
        static readonly Color Moss           = new(0.30f, 0.46f, 0.16f);
        static readonly Color MossLight      = new(0.46f, 0.56f, 0.20f);
        static readonly Color Sporangium     = new(0.62f, 0.45f, 0.20f);
        static readonly Color Rhynia         = new(0.42f, 0.54f, 0.24f);
        static readonly Color Glossopteris   = new(0.32f, 0.42f, 0.18f);
        static readonly Color GinkgoLeaf     = new(0.50f, 0.62f, 0.24f);
        static readonly Color AraucariaGreen = new(0.12f, 0.30f, 0.16f);
        static readonly Color CordaitesLeaf  = new(0.18f, 0.36f, 0.16f);
        static readonly Color Stromatolite   = new(0.55f, 0.50f, 0.42f);
        static readonly Color MatOlive       = new(0.36f, 0.36f, 0.22f);
        static readonly Color MatPurple      = new(0.36f, 0.28f, 0.26f);
        static readonly Color BarrenGrey     = new(0.48f, 0.46f, 0.44f);
        static readonly Color BarrenRed      = new(0.58f, 0.42f, 0.34f);
        static readonly Color SwampWater     = new(0.12f, 0.18f, 0.12f);
        static readonly Color Archaeocyath   = new(0.86f, 0.78f, 0.62f);
        static readonly Color[] PaleozoicReefColors =
        {
            new(0.85f, 0.70f, 0.50f), new(0.75f, 0.55f, 0.70f), new(0.90f, 0.80f, 0.60f), new(0.70f, 0.45f, 0.35f),
        };

        // (needle, tip) colours for the conifers of each period
        static readonly (Color, Color) Walchia = (new(0.16f, 0.34f, 0.20f), new(0.28f, 0.46f, 0.26f));
        static readonly (Color, Color) Voltzia = (new(0.18f, 0.36f, 0.22f), new(0.30f, 0.48f, 0.28f));
        static readonly (Color, Color) Redwood = (new(0.10f, 0.28f, 0.18f), new(0.20f, 0.40f, 0.24f));
        static readonly (Color, Color) Magnolia = (new(0.18f, 0.40f, 0.18f), new(0.32f, 0.54f, 0.22f));

        // Leaf colour multiplier of the plant being built (PlantDefinition.tint); white otherwise
        static Color leafTint = Color.white;
        static Color L(Color c) => c * leafTint;

        // ---- Forests, reefs and oases ----

        // A stand of the period's trees with undergrowth, or null before the first forests (Devonian).
        public static Mesh CreateEraForest(System.Random rng, float size, GeologicalAge age, TerrainFeature feature)
        {
            if (age < GeologicalAge.Devonian) return null;
            if (age >= GeologicalAge.Paleogene)
                return feature == TerrainFeature.Jungle ? CreateJungle(rng, size) : CreateForest(rng, size, feature == TerrainFeature.ConiferForest);

            bool conifer = feature == TerrainFeature.ConiferForest, jungle = feature == TerrainFeature.Jungle;
            var b = new Builder { Foliage = true }; // plants: rough, speckled leaf clumps
            float spread = 0.5f * size;
            var trees = Scatter(rng, jungle ? rng.Next(8, 12) : rng.Next(5, 8), spread, (jungle ? 0.15f : 0.2f) * size, new List<Vector2>());
            foreach (var p in trees)
            {
                float s = size * Range(rng, 0.85f, 1.1f) * Mathf.Lerp(1.1f, 0.8f, p.magnitude / spread);
                AddEraTree(b, rng, new Vector3(p.x, 0f, p.y), s, age, conifer, jungle);
            }
            foreach (var p in Scatter(rng, rng.Next(3, 7), 0.62f * size, 0.1f * size, trees))
                AddUndergrowth(b, rng, new Vector3(p.x, 0f, p.y), size, age);
            return b.ToMesh($"{age}{feature}");
        }

        static void AddEraTree(Builder b, System.Random rng, Vector3 root, float s, GeologicalAge age, bool conifer, bool jungle)
        {
            double r = rng.NextDouble();
            switch (age)
            {
                case GeologicalAge.Devonian:
                    if (jungle) { if (r < 0.7) AddWattieza(b, rng, root, s); else AddLepidodendron(b, rng, root, s * 0.6f); }
                    else if (r < 0.8) AddArchaeopteris(b, rng, root, s);
                    else AddWattieza(b, rng, root, s);
                    break;
                case GeologicalAge.Carboniferous:
                    if (conifer)     AddCordaites(b, rng, root, s);
                    else if (jungle) { if (r < 0.45) AddLepidodendron(b, rng, root, s); else if (r < 0.65) AddSigillaria(b, rng, root, s);
                                       else if (r < 0.85) AddCalamites(b, rng, root, s); else AddTreeFern(b, rng, root, s); }
                    else             { if (r < 0.35) AddLepidodendron(b, rng, root, s); else if (r < 0.6) AddTreeFern(b, rng, root, s);
                                       else if (r < 0.8) AddSigillaria(b, rng, root, s); else AddCordaites(b, rng, root, s); }
                    break;
                case GeologicalAge.Permian:
                    if (conifer)     AddConifer(b, rng, root, s, Walchia.Item1, Walchia.Item2);
                    else if (jungle) { if (r < 0.45) AddTreeFern(b, rng, root, s); else if (r < 0.7) AddCycad(b, rng, root, s * 1.4f); else AddCalamites(b, rng, root, s); }
                    else if (r < 0.75) AddGlossopteris(b, rng, root, s);
                    else AddConifer(b, rng, root, s, Walchia.Item1, Walchia.Item2);
                    break;
                case GeologicalAge.Triassic:
                    if (conifer)     AddConifer(b, rng, root, s, Voltzia.Item1, Voltzia.Item2);
                    else if (jungle) { if (r < 0.55) AddTreeFern(b, rng, root, s); else AddCycad(b, rng, root, s * 1.4f); }
                    else             { if (r < 0.4) AddConifer(b, rng, root, s, Voltzia.Item1, Voltzia.Item2); else if (r < 0.7) AddGinkgo(b, rng, root, s); else AddCycad(b, rng, root, s * 1.4f); }
                    break;
                case GeologicalAge.Jurassic:
                    if (conifer)     { if (r < 0.6) AddAraucaria(b, rng, root, s); else AddConifer(b, rng, root, s, Redwood.Item1, Redwood.Item2); }
                    else if (jungle) { if (r < 0.6) AddTreeFern(b, rng, root, s * 1.1f); else AddCycad(b, rng, root, s * 1.5f); }
                    else             { if (r < 0.4) AddAraucaria(b, rng, root, s); else if (r < 0.65) AddGinkgo(b, rng, root, s); else AddTreeFern(b, rng, root, s * 1.1f); }
                    break;
                default: // Cretaceous: flowering trees spread among the conifers
                    if (conifer)     AddConifer(b, rng, root, s, Redwood.Item1, Redwood.Item2);
                    else if (jungle) { if (r < 0.5) AddBroadleaf(b, rng, root, s, Magnolia.Item1, Magnolia.Item2); else if (r < 0.75) AddTreeFern(b, rng, root, s); else AddPalm(b, rng, root, s * 1.1f); }
                    else             { if (r < 0.55) AddBroadleaf(b, rng, root, s, Magnolia.Item1, Magnolia.Item2); else if (r < 0.8) AddConifer(b, rng, root, s, Redwood.Item1, Redwood.Item2); else AddGinkgo(b, rng, root, s); }
                    break;
            }
        }

        static void AddUndergrowth(Builder b, System.Random rng, Vector3 root, float size, GeologicalAge age)
        {
            switch (age)
            {
                case GeologicalAge.Devonian:
                    if (rng.NextDouble() < 0.5) AddMossCushion(b, rng, root, size * Range(rng, 0.03f, 0.05f));
                    else AddHorsetails(b, rng, root, size * 0.07f, L(Rhynia));
                    break;
                case GeologicalAge.Carboniferous:
                    if (rng.NextDouble() < 0.5) AddHorsetails(b, rng, root, size * 0.1f, L(Horsetail));
                    else AddGroundFern(b, rng, root, size * 0.09f);
                    break;
                case GeologicalAge.Jurassic:
                    AddGroundFern(b, rng, root, size * Range(rng, 0.11f, 0.15f));
                    break;
                default:
                    AddGroundFern(b, rng, root, size * Range(rng, 0.07f, 0.1f));
                    break;
            }
        }

        // Before the Middle Triassic there were no modern (scleractinian) corals: Cambrian reefs are
        // stromatolites and archaeocyathid sponges, later Paleozoic ones tabulate and rugose corals,
        // sponges and crinoid meadows.
        public static Mesh CreateEraReef(System.Random rng, float size, GeologicalAge age)
        {
            if (age >= GeologicalAge.Triassic) return CreateReef(rng, size);
            var b = new Builder();
            foreach (var p in Scatter(rng, rng.Next(7, 12), 0.6f * size, 0.12f * size, new List<Vector2>()))
            {
                var root = new Vector3(p.x, -0.02f, p.y);
                float r  = size * Range(rng, 0.05f, 0.09f);
                if (age <= GeologicalAge.Cambrian) // Ediacaran Cloudina reefs look much the same
                {
                    if (rng.NextDouble() < 0.6) AddBlob(b, rng, root + Vector3.up * r * 0.3f, r, 0.6f, 0, Shade(rng, Stromatolite));
                    else for (int k = rng.Next(2, 5); k > 0; k--) AddCup(b, rng, root, r * 1.6f, Shade(rng, Archaeocyath));
                    continue;
                }
                var color = Shade(rng, PaleozoicReefColors[rng.Next(PaleozoicReefColors.Length)]);
                switch (rng.Next(4))
                {
                    case 0: AddBlob(b, rng, root + Vector3.up * r * 0.3f, r, 0.5f, 0, color); break; // tabulate coral head
                    case 1: for (int k = rng.Next(2, 5); k > 0; k--) AddCup(b, rng, root, r * 1.4f, color); break; // rugose horn corals
                    case 2: AddCrinoid(b, rng, root, r * 2.6f, color); break;
                    default: AddCup(b, rng, root, r * 2f, color * 1.05f); break; // vase sponge
                }
            }
            return b.ToMesh($"{age}Reef");
        }

        // A spring-fed pool ringed with whatever grew by water in the period (palms from the Cretaceous).
        public static Mesh CreateEraOasis(System.Random rng, float size, GeologicalAge age)
        {
            if (age >= GeologicalAge.Cretaceous) return CreateOasis(rng, size);
            var b = new Builder { Foliage = true }; // plants: rough, speckled leaf clumps
            var center = new Vector3(Range(rng, -0.06f, 0.06f) * size, 0.004f, Range(rng, -0.06f, 0.06f) * size);
            AddOasisShore(b, rng, center, 0.24f * size, size, green: age >= GeologicalAge.Devonian);

            int plants  = rng.Next(3, 6);
            float angle = Range(rng, 0f, 360f);
            for (int i = 0; i < plants; i++, angle += 360f / plants + Range(rng, -30f, 30f))
            {
                float a = angle * Mathf.Deg2Rad, d = Range(rng, 0.32f, 0.45f) * size;
                var at  = center + new Vector3(Mathf.Sin(a) * d, -0.004f, Mathf.Cos(a) * d);
                switch (age)
                {
                    case < GeologicalAge.Devonian:
                        if (i % 2 == 0) AddMatPatch(b, rng, at, size * 0.07f); else AddStromatolites(b, rng, at, size * 0.035f);
                        break;
                    case GeologicalAge.Devonian:
                        if (i % 2 == 0) AddHorsetails(b, rng, at, size * 0.08f, L(Rhynia)); else AddMossCushion(b, rng, at, size * 0.045f);
                        break;
                    case GeologicalAge.Carboniferous:
                        if (i % 2 == 0) AddCalamites(b, rng, at, size * 0.7f); else AddTreeFern(b, rng, at, size * 0.8f);
                        break;
                    default:
                        if (i % 2 == 0) AddCycad(b, rng, at, size * 1.2f); else AddTreeFern(b, rng, at, size * 0.85f);
                        break;
                }
            }
            return b.ToMesh($"{age}Oasis");
        }

        // ---- Ground details ----

        // Small props for a terrain tile in a period, or null if it has none. Falls back to the
        // modern details (CreateDetail) where nothing differs.
        public static Mesh CreateEraDetail(System.Random rng, float size, TerrainKind kind, GeologicalAge age)
        {
            var b = new Builder { Foliage = true }; // plants: rough, speckled leaf clumps
            var taken = new List<Vector2>();
            // older periods: more and bigger of their small plants and mats, spread wider (AgeBoost)
            var (grow, dense) = AgeBoost(age);
            List<Vector2> Spots(int min, int max, float gap)
            {
                int count = Mathf.RoundToInt(rng.Next(min, max + 1) * (kind == TerrainKind.Barren ? 1f : dense));
                var spots = Scatter(rng, count, (dense > 1.2f ? 0.8f : 0.62f) * size, gap * size, taken);
                taken.AddRange(spots);
                return spots;
            }
            Vector3 At(Vector2 p) => new(p.x, 0f, p.y);
            void Flexible(Vector3 root, float flex, System.Action add)
            {
                int from = b.VertexCount;
                add();
                MakeFlexible(b, from, root, flex, size);
            }

            switch (kind)
            {
                case TerrainKind.Barren:
                    foreach (var p in Spots(2, 5, 0.12f))
                        AddRock(b, rng, At(p), size * Range(rng, 0.03f, 0.07f), Color.Lerp(BarrenGrey, BarrenRed, Range(rng, 0f, 1f)));
                    foreach (var p in Spots(2, 5, 0.06f))
                        AddRock(b, rng, At(p), size * Range(rng, 0.012f, 0.022f), Color.Lerp(BarrenGrey, BarrenRed, Range(rng, 0f, 1f)));
                    break;
                case TerrainKind.MicrobialMat:
                    foreach (var p in Spots(2, 4, 0.15f)) AddMatPatch(b, rng, At(p), size * grow * Range(rng, 0.05f, 0.09f));
                    foreach (var p in Spots(1, 3, 0.15f)) AddStromatolites(b, rng, At(p), size * grow * Range(rng, 0.03f, 0.05f));
                    break;
                case TerrainKind.Mossland:
                    foreach (var p in Spots(4, 7, 0.1f)) AddMossCushion(b, rng, At(p), size * grow * Range(rng, 0.03f, 0.055f));
                    if (age >= GeologicalAge.Silurian)
                        foreach (var p in Spots(2, 4, 0.08f)) Flexible(At(p), 1f, () => AddCooksonia(b, rng, At(p), size * grow * 0.06f));
                    if (age == GeologicalAge.Devonian)
                        foreach (var p in Spots(1, 3, 0.1f)) Flexible(At(p), 0.8f, () => AddHorsetails(b, rng, At(p), size * grow * 0.07f, L(Rhynia)));
                    break;
                case TerrainKind.FernPrairie:
                    // Jurassic fern prairies: ferns as tall as a person, the "grassland" of the dinosaurs
                    float fern = age == GeologicalAge.Jurassic ? 0.15f : age is GeologicalAge.Triassic or GeologicalAge.Cretaceous ? 0.1f : 0.085f;
                    foreach (var p in Spots(3, 6, fern * 1.4f)) Flexible(At(p), 0.6f, () => AddGroundFern(b, rng, At(p), size * fern * Range(rng, 0.8f, 1.2f)));
                    foreach (var p in Spots(0, 2, 0.1f)) Flexible(At(p), 0.8f, () => AddHorsetails(b, rng, At(p), size * 0.08f, L(Horsetail)));
                    if (age >= GeologicalAge.Permian && rng.NextDouble() < 0.35)
                        foreach (var p in Spots(1, 1, 0.2f)) AddCycad(b, rng, At(p), size * Range(rng, 0.7f, 1f));
                    if (age is GeologicalAge.Carboniferous or GeologicalAge.Jurassic && rng.NextDouble() < 0.25)
                        foreach (var p in Spots(1, 1, 0.25f)) AddTreeFern(b, rng, At(p), size * Range(rng, 0.6f, 0.8f));
                    if (age == GeologicalAge.Cretaceous) // the first flowers
                        foreach (var p in Spots(0, 3, 0.06f))
                            AddBlob(b, rng, At(p) + Vector3.up * 0.02f * size, 0.016f * size, 1f, 0, FlowerColors[rng.Next(FlowerColors.Length)]);
                    break;
                case TerrainKind.CoalSwamp:
                    foreach (var p in Spots(1, 2, 0.18f)) AddPond(b, rng, At(p) + Vector3.up * 0.004f, size * Range(rng, 0.06f, 0.1f), SwampWater);
                    foreach (var p in Spots(2, 4, 0.12f)) AddHorsetails(b, rng, At(p), size * 0.13f, L(Horsetail));
                    if (rng.NextDouble() < 0.4)
                        foreach (var p in Spots(1, 1, 0.25f)) AddLepidodendron(b, rng, At(p), size * 0.55f);
                    break;
                // Reeds, sedges and water lilies are flowering plants
                case TerrainKind.Wetland when age < GeologicalAge.Cretaceous:
                    foreach (var p in Spots(3, 5, 0.12f)) AddHorsetails(b, rng, At(p), size * 0.1f, L(Horsetail));
                    foreach (var p in Spots(1, 3, 0.12f)) AddGroundFern(b, rng, At(p), size * 0.08f);
                    break;
                case TerrainKind.Rainforest when age < GeologicalAge.Paleogene:
                    foreach (var p in Spots(3, 5, 0.14f)) AddGroundFern(b, rng, At(p), size * 0.11f);
                    foreach (var p in Spots(0, 2, 0.2f)) AddCycad(b, rng, At(p), size * 0.8f);
                    break;
                case TerrainKind.Hill when age < GeologicalAge.Paleogene:
                    foreach (var p in Spots(2, 4, 0.15f)) AddRock(b, rng, At(p), size * Range(rng, 0.04f, 0.07f), Rock);
                    foreach (var p in Spots(2, 4, 0.12f)) AddGroundFern(b, rng, At(p), size * 0.07f);
                    break;
                // Paleogene open country: herbs and shrubs, grasses only just appearing
                case TerrainKind.Plain when age == GeologicalAge.Paleogene:
                    foreach (var p in Spots(2, 4, 0.12f))
                        AddBlob(b, rng, At(p) + Vector3.up * 0.01f * size, size * Range(rng, 0.035f, 0.05f), 0.7f, 0, Shade(rng, Shrub));
                    foreach (var p in Spots(1, 3, 0.1f)) AddTuft(b, rng, At(p), size, Grass);
                    foreach (var p in Spots(0, 3, 0.06f))
                        AddBlob(b, rng, At(p) + Vector3.up * 0.02f * size, 0.018f * size, 1f, 0, FlowerColors[rng.Next(FlowerColors.Length)]);
                    break;
                default:
                    return CreateDetail(rng, size, kind);
            }
            return b.ToMesh($"{age}{kind}Detail");
        }

        // ---- Plant species (plants.json) ----

        // Highest icosphere detail leaf clumps may use (open ground drops to the 20-face version;
        // forest stands keep 80 faces so crowns read as round, not boxy)
        static int maxBlobDetail = 1;

        // Blobs smaller than this use the 20-face version (smooth shading hides it on small clumps);
        // set in forest stands, where thousands of clumps would otherwise cost millions of triangles
        static float smallBlobRadius = 0f;

        // Fine detail for the under layer's water plants and fungi: they are grown large (more so
        // in early ages, see AgeSize) and seen close up, where the low-poly shapes read as a mosaic.
        // Balls become 80- or 320-face spheres, stems round 10-sided tubes, fronds and caps smooth
        // curves. Stones stay angular. Set by CreateUnderDetail while it builds a tile.
        static bool fineDetail;
        static float fineBlobRadius; // balls at least this big get the 320-face sphere

        // A dense stand filling the whole hex out to its edges, so neighbouring forest tiles run into
        // each other: mostly the dominant canopy species, some of the second (which neighbouring
        // regions tend to share, softening the change), with understory between the trunks. The
        // stand is hex-shaped, so HexGrid only turns it by multiples of 60°.
        public static Mesh CreatePlantStand(System.Random rng, float size, PlantDefinition canopy, PlantDefinition canopy2, PlantDefinition under,
                                             PlantDefinition fungus = null)
        {
            var b = new Builder { Foliage = true }; // plants: rough, speckled leaf clumps
            bool dense = canopy.form is "Palm" or "TreeFern" or "Calamites" or "Bamboo" or "Cycad" or "Mangrove" or "Lycopsid" or "Sigillaria";
            float apothem = 0.8660254f * size;
            smallBlobRadius = 0.09f * size;
            // fewer, bigger trees, so each one reads as a tree with its own crown, blossom and fruit;
            // the one nearest the middle is a big old tree of the dominant species
            var trees = HexScatter(rng, Thinner(dense ? rng.Next(18, 24) : rng.Next(12, 16)), apothem * 0.95f, (dense ? 0.15f : 0.2f) * size * LandGap, new List<Vector2>());
            int feature = 0;
            for (int i = 1; i < trees.Count; i++) if (trees[i].sqrMagnitude < trees[feature].sqrMagnitude) feature = i;
            for (int i = 0; i < trees.Count; i++)
            {
                var p = trees[i];
                var plant = i != feature && canopy2 != null && rng.NextDouble() < 0.3 ? canopy2 : canopy;
                float s = size * plant.size * (dense ? Range(rng, 0.75f, 1f) : Range(rng, 0.85f, 1.15f)) * (i == feature ? 1.35f : 1f);
                int from = b.VertexCount;
                AddCanopyPlant(b, rng, new Vector3(p.x, 0f, p.y), s, plant);
                b.SinkBase(from, 0.02f * size, 0.12f * size);
            }
            if (under != null)
                foreach (var p in HexScatter(rng, Denser(rng.Next(10, 16)), apothem * 0.97f, 0.08f * size * LandGap, trees))
                {
                    int from = b.VertexCount;
                    AddGroundPlant(b, rng, new Vector3(p.x, 0f, p.y), size, under, 0.8f);
                    b.SinkBase(from, 0.005f * size, 0.04f * size);
                }
            AddLandFungi(b, rng, size, fungus, trees); // the odd tile (LandFungi.cs)
            smallBlobRadius = 0f;
            return b.ToMesh($"Stand_{canopy.id}_{canopy2?.id}_{under?.id}");
        }

        // Open ground covering the whole hex: many clumps of the main species, fewer of the second,
        // and the terrain's stones.
        public static Mesh CreatePlantGround(System.Random rng, float size, PlantDefinition main, PlantDefinition second, TerrainKind kind,
                                             IReadOnlyList<PlantDefinition> extras = null, bool sparse = false, PlantDefinition fungus = null)
        {
            var b = new Builder { Foliage = true }; // plants: rough, speckled leaf clumps
            var taken = new List<Vector2>();
            float apothem = 0.8660254f * size;
            bool big = main.form is "Cactus" or "Cycad" or "Bennettitalean" or "Succulent" or "Shrub";
            maxBlobDetail = 0;
            void Plant(PlantDefinition plant, int min, int max, float gap, float scale)
            {
                var spots = HexScatter(rng, Denser(rng.Next(min, max + 1)), apothem * 0.96f, gap * size * LandGap * Mathf.Sqrt(HerbScale) * Mathf.Lerp(1f, AgeSize, 0.5f) / Mathf.Max(AgeDensity, 1f), taken);
                taken.AddRange(spots);
                foreach (var p in spots)
                {
                    int from = b.VertexCount;
                    AddGroundPlant(b, rng, new Vector3(p.x, 0f, p.y), size, plant, scale * Range(rng, 0.85f, 1.1f));
                    b.SinkBase(from, 0.005f * size, 0.04f * size);
                }
            }
            if (sparse) Plant(main, big ? 2 : 3, big ? 4 : 6, 0.25f, 1f); // a thinly planted region: a few, well apart
            else if (big) Plant(main, 6, 10, 0.16f, 1f);
            else     Plant(main, 14, 22, 0.09f, 0.95f);
            if (second != null) Plant(second, 4, 8, 0.1f, 0.9f);
            if (extras != null) foreach (var extra in extras) Plant(extra, 2, 4, 0.1f, Range(rng, 0.75f, 1.05f)); // a few others mixed in

            var stone = kind switch
            {
                TerrainKind.Desert => Sandstone,
                TerrainKind.Barren => Color.Lerp(BarrenGrey, BarrenRed, Range(rng, 0f, 1f)),
                TerrainKind.Tundra => Lichen,
                _                  => Rock,
            };
            if (kind is TerrainKind.Desert or TerrainKind.Barren or TerrainKind.Hill or TerrainKind.Tundra or TerrainKind.Steppe)
                foreach (var p in HexScatter(rng, rng.Next(2, 5), apothem * 0.9f, 0.1f * size, taken))
                    AddRock(b, rng, new Vector3(p.x, 0f, p.y), size * Range(rng, 0.025f, 0.05f), stone);
            AddLandFungi(b, rng, size, fungus, taken); // the odd tile (LandFungi.cs)
            maxBlobDetail = 1;
            return b.ToMesh($"Ground_{main.id}_{second?.id}");
        }

        // Up to `count` points inside a pointy-top hexagon with the given apothem (centre to edge),
        // each at least minGap from the others and from `taken`.
        // Older periods' plants are small (mosses, Cooksonia, Rhynia, early ferns) and would be hard
        // to see at map scale, so meshes built for them grow their plants bigger (AgeSize) and more
        // of them (AgeDensity); from the Jurassic on there are half as many. Set by PlantPlanner while
        // it builds a period's meshes.
        static float AgeSize = 1f, AgeDensity = 1f;
        public static void SetAgeBoost(GeologicalAge age)
        {
            (AgeSize, AgeDensity) = AgeBoost(age);
            AgeWaterDensity = WaterBoost(age);
            AgeWaterSize = age == GeologicalAge.Cretaceous ? 1.5f : 1f;
            AgeThin = age >= GeologicalAge.Cretaceous ? 0.8f : 1f;
        }

        // Cave and soil fungi in the late periods: one clump in five left out (UnderMeshes)
        static float AgeThin = 1f;

        // Seabed and lakebed beds thicken through time as marine plants diversify: thin early algal
        // turfs, Mesozoic seagrass and kelp beds, dense modern meadows and forests (UnderMeshes).
        static float AgeWaterDensity = 1f;
        // Cretaceous seagrasses and waterweeds are grown half as big again, so the young flowering-plant
        // meadows stand out (UnderMeshes)
        static float AgeWaterSize = 1f;
        static float WaterBoost(GeologicalAge age) => age switch
        {
            // later periods 20% sparser than they were (1.3 / 1.6 / 1.9 / 2.3): the beds stay full
            // but lighter to draw, and many of their tiles are painted meadows anyway (HexGrid.Under)
            <= GeologicalAge.Silurian   => 1f,
            <= GeologicalAge.Permian    => 1.04f,
            <= GeologicalAge.Jurassic   => 1.28f,
            GeologicalAge.Cretaceous    => 0.98f, // the last periods twice 20% sparser (were 1.52 / 1.84, then 1.22 / 1.47):
            _                           => 1.18f, // their seas are large and more of their beds are painted meadows
        };
        static (float size, float density) AgeBoost(GeologicalAge age) => age switch
        {
            <= GeologicalAge.Silurian      => (2.0f, 1.6f),
            GeologicalAge.Devonian         => (1.7f, 1.5f),
            GeologicalAge.Carboniferous    => (1.35f, 1.3f),
            GeologicalAge.Permian          => (1.25f, 1.2f),
            GeologicalAge.Triassic         => (1.1f, 1.1f),
            _                              => (1f, 0.5f), // Jurassic on: plants are big enough to see, so half as many
        };
        // Land tiles in every period: 1.5x the trees, plants and flowers, packed
        // a little closer so they all fit in the hex
        const float LandDensity = 1.5f;
        static readonly float LandGap = 1f / Mathf.Sqrt(LandDensity);
        static int Denser(int count) => Mathf.RoundToInt(count * AgeDensity * LandDensity);
        // trees only ever get fewer than the base count from the age (later periods), never more
        static int Thinner(int count) => Mathf.Max(1, Mathf.RoundToInt(count * Mathf.Min(AgeDensity, 1f) * LandDensity));

        static List<Vector2> HexScatter(System.Random rng, int count, float apothem, float minGap, List<Vector2> taken)
        {
            var placed = new List<Vector2>();
            float gapSq = minGap * minGap, radius = apothem / 0.8660254f;
            for (int tries = 0; tries < count * 15 && placed.Count < count; tries++)
            {
                var p = new Vector2(Range(rng, -apothem, apothem), Range(rng, -radius, radius));
                bool inside = true;
                for (int e = 0; e < 3 && inside; e++) // edge normals at 30°, 90°, 150° (and their opposites)
                {
                    float a = (60f * e + 30f) * Mathf.Deg2Rad;
                    inside = Mathf.Abs(p.x * Mathf.Sin(a) + p.y * Mathf.Cos(a)) <= apothem;
                }
                if (!inside) continue;
                if (placed.Exists(q => (q - p).sqrMagnitude < gapSq) || taken.Exists(q => (q - p).sqrMagnitude < gapSq)) continue;
                placed.Add(p);
            }
            return placed;
        }

        // One tree of a canopy species; `s` ≈ cell size × the species' size
        // Trees and other canopy plants are drawn this much taller than their width would make them
        const float WoodyStretch = 1.2f;

        static void AddCanopyPlant(Builder b, System.Random rng, Vector3 root, float s, PlantDefinition plant)
        {
            int from = b.VertexCount;
            leafTint = plant.Tint;
            hasCrown = TryColor(plant.crown, out crownColor); // all-pink, red or purple crowns (PlantShapes.cs)
            switch (plant.form)
            {
                case "Lycopsid":       AddLepidodendron(b, rng, root, s); break;
                case "Sigillaria":     AddSigillaria(b, rng, root, s); break;
                case "Calamites":      AddCalamites(b, rng, root, s); break;
                case "TreeFern":       AddTreeFern(b, rng, root, s); break;
                case "Cycad":          AddCycad(b, rng, root, s * 1.4f); break;
                case "Bennettitalean": AddBennettitalean(b, rng, root, s * 1.4f); break;
                case "Araucaria":      AddAraucaria(b, rng, root, s); break;
                case "Ginkgo":         AddGinkgo(b, rng, root, s); break;
                case "Glossopteris":   AddGlossopteris(b, rng, root, s); break;
                case "Cordaites":      AddCordaites(b, rng, root, s); break;
                case "Archaeopteris":  AddArchaeopteris(b, rng, root, s); break;
                case "Wattieza":       AddWattieza(b, rng, root, s); break;
                case "Conifer":        AddShapedConifer(b, rng, root, s, plant.shape); break;
                case "Palm":           AddPalm(b, rng, root, s * 1.15f); break;
                case "Acacia":         AddAcacia(b, rng, root, s); break;
                case "Baobab":         AddBaobab(b, rng, root, s); break;
                case "Mangrove":       AddMangrove(b, rng, root, s); break;
                case "Bamboo":         AddBamboo(b, rng, root, s); break;
                default:               AddShapedBroadleaf(b, rng, root, s, plant.shape); break;
            }
            b.StretchUp(from, root, WoodyStretch);      // trees stand taller over the ground plants
            PaintCrown(b, from);                        // see PlantShapes.cs
            AddFruitAndBlossom(b, rng, from, s, plant);
            hasCrown = false;
            leafTint = Color.white;
        }

        // One clump of a ground species; `size` is the cell size, `scale` an extra factor
        // Herbs, flowers, succulents and the rest of the ground layer are drawn this much bigger, so
        // they (and their flowers and fruit) read from the map camera
        const float HerbScale = 2f;

        static void AddGroundPlant(Builder b, System.Random rng, Vector3 root, float size, PlantDefinition plant, float scale)
        {
            float m = plant.size * scale * AgeSize * HerbScale * Range(rng, 0.8f, 1.15f);
            int from = b.VertexCount;
            leafTint = plant.form == "Flower" ? Color.white : plant.Tint; // flowers: the tint is the petal colour
            switch (plant.form)
            {
                case "GroundFern":     AddShapedGroundFern(b, rng, root, size * 0.09f * m, plant.shape); break;
                case "Horsetail":      AddHorsetails(b, rng, root, size * 0.09f * m, L(Horsetail)); break;
                case "Moss":           AddMossCushion(b, rng, root, size * 0.04f * m); break;
                case "Cooksonia":      AddCooksonia(b, rng, root, size * 0.06f * m); break;
                case "Clubmoss":       AddClubmoss(b, rng, root, size * 0.07f * m); break;
                case "Grass":          AddShapedGrass(b, rng, root, size * m, plant.shape); break;
                case "Shrub":          AddShapedShrub(b, rng, root, size * 0.045f * m, plant.shape); break;
                case "Flower":         AddFlowers(b, rng, root, size * m, plant.Tint); break;
                case "Reed":           AddReeds(b, rng, root, size * m); break;
                case "WaterLily":      AddWaterLilies(b, rng, root, size * m, plant.Tint); break;
                case "Succulent":      AddSucculent(b, rng, root, size * 0.18f * m); break; // desert plants drawn big enough to read from above
                case "Cactus":         AddCactus(b, rng, root, size * 0.42f * m); break;
                case "Cycad":          AddCycad(b, rng, root, size * 0.8f * m); break;
                case "Bennettitalean": AddBennettitalean(b, rng, root, size * 0.8f * m); break;
                default:               AddTuft(b, rng, root, size * m, L(Grass)); break;
            }
            AddFruitAndBlossom(b, rng, from, size * 0.8f * m, plant); // (big enough to see on the low plants)
            MakeFlexible(b, from, root, Flexibility(plant.form), size);
            leafTint = Color.white;
        }

        // How much a ground plant's form bends in the wind (0 = stiff)
        static float Flexibility(string form) => form switch
        {
            "Grass" => 1f, "Reed" => 1f, "Cooksonia" => 1f, "Horsetail" => 0.8f, "Flower" => 0.9f,
            "GroundFern" => 0.6f, "Clubmoss" => 0.4f, "Shrub" => 0.25f,
            "Moss" or "Succulent" or "Cactus" or "Cycad" or "Bennettitalean" or "WaterLily" => 0f,
            _ => 1f, // tufts
        };

        // Marks the vertices added since `from` (one plant standing at root) as bending in the wind
        // (MapFeature.shader ApplyWind): nothing at the foot, most at the
        // top; taller plants bend further.
        static void MakeFlexible(Builder b, int from, Vector3 root, float flex, float cellSize)
        {
            if (flex <= 0f || b.VertexCount <= from) return;
            float top = 0f;
            for (int i = from; i < b.VertexCount; i++) top = Mathf.Max(top, b.Vertex(i).y - root.y);
            if (top <= 1e-5f) return;
            float tall = Mathf.Clamp(top / (0.12f * cellSize), 0.35f, 1f);
            for (int i = from; i < b.VertexCount; i++)
            {
                float h = Mathf.Clamp01((b.Vertex(i).y - root.y) / top);
                b.SetFlex(i, flex * tall * h * h);
            }
        }

        static readonly Color BennettitaleanCone = new(0.85f, 0.55f, 0.35f);
        static readonly Color CactusGreen        = new(0.32f, 0.50f, 0.30f);
        static readonly Color SucculentGreen     = new(0.45f, 0.58f, 0.42f);
        static readonly Color BaobabBark         = new(0.55f, 0.48f, 0.42f);
        static readonly Color BambooStem         = new(0.52f, 0.62f, 0.26f);

        // Bennettitalean (Williamsonia, Cycadeoidea): a cycad-like rosette around flower-like cones
        static void AddBennettitalean(Builder b, System.Random rng, Vector3 root, float s)
        {
            AddCycad(b, rng, root, s);
            float h = s * 0.12f;
            for (int i = rng.Next(2, 4); i > 0; i--)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                var at  = root + new Vector3(Mathf.Sin(a) * 0.03f * s, h, Mathf.Cos(a) * 0.03f * s);
                AddBlob(b, rng, at, 0.022f * s, 1.2f, 0, Shade(rng, BennettitaleanCone));
            }
        }

        // Clubmoss / spikemoss: upright little stems densely clad in tiny leaves
        static void AddClubmoss(Builder b, System.Random rng, Vector3 root, float h)
        {
            for (int i = rng.Next(4, 8); i > 0; i--)
            {
                var foot = root + new Vector3(Range(rng, -0.5f, 0.5f), 0f, Range(rng, -0.5f, 0.5f)) * h;
                var tip  = foot + new Vector3(Range(rng, -0.15f, 0.15f) * h, Range(rng, 0.6f, 1f) * h, Range(rng, -0.15f, 0.15f) * h);
                AddBlob(b, rng, (foot + tip) * 0.5f, 0.12f * h, 4f, 0, Shade(rng, L(LycopsidLeaf)));
            }
        }

        // Herbs in flower: a couple of grass-like tufts and coloured blooms (petal = tint, or random)
        // Flowering herbs: a tuft of leaves with a few flowers on stems standing above it, each an open
        // head of petals round a contrasting heart (dark for yellow and orange heads, like a sunflower;
        // golden for the rest), tipped toward the sky so they read from the map camera
        static void AddFlowers(Builder b, System.Random rng, Vector3 root, float size, Color petal)
        {
            AddTuft(b, rng, root, size * 0.8f, Grass);
            bool random = petal.r > 0.99f && petal.g > 0.99f && petal.b > 0.99f;
            for (int i = rng.Next(1, 4); i > 0; i--)
            {
                var head = root + new Vector3(Range(rng, -0.06f, 0.06f), Range(rng, 0.14f, 0.22f), Range(rng, -0.06f, 0.06f)) * size;
                var c  = Shade(rng, random ? FlowerColors[rng.Next(FlowerColors.Length)] : petal, 0.05f);
                bool warm = c.r > 0.7f && c.g > 0.45f && c.b < 0.45f;
                var heart = warm ? new Color(0.32f, 0.2f, 0.1f) : new Color(0.98f, 0.8f, 0.25f);
                AddLimb(b, root, head, 0.006f * size, 0.004f * size, Shade(rng, Grass, 0.06f));
                var facing = (Vector3.up + new Vector3(Range(rng, -0.35f, 0.35f), 0f, Range(rng, -0.35f, 0.35f))).normalized;
                AddFlowerHead(b, rng, head, Range(rng, 0.0525f, 0.0735f) * size, c, heart, facing); // big enough to read from the map camera
            }
        }

        static void AddFlowerHead(Builder b, System.Random rng, Vector3 centre, float r, Color petal, Color heart, Vector3 facing)
        {
            var u = Vector3.Cross(facing, Vector3.forward).sqrMagnitude > 1e-4f ? Vector3.Cross(facing, Vector3.forward).normalized : Vector3.right;
            var v = Vector3.Cross(facing, u);
            int n = rng.Next(9, 14);
            float turn = Range(rng, 0f, Mathf.PI * 2f), half = Mathf.PI / n * 0.8f;
            var below = centre - facing * r;
            for (int k = 0; k < n; k++)
            {
                float a = turn + k * Mathf.PI * 2f / n;
                Vector3 Dir(float t) => u * Mathf.Cos(t) + v * Mathf.Sin(t);
                var tip   = centre + Dir(a) * r + facing * 0.08f * r;
                var left  = centre + Dir(a - half) * 0.45f * r + facing * 0.04f * r;
                var right = centre + Dir(a + half) * 0.45f * r + facing * 0.04f * r;
                var col = petal * Range(rng, 0.92f, 1.06f);
                b.AddTri(centre, left, tip, col, below);
                b.AddTri(centre, tip, right, col, below);
            }
            AddBlob(b, rng, centre + facing * 0.08f * r, 0.36f * r, 0.45f, 1, heart);
        }

        static void AddWaterLilies(Builder b, System.Random rng, Vector3 root, float size, Color flower)
        {
            for (int i = rng.Next(2, 4); i > 0; i--)
            {
                var c   = root + new Vector3(Range(rng, -0.04f, 0.04f), 0.004f, Range(rng, -0.04f, 0.04f)) * size;
                var rim = Ring(rng, c, 0.03f * size, 7, 0.15f);
                var pad = Shade(rng, L(LilyPad));
                for (int k = 0; k < rim.Length; k++) b.AddTri(c, rim[k], rim[(k + 1) % rim.Length], pad, c - Vector3.up);
                if (rng.NextDouble() < 0.6)
                    AddBlob(b, rng, c + Vector3.up * 0.01f * size, 0.011f * size, 0.7f, 0, flower.r > 0.99f && flower.g > 0.99f ? new Color(0.98f, 0.85f, 0.9f) : flower);
            }
        }

        // Rosette of thick, upturned leaves (aloes, Welwitschia, prickly pear pads)
        static void AddSucculent(Builder b, System.Random rng, Vector3 root, float s)
        {
            AddFrondRosette(b, rng, root + Vector3.up * 0.003f, rng.Next(5, 9), s, s * 0.7f, s * 0.15f, s * 0.22f, Shade(rng, L(SucculentGreen)));
        }

        // Columnar cactus with a couple of upturned arms; `h` is its height
        static void AddCactus(Builder b, System.Random rng, Vector3 root, float h)
        {
            var green = Shade(rng, L(CactusGreen));
            float r = 0.08f * h;
            var top = root + Vector3.up * h;
            AddLimb(b, root - Vector3.up * 0.01f, top, r, r * 0.9f, green);
            AddBlob(b, rng, top, r * 0.95f, 0.8f, 0, green);
            for (int i = rng.Next(0, 3); i > 0; i--)
            {
                float a  = Range(rng, 0f, Mathf.PI * 2f);
                var side = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a));
                var at   = root + Vector3.up * h * Range(rng, 0.35f, 0.6f);
                var elbow = at + side * h * 0.22f;
                var tip   = elbow + Vector3.up * h * Range(rng, 0.2f, 0.35f);
                AddLimb(b, at, elbow, r * 0.7f, r * 0.65f, green);
                AddLimb(b, elbow, tip, r * 0.65f, r * 0.6f, green);
                AddBlob(b, rng, tip, r * 0.62f, 0.8f, 0, green);
            }
        }

        // Baobab: a huge, swollen trunk under a small, flat crown of stubby branches
        static void AddBaobab(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h  = s * Range(rng, 0.4f, 0.5f);
            var bark = Shade(rng, BaobabBark);
            var top  = root + Vector3.up * h;
            AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * h * 0.5f, 0.09f * s, 0.085f * s, bark);
            AddLimb(b, root + Vector3.up * h * 0.5f, top, 0.085f * s, 0.05f * s, bark);
            for (int i = rng.Next(4, 7); i > 0; i--)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                var tip = top + new Vector3(Mathf.Sin(a) * 0.12f, Range(rng, 0.03f, 0.08f), Mathf.Cos(a) * 0.12f) * s;
                AddLimb(b, top, tip, 0.018f * s, 0.01f * s, bark);
                AddBlob(b, rng, tip, 0.045f * s, 0.6f, 0, Shade(rng, L(Leaf)));
            }
        }

        // Mangrove: a leafy crown standing on arching stilt roots
        static void AddMangrove(Builder b, System.Random rng, Vector3 root, float s)
        {
            float lift = 0.1f * s;
            var hub = root + Vector3.up * lift;
            var bark = Shade(rng, Bark * 1.2f);
            for (int i = rng.Next(4, 7); i > 0; i--)
            {
                float a  = Range(rng, 0f, Mathf.PI * 2f);
                var foot = root + new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a)) * 0.09f * s - Vector3.up * 0.01f;
                AddLimb(b, foot, hub, 0.008f * s, 0.01f * s, bark);
            }
            AddBroadleaf(b, rng, hub, s * 0.8f, new Color(0.18f, 0.40f, 0.20f), new Color(0.28f, 0.50f, 0.24f));
        }

        // Bamboo: a clump of jointed stalks with leafy tops
        static void AddBamboo(Builder b, System.Random rng, Vector3 root, float s)
        {
            for (int i = rng.Next(4, 7); i > 0; i--)
            {
                var foot = root + new Vector3(Range(rng, -0.05f, 0.05f), 0f, Range(rng, -0.05f, 0.05f)) * s;
                float h  = s * Range(rng, 0.5f, 0.75f);
                var lean = new Vector3(Range(rng, -0.08f, 0.08f), 0f, Range(rng, -0.08f, 0.08f)) * h;
                int joints = rng.Next(4, 7);
                var prev = foot - Vector3.up * 0.01f;
                for (int k = 1; k <= joints; k++)
                {
                    float t = k / (float)joints;
                    var p = foot + Vector3.up * h * t + lean * t * t;
                    AddLimb(b, prev, p, 0.009f * s, 0.008f * s, Shade(rng, BambooStem * (k % 2 == 0 ? 1f : 0.9f), 0.04f));
                    prev = p;
                }
                AddLeafSpray(b, rng, prev, 0.08f * s, rng.Next(6, 9), L(Leaf));
            }
        }

        // ---- Plants ----

        // Arching leaf from `root` along horizontal `dir`: rises, then droops to a pointed tip.
        // Faces point up (the camera looks down on them).
        static void AddFrond(Builder b, Vector3 root, Vector3 dir, float length, float rise, float droop, float width, Color color)
        {
            var side  = Vector3.Cross(Vector3.up, dir).normalized * width;
            var p1    = root + dir * length * 0.35f + Vector3.up * rise;
            var p2    = root + dir * length * 0.7f + Vector3.up * (rise * 0.7f - droop * 0.3f);
            var tip   = root + dir * length + Vector3.up * (rise * 0.2f - droop);
            var below = root + dir * length * 0.5f - Vector3.up * length;
            if (fineDetail)
            {
                // the same leaf as a smooth curve through those points, widening and tapering gradually
                const int segs = 10;
                Vector3 At(float t) => t < 0.5f
                    ? Vector3.Lerp(Vector3.Lerp(root, p1, t * 2f), Vector3.Lerp(p1, p2, t * 2f), t * 2f)
                    : Vector3.Lerp(Vector3.Lerp(p1, p2, t * 2f - 1f), Vector3.Lerp(p2, tip, t * 2f - 1f), t * 2f - 1f);
                float Width(float t) => t < 0.35f ? Mathf.Lerp(0.3f, 1f, Mathf.Sin(t / 0.35f * Mathf.PI * 0.5f))
                                                  : Mathf.Lerp(1f, 0f, Mathf.Pow((t - 0.35f) / 0.65f, 1.6f));
                var prevAt = At(0f);
                float prevW = Width(0f);
                for (int i = 1; i <= segs; i++)
                {
                    float t = i / (float)segs;
                    var at = At(t);
                    float w = Width(t);
                    var col = color * Mathf.Lerp(1f, 0.9f, t);
                    if (i < segs) b.AddQuad(prevAt + side * prevW, at + side * w, at - side * w, prevAt - side * prevW, col, below);
                    else          b.AddTri(prevAt + side * prevW, at, prevAt - side * prevW, col, below);
                    prevAt = at;
                    prevW  = w;
                }
                return;
            }
            b.AddQuad(root + side * 0.3f, p1 + side, p1 - side, root - side * 0.3f, color, below);
            b.AddQuad(p1 + side, p2 + side * 0.75f, p2 - side * 0.75f, p1 - side, color * 0.95f, below);
            b.AddTri(p2 + side * 0.75f, tip, p2 - side * 0.75f, color * 0.9f, below);
        }

        // Fronds radiating evenly from one point, with random spacing and length.
        static void AddFrondRosette(Builder b, System.Random rng, Vector3 center, int count, float length, float rise, float droop, float width, Color color)
        {
            float start = Range(rng, 0f, 360f);
            for (int i = 0; i < count; i++)
            {
                float a = (start + i * 360f / count + Range(rng, -12f, 12f)) * Mathf.Deg2Rad;
                float k = Range(rng, 0.8f, 1.1f);
                AddFrond(b, center, new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a)), length * k, rise * k, droop * k, width, color * Range(rng, 0.9f, 1.08f));
            }
        }

        // Thin leaves sprouting in all directions from one point (lycopsid and Cordaites crowns).
        static void AddLeafSpray(Builder b, System.Random rng, Vector3 center, float length, int count, Color color)
        {
            for (int i = 0; i < count; i++)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f), e = Range(rng, -0.5f, 1.2f);
                var dir = new Vector3(Mathf.Sin(a) * Mathf.Cos(e), Mathf.Sin(e), Mathf.Cos(a) * Mathf.Cos(e));
                AddLimb(b, center, center + dir * length * Range(rng, 0.7f, 1.1f), 0.08f * length, 0.01f * length, Shade(rng, color));
            }
        }

        // Tree fern (Psaronius, Dicksonia): a fibrous trunk under a crown of long arching fronds.
        static void AddTreeFern(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h   = s * Range(rng, 0.32f, 0.48f);
            var lean  = new Vector3(Range(rng, -1f, 1f), 0f, Range(rng, -1f, 1f)).normalized * 0.08f * h;
            var crown = root + Vector3.up * h + lean;
            var trunk = Shade(rng, FernTrunk);
            AddLimb(b, root - Vector3.up * 0.01f, crown, 0.026f * s, 0.02f * s, trunk);
            AddBlob(b, rng, crown - Vector3.up * 0.015f * s, 0.03f * s, 0.8f, 0, trunk * 1.2f); // old frond bases
            AddFrondRosette(b, rng, crown, rng.Next(9, 13), 0.21f * s, 0.04f * s, 0.08f * s, 0.035f * s, Shade(rng, L(FernGreen)));
            AddFrondRosette(b, rng, crown, rng.Next(2, 4), 0.07f * s, 0.07f * s, 0f, 0.014f * s, L(FernLight)); // unrolling fiddleheads
        }

        // Clump of ferns growing straight from the ground; `s` is the frond length.
        static void AddGroundFern(Builder b, System.Random rng, Vector3 root, float s)
        {
            var color = Color.Lerp(L(FernDark), L(FernGreen), Range(rng, 0.4f, 1f));
            AddFrondRosette(b, rng, root + Vector3.up * 0.003f, rng.Next(6, 10), s, s * Range(rng, 0.35f, 0.55f), s * 0.25f, s * 0.16f, color);
        }

        // Cycad: a stout, scaly trunk with a stiff rosette of fronds and a cone in the middle.
        static void AddCycad(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h = s * Range(rng, 0.06f, 0.16f);
            var top = root + Vector3.up * h;
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.04f * s, 0.034f * s, Shade(rng, CycadTrunk));
            AddFrondRosette(b, rng, top, rng.Next(9, 14), 0.14f * s, 0.07f * s, 0.03f * s, 0.022f * s, Shade(rng, L(CycadLeaf)));
            AddCone(b, rng, top - Vector3.up * 0.005f * s, 0.02f * s, 0.045f * s, Shade(rng, CycadCone));
        }

        // Lepidodendron, the giant club moss of the coal swamps: a tall, straight pole whose crown
        // forks again and again into leafy shoots.
        static void AddLepidodendron(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h  = s * Range(rng, 0.7f, 0.95f);
            var bark = Shade(rng, LycopsidBark);
            var top  = root + new Vector3(Range(rng, -0.02f, 0.02f) * h, h, Range(rng, -0.02f, 0.02f) * h);
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.034f * s, 0.022f * s, bark);
            AddCone(b, rng, root - Vector3.up * 0.01f * s, 0.05f * s, 0.06f * s, bark * 0.9f); // flared base
            AddForks(b, rng, top, Vector3.up, 0.13f * s, 0.02f * s, 3, Range(rng, 0f, Mathf.PI * 2f), bark, s);
        }

        // Splits into two branches, each splitting again at right angles, ending in leaf tufts.
        static void AddForks(Builder b, System.Random rng, Vector3 from, Vector3 dir, float length, float radius, int depth, float yaw, Color bark, float s)
        {
            var axis = new Vector3(Mathf.Cos(yaw), 0f, Mathf.Sin(yaw));
            for (int k = -1; k <= 1; k += 2)
            {
                float angle = Range(rng, 28f, 40f) * Mathf.Deg2Rad;
                var d  = (dir * Mathf.Cos(angle) + axis * (k * Mathf.Sin(angle))).normalized;
                var to = from + d * length * Range(rng, 0.85f, 1.1f);
                AddLimb(b, from, to, radius, radius * 0.75f, bark);
                if (depth > 1) AddForks(b, rng, to, d, length * 0.75f, radius * 0.72f, depth - 1, yaw + Mathf.PI * 0.5f, bark, s);
                else AddBlob(b, rng, to + d * 0.02f * s, 0.032f * s, 1.3f, 0, Shade(rng, L(LycopsidLeaf)));
            }
        }

        // Sigillaria: a thick ribbed pole (sometimes forked once) topped by brushes of grassy leaves.
        static void AddSigillaria(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h  = s * Range(rng, 0.5f, 0.7f);
            var bark = Shade(rng, LycopsidBark * 1.08f);
            var top  = root + Vector3.up * h;
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.04f * s, 0.032f * s, bark);
            if (rng.NextDouble() < 0.4)
            {
                float yaw = Range(rng, 0f, Mathf.PI * 2f);
                var axis  = new Vector3(Mathf.Cos(yaw), 0f, Mathf.Sin(yaw));
                for (int k = -1; k <= 1; k += 2)
                {
                    var tip = top + Vector3.up * 0.12f * s + axis * (k * 0.07f * s);
                    AddLimb(b, top, tip, 0.028f * s, 0.024f * s, bark);
                    AddLeafSpray(b, rng, tip, 0.1f * s, rng.Next(10, 14), L(LycopsidLeaf));
                }
            }
            else AddLeafSpray(b, rng, top, 0.12f * s, rng.Next(13, 18), L(LycopsidLeaf));
        }

        // Calamites, the tree-sized horsetail: a jointed stem with whorls of needle leaves at each node.
        static void AddCalamites(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h   = s * Range(rng, 0.45f, 0.7f);
            int nodes = rng.Next(5, 8);
            var stem  = Shade(rng, CalamitesStem);
            var prev  = root - Vector3.up * 0.01f;
            for (int i = 1; i <= nodes; i++)
            {
                float t = i / (float)nodes;
                var p   = root + Vector3.up * h * t;
                float r = Mathf.Lerp(0.022f, 0.01f, t) * s;
                AddLimb(b, prev, p, r * 1.05f, r, i % 2 == 0 ? stem : stem * 0.88f);
                prev = p;
                if (i < 2) continue;
                int whorl  = rng.Next(6, 9);
                float len  = Mathf.Lerp(0.1f, 0.035f, t) * s;
                float rot  = Range(rng, 0f, Mathf.PI * 2f);
                for (int k = 0; k < whorl; k++)
                {
                    float a = rot + k * Mathf.PI * 2f / whorl;
                    var dir = new Vector3(Mathf.Sin(a) * 0.85f, 0.5f, Mathf.Cos(a) * 0.85f).normalized;
                    AddLimb(b, p, p + dir * len, 0.005f * s, 0.001f * s, Shade(rng, L(Horsetail)));
                }
            }
            AddCone(b, rng, prev, 0.01f * s, 0.04f * s, stem * 1.1f);
        }

        // Archaeopteris (Late Devonian), the first modern-looking tree: a conifer-like trunk with
        // flat, fern-like branch systems.
        static void AddArchaeopteris(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h = s * Range(rng, 0.6f, 0.8f);
            AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * 0.9f * h, 0.032f * s, 0.012f * s, Shade(rng, Bark));
            int tiers = rng.Next(4, 6);
            for (int i = 0; i < tiers; i++)
            {
                float t    = i / (float)(tiers - 1);
                var center = root + Vector3.up * Mathf.Lerp(0.3f, 0.82f, t) * h;
                AddBoughTier(b, rng, center, Mathf.Lerp(0.17f, 0.07f, t) * s * Range(rng, 0.9f, 1.1f), Mathf.Lerp(0.12f, 0.1f, t) * h,
                             Color.Lerp(L(FernDark), L(FernGreen), t));
            }
        }

        // Wattieza (Middle Devonian), the earliest known tree: a pole with a shaving-brush crown of branches.
        static void AddWattieza(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h = s * Range(rng, 0.4f, 0.55f);
            var top = root + Vector3.up * h;
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.03f * s, 0.024f * s, Shade(rng, FernTrunk * 1.2f));
            int branches = rng.Next(8, 11);
            float rot = Range(rng, 0f, Mathf.PI * 2f);
            for (int k = 0; k < branches; k++)
            {
                float a = rot + k * Mathf.PI * 2f / branches, e = Range(rng, 0.7f, 1.2f);
                var dir = new Vector3(Mathf.Sin(a) * Mathf.Cos(e), Mathf.Sin(e), Mathf.Cos(a) * Mathf.Cos(e));
                var tip = top + dir * 0.09f * s * Range(rng, 0.8f, 1.15f);
                AddLimb(b, top, tip, 0.008f * s, 0.005f * s, Shade(rng, L(FernGreen) * 0.8f));
                AddBlob(b, rng, tip, 0.022f * s, 0.8f, 0, Shade(rng, L(FernGreen)));
            }
        }

        // Cordaites: a tall, slender trunk with a few branches ending in clusters of strap-shaped leaves.
        static void AddCordaites(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h  = s * Range(rng, 0.7f, 0.9f);
            var bark = Shade(rng, Bark);
            var top  = root + Vector3.up * h;
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.028f * s, 0.014f * s, bark);
            int branches = rng.Next(3, 6);
            float rot = Range(rng, 0f, Mathf.PI * 2f);
            for (int k = 0; k < branches; k++)
            {
                float a  = rot + k * Mathf.PI * 2f / branches;
                var from = top - Vector3.up * Range(rng, 0f, 0.15f) * h;
                var tip  = from + new Vector3(Mathf.Sin(a) * 0.09f, Range(rng, 0.05f, 0.1f), Mathf.Cos(a) * 0.09f) * s;
                AddLimb(b, from, tip, 0.01f * s, 0.006f * s, bark);
                AddLeafSpray(b, rng, tip, 0.06f * s, rng.Next(6, 9), L(CordaitesLeaf));
            }
        }

        // Glossopteris (Permian Gondwana): a dense, egg-shaped crown of tongue-shaped leaves.
        static void AddGlossopteris(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h = s * Range(rng, 0.5f, 0.62f);
            AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * 0.75f * h, 0.03f * s, 0.016f * s, Shade(rng, Bark));
            var leaf = Shade(rng, L(Glossopteris));
            AddBlob(b, rng, root + Vector3.up * 0.6f * h, 0.15f * s, 0.75f, 1, leaf);
            AddBlob(b, rng, root + Vector3.up * 0.85f * h, 0.12f * s, 0.8f, 1, leaf * 1.05f);
            AddBlob(b, rng, root + Vector3.up * 1.05f * h, 0.075f * s, 0.9f, 0, leaf * 1.1f);
        }

        // Ginkgo: an upright trunk with ascending branches and light, fan-leaved clumps.
        static void AddGinkgo(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h  = s * Range(rng, 0.55f, 0.7f);
            var bark = Shade(rng, Bark * 1.1f);
            var top  = root + Vector3.up * h;
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.03f * s, 0.014f * s, bark);
            int branches = rng.Next(3, 5);
            float angle  = Range(rng, 0f, 360f);
            for (int i = 0; i < branches; i++, angle += 360f / branches + Range(rng, -30f, 30f))
            {
                float t  = Mathf.Lerp(0.35f, 0.85f, i / (float)Mathf.Max(1, branches - 1));
                float a  = angle * Mathf.Deg2Rad;
                var fork = root + Vector3.up * t * h;
                var tip  = fork + new Vector3(Mathf.Sin(a), 1f, Mathf.Cos(a)).normalized * 0.12f * s * (1f - 0.4f * t);
                AddLimb(b, fork, tip, 0.012f * s, 0.007f * s, bark);
                AddBlob(b, rng, tip, 0.07f * s, 0.8f, 0, Shade(rng, L(GinkgoLeaf)));
            }
            AddBlob(b, rng, top, 0.07f * s, 0.9f, 0, Shade(rng, L(GinkgoLeaf) * 1.05f));
        }

        // Araucaria (monkey puzzle), the giant Jurassic conifer: a long bare trunk under a domed
        // umbrella of upturned branch whorls.
        static void AddAraucaria(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h  = s * Range(rng, 0.85f, 1.05f);
            var bark = Shade(rng, Bark * 1.1f);
            var top  = root + Vector3.up * h;
            var dark = Shade(rng, L(AraucariaGreen));
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.035f * s, 0.014f * s, bark);
            for (int w = 0; w < 3; w++)
            {
                float t   = w / 2f;
                var at    = root + Vector3.up * Mathf.Lerp(0.68f, 0.95f, t) * h;
                float len = Mathf.Lerp(0.17f, 0.08f, t) * s;
                float rot = Range(rng, 0f, Mathf.PI * 2f);
                for (int k = 0; k < 5; k++)
                {
                    float a = rot + k * Mathf.PI * 2f / 5f;
                    var tip = at + new Vector3(Mathf.Sin(a), 0.3f, Mathf.Cos(a)).normalized * len;
                    AddLimb(b, at, tip, 0.01f * s, 0.006f * s, bark);
                    AddBlob(b, rng, tip + Vector3.up * 0.015f * s, 0.045f * s, 0.45f, 0, dark * Range(rng, 0.9f, 1.1f));
                }
            }
            AddBlob(b, rng, top, 0.06f * s, 0.5f, 0, dark * 1.08f);
        }

        // Rhynia / early horsetails: a clump of upright green stems; `height` is the tallest stem.
        static void AddHorsetails(Builder b, System.Random rng, Vector3 root, float height, Color color)
        {
            for (int i = rng.Next(5, 9); i > 0; i--)
            {
                var foot = root + new Vector3(Range(rng, -0.4f, 0.4f), 0f, Range(rng, -0.4f, 0.4f)) * height;
                var tip  = foot + new Vector3(Range(rng, -0.1f, 0.1f) * height, Range(rng, 0.6f, 1f) * height, Range(rng, -0.1f, 0.1f) * height);
                AddLimb(b, foot - Vector3.up * 0.005f, tip, 0.06f * height, 0.03f * height, Shade(rng, color));
                AddCone(b, rng, tip, 0.04f * height, 0.1f * height, Shade(rng, Sporangium)); // spore cone
            }
        }

        static void AddMossCushion(Builder b, System.Random rng, Vector3 root, float radius) =>
            AddBlob(b, rng, root + Vector3.up * radius * 0.1f, radius, 0.35f, 0, Color.Lerp(L(Moss), L(MossLight), Range(rng, 0f, 1f)));

        // Cooksonia (Silurian), the first vascular plant: tiny forked stems tipped with spore capsules.
        static void AddCooksonia(Builder b, System.Random rng, Vector3 root, float h)
        {
            var green = Shade(rng, L(Rhynia));
            for (int i = rng.Next(3, 6); i > 0; i--)
            {
                var foot = root + new Vector3(Range(rng, -0.4f, 0.4f), 0f, Range(rng, -0.4f, 0.4f)) * h;
                var fork = foot + new Vector3(Range(rng, -0.1f, 0.1f) * h, Range(rng, 0.5f, 0.7f) * h, Range(rng, -0.1f, 0.1f) * h);
                AddLimb(b, foot, fork, 0.08f * h, 0.06f * h, green);
                float a   = Range(rng, 0f, Mathf.PI * 2f);
                var side  = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a)) * 0.25f * h;
                for (int k = -1; k <= 1; k += 2)
                {
                    var tip = fork + side * k + Vector3.up * 0.4f * h;
                    AddLimb(b, fork, tip, 0.06f * h, 0.05f * h, green);
                    AddBlob(b, rng, tip, 0.1f * h, 1f, 0, Shade(rng, Sporangium));
                }
            }
        }

        // A few domed stromatolites side by side; `radius` is the largest dome.
        static void AddStromatolites(Builder b, System.Random rng, Vector3 root, float radius, Color? tint = null)
        {
            var stone = tint is Color t ? new Color(Stromatolite.r * t.r, Stromatolite.g * t.g, Stromatolite.b * t.b) : Stromatolite;
            for (int i = rng.Next(2, 5); i > 0; i--)
            {
                var at  = root + new Vector3(Range(rng, -1f, 1f), 0f, Range(rng, -1f, 1f)) * radius;
                float r = radius * Range(rng, 0.5f, 1f);
                AddBlob(b, rng, at, r, 0.7f, 0, Shade(rng, stone));
            }
        }

        // Flat crust of microbial mat: olive green or purplish brown.
        static void AddMatPatch(Builder b, System.Random rng, Vector3 center, float radius)
        {
            var c   = center + Vector3.up * 0.003f;
            var rim = Ring(rng, c, radius, 7, 0.3f);
            var col = Shade(rng, rng.NextDouble() < 0.5 ? MatOlive : MatPurple);
            for (int i = 0; i < rim.Length; i++) b.AddTri(c, rim[i], rim[(i + 1) % rim.Length], col, c - Vector3.up);
        }

        static void AddPond(Builder b, System.Random rng, Vector3 center, float radius, Color color)
        {
            var rim = Ring(rng, center, radius, 10, 0.2f);
            for (int i = 0; i < rim.Length; i++) b.AddTri(center, rim[i], rim[(i + 1) % rim.Length], color, center - Vector3.up);
        }

        // Cup that widens upward: archaeocyathids, horn corals and vase sponges.
        static void AddCup(Builder b, System.Random rng, Vector3 root, float height, Color color)
        {
            var foot = root + new Vector3(Range(rng, -0.5f, 0.5f), 0f, Range(rng, -0.5f, 0.5f)) * height;
            var rim  = foot + new Vector3(Range(rng, -0.25f, 0.25f) * height, height * Range(rng, 0.7f, 1f), Range(rng, -0.25f, 0.25f) * height);
            AddLimb(b, foot, rim, 0.1f * height, 0.3f * height, color);
        }

        // Crinoid (sea lily): a long stalk topped by a cup and feathery arms.
        static void AddCrinoid(Builder b, System.Random rng, Vector3 root, float height, Color color)
        {
            var top = root + new Vector3(Range(rng, -0.15f, 0.15f) * height, height, Range(rng, -0.15f, 0.15f) * height);
            AddLimb(b, root, top, 0.04f * height, 0.035f * height, color * 0.9f);
            float rot = Range(rng, 0f, Mathf.PI * 2f);
            for (int k = 0; k < 5; k++)
            {
                float a = rot + k * Mathf.PI * 2f / 5f;
                var tip = top + new Vector3(Mathf.Sin(a) * 0.25f, 0.3f, Mathf.Cos(a) * 0.25f) * height;
                AddLimb(b, top, tip, 0.03f * height, 0.01f * height, color);
            }
            AddBlob(b, rng, top, 0.07f * height, 0.8f, 0, color);
        }
    }
}
