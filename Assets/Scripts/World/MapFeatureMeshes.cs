using System.Collections.Generic;
using UnityEngine;

namespace NaturalHistory.World
{
    // Low-poly, flat-shaded props that sit on a hex tile's top face: mountain peaks and tree clusters.
    // Colors are baked into vertex colors so all props share one material (MapFeature shader).
    // Meshes are centred on the tile (y = 0 is the top face) and stay inside the hex's inner radius.
    public static class MapFeatureMeshes
    {
        static readonly Color Rock   = new(0.46f, 0.42f, 0.38f);
        static readonly Color Snow   = new(0.94f, 0.96f, 0.99f);
        static readonly Color Bark   = new(0.36f, 0.25f, 0.16f);
        static readonly Color Leaf   = new(0.30f, 0.52f, 0.20f);
        static readonly Color Needle = new(0.12f, 0.33f, 0.20f);

        // One large peak plus 1–2 smaller ones. snowLine = fraction of the main peak's height
        // (from the top) covered in snow; smaller peaks below that height stay bare rock.
        public static Mesh CreateMountain(System.Random rng, float size, float snowLine)
        {
            var b = new Builder();
            float mainHeight = size * Range(rng, 0.9f, 1.2f);
            float snowY      = mainHeight * (1f - snowLine);

            var mainCenter = new Vector3(Range(rng, -0.08f, 0.08f), 0f, Range(rng, -0.08f, 0.08f)) * size;
            AddPeak(b, rng, mainCenter, size * Range(rng, 0.42f, 0.5f), mainHeight, snowY);

            int extra   = rng.Next(1, 3);
            float angle = Range(rng, 0f, 360f);
            for (int i = 0; i < extra; i++, angle += Range(rng, 110f, 160f))
            {
                float a = angle * Mathf.Deg2Rad;
                float d = size * Range(rng, 0.32f, 0.4f);
                var center = new Vector3(Mathf.Sin(a) * d, 0f, Mathf.Cos(a) * d);
                AddPeak(b, rng, center, size * Range(rng, 0.24f, 0.32f), mainHeight * Range(rng, 0.45f, 0.65f), snowY);
            }
            return b.ToMesh("MountainPeaks");
        }

        // 7–10 trees scattered over the tile without overlapping.
        public static Mesh CreateForest(System.Random rng, float size, bool conifer)
        {
            var b = new Builder();
            var spots = new List<Vector2>();
            int target = rng.Next(7, 11);
            float minGap = 0.17f * size;
            for (int tries = 0; tries < 80 && spots.Count < target; tries++)
            {
                float a = Range(rng, 0f, Mathf.PI * 2f);
                float d = Mathf.Sqrt((float)rng.NextDouble()) * 0.62f * size; // sqrt → uniform over the disc
                var p = new Vector2(Mathf.Sin(a) * d, Mathf.Cos(a) * d);
                if (spots.Exists(s => (s - p).sqrMagnitude < minGap * minGap)) continue;
                spots.Add(p);
            }

            foreach (var p in spots)
            {
                var root  = new Vector3(p.x, 0f, p.y);
                float s   = size * Range(rng, 0.8f, 1.25f);
                if (conifer) AddConifer(b, rng, root, s);
                else         AddBroadleaf(b, rng, root, s);
            }
            return b.ToMesh(conifer ? "ConiferForest" : "BroadleafForest");
        }

        // Jittered six-sided cone; faces above snowY are white.
        static void AddPeak(Builder b, System.Random rng, Vector3 center, float radius, float height, float snowY)
        {
            const int sides = 6;
            const float baseY = -0.01f; // sink slightly into the tile so no seam shows
            var apex = center + new Vector3(Range(rng, -0.1f, 0.1f) * radius, height, Range(rng, -0.1f, 0.1f) * radius);
            var ring = Ring(rng, center + Vector3.up * baseY, radius, sides, 0.15f);
            var inside = center + Vector3.up * baseY;

            // Fraction of the way up each edge where snow begins (≥ 1 → no snow on this peak)
            float s = (snowY - baseY) / (height - baseY);
            for (int i = 0; i < sides; i++)
            {
                var p0 = ring[i];
                var p1 = ring[(i + 1) % sides];
                if (s >= 1f)
                {
                    b.AddTri(p0, p1, apex, Shade(rng, Rock), inside);
                    continue;
                }
                var m0 = Vector3.Lerp(p0, apex, s);
                var m1 = Vector3.Lerp(p1, apex, s);
                b.AddQuad(p0, p1, m1, m0, Shade(rng, Rock), inside);
                b.AddTri(m0, m1, apex, Shade(rng, Snow, 0.04f), inside);
            }
        }

        static void AddConifer(Builder b, System.Random rng, Vector3 root, float s)
        {
            var color = Shade(rng, Needle);
            AddTrunk(b, root, 0.025f * s, 0.08f * s);
            AddCone(b, rng, root + Vector3.up * 0.05f * s, 0.12f * s,  0.20f * s, color);
            AddCone(b, rng, root + Vector3.up * 0.14f * s, 0.085f * s, 0.17f * s, color * 1.1f);
        }

        // Trunk plus a faceted, roughly round crown (double pyramid).
        static void AddBroadleaf(Builder b, System.Random rng, Vector3 root, float s)
        {
            const int sides = 6;
            var color = Shade(rng, Leaf);
            AddTrunk(b, root, 0.025f * s, 0.12f * s);

            var mid    = root + Vector3.up * 0.18f * s;
            var top    = root + Vector3.up * 0.31f * s;
            var bottom = root + Vector3.up * 0.09f * s;
            var ring   = Ring(rng, mid, 0.11f * s, sides, 0.2f);
            for (int i = 0; i < sides; i++)
            {
                var p0 = ring[i];
                var p1 = ring[(i + 1) % sides];
                b.AddTri(p0, p1, top, color * 1.08f, mid);
                b.AddTri(p0, p1, bottom, color * 0.85f, mid);
            }
        }

        static void AddTrunk(Builder b, Vector3 root, float radius, float height)
        {
            const int sides = 4;
            var inside = root + Vector3.up * height * 0.5f;
            for (int i = 0; i < sides; i++)
            {
                float a0 = Mathf.PI * 2f * i / sides, a1 = Mathf.PI * 2f * (i + 1) / sides;
                var p0 = root + new Vector3(Mathf.Sin(a0), 0f, Mathf.Cos(a0)) * radius;
                var p1 = root + new Vector3(Mathf.Sin(a1), 0f, Mathf.Cos(a1)) * radius;
                b.AddQuad(p0, p1, p1 + Vector3.up * height, p0 + Vector3.up * height, Bark, inside);
            }
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
            public void AddTri(Vector3 a, Vector3 b, Vector3 c, Color color, Vector3 inside)
            {
                var n = Vector3.Cross(b - a, c - a);
                if (Vector3.Dot(n, (a + b + c) / 3f - inside) < 0f) { (b, c) = (c, b); n = -n; }
                n.Normalize();

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
