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

        // ---- Forests, reefs and oases ----

        // A stand of the period's trees with undergrowth, or null before the first forests (Devonian).
        public static Mesh CreateEraForest(System.Random rng, float size, GeologicalAge age, TerrainFeature feature)
        {
            if (age < GeologicalAge.Devonian) return null;
            if (age >= GeologicalAge.Paleogene)
                return feature == TerrainFeature.Jungle ? CreateJungle(rng, size) : CreateForest(rng, size, feature == TerrainFeature.ConiferForest);

            bool conifer = feature == TerrainFeature.ConiferForest, jungle = feature == TerrainFeature.Jungle;
            var b = new Builder();
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
                    else AddHorsetails(b, rng, root, size * 0.07f, Rhynia);
                    break;
                case GeologicalAge.Carboniferous:
                    if (rng.NextDouble() < 0.5) AddHorsetails(b, rng, root, size * 0.1f, Horsetail);
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
                if (age == GeologicalAge.Cambrian)
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
            var b = new Builder();
            var center = new Vector3(Range(rng, -0.06f, 0.06f) * size, 0.004f, Range(rng, -0.06f, 0.06f) * size);
            AddPond(b, rng, center, 0.24f * size, PondWater);

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
                        if (i % 2 == 0) AddHorsetails(b, rng, at, size * 0.08f, Rhynia); else AddMossCushion(b, rng, at, size * 0.045f);
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
                case TerrainKind.Barren:
                    foreach (var p in Spots(2, 5, 0.12f))
                        AddRock(b, rng, At(p), size * Range(rng, 0.03f, 0.07f), Color.Lerp(BarrenGrey, BarrenRed, Range(rng, 0f, 1f)));
                    foreach (var p in Spots(2, 5, 0.06f))
                        AddRock(b, rng, At(p), size * Range(rng, 0.012f, 0.022f), Color.Lerp(BarrenGrey, BarrenRed, Range(rng, 0f, 1f)));
                    break;
                case TerrainKind.MicrobialMat:
                    foreach (var p in Spots(2, 4, 0.15f)) AddMatPatch(b, rng, At(p), size * Range(rng, 0.05f, 0.09f));
                    foreach (var p in Spots(1, 3, 0.15f)) AddStromatolites(b, rng, At(p), size * Range(rng, 0.03f, 0.05f));
                    break;
                case TerrainKind.Mossland:
                    foreach (var p in Spots(4, 7, 0.1f)) AddMossCushion(b, rng, At(p), size * Range(rng, 0.03f, 0.055f));
                    if (age >= GeologicalAge.Silurian)
                        foreach (var p in Spots(2, 4, 0.08f)) AddCooksonia(b, rng, At(p), size * 0.06f);
                    if (age == GeologicalAge.Devonian)
                        foreach (var p in Spots(1, 3, 0.1f)) AddHorsetails(b, rng, At(p), size * 0.07f, Rhynia);
                    break;
                case TerrainKind.FernPrairie:
                    // Jurassic fern prairies: ferns as tall as a person, the "grassland" of the dinosaurs
                    float fern = age == GeologicalAge.Jurassic ? 0.15f : age is GeologicalAge.Triassic or GeologicalAge.Cretaceous ? 0.1f : 0.085f;
                    foreach (var p in Spots(3, 6, fern * 1.4f)) AddGroundFern(b, rng, At(p), size * fern * Range(rng, 0.8f, 1.2f));
                    foreach (var p in Spots(0, 2, 0.1f)) AddHorsetails(b, rng, At(p), size * 0.08f, Horsetail);
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
                    foreach (var p in Spots(2, 4, 0.12f)) AddHorsetails(b, rng, At(p), size * 0.13f, Horsetail);
                    if (rng.NextDouble() < 0.4)
                        foreach (var p in Spots(1, 1, 0.25f)) AddLepidodendron(b, rng, At(p), size * 0.55f);
                    break;
                // Reeds, sedges and water lilies are flowering plants
                case TerrainKind.Wetland when age < GeologicalAge.Cretaceous:
                    foreach (var p in Spots(3, 5, 0.12f)) AddHorsetails(b, rng, At(p), size * 0.1f, Horsetail);
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
            AddFrondRosette(b, rng, crown, rng.Next(9, 13), 0.21f * s, 0.04f * s, 0.08f * s, 0.035f * s, Shade(rng, FernGreen));
            AddFrondRosette(b, rng, crown, rng.Next(2, 4), 0.07f * s, 0.07f * s, 0f, 0.014f * s, FernLight); // unrolling fiddleheads
        }

        // Clump of ferns growing straight from the ground; `s` is the frond length.
        static void AddGroundFern(Builder b, System.Random rng, Vector3 root, float s)
        {
            var color = Color.Lerp(FernDark, FernGreen, Range(rng, 0.4f, 1f));
            AddFrondRosette(b, rng, root + Vector3.up * 0.003f, rng.Next(6, 10), s, s * Range(rng, 0.35f, 0.55f), s * 0.25f, s * 0.16f, color);
        }

        // Cycad: a stout, scaly trunk with a stiff rosette of fronds and a cone in the middle.
        static void AddCycad(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h = s * Range(rng, 0.06f, 0.16f);
            var top = root + Vector3.up * h;
            AddLimb(b, root - Vector3.up * 0.01f, top, 0.04f * s, 0.034f * s, Shade(rng, CycadTrunk));
            AddFrondRosette(b, rng, top, rng.Next(9, 14), 0.14f * s, 0.07f * s, 0.03f * s, 0.022f * s, Shade(rng, CycadLeaf));
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
                else AddBlob(b, rng, to + d * 0.02f * s, 0.032f * s, 1.3f, 0, Shade(rng, LycopsidLeaf));
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
                    AddLeafSpray(b, rng, tip, 0.1f * s, rng.Next(10, 14), LycopsidLeaf);
                }
            }
            else AddLeafSpray(b, rng, top, 0.12f * s, rng.Next(13, 18), LycopsidLeaf);
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
                    AddLimb(b, p, p + dir * len, 0.005f * s, 0.001f * s, Shade(rng, Horsetail));
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
                             Color.Lerp(FernDark, FernGreen, t));
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
                AddLimb(b, top, tip, 0.008f * s, 0.005f * s, Shade(rng, FernGreen * 0.8f));
                AddBlob(b, rng, tip, 0.022f * s, 0.8f, 0, Shade(rng, FernGreen));
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
                AddLeafSpray(b, rng, tip, 0.06f * s, rng.Next(6, 9), CordaitesLeaf);
            }
        }

        // Glossopteris (Permian Gondwana): a dense, egg-shaped crown of tongue-shaped leaves.
        static void AddGlossopteris(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h = s * Range(rng, 0.5f, 0.62f);
            AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * 0.75f * h, 0.03f * s, 0.016f * s, Shade(rng, Bark));
            var leaf = Shade(rng, Glossopteris);
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
                AddBlob(b, rng, tip, 0.07f * s, 0.8f, 0, Shade(rng, GinkgoLeaf));
            }
            AddBlob(b, rng, top, 0.07f * s, 0.9f, 0, Shade(rng, GinkgoLeaf * 1.05f));
        }

        // Araucaria (monkey puzzle), the giant Jurassic conifer: a long bare trunk under a domed
        // umbrella of upturned branch whorls.
        static void AddAraucaria(Builder b, System.Random rng, Vector3 root, float s)
        {
            float h  = s * Range(rng, 0.85f, 1.05f);
            var bark = Shade(rng, Bark * 1.1f);
            var top  = root + Vector3.up * h;
            var dark = Shade(rng, AraucariaGreen);
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
            AddBlob(b, rng, root + Vector3.up * radius * 0.1f, radius, 0.35f, 0, Color.Lerp(Moss, MossLight, Range(rng, 0f, 1f)));

        // Cooksonia (Silurian), the first vascular plant: tiny forked stems tipped with spore capsules.
        static void AddCooksonia(Builder b, System.Random rng, Vector3 root, float h)
        {
            var green = Shade(rng, Rhynia);
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
        static void AddStromatolites(Builder b, System.Random rng, Vector3 root, float radius)
        {
            for (int i = rng.Next(2, 5); i > 0; i--)
            {
                var at  = root + new Vector3(Range(rng, -1f, 1f), 0f, Range(rng, -1f, 1f)) * radius;
                float r = radius * Range(rng, 0.5f, 1f);
                AddBlob(b, rng, at, r, 0.7f, 0, Shade(rng, Stromatolite));
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
