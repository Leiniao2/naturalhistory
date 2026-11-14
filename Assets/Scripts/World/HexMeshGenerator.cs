using System.Collections.Generic;
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

        // Land tile whose rim slopes to meet its neighbours instead of stepping up or down. The
        // middle (`solid` × the tile radius) is flat at y=height; from there the top slopes out to
        // the rim, whose corners and edge midpoints sit at the given heights. Neighbours are given
        // the same rim heights, so adjacent tiles meet without a step. Walls run from the rim down
        // to y=0 (seen in the groove between tiles and along coasts).
        //
        // Corner i points 60i degrees clockwise from +Z; edge e faces 60e + 30 (between corners e
        // and e+1). joined[e] = the edge reaches the full cell boundary (cellRadius) with no wall
        // and no rim darkening, so the ground runs straight into that neighbour.
        public static Mesh CreateSloped(float tileRadius, float cellRadius, float height, float solid,
                                        float[] cornerHeights, float[] edgeHeights, bool[] joined)
        {
            var mesh = new Mesh { name = "HexTileSloped" };

            var dirs = new Vector3[6];
            for (int i = 0; i < 6; i++)
            {
                float a = Mathf.Deg2Rad * (60f * i);
                dirs[i] = new Vector3(Mathf.Sin(a), 0f, Mathf.Cos(a));
            }

            // Rim points: corners at even k, edge midpoints at odd k (12 around)
            var rim     = new Vector3[12];
            var rimDark = new bool[12]; // false → keep the shader's rim darkening off here
            for (int i = 0; i < 6; i++)
            {
                bool full = joined[(i + 5) % 6] || joined[i];
                rim[2 * i]     = dirs[i] * (full ? cellRadius : tileRadius) + Vector3.up * cornerHeights[i];
                rimDark[2 * i] = !(joined[(i + 5) % 6] && joined[i]);
            }
            for (int e = 0; e < 6; e++)
            {
                var mid = (rim[2 * e] + rim[(2 * e + 2) % 12]) * 0.5f;
                rim[2 * e + 1]     = new Vector3(mid.x, edgeHeights[e], mid.z);
                rimDark[2 * e + 1] = !joined[e];
            }

            var verts = new List<Vector3>();
            var uvs   = new List<Vector2>();
            var tris  = new List<int>();
            // Radial UVs as in Create (corners at distance 0.5); rim points that shouldn't be
            // darkened get pulled in to the flat middle's UV radius.
            Vector2 Uv(Vector3 p, float pull) => new(0.5f + 0.5f * p.x / tileRadius * pull, 0.5f + 0.5f * p.z / tileRadius * pull);

            verts.Add(new Vector3(0f, height, 0f));
            uvs.Add(new Vector2(0.5f, 0.5f));
            for (int k = 0; k < 12; k++) // flat middle: 1..12
            {
                var p = (k % 2 == 0 ? dirs[k / 2] * tileRadius : (dirs[k / 2] + dirs[(k / 2 + 1) % 6]) * 0.5f * tileRadius) * solid;
                verts.Add(p + Vector3.up * height);
                uvs.Add(Uv(p, 1f));
            }
            for (int k = 0; k < 12; k++) // rim: 13..24
            {
                verts.Add(rim[k]);
                uvs.Add(Uv(rim[k], rimDark[k] ? 1f : solid * tileRadius / new Vector2(rim[k].x, rim[k].z).magnitude));
            }

            // Same winding as Create: clockwise seen from above / outside
            for (int k = 0; k < 12; k++)
            {
                int next = (k + 1) % 12;
                tris.Add(0); tris.Add(1 + k); tris.Add(1 + next);
                int u0 = 1 + k, u1 = 1 + next, l0 = 13 + k, l1 = 13 + next;
                tris.Add(u0); tris.Add(l0); tris.Add(l1);
                tris.Add(u0); tris.Add(l1); tris.Add(u1);
            }

            // Walls get their own vertices so they stay flat-shaded and don't bend the top's normals
            for (int e = 0; e < 6; e++)
            {
                if (joined[e]) continue;
                int b = verts.Count;
                for (int s = 0; s < 3; s++)
                {
                    var top = rim[(2 * e + s) % 12];
                    verts.Add(top);
                    verts.Add(new Vector3(top.x, 0f, top.z));
                    uvs.Add(Uv(top, 1f));
                    uvs.Add(Uv(top, 1f));
                }
                for (int s = 0; s < 2; s++)
                {
                    int u0 = b + 2 * s, l0 = u0 + 1, u1 = u0 + 2, l1 = u0 + 3;
                    tris.Add(u0); tris.Add(l0); tris.Add(l1);
                    tris.Add(u0); tris.Add(l1); tris.Add(u1);
                }
            }

            mesh.SetVertices(verts);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}
