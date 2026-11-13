using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    public static class WorldGenerator
    {
        public static void Generate(HexCell[,] cells, int width, int height, int seed)
        {
            var terrains = new Dictionary<TerrainKind, TerrainType>();
            foreach (var t in Resources.LoadAll<TerrainType>("Terrains"))
                terrains[t.kind] = t;

            if (terrains.Count == 0)
            {
                Debug.LogWarning("[WorldGenerator] No terrain assets found in Resources/Terrains.");
                return;
            }

            var rng   = new System.Random(seed);
            float eOX = (float)(rng.NextDouble() * 1000);
            float eOY = (float)(rng.NextDouble() * 1000);
            float mOX = (float)(rng.NextDouble() * 1000);
            float mOY = (float)(rng.NextDouble() * 1000);
            float fOX = (float)(rng.NextDouble() * 1000);
            float fOY = (float)(rng.NextDouble() * 1000);
            const float scale = 0.2f;
            const float forestScale = 0.35f; // finer than climate noise → patchy woods, not one huge forest

            for (int r = 0; r < height; r++)
            for (int q = 0; q < width; q++)
            {
                // fBm elevation (5 octaves) + island mask
                float e  = FBm(q * scale + eOX, r * scale + eOY, 5);
                float cx = (q / (float)(width  - 1) - 0.5f) * 2f;
                float cy = (r / (float)(height - 1) - 0.5f) * 2f;
                e = Mathf.Clamp01(e - Mathf.Sqrt(cx * cx + cy * cy) * 0.45f);

                // fBm moisture (4 octaves)
                float m = FBm(q * scale + mOX, r * scale + mOY, 4);

                // Temperature: hot at equator (center row), cold at poles and altitude
                float lat  = Mathf.Abs(r / (float)(height - 1) - 0.5f) * 2f;
                float temp = Mathf.Clamp01(1f - lat * 0.9f - e * 0.3f);

                var kind = ClassifyTerrain(e, m, temp);
                if (terrains.TryGetValue(kind, out var terrain))
                    cells[q, r].SetTerrain(terrain);
                cells[q, r].SetElevation(ToElevationLevel(e, kind));

                float f = FBm(q * forestScale + fOX, r * forestScale + fOY, 3);
                cells[q, r].SetFeature(ChooseFeature(kind, m, temp, f));
            }

            Debug.Log($"[WorldGenerator] Generated world (seed={seed}).");
        }

        public const int MaxElevation = 10;
        const float WaterThreshold    = 0.38f; // matches the FreshWater cutoff in ClassifyTerrain
        const float MountainThreshold = 0.82f; // matches the Mountain cutoff in ClassifyTerrain

        // Lowest terrace level of mountain-height terrain (Mountain, or IceSheet at that altitude)
        public static readonly int MountainElevation = ToElevationLevel(MountainThreshold, TerrainKind.Mountain);

        // Quantize raw elevation into terrace levels: water = 0, land = 1..MaxElevation.
        // Each land step spans an equal slice of the noise range above the waterline.
        static int ToElevationLevel(float e, TerrainKind kind)
        {
            if (kind is TerrainKind.SaltWater or TerrainKind.FreshWater) return 0;
            float t = Mathf.InverseLerp(WaterThreshold, 0.9f, e);
            return Mathf.Clamp(1 + Mathf.FloorToInt(t * MaxElevation), 1, MaxElevation);
        }

        // Forests grow on moist, not-too-cold land; f is patchiness noise.
        // Conifers take the cold end (tundra edge, high latitudes, altitude).
        static TerrainFeature ChooseFeature(TerrainKind kind, float m, float temp, float f)
        {
            bool forested = kind switch
            {
                TerrainKind.Plain   => m > 0.45f && f > 0.45f,
                TerrainKind.Hill    => m > 0.40f && f > 0.50f,
                TerrainKind.Wetland => f > 0.55f,
                TerrainKind.Tundra  => m > 0.50f && f > 0.50f,
                _                   => false,
            };
            if (!forested) return TerrainFeature.None;
            return kind == TerrainKind.Tundra || temp < 0.45f ? TerrainFeature.ConiferForest : TerrainFeature.BroadleafForest;
        }

        // Fractal Brownian Motion: sum octaves at doubling frequency, halving amplitude
        static float FBm(float x, float y, int octaves)
        {
            float val = 0f, amp = 0.5f, freq = 1f, max = 0f;
            for (int o = 0; o < octaves; o++)
            {
                val  += Mathf.PerlinNoise(x * freq, y * freq) * amp;
                max  += amp;
                amp  *= 0.5f;
                freq *= 2f;
            }
            return val / max;
        }

        // Whittaker biome classification: elevation drives water/mountain/hill,
        // then temperature × moisture drive lowland biomes.
        static TerrainKind ClassifyTerrain(float e, float m, float temp)
        {
            // Water
            if (e < 0.30f) return TerrainKind.SaltWater;
            if (e < 0.38f) return TerrainKind.FreshWater;

            // High-elevation terrain overrides climate
            if (e > MountainThreshold) return temp < 0.20f ? TerrainKind.IceSheet : TerrainKind.Mountain;
            if (e > 0.62f) return TerrainKind.Hill;

            // Lowland: Whittaker biome (temperature × moisture)
            if (temp < 0.15f) return TerrainKind.IceSheet;
            if (temp < 0.28f) return TerrainKind.Tundra;
            if (m   < 0.25f) return TerrainKind.Desert;
            if (m   > 0.72f) return TerrainKind.Wetland;
            return TerrainKind.Plain;
        }
    }
}
