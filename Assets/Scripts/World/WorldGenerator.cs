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
            const float scale = 0.2f;

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
            }

            Debug.Log($"[WorldGenerator] Generated world (seed={seed}).");
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
            if (e > 0.82f) return temp < 0.20f ? TerrainKind.IceSheet : TerrainKind.Mountain;
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
