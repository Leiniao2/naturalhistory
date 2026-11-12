using UnityEngine;

namespace NaturalHistory.World
{
    public static class HexMeshGenerator
    {
        // Pointy-top hexagonal prism. Top face sits at y=height, bottom at y=0.
        // height=0 produces a flat disc (top face only).
        public static Mesh Create(float outerRadius, float height = 0f)
        {
            var mesh = new Mesh { name = "HexTile" };

            bool hasSides = height > 0.001f;

            // Corner positions at ground level
            var corners = new Vector3[6];
            for (int i = 0; i < 6; i++)
            {
                float a = Mathf.Deg2Rad * (60f * i);
                corners[i] = new Vector3(outerRadius * Mathf.Sin(a), 0f, outerRadius * Mathf.Cos(a));
            }

            // Top face: 7 verts (center + 6 corners at y=height)
            // Side faces: 6 quads × 4 verts = 24 verts (separate to allow outward normals)
            int vertCount = hasSides ? 7 + 24 : 7;
            var verts = new Vector3[vertCount];
            var norms = new Vector3[vertCount];
            var uvs   = new Vector2[vertCount];

            // --- Top face ---
            verts[0] = new Vector3(0f, height, 0f);
            norms[0] = Vector3.up;
            uvs[0]   = new Vector2(0.5f, 0.5f);
            for (int i = 0; i < 6; i++)
            {
                float a = Mathf.Deg2Rad * (60f * i);
                verts[i + 1] = corners[i] + Vector3.up * height;
                norms[i + 1] = Vector3.up;
                uvs[i + 1]   = new Vector2(0.5f + 0.5f * Mathf.Sin(a), 0.5f + 0.5f * Mathf.Cos(a));
            }

            // Top face triangles
            int triCount = hasSides ? 6 + 12 : 6;
            var tris = new int[triCount * 3];
            for (int i = 0; i < 6; i++)
            {
                tris[i * 3]     = 0;
                tris[i * 3 + 1] = i + 1;
                tris[i * 3 + 2] = (i + 1) % 6 + 1;
            }

            // --- Side faces ---
            if (hasSides)
            {
                for (int i = 0; i < 6; i++)
                {
                    int next = (i + 1) % 6;
                    var mid  = (corners[i] + corners[next]) * 0.5f;
                    var norm = new Vector3(mid.x, 0f, mid.z).normalized;

                    int v0 = 7 + i * 4;
                    verts[v0 + 0] = corners[i]    + Vector3.up * height; // top-left
                    verts[v0 + 1] = corners[next] + Vector3.up * height; // top-right
                    verts[v0 + 2] = corners[next];                        // bottom-right
                    verts[v0 + 3] = corners[i];                           // bottom-left

                    norms[v0 + 0] = norm; norms[v0 + 1] = norm;
                    norms[v0 + 2] = norm; norms[v0 + 3] = norm;

                    uvs[v0 + 0] = new Vector2((float)i / 6,           1f);
                    uvs[v0 + 1] = new Vector2((float)(i + 1) / 6,     1f);
                    uvs[v0 + 2] = new Vector2((float)(i + 1) / 6,     0f);
                    uvs[v0 + 3] = new Vector2((float)i / 6,           0f);

                    int t0 = 18 + i * 6;
                    // CCW winding viewed from outside → outward-facing
                    tris[t0 + 0] = v0; tris[t0 + 1] = v0 + 3; tris[t0 + 2] = v0 + 2;
                    tris[t0 + 3] = v0; tris[t0 + 4] = v0 + 2; tris[t0 + 5] = v0 + 1;
                }
            }

            mesh.vertices  = verts;
            mesh.normals   = norms;
            mesh.uv        = uvs;
            mesh.triangles = tris;
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}
