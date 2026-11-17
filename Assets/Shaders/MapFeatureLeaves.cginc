// Leaf texture for MapFeature.shader: tree crowns and other leaf clumps (MapFeatureMeshes
// FoliageBlob marks their vertices with colour alpha 0) are covered in small overlapping leaves
// instead of a plain smooth colour. Procedural, in object space (the meshes have no UVs), so the
// leaves stay put as the trees bend in the wind: each cell of a 3D Voronoi pattern is one leaf with
// its own shade and a dark crevice round it, over coarser clumps with shadowed gaps between them.
// Each scale fades out where it would be finer than a pixel, so from far away only the clumps
// remain. _NHLeafFreq (global, set by HexGrid from the cell size) is leaves per object-space unit.
#ifndef MAP_FEATURE_LEAVES_INCLUDED
#define MAP_FEATURE_LEAVES_INCLUDED

float _NHLeafFreq;

float3 LeafHash3(float3 p)
{
    p = float3(dot(p, float3(127.1, 311.7, 74.7)), dot(p, float3(269.5, 183.3, 246.1)), dot(p, float3(113.5, 271.9, 124.6)));
    return frac(sin(p) * 43758.5453);
}

// Distance to the nearest and second-nearest leaf centre, and the nearest leaf's own random value
float3 LeafCells(float3 p)
{
    float3 i = floor(p), f = frac(p);
    float d1 = 8.0, d2 = 8.0, id = 0.0;
    for (int z = -1; z <= 1; z++)
    for (int y = -1; y <= 1; y++)
    for (int x = -1; x <= 1; x++)
    {
        float3 o = float3(x, y, z);
        float3 h = LeafHash3(i + o);
        float3 r = o + h - f;
        float d = dot(r, r);
        if (d < d1) { d2 = d1; d1 = d; id = h.x; }
        else if (d < d2) d2 = d;
    }
    return float3(sqrt(d1), sqrt(d2), id);
}

// Shade multiplier (around 1) for foliage at object-space posOS; leaf = 1 on leaf clumps, else 0
float LeafShade(float3 posOS, float3 normalOS, float leaf)
{
    float freq = _NHLeafFreq > 0.0 ? _NHLeafFreq : 400.0;
    float3 p = posOS * freq;
    float3 pc = p * 0.22 + 5.3;
    float leavesSeen = saturate(1.8 - length(fwidth(p)) * 1.6);   // (derivatives before the branch)
    float clumpsSeen = saturate(1.8 - length(fwidth(pc)) * 1.6);
    if (leaf < 0.5 || clumpsSeen <= 0.0) return 1.0; // trunks, rocks, animals untouched; too far to see

    // coarse clumps: sunlit masses with shadowed hollows between them
    float3 c = LeafCells(pc);
    float clump = smoothstep(0.0, 0.5, c.y - c.x);
    float clumpShade = lerp(0.62, 1.08, clump) * (0.9 + 0.2 * c.z);

    if (leavesSeen <= 0.0) return lerp(1.0, clumpShade, clumpsSeen); // (skip the fine pattern far away)

    // single leaves: each its own shade (some catch the light, some turn away), dark at the edges
    float3 l = LeafCells(p);
    float edge = smoothstep(0.0, 0.18, l.y - l.x);
    float upward = saturate(normalize(normalOS).y * 0.5 + 0.5);
    float leafShade = lerp(0.55, 1.0, edge) * (0.78 + 0.42 * l.z) * lerp(0.92, 1.08, upward);

    return lerp(1.0, clumpShade, clumpsSeen) * lerp(1.0, leafShade, leavesSeen);
}

#endif
