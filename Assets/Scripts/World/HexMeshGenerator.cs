using UnityEngine;

namespace NaturalHistory.World
{
    public static class HexMeshGenerator
    {
        const int ShoulderSteps = 3; // segments in the rounded top edge

        // Pointy-top hexagonal prism with a rounded top edge. Top face sits at y=height, bottom at y=0.
        // bevel = horizontal width of the rounded shoulder (0 → sharp edge); it is clamped to the
        // tile height, so low water tiles get only a slight rounding. height=0 → flat disc.
        //
        // Vertices are shared between neighbouring faces and normals blend from straight up (flat
        // top) to pointing out of each corner (walls), so the edge catches light like a rounded block.
        public static Mesh Create(float outerRadius, float height = 0f, float bevel = 0f)
        {
            var mesh = new Mesh { name = "HexTile" };

            bool hasSides = height > 0.001f;
            bevel = hasSides ? Mathf.Min(bevel, outerRadius * 0.3f, height) : 0f;
            float drop = bevel * 0.7f; // how far the shoulder falls below the top face

            // Profile from the edge of the flat top down to the ground: inset from the outer edge,
            // height, and angle of the normal away from vertical.
            int rings   = 1 + (bevel > 0f ? ShoulderSteps : 0) + (hasSides ? 1 : 0);
            var inset   = new float[rings];
            var ringY   = new float[rings];
            var tilt    = new float[rings];
            int k = 0;
            inset[k] = bevel; ringY[k] = height; tilt[k] = 0f; k++;
            if (bevel > 0f)
            {
                for (int s = 1; s <= ShoulderSteps; s++, k++)
                {
                    float a  = s / (float)ShoulderSteps * Mathf.PI * 0.5f;
                    inset[k] = bevel * (1f - Mathf.Sin(a));
                    ringY[k] = height - drop * (1f - Mathf.Cos(a));
                    tilt[k]  = a;
                }
            }
            if (hasSides) { inset[k] = 0f; ringY[k] = 0f; tilt[k] = Mathf.PI * 0.5f; }

            var dirs = new Vector3[6]; // unit vectors to the corners
            for (int i = 0; i < 6; i++)
            {
                float a = Mathf.Deg2Rad * (60f * i);
                dirs[i] = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a));
            }

            // Vertex 0 = top centre, then 6 corners per ring. An edge inset of d moves a corner by d / cos 30°.
            int vertCount = 1 + rings * 6;
            var verts = new Vector3[vertCount];
            var norms = new Vector3[vertCount];
            var uvs   = new Vector2[vertCount];
            verts[0] = new Vector3(0f, height, 0f);
            norms[0] = Vector3.up;
            uvs[0]   = new Vector2(0.5f, 0.5f);
            for (int r = 0; r < rings; r++)
            for (int i = 0; i < 6; i++)
            {
                int v = 1 + r * 6 + i;
                float radius = outerRadius - inset[r] / 0.8660254f;
                verts[v] = dirs[i] * radius + Vector3.up * ringY[r];
                norms[v] = (Vector3.up * Mathf.Cos(tilt[r]) + dirs[i] * Mathf.Sin(tilt[r])).normalized;
                // Radial UVs: 0.5 at the centre, corners at distance 0.5 (the shader darkens toward the rim)
                uvs[v]   = new Vector2(0.5f + 0.5f * dirs[i].x * radius / outerRadius, 0.5f + 0.5f * dirs[i].z * radius / outerRadius);
            }

            var tris = new int[(6 + (rings - 1) * 12) * 3];
            int t = 0;
            for (int i = 0; i < 6; i++)
            {
                tris[t++] = 0;
                tris[t++] = 1 + i;
                tris[t++] = 1 + (i + 1) % 6;
            }
            // Bands between consecutive rings; CCW viewed from outside → outward-facing
            for (int r = 0; r < rings - 1; r++)
            for (int i = 0; i < 6; i++)
            {
                int next = (i + 1) % 6;
                int u0 = 1 + r * 6 + i, u1 = 1 + r * 6 + next;
                int l0 = u0 + 6,        l1 = u1 + 6;
                tris[t++] = u0; tris[t++] = l0; tris[t++] = l1;
                tris[t++] = u0; tris[t++] = l1; tris[t++] = u1;
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
