// Fur for MapFeature.shader; needs _Fur declared first: x amount (0 = none, up to 1.25 for woolly
// coats), y strands per object-space unit (World/AnimalFur sets both per renderer).
//
// The models have no UVs, so the coat is procedural, in object space (it stays put as the animal
// walks): fine strands combed down and back along the surface (the models face +Z), varying in
// shade, over coarser tufts. Each scale fades out where it would be finer than a pixel, so on the
// map, far away, only the tufts and the lighting remain. FurLight replaces Lambert's hard terminator
// with light that wraps round the body and a sheen at the silhouette, the way hair scatters it.
#ifndef MAP_FEATURE_FUR_INCLUDED
#define MAP_FEATURE_FUR_INCLUDED

float FurHash(float3 p)
{
    p = frac(p * 0.3183099 + 0.1);
    p *= 17.0;
    return frac(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float FurNoise(float3 p)
{
    float3 i = floor(p), f = frac(p);
    float3 u = f * f * (3.0 - 2.0 * f);
    return lerp(lerp(lerp(FurHash(i),                   FurHash(i + float3(1, 0, 0)), u.x),
                     lerp(FurHash(i + float3(0, 1, 0)), FurHash(i + float3(1, 1, 0)), u.x), u.y),
                lerp(lerp(FurHash(i + float3(0, 0, 1)), FurHash(i + float3(1, 0, 1)), u.x),
                     lerp(FurHash(i + float3(0, 1, 1)), FurHash(i + float3(1, 1, 1)), u.x), u.y), u.z);
}

// Shade multiplier (around 1) for the coat at object-space point posOS with normal normalOS
float FurShade(float3 posOS, float3 normalOS)
{
    float amount = saturate(_Fur.x);
    float3 p = posOS * _Fur.y;
    float3 n = normalize(normalOS);

    // the comb direction in the surface: back and down, straight down where the surface faces back
    float3 comb = float3(0, -0.55, -1);
    float3 dir = comb - n * dot(comb, n);
    dir = dot(dir, dir) > 1e-4 ? normalize(dir) : float3(0, -1, 0);

    // squash the noise along the strands, more for longer coats, so it draws streaks
    float squash = lerp(0.8, 0.92, saturate(_Fur.x - 0.25));
    float3 q = p - dir * dot(p, dir) * squash;

    float3 qt = q * 0.16 + 3.7;
    float strandsSeen = saturate(1.6 - length(fwidth(q)) * 2.2);  // (derivatives before the branch)
    float tuftsSeen   = saturate(1.6 - length(fwidth(qt)) * 2.2);
    if (amount <= 0.0) return 1.0; // every other prop on the map: no coat
    float strand = FurNoise(q) * 0.6 + FurNoise(q * 2.3 + 7.1) * 0.4;
    float tuft = FurNoise(qt);

    float shade = lerp(1.0, 0.74 + 0.46 * strand, strandsSeen) * lerp(1.0, 0.84 + 0.3 * tuft, tuftsSeen);
    return lerp(1.0, shade, amount);
}

// Direct light on fur: wrapped diffuse plus a sheen toward the silhouette on the lit side
// (amount 0 gives plain Lambert: albedo * ndotl)
half3 FurLight(half3 albedo, half3 n, half3 lightDir, half3 viewDir, half amount)
{
    half ndl  = dot(n, lightDir);
    half w    = 0.45 * saturate(amount);
    half diff = saturate((ndl + w) / (1.0 + w));
    half rim  = pow(1.0 - saturate(dot(n, viewDir)), 3.0) * saturate(ndl + 0.6) * 0.35 * saturate(amount);
    return albedo * diff + lerp(albedo, half3(1, 1, 1), 0.35) * rim;
}

#endif
