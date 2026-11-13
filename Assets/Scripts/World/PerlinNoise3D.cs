using UnityEngine;

namespace NaturalHistory.World
{
    // Ken Perlin's improved noise in 3D. Unity only ships 2D Perlin noise; the world generator
    // needs 3D to sample around a cylinder so the map wraps east–west without a seam.
    public static class PerlinNoise3D
    {
        static readonly int[] perm = BuildPermutation();

        // Roughly −1..1
        public static float Sample(float x, float y, float z)
        {
            int xi = Mathf.FloorToInt(x), yi = Mathf.FloorToInt(y), zi = Mathf.FloorToInt(z);
            x -= xi; y -= yi; z -= zi;
            xi &= 255; yi &= 255; zi &= 255;
            float u = Fade(x), v = Fade(y), w = Fade(z);

            int a = perm[xi] + yi,     aa = perm[a] + zi, ab = perm[a + 1] + zi;
            int b = perm[xi + 1] + yi, ba = perm[b] + zi, bb = perm[b + 1] + zi;

            return Mathf.Lerp(
                Mathf.Lerp(Mathf.Lerp(Grad(perm[aa],     x, y,     z),     Grad(perm[ba],     x - 1, y,     z),     u),
                           Mathf.Lerp(Grad(perm[ab],     x, y - 1, z),     Grad(perm[bb],     x - 1, y - 1, z),     u), v),
                Mathf.Lerp(Mathf.Lerp(Grad(perm[aa + 1], x, y,     z - 1), Grad(perm[ba + 1], x - 1, y,     z - 1), u),
                           Mathf.Lerp(Grad(perm[ab + 1], x, y - 1, z - 1), Grad(perm[bb + 1], x - 1, y - 1, z - 1), u), v),
                w);
        }

        static float Fade(float t) => t * t * t * (t * (t * 6f - 15f) + 10f);

        static float Grad(int hash, float x, float y, float z)
        {
            int h = hash & 15;
            float u = h < 8 ? x : y;
            float v = h < 4 ? y : h is 12 or 14 ? x : z;
            return ((h & 1) == 0 ? u : -u) + ((h & 2) == 0 ? v : -v);
        }

        // Fixed shuffle (the world seed only picks sampling offsets), so maps stay reproducible.
        static int[] BuildPermutation()
        {
            var p = new int[512];
            var rng = new System.Random(1337);
            for (int i = 0; i < 256; i++) p[i] = i;
            for (int i = 255; i > 0; i--) { int j = rng.Next(i + 1); (p[i], p[j]) = (p[j], p[i]); }
            for (int i = 0; i < 256; i++) p[256 + i] = p[i];
            return p;
        }
    }
}
