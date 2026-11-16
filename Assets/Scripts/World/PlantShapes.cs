using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Silhouettes within a plant form (plants.json "shape"), so species that share a form still
    // look like themselves on the map: an oak is broad and round, a birch slender and white, a kapok
    // an emergent umbrella; a pine is a bare trunk with tufts on top, a spruce a narrow spire, a
    // redwood a tall red column. An empty or unknown shape gives the form's default.
    public static partial class MapFeatureMeshes
    {
        static readonly Color BirchBark   = new(0.86f, 0.85f, 0.80f);
        static readonly Color BirchMark   = new(0.20f, 0.19f, 0.18f);
        static readonly Color GumBark     = new(0.80f, 0.74f, 0.64f);
        static readonly Color PlaneBark   = new(0.64f, 0.60f, 0.50f);
        static readonly Color PineBark    = new(0.46f, 0.30f, 0.20f);
        static readonly Color RedwoodBark = new(0.50f, 0.25f, 0.15f);
        static readonly Color Blossom     = new(0.97f, 0.90f, 0.93f);
        static readonly Color PinkBloom   = new(0.90f, 0.42f, 0.66f);
        static readonly Color Berry       = new(0.78f, 0.10f, 0.10f);
        static readonly Color BanksiaCone = new(0.92f, 0.70f, 0.25f);
        static readonly Color SeedHead    = new(0.62f, 0.42f, 0.24f);
        static readonly Color Plume       = new(0.92f, 0.90f, 0.80f);

        // ---- Broadleaf trees ----

        // Set while a plant with a coloured crown (plants.json "crown") is built
        static bool hasCrown;
        static Color crownColor;

        static void AddShapedBroadleaf(Builder b, System.Random rng, Vector3 root, float s, string shape)
        {
            var leaf = L(Color.Lerp(Leaf, LeafLight, Range(rng, 0f, 0.45f)));
            var bark = Shade(rng, Bark);
            var up   = Vector3.up;
            switch (shape)
            {
                case "Round":
                case "Mottled": // plane trees: the same broad crown on pale, patchy bark
                {
                    float h = s * Range(rng, 0.55f, 0.65f);
                    var c   = root + up * 0.66f * h;
                    Trunk(b, root, c - up * 0.12f * h, 0.04f * s, 0.026f * s, shape == "Mottled" ? Shade(rng, PlaneBark) : bark);
                    Limbs(b, rng, c - up * 0.14f * h, 3, 0.16f * s, 0.12f * h, 0.014f * s, bark);
                    AddCrown(b, rng, c, new Vector3(0.25f, 0.18f, 0.25f) * s, 7, 0.095f * s, leaf);
                    break;
                }
                case "Dome": // beech, camphor: one dense, smooth dome low over a short trunk
                {
                    float h = s * Range(rng, 0.55f, 0.62f);
                    var c   = root + up * 0.6f * h;
                    Trunk(b, root, c, 0.042f * s, 0.03f * s, bark);
                    AddBlob(b, rng, c + up * 0.06f * h, 0.24f * s, 0.78f, 1, leaf * 1.02f);
                    AddCrown(b, rng, c, new Vector3(0.24f, 0.2f, 0.24f) * s, 6, 0.1f * s, leaf);
                    break;
                }
                case "Oval":
                case "Tall": // alder, sassafras / tulip tree: narrow upright crowns
                case "Flowering": // magnolia: an oval crown dotted with big pale blossoms
                {
                    float tall = shape == "Tall" ? 1.25f : 1f;
                    float h = s * Range(rng, 0.7f, 0.8f) * tall;
                    var c   = root + up * 0.6f * h;
                    Trunk(b, root, c, 0.032f * s, 0.018f * s, bark);
                    var radii = new Vector3(0.15f, 0.28f * tall, 0.15f) * s;
                    AddCrown(b, rng, c, radii, 8, 0.075f * s, leaf);
                    if (shape == "Flowering") Dots(b, rng, c, radii * 1.05f, rng.Next(9, 14), 0.018f * s, Blossom);
                    break;
                }
                case "Slender": // birch: thin white trunk with dark marks, small airy clumps that droop
                {
                    float h = s * Range(rng, 0.72f, 0.82f);
                    var top = root + up * 0.92f * h + new Vector3(Range(rng, -0.03f, 0.03f), 0f, Range(rng, -0.03f, 0.03f)) * h;
                    Banded(b, rng, root - up * 0.01f, top, 0.022f * s, 0.008f * s, BirchBark, BirchMark, 6);
                    for (int i = 0, n = rng.Next(5, 8); i < n; i++)
                    {
                        float t = Range(rng, 0.45f, 0.95f);
                        var at  = Vector3.Lerp(root, top, t);
                        float a = Range(rng, 0f, Mathf.PI * 2f);
                        var tip = at + new Vector3(Mathf.Cos(a) * 0.11f * s, -0.02f * h, Mathf.Sin(a) * 0.11f * s);
                        AddLimb(b, at, tip, 0.006f * s, 0.003f * s, BirchBark * 0.9f);
                        AddBlob(b, rng, tip - up * 0.02f * h, Range(rng, 0.045f, 0.065f) * s, 1.25f, 1, leaf * Range(rng, 0.95f, 1.1f));
                    }
                    AddBlob(b, rng, top, 0.05f * s, 1.3f, 1, leaf * 1.05f);
                    break;
                }
                case "Open": // eucalyptus: tall pale trunk forking into a few limbs, sparse tufts at the ends
                {
                    float h  = s * Range(rng, 0.8f, 0.92f);
                    var fork = root + up * 0.5f * h;
                    Trunk(b, root, fork, 0.034f * s, 0.024f * s, Shade(rng, GumBark));
                    for (int i = 0, n = rng.Next(3, 5); i < n; i++)
                    {
                        float a  = (i / (float)n + Range(rng, -0.08f, 0.08f)) * Mathf.PI * 2f;
                        var mid  = fork + new Vector3(Mathf.Cos(a) * 0.08f * s, 0.2f * h, Mathf.Sin(a) * 0.08f * s);
                        var tip  = mid + new Vector3(Mathf.Cos(a) * 0.07f * s, Range(rng, 0.15f, 0.28f) * h, Mathf.Sin(a) * 0.07f * s);
                        AddLimb(b, fork, mid, 0.016f * s, 0.011f * s, GumBark);
                        AddLimb(b, mid, tip, 0.011f * s, 0.006f * s, GumBark);
                        AddBlob(b, rng, tip, Range(rng, 0.06f, 0.085f) * s, 0.6f, 1, leaf * Range(rng, 0.9f, 1.05f));
                        if (rng.NextDouble() < 0.6)
                            AddBlob(b, rng, Vector3.Lerp(mid, tip, 0.4f) + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * 0.04f * s,
                                    0.045f * s, 0.6f, 1, leaf * 0.92f);
                    }
                    break;
                }
                case "Emergent": // kapok, dipterocarps: towering straight trunk on buttresses, flat umbrella crown
                {
                    float h = s * Range(rng, 1.0f, 1.15f);
                    var c   = root + up * 0.86f * h;
                    Trunk(b, root, c, 0.04f * s, 0.024f * s, bark);
                    Buttresses(b, rng, root, 0.09f * s, 0.14f * h, 0.012f * s, bark);
                    Limbs(b, rng, c - up * 0.06f * h, 4, 0.2f * s, 0.05f * h, 0.012f * s, bark);
                    AddCrown(b, rng, c + up * 0.03f * h, new Vector3(0.3f, 0.08f, 0.3f) * s, 9, 0.095f * s, leaf);
                    break;
                }
                case "Spreading": // fig: short heavy trunk, a wide low crown and aerial roots hanging from it
                {
                    float h = s * Range(rng, 0.48f, 0.56f);
                    var c   = root + up * 0.62f * h;
                    Trunk(b, root, c, 0.05f * s, 0.035f * s, bark);
                    Limbs(b, rng, c - up * 0.08f * h, 4, 0.24f * s, 0.06f * h, 0.016f * s, bark);
                    var radii = new Vector3(0.34f, 0.13f, 0.34f) * s;
                    AddCrown(b, rng, c + up * 0.05f * h, radii, 10, 0.09f * s, leaf);
                    for (int i = 0, n = rng.Next(3, 6); i < n; i++)
                    {
                        float a = Range(rng, 0f, Mathf.PI * 2f), r = Range(rng, 0.12f, 0.28f) * s;
                        var top = c + new Vector3(Mathf.Cos(a) * r, -0.02f * h, Mathf.Sin(a) * r);
                        AddLimb(b, top, new Vector3(top.x, root.y - 0.01f, top.z), 0.006f * s, 0.008f * s, bark * 1.1f);
                    }
                    break;
                }
                case "Layered": // southern beech: flat, horizontal sprays in tiers up the trunk
                {
                    float h = s * Range(rng, 0.62f, 0.72f);
                    var top = root + up * 0.95f * h;
                    Trunk(b, root, top, 0.032f * s, 0.012f * s, bark);
                    int tiers = rng.Next(3, 5);
                    for (int i = 0; i < tiers; i++)
                    {
                        float t = (i + 0.5f) / tiers;
                        var at  = Vector3.Lerp(root + up * 0.35f * h, top, t);
                        float r = Mathf.Lerp(0.22f, 0.1f, t) * s;
                        for (int k = 0, n = rng.Next(3, 5); k < n; k++)
                        {
                            float a = (k / (float)n + Range(rng, 0f, 0.2f)) * Mathf.PI * 2f;
                            var p   = at + new Vector3(Mathf.Cos(a) * r * 0.6f, 0f, Mathf.Sin(a) * r * 0.6f);
                            AddLimb(b, at, p, 0.008f * s, 0.004f * s, bark);
                            AddBlob(b, rng, p, r * 0.55f, 0.32f, 1, leaf * Mathf.Lerp(0.88f, 1.08f, t));
                        }
                    }
                    break;
                }
                case "Bushy": // laurel: several stems and a dense crown nearly to the ground
                {
                    float h = s * Range(rng, 0.45f, 0.55f);
                    var c   = root + up * 0.5f * h;
                    for (int i = 0; i < 3; i++)
                    {
                        var foot = root + new Vector3(Range(rng, -0.03f, 0.03f), 0f, Range(rng, -0.03f, 0.03f)) * s;
                        AddLimb(b, foot - up * 0.01f, c + new Vector3(Range(rng, -0.05f, 0.05f), 0f, Range(rng, -0.05f, 0.05f)) * s, 0.016f * s, 0.01f * s, bark);
                    }
                    AddCrown(b, rng, c, new Vector3(0.2f, 0.24f, 0.2f) * s, 9, 0.075f * s, leaf * 0.92f);
                    break;
                }
                default:
                    AddBroadleaf(b, rng, root, s);
                    break;
            }
        }

        // ---- Conifers ----

        static void AddShapedConifer(Builder b, System.Random rng, Vector3 root, float s, string shape)
        {
            var up = Vector3.up;
            switch (shape)
            {
                case "Spruce": // narrow dark spire of many drooping tiers
                    Tiers(b, rng, root, s, h: s * Range(rng, 0.85f, 0.98f), tiers: rng.Next(7, 10), from: 0.1f, to: 0.82f,
                          r0: 0.14f, r1: 0.035f, depth: 0.2f, L(Needle) * 0.85f, L(NeedleTip) * 0.9f, Shade(rng, Bark));
                    break;
                case "Larch": // airy: few, thin, widely spaced tiers with the trunk showing between them
                    Tiers(b, rng, root, s, h: s * Range(rng, 0.75f, 0.85f), tiers: rng.Next(5, 7), from: 0.2f, to: 0.85f,
                          r0: 0.13f, r1: 0.04f, depth: 0.09f, L(NeedleTip) * 1.1f, L(NeedleTip) * 1.25f, Shade(rng, Bark));
                    break;
                case "Redwood": // very tall red trunk, a narrow crown only on its upper half
                    Tiers(b, rng, root, s, h: s * Range(rng, 1.2f, 1.4f), tiers: rng.Next(6, 9), from: 0.45f, to: 0.92f,
                          r0: 0.11f, r1: 0.035f, depth: 0.13f, L(Needle), L(NeedleTip), Shade(rng, RedwoodBark), trunk: 0.05f);
                    break;
                case "Buttressed": // bald cypress: flared base, broad open tiers, flattish top
                {
                    float h = s * Range(rng, 0.7f, 0.8f);
                    Buttresses(b, rng, root, 0.07f * s, 0.12f * h, 0.012f * s, Shade(rng, Bark));
                    Tiers(b, rng, root, s, h, tiers: 4, from: 0.35f, to: 0.8f, r0: 0.2f, r1: 0.13f, depth: 0.12f,
                          L(NeedleTip), L(NeedleTip) * 1.15f, Shade(rng, Bark), spire: false);
                    break;
                }
                case "Pine": // tall, often leaning bare trunk; a few flat needle tufts on branches at the top
                {
                    float h   = s * Range(rng, 0.85f, 1f);
                    var lean  = new Vector3(Range(rng, -0.08f, 0.08f), 0f, Range(rng, -0.08f, 0.08f)) * h;
                    var mid   = root + up * 0.45f * h + lean * 0.4f;
                    var top   = root + up * 0.85f * h + lean;
                    var bark  = Shade(rng, PineBark);
                    AddLimb(b, root - up * 0.01f, mid, 0.03f * s, 0.022f * s, bark);
                    AddLimb(b, mid, top, 0.022f * s, 0.012f * s, bark);
                    var needle = L(Needle) * 1.1f;
                    for (int i = 0, n = rng.Next(3, 6); i < n; i++)
                    {
                        var at  = Vector3.Lerp(mid, top, Range(rng, 0.4f, 0.95f));
                        float a = Range(rng, 0f, Mathf.PI * 2f);
                        var tip = at + new Vector3(Mathf.Cos(a) * Range(rng, 0.09f, 0.15f) * s, Range(rng, 0.02f, 0.06f) * h, Mathf.Sin(a) * Range(rng, 0.09f, 0.15f) * s);
                        AddLimb(b, at, tip, 0.009f * s, 0.005f * s, bark);
                        AddBlob(b, rng, tip + up * 0.015f * h, Range(rng, 0.07f, 0.1f) * s, 0.45f, 1, needle * Range(rng, 0.9f, 1.1f));
                    }
                    AddBlob(b, rng, top + up * 0.03f * h, 0.085f * s, 0.55f, 1, needle * 1.08f);
                    break;
                }
                case "Columnar": // cypress-like scale-leaf conifers: a dense green flame
                {
                    float h = s * Range(rng, 0.75f, 0.9f);
                    var color = L(Needle) * 1.05f;
                    AddLimb(b, root - up * 0.01f, root + up * 0.2f * h, 0.022f * s, 0.018f * s, Shade(rng, Bark));
                    for (int i = 0; i < 5; i++)
                    {
                        float t = i / 4f;
                        AddBlob(b, rng, root + up * Mathf.Lerp(0.25f, 0.82f, t) * h, Mathf.Lerp(0.085f, 0.035f, t) * s, 1.7f, 1,
                                Color.Lerp(color, L(NeedleTip), t * 0.6f));
                    }
                    break;
                }
                case "Umbrella": // umbrella pine: whorls of long needles radiating like spokes
                {
                    float h = s * Range(rng, 0.7f, 0.8f);
                    var top = root + up * 0.92f * h;
                    AddLimb(b, root - up * 0.01f, top, 0.026f * s, 0.01f * s, Shade(rng, Bark));
                    int tiers = rng.Next(5, 7);
                    for (int i = 0; i < tiers; i++)
                    {
                        float t = i / (float)(tiers - 1);
                        var at  = Vector3.Lerp(root + up * 0.22f * h, top, t);
                        float r = Mathf.Lerp(0.16f, 0.05f, t) * s;
                        AddFrondRosette(b, rng, at, rng.Next(9, 13), r, r * 0.25f, r * 0.15f, r * 0.12f, Color.Lerp(L(Needle), L(NeedleTip), t));
                    }
                    break;
                }
                case "Whorled": // early (voltzian) conifers: horizontal branch whorls tipped with drooping needle sprays
                {
                    float h = s * Range(rng, 0.7f, 0.85f);
                    var top = root + up * 0.95f * h;
                    var bark = Shade(rng, Bark);
                    AddLimb(b, root - up * 0.01f, top, 0.026f * s, 0.01f * s, bark);
                    int whorls = rng.Next(4, 6);
                    for (int i = 0; i < whorls; i++)
                    {
                        float t = (i + 0.5f) / whorls;
                        var at  = Vector3.Lerp(root + up * 0.3f * h, top, t);
                        float r = Mathf.Lerp(0.17f, 0.06f, t) * s;
                        float a0 = Range(rng, 0f, Mathf.PI * 2f);
                        for (int k = 0, n = rng.Next(4, 6); k < n; k++)
                        {
                            float a = a0 + k * Mathf.PI * 2f / n;
                            var tip = at + new Vector3(Mathf.Cos(a) * r, -0.02f * h, Mathf.Sin(a) * r);
                            AddLimb(b, at, tip, 0.006f * s, 0.004f * s, bark);
                            AddBlob(b, rng, Vector3.Lerp(at, tip, 0.7f) - up * 0.015f * h, r * 0.42f, 0.55f, 1, L(Needle) * Range(rng, 0.95f, 1.15f));
                        }
                    }
                    AddBlob(b, rng, top, 0.04f * s, 1.4f, 1, L(NeedleTip));
                    break;
                }
                case "Open": // broad-leaved conifers (Podozamites): a loose crown of small leafy clumps
                {
                    float h = s * Range(rng, 0.65f, 0.75f);
                    var c   = root + up * 0.62f * h;
                    Trunk(b, root, c, 0.026f * s, 0.014f * s, Shade(rng, Bark));
                    Limbs(b, rng, c - up * 0.12f * h, 4, 0.14f * s, 0.16f * h, 0.008f * s, Bark);
                    AddCrown(b, rng, c, new Vector3(0.17f, 0.2f, 0.17f) * s, 7, 0.06f * s, L(NeedleTip), 0.2f);
                    break;
                }
                case "Shrubby": // Frenelopsis: a low thicket of jointed green stems
                {
                    float h = s * Range(rng, 0.35f, 0.45f);
                    for (int i = 0, n = rng.Next(4, 7); i < n; i++)
                    {
                        var tip = root + new Vector3(Range(rng, -0.12f, 0.12f) * s, Range(rng, 0.7f, 1f) * h, Range(rng, -0.12f, 0.12f) * s);
                        Banded(b, rng, root - up * 0.01f, tip, 0.014f * s, 0.006f * s, L(NeedleTip), L(Needle), 4);
                        AddBlob(b, rng, tip, 0.03f * s, 1.5f, 1, L(NeedleTip));
                    }
                    break;
                }
                default: // fir: a dense, symmetrical cone
                    AddConifer(b, rng, root, s);
                    break;
            }
        }

        // ---- Shrubs, grasses, ferns ----

        // `r` is the size of the main clump
        static void AddShapedShrub(Builder b, System.Random rng, Vector3 root, float r, string shape)
        {
            var leaf = Shade(rng, L(Shrub));
            var up   = Vector3.up;
            switch (shape)
            {
                case "Twiggy": // sagebrush, creosote: bare twigs ending in small grey-green tufts
                case "Banksia": // with upright golden flower cones
                    for (int i = 0, n = rng.Next(4, 7); i < n; i++)
                    {
                        var tip = root + new Vector3(Range(rng, -1f, 1f) * r, Range(rng, 0.9f, 1.5f) * r, Range(rng, -1f, 1f) * r);
                        AddLimb(b, root, tip, 0.12f * r, 0.05f * r, Bark * 1.2f);
                        AddBlob(b, rng, tip, Range(rng, 0.35f, 0.5f) * r, 0.8f, 0, leaf * Range(rng, 0.9f, 1.1f));
                        if (shape == "Banksia" && i % 2 == 0)
                            AddLimb(b, tip, tip + up * 0.45f * r, 0.13f * r, 0.1f * r, BanksiaCone);
                    }
                    break;
                case "Mat": // heather, arctic willow: a low, wide carpet
                    for (int i = 0, n = rng.Next(3, 5); i < n; i++)
                    {
                        var p = root + new Vector3(Range(rng, -1.1f, 1.1f) * r, 0.15f * r, Range(rng, -1.1f, 1.1f) * r);
                        AddBlob(b, rng, p, Range(rng, 0.6f, 0.85f) * r, 0.35f, 0, leaf * Range(rng, 0.9f, 1.1f));
                    }
                    break;
                case "Flowering": // rhododendron: a rounded bush covered in pink trusses
                case "Berries":   // holly: dark glossy bush with red berries
                {
                    var c = root + up * 0.8f * r;
                    AddBlob(b, rng, c, r * 1.05f, 0.8f, 1, shape == "Berries" ? leaf * 0.75f : leaf);
                    AddBlob(b, rng, c + new Vector3(0.6f, -0.2f, 0.3f) * r, r * 0.7f, 0.8f, 0, leaf * 0.9f);
                    Dots(b, rng, c, new Vector3(1.05f, 0.85f, 1.05f) * r, rng.Next(6, 10), (shape == "Berries" ? 0.1f : 0.2f) * r,
                         shape == "Berries" ? Berry : PinkBloom);
                    break;
                }
                default: // a few overlapping rounded clumps
                    AddBlob(b, rng, root + up * 0.3f * r, r, 0.7f, 0, leaf);
                    AddBlob(b, rng, root + new Vector3(0.6f, 0.15f, -0.3f) * r, r * 0.7f, 0.7f, 0, leaf * 0.92f);
                    if (rng.NextDouble() < 0.6) AddBlob(b, rng, root + new Vector3(-0.5f, 0.12f, 0.45f) * r, r * 0.6f, 0.7f, 0, leaf * 1.06f);
                    break;
            }
        }

        // `size` is the cell size × the species' size
        static void AddShapedGrass(Builder b, System.Random rng, Vector3 root, float size, string shape)
        {
            var grass = Shade(rng, L(Grass));
            switch (shape)
            {
                case "Tall": // bluestem, red oat grass: tall leaning blades with rusty seed heads
                    for (int i = rng.Next(6, 9); i > 0; i--)
                    {
                        var foot = root + new Vector3(Range(rng, -0.012f, 0.012f), 0f, Range(rng, -0.012f, 0.012f)) * size;
                        var tip  = foot + new Vector3(Range(rng, -0.035f, 0.035f), Range(rng, 0.11f, 0.16f), Range(rng, -0.035f, 0.035f)) * size;
                        AddLimb(b, foot, tip, 0.006f * size, 0.002f * size, grass * Range(rng, 0.9f, 1.1f));
                        if (rng.NextDouble() < 0.5)
                            AddLimb(b, tip, tip + (tip - foot).normalized * 0.025f * size, 0.005f * size, 0.002f * size, L(SeedHead));
                    }
                    break;
                case "Feather": // feather grass: long, fine arching blades with pale plumes
                    for (int i = rng.Next(5, 8); i > 0; i--)
                    {
                        float a  = Range(rng, 0f, Mathf.PI * 2f);
                        var dir  = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
                        var bend = root + dir * 0.03f * size + Vector3.up * 0.09f * size;
                        var tip  = bend + dir * 0.05f * size + Vector3.up * 0.01f * size;
                        AddLimb(b, root, bend, 0.004f * size, 0.003f * size, grass);
                        AddLimb(b, bend, tip, 0.003f * size, 0.001f * size, grass);
                        AddLimb(b, bend, tip + Vector3.up * 0.005f * size, 0.006f * size, 0.002f * size, Plume);
                    }
                    break;
                case "Hummock": // spinifex: a spiky dome of needle-like leaves
                {
                    var c = root + Vector3.up * 0.015f * size;
                    AddBlob(b, rng, c, 0.035f * size, 0.5f, 0, grass * 0.8f);
                    for (int i = rng.Next(12, 18); i > 0; i--)
                    {
                        float a = Range(rng, 0f, Mathf.PI * 2f), e = Range(rng, 0.15f, 1.2f);
                        var dir = new Vector3(Mathf.Cos(a) * Mathf.Cos(e), Mathf.Sin(e), Mathf.Sin(a) * Mathf.Cos(e));
                        AddLimb(b, c, c + dir * Range(rng, 0.045f, 0.065f) * size, 0.004f * size, 0.0005f * size, grass * Range(rng, 0.95f, 1.15f));
                    }
                    break;
                }
                default: // short tufts
                    AddTuft(b, rng, root, size, grass);
                    AddTuft(b, rng, root + new Vector3(0.02f, 0f, 0.015f) * size, size, grass);
                    break;
            }
        }

        // `s` is the frond length
        static void AddShapedGroundFern(Builder b, System.Random rng, Vector3 root, float s, string shape)
        {
            switch (shape)
            {
                case "Nest": // bird's-nest fern: a vase of broad, glossy, undivided leaves
                    AddFrondRosette(b, rng, root + Vector3.up * 0.003f, rng.Next(7, 10), s * 1.1f, s * 0.9f, s * 0.1f, s * 0.32f,
                                    Color.Lerp(L(FernGreen), L(FernLight), 0.6f));
                    break;
                case "Tall": // royal fern: upright fronds and a rusty fertile spike in the middle
                    AddFrondRosette(b, rng, root + Vector3.up * 0.003f, rng.Next(5, 8), s * 0.9f, s * 1.1f, s * 0.15f, s * 0.15f, L(FernGreen));
                    AddLimb(b, root, root + Vector3.up * s * 1.2f, 0.03f * s, 0.015f * s, L(Sporangium));
                    break;
                default:
                    AddGroundFern(b, rng, root, s);
                    break;
            }
        }

        // ---- Helpers ----

        static void Trunk(Builder b, Vector3 root, Vector3 top, float r0, float r1, Color bark) =>
            AddLimb(b, root - Vector3.up * 0.01f, top, r0, r1, bark);

        // `count` branches spreading from `from` out to `reach` and up by `rise`
        static void Limbs(Builder b, System.Random rng, Vector3 from, int count, float reach, float rise, float radius, Color bark)
        {
            float a0 = Range(rng, 0f, Mathf.PI * 2f);
            for (int i = 0; i < count; i++)
            {
                float a = a0 + (i + Range(rng, -0.2f, 0.2f)) * Mathf.PI * 2f / count;
                AddLimb(b, from, from + new Vector3(Mathf.Cos(a) * reach * 0.7f, rise, Mathf.Sin(a) * reach * 0.7f), radius, radius * 0.5f, bark);
            }
        }

        // Overlapping leaf clumps filling an ellipsoid: one in the middle (so it's never hollow) and
        // `count` around its upper surface, lighter toward the top where the sun catches them.
        static void AddCrown(Builder b, System.Random rng, Vector3 center, Vector3 radii, int count, float clump, Color leaf, float lightTop = 0.12f)
        {
            AddBlob(b, rng, center, Mathf.Min(radii.x, radii.z) * 0.8f, radii.y / Mathf.Max(radii.x, 1e-4f), 1, leaf * 0.9f);
            for (int i = 0; i < count; i++)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                float y = Range(rng, -0.35f, 1f);
                float r = Mathf.Sqrt(1f - y * y);
                var p   = center + Vector3.Scale(new Vector3(Mathf.Cos(a) * r, y, Mathf.Sin(a) * r), radii) * 0.8f;
                AddBlob(b, rng, p, clump * Range(rng, 0.8f, 1.2f), 0.85f, 1, leaf * (1f + lightTop * y) * Range(rng, 0.93f, 1.05f));
            }
        }

        // Small coloured blobs (blossoms, berries) scattered over the upper surface of an ellipsoid
        static void Dots(Builder b, System.Random rng, Vector3 center, Vector3 radii, int count, float r, Color color)
        {
            for (int i = 0; i < count; i++)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                float y = Range(rng, -0.1f, 0.95f);
                float k = Mathf.Sqrt(1f - y * y);
                AddBlob(b, rng, center + Vector3.Scale(new Vector3(Mathf.Cos(a) * k, y, Mathf.Sin(a) * k), radii), r, 0.8f, 0, color * Range(rng, 0.92f, 1.05f));
            }
        }

        // A trunk in alternating colour bands (birch marks, jointed stems)
        static void Banded(Builder b, System.Random rng, Vector3 from, Vector3 to, float r0, float r1, Color main, Color band, int segments)
        {
            for (int i = 0; i < segments; i++)
            {
                float t0 = i / (float)segments, t1 = (i + 1) / (float)segments;
                bool mark = i % 2 == 1 && rng.NextDouble() < 0.8;
                AddLimb(b, Vector3.Lerp(from, to, t0), Vector3.Lerp(from, to, t1), Mathf.Lerp(r0, r1, t0), Mathf.Lerp(r0, r1, t1),
                        mark ? Color.Lerp(main, band, 0.75f) : main * Range(rng, 0.95f, 1.03f));
            }
        }

        // Flared root wedges around the foot of a big tree
        static void Buttresses(Builder b, System.Random rng, Vector3 root, float reach, float height, float radius, Color bark)
        {
            float a0 = Range(rng, 0f, Mathf.PI * 2f);
            for (int i = 0, n = rng.Next(4, 6); i < n; i++)
            {
                float a  = a0 + i * Mathf.PI * 2f / n;
                var foot = root + new Vector3(Mathf.Cos(a) * reach, -0.01f, Mathf.Sin(a) * reach);
                AddLimb(b, foot, root + Vector3.up * height, radius * 0.6f, radius, bark);
            }
        }

        // Conifer of stacked bough tiers between `from` and `to` (fractions of the height h), with
        // radii from r0 at the bottom to r1 at the top; depth = each tier's height relative to h.
        static void Tiers(Builder b, System.Random rng, Vector3 root, float s, float h, int tiers, float from, float to,
                          float r0, float r1, float depth, Color dark, Color tip, Color bark, float trunk = 0.03f, bool spire = true)
        {
            var lean = new Vector3(Range(rng, -0.025f, 0.025f), 0f, Range(rng, -0.025f, 0.025f)) * h;
            AddLimb(b, root - Vector3.up * 0.01f, root + Vector3.up * (to + 0.05f) * h + lean, trunk * s, trunk * 0.3f * s, bark);
            for (int i = 0; i < tiers; i++)
            {
                float t = i / (float)Mathf.Max(1, tiers - 1);
                var center = root + Vector3.up * Mathf.Lerp(from, to, t) * h + lean * t;
                float r = Mathf.Lerp(r0, r1, t) * s * Range(rng, 0.9f, 1.1f);
                AddBoughTier(b, rng, center, r, depth * h, Color.Lerp(dark, tip, t * 0.8f));
            }
            if (spire) AddCone(b, rng, root + Vector3.up * (to + 0.04f) * h + lean, r1 * 0.5f * s, 0.12f * h, tip);
        }

        // ---- Blossom and fruit (plants.json "blossom", "fruit", "fruitForm") ----

        static readonly Dictionary<string, Color> parsedColors = new();

        static bool TryColor(string hex, out Color c)
        {
            c = Color.white;
            if (string.IsNullOrEmpty(hex)) return false;
            if (parsedColors.TryGetValue(hex, out c)) return true;
            if (!ColorUtility.TryParseHtmlString(hex, out c)) return false;
            parsedColors[hex] = c;
            return true;
        }

        // Dots the plant just built (vertices from `from` on) with its blossom and fruit. They sit on
        // its own leaf surfaces (green vertices facing out), so this works for every form: round
        // crowns, conifer tiers, palm and fern fronds, cycad rosettes, shrubs. Upright things (spore
        // cones, fir cones, flowers) go on top; hanging fruit, pods and catkins on the sides and
        // underneath, pointing down. `s` is the plant's scale.
        static void AddFruitAndBlossom(Builder b, System.Random rng, int from, float s, PlantDefinition plant)
        {
            bool bloom = TryColor(plant.blossom, out var petal);
            bool fruit = TryColor(plant.fruit, out var fruitColor);
            if (!bloom && !fruit) return;

            var top = new List<int>();   // leafy, facing up
            var side = new List<int>();  // leafy, facing out or down
            for (int i = from; i < b.VertexCount; i += 3) // one corner per triangle is plenty
            {
                var c = b.VertexColor(i);
                if (!IsLeafColor(c)) continue; // leaves only, not bark or rock
                var n = b.Normal(i);
                if (n.y > 0.45f) top.Add(i);
                else if (n.y > -0.7f) side.Add(i);
            }
            if (top.Count + side.Count == 0) return;
            int Pick(List<int> prefer)
            {
                var list = prefer.Count > 0 ? prefer : (top.Count > 0 ? top : side);
                return list[rng.Next(list.Count)];
            }

            if (bloom)
            {
                // flowers in little clusters over the upper crown, each with a paler or golden heart
                var heart = petal.grayscale > 0.6f ? new Color(0.98f, 0.82f, 0.25f) : Color.Lerp(petal, Color.white, 0.6f);
                for (int i = 0, n = rng.Next(14, 22); i < n; i++)
                {
                    int v = Pick(rng.NextDouble() < 0.75 ? top : side);
                    var at = b.Vertex(v) + b.Normal(v) * 0.01f * s;
                    for (int k = 0, m = rng.Next(1, 3); k < m; k++)
                    {
                        var p = at + new Vector3(Range(rng, -1f, 1f), Range(rng, -0.3f, 0.6f), Range(rng, -1f, 1f)) * 0.018f * s;
                        AddGem(b, p, new Vector3(0.017f, 0.008f, 0.017f) * s, petal * Range(rng, 0.92f, 1.08f), b.Normal(v));
                        if (k == 0) AddGem(b, p + b.Normal(v) * 0.005f * s, Vector3.one * 0.005f * s, heart, b.Normal(v));
                    }
                }
            }
            if (!fruit) return;

            var down = Vector3.down;
            switch (plant.fruitForm)
            {
                case "Berry": // clusters of small berries
                    for (int i = 0, n = rng.Next(8, 13); i < n; i++)
                    {
                        int v = Pick(side);
                        var at = b.Vertex(v) + b.Normal(v) * 0.008f * s;
                        for (int k = 0, m = rng.Next(3, 6); k < m; k++)
                            AddGem(b, at + new Vector3(Range(rng, -1f, 1f), Range(rng, -1.5f, 0f), Range(rng, -1f, 1f)) * 0.008f * s,
                                   Vector3.one * 0.007f * s, fruitColor * Range(rng, 0.85f, 1.1f), b.Normal(v));
                    }
                    break;
                case "Nut": // acorns, beechnuts, gumnuts: small and dull, in twos and threes
                case "Seed":
                    for (int i = 0, n = rng.Next(8, 13); i < n; i++)
                    {
                        int v = Pick(side);
                        var at = b.Vertex(v) + b.Normal(v) * 0.008f * s;
                        for (int k = 0, m = rng.Next(1, 4); k < m; k++)
                            AddGem(b, at + new Vector3(Range(rng, -1f, 1f), -k, Range(rng, -1f, 1f)) * 0.01f * s,
                                   new Vector3(0.009f, 0.012f, 0.009f) * s, fruitColor * Range(rng, 0.9f, 1.1f), down);
                    }
                    break;
                case "Samara": // winged seeds (maple keys) hanging in bunches, catching the light
                    for (int i = 0, n = rng.Next(8, 12); i < n; i++)
                    {
                        int v = Pick(side);
                        var at = b.Vertex(v) + b.Normal(v) * 0.01f * s;
                        for (int k = 0; k < 2; k++)
                        {
                            var wing = Quaternion.Euler(0f, Range(rng, 0f, 360f), 0f) * new Vector3(0.012f, -0.006f, 0f) * s;
                            AddGem(b, at + wing, new Vector3(0.014f, 0.004f, 0.007f) * s, fruitColor * Range(rng, 0.9f, 1.1f), wing.normalized);
                        }
                    }
                    break;
                case "Ball": // plane-tree seed balls dangling on stalks
                    for (int i = 0, n = rng.Next(6, 10); i < n; i++)
                    {
                        int v = Pick(side);
                        var at = b.Vertex(v) + b.Normal(v) * 0.01f * s;
                        AddLimb(b, at, at + down * 0.03f * s, 0.0015f * s, 0.0015f * s, Bark);
                        AddGem(b, at + down * 0.035f * s, Vector3.one * 0.012f * s, fruitColor, down);
                    }
                    break;
                case "Catkin": // birch and alder catkins: long, drooping tassels
                    for (int i = 0, n = rng.Next(10, 16); i < n; i++)
                    {
                        int v = Pick(side);
                        var at = b.Vertex(v) + b.Normal(v) * 0.006f * s;
                        var tip = at + (down + b.Normal(v) * 0.3f).normalized * 0.035f * s;
                        AddLimb(b, at, tip, 0.005f * s, 0.003f * s, fruitColor * Range(rng, 0.9f, 1.1f));
                    }
                    break;
                case "Cone": // pendant cones (pine, spruce) hanging from the tiers
                    for (int i = 0, n = rng.Next(7, 12); i < n; i++)
                    {
                        int v = Pick(side);
                        var at = b.Vertex(v) + b.Normal(v) * 0.006f * s;
                        AddGem(b, at + down * 0.014f * s, new Vector3(0.01f, 0.022f, 0.01f) * s, fruitColor * Range(rng, 0.9f, 1.1f), down);
                    }
                    break;
                case "UprightCone": // fir and cedar cones standing on the upper branches like candles
                case "Strobilus":   // spore cones of tree ferns, horsetails, scale trees, cycads
                    for (int i = 0, n = rng.Next(plant.fruitForm == "Strobilus" ? 8 : 6, plant.fruitForm == "Strobilus" ? 14 : 10); i < n; i++)
                    {
                        int v = Pick(top);
                        var at = b.Vertex(v) + Vector3.up * 0.016f * s;
                        AddGem(b, at, new Vector3(0.009f, 0.02f, 0.009f) * s, fruitColor * Range(rng, 0.9f, 1.15f), Vector3.up);
                    }
                    break;
                case "Pod": // long hanging pods (kapok, acacia, glossopterids)
                    for (int i = 0, n = rng.Next(6, 10); i < n; i++)
                    {
                        int v = Pick(side);
                        var at = b.Vertex(v) + b.Normal(v) * 0.008f * s;
                        AddLimb(b, at, at + (down + b.Normal(v) * 0.4f).normalized * 0.05f * s, 0.008f * s, 0.004f * s, fruitColor * Range(rng, 0.9f, 1.1f));
                    }
                    break;
                case "Hanging": // dates, mangrove propagules: bunches hanging well below the crown
                    for (int i = 0, n = rng.Next(4, 7); i < n; i++)
                    {
                        int v = Pick(side);
                        var at = b.Vertex(v);
                        for (int k = 0, m = rng.Next(4, 8); k < m; k++)
                        {
                            var off = new Vector3(Range(rng, -1f, 1f), 0f, Range(rng, -1f, 1f)) * 0.012f * s;
                            AddLimb(b, at + off, at + off + down * Range(rng, 0.03f, 0.06f) * s, 0.004f * s, 0.006f * s, fruitColor * Range(rng, 0.85f, 1.1f));
                        }
                    }
                    break;
                case "Coconut": // a cluster of big nuts right under the crown
                {
                    float topY = float.MinValue; Vector3 crown = default; int count = 0;
                    foreach (var v in top) { var p = b.Vertex(v); crown += p; count++; topY = Mathf.Max(topY, p.y); }
                    if (count == 0) break;
                    crown /= count;
                    for (int k = 0, m = rng.Next(4, 8); k < m; k++)
                        AddGem(b, new Vector3(crown.x, crown.y - 0.03f * s, crown.z) + new Vector3(Range(rng, -1f, 1f), Range(rng, -0.6f, 0f), Range(rng, -1f, 1f)) * 0.03f * s,
                               Vector3.one * 0.022f * s, fruitColor * Range(rng, 0.85f, 1.1f), down);
                    break;
                }
                default: // "Round": apples, figs, oranges, ginkgo nuts: round fruit among the leaves
                    for (int i = 0, n = rng.Next(8, 14); i < n; i++)
                    {
                        int v = Pick(rng.NextDouble() < 0.7 ? side : top);
                        AddGem(b, b.Vertex(v) + b.Normal(v) * 0.01f * s, Vector3.one * 0.014f * s, fruitColor * Range(rng, 0.85f, 1.1f), b.Normal(v));
                    }
                    break;
            }
        }

        // Repaints the green leaves of the plant just built (vertices from `from` on) in its crown
        // colour, keeping their light and shade: works for any form (ginkgo fans, larch tiers, crowns)
        static void PaintCrown(Builder b, int from)
        {
            if (!hasCrown) return;
            float sum = 0f; int n = 0;
            for (int i = from; i < b.VertexCount; i++)
            {
                var c = b.VertexColor(i);
                if (c.g > c.r * 1.02f && c.g > c.b * 0.95f) { sum += c.grayscale; n++; }
            }
            if (n == 0) return;
            float mean = sum / n;
            for (int i = from; i < b.VertexCount; i++)
            {
                var c = b.VertexColor(i);
                if (!(c.g > c.r * 1.02f && c.g > c.b * 0.95f)) continue;
                b.SetVertexColor(i, crownColor * Mathf.Clamp(c.grayscale / mean, 0.55f, 1.35f));
            }
        }

        // Green leaves, or the plant's coloured crown (compared by hue, so shading doesn't matter)
        static bool IsLeafColor(Color c)
        {
            if (c.g > c.r * 1.02f && c.g > c.b * 0.95f) return true;
            if (!hasCrown) return false;
            float sum = c.r + c.g + c.b, k = crownColor.r + crownColor.g + crownColor.b;
            if (sum < 1e-4f || k < 1e-4f) return false;
            return Mathf.Abs(c.r / sum - crownColor.r / k) + Mathf.Abs(c.g / sum - crownColor.g / k) + Mathf.Abs(c.b / sum - crownColor.b / k) < 0.12f;
        }

        // Tiny faceted body (8 triangles): cheap enough to scatter hundreds of flowers and fruit.
        // `radii` along (side, axis, side) with the axis turned to `up`.
        static void AddGem(Builder b, Vector3 center, Vector3 radii, Color color, Vector3 up)
        {
            var rot = Quaternion.FromToRotation(Vector3.up, up.sqrMagnitude > 1e-6f ? up.normalized : Vector3.up);
            var px = center + rot * new Vector3(radii.x, 0f, 0f);
            var nx = center - rot * new Vector3(radii.x, 0f, 0f);
            var pz = center + rot * new Vector3(0f, 0f, radii.z);
            var nz = center - rot * new Vector3(0f, 0f, radii.z);
            var py = center + rot * new Vector3(0f, radii.y, 0f);
            var ny = center - rot * new Vector3(0f, radii.y, 0f);
            var lit = color * 1.08f; var dark = color * 0.82f; // facets catch the light
            b.AddTri(px, pz, py, lit, center);  b.AddTri(pz, nx, py, lit, center);
            b.AddTri(nx, nz, py, lit, center);  b.AddTri(nz, px, py, lit, center);
            b.AddTri(px, pz, ny, dark, center); b.AddTri(pz, nx, ny, dark, center);
            b.AddTri(nx, nz, ny, dark, center); b.AddTri(nz, px, ny, dark, center);
        }
    }
}