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
        // and no rim darkening, so the ground runs straight into that neighbour. cliff[e] = the edge
        // drops to the sea: its wall becomes a broken rock face (see AddCliff) instead of a flat side.
        public static Mesh CreateSloped(float tileRadius, float cellRadius, float height, float solid,
                                        float[] cornerHeights, float[] edgeHeights, bool[] joined, bool[] cliff = null)
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
                if (cliff != null && cliff[e]) { AddCliff(verts, uvs, tris, rim, e, dirs, tileRadius, Uv); continue; }
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

        // Sea cliff along edge e, shaped like a real rocky coast:
        //  - in plan it isn't the straight hex edge: headlands bulge out over the sea between coves,
        //    with a flat cap of clifftop joining them to the tile top
        //  - in profile: a near-vertical face of bedded rock with small ledges, a wave-cut notch
        //    just above the waterline, then a boulder apron / rock platform at sea level
        // Both ends stay vertical on the hex corner, so it meets the walls of the neighbouring
        // edges without gaps. Every facet has its own vertices (faceted rock); the shape is seeded
        // from the edge's heights, so cached meshes repeat it exactly.
        static void AddCliff(List<Vector3> verts, List<Vector2> uvs, List<int> tris, Vector3[] rim, int e, Vector3[] dirs,
                             float tileRadius, System.Func<Vector3, float, Vector2> uv)
        {
            const int cols = 10;
            var a = rim[2 * e]; var m = rim[2 * e + 1]; var c = rim[(2 * e + 2) % 12];
            var outward = (dirs[e] + dirs[(e + 1) % 6]).normalized;
            var rng = new System.Random(e * 7919 + Mathf.RoundToInt(a.y * 1e4f) * 31 + Mathf.RoundToInt(c.y * 1e4f) * 17 + Mathf.RoundToInt(m.y * 1e4f));
            float R(float min, float max) => min + (float)rng.NextDouble() * (max - min);
            // sin(πt) clamped: at t = 1 it comes out slightly negative, and Pow/Sqrt of that is NaN
            static float Arch(float t) => Mathf.Max(0f, Mathf.Sin(t * Mathf.PI));

            // Plan: one or two headlands along the edge, nothing at the corners
            float c1 = R(0.2f, 0.45f), c2 = R(0.55f, 0.8f), w1 = R(0.1f, 0.2f), w2 = R(0.1f, 0.2f);
            float h1 = R(0.05f, 0.28f) * tileRadius, h2 = rng.NextDouble() < 0.6 ? R(0.04f, 0.22f) * tileRadius : 0f;
            float Bulge(float t) =>
                Mathf.Pow(Arch(t), 0.7f) * (0.02f * tileRadius
                + h1 * Mathf.Exp(-Mathf.Pow((t - c1) / w1, 2f)) + h2 * Mathf.Exp(-Mathf.Pow((t - c2) / w2, 2f)));

            // Profile rows from the clifftop down: (height fraction, extra outward offset)
            var rows = new (float f, float o)[]
            {
                (1.00f,  0.000f),
                (0.82f,  0.008f), // ledges where harder beds stick out
                (0.58f, -0.004f),
                (0.34f,  0.010f),
                (0.00f, -0.022f), // wave-cut notch (height set below)
                (0.00f,  0.012f), // foot
                (0.00f,  0.085f), // boulder apron / platform at sea level
            };
            var heightsAt = new[] { -1f, -1f, -1f, -1f, 0.085f, 0.03f, 0f }; // absolute heights near the waterline
            int nRows = rows.Length;

            var grid    = new Vector3[cols + 1, nRows];
            var capEdge = new Vector3[cols + 1];
            for (int k = 0; k <= cols; k++)
            {
                float t   = k / (float)cols;
                var top   = t < 0.5f ? Vector3.Lerp(a, m, t * 2f) : Vector3.Lerp(m, c, t * 2f - 1f);
                capEdge[k] = top;
                float taper = Mathf.Sqrt(Arch(t)); // 0 at the corners
                float plan  = Bulge(t);
                for (int r = 0; r < nRows; r++)
                {
                    float y = heightsAt[r] >= 0f ? Mathf.Min(heightsAt[r], top.y * 0.3f) : top.y * rows[r].f;
                    if (r > 0 && heightsAt[r] < 0f) y += R(-0.03f, 0.03f) * top.y;
                    float o = plan + taper * (rows[r].o * tileRadius / 0.985f + (r > 0 ? R(-0.012f, 0.012f) : 0f));
                    if (r == 0) y -= 0.15f * plan; // headland caps dip slightly seaward
                    grid[k, r] = new Vector3(top.x, Mathf.Max(0f, y), top.z) + outward * o;
                }
            }

            void Facet(Vector3 x, Vector3 y, Vector3 z, Vector3 facing)
            {
                // Front faces are clockwise in Unity: make the normal point along `facing`
                if (Vector3.Dot(Vector3.Cross(y - x, z - x), facing) < 0f) (y, z) = (z, y);
                int i = verts.Count;
                verts.Add(x); verts.Add(y); verts.Add(z);
                uvs.Add(uv(x, 1f)); uvs.Add(uv(y, 1f)); uvs.Add(uv(z, 1f));
                tris.Add(i); tris.Add(i + 1); tris.Add(i + 2);
            }

            for (int k = 0; k < cols; k++)
            {
                // Clifftop cap from the tile's rim out to the headland edge
                Facet(capEdge[k], capEdge[k + 1], grid[k + 1, 0], Vector3.up);
                Facet(capEdge[k], grid[k + 1, 0], grid[k, 0], Vector3.up);
                for (int r = 0; r < nRows - 1; r++)
                {
                    // Columns run clockwise (seen from above) and rows downward, so down × along points
                    // out of the rock, also on the flanks of a headland
                    var face = Vector3.Cross(grid[k, r + 1] - grid[k, r], grid[k + 1, r] - grid[k, r]);
                    if (face.sqrMagnitude < 1e-10f) face = outward;
                    Facet(grid[k, r], grid[k, r + 1], grid[k + 1, r + 1], face);
                    Facet(grid[k, r], grid[k + 1, r + 1], grid[k + 1, r], face);
                }
            }
        }
    }
}
