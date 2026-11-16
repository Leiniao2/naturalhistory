// Wing/fin beat for MapFeature.shader; needs _Flap, _FlapRoot and _FlapSpan declared first.
// Rotates everything outboard of |x| = _FlapRoot about the body's long (z) axis, easing in over the
// first part of the wing so the shoulder doesn't crease, and bending the tips a little further.
// Inside the root the angle is 0, so the body is untouched.
#ifndef MAP_FEATURE_FLAP_INCLUDED
#define MAP_FEATURE_FLAP_INCLUDED

void ApplyFlap(inout float3 p, inout float3 n)
{
    float side  = p.x >= 0 ? 1.0 : -1.0;
    float d     = abs(p.x) - _FlapRoot; // distance out along the wing
    float reach = max(_FlapSpan - _FlapRoot, 1e-4);
    float a     = _Flap * (saturate(d / (reach * 0.25)) + 0.35 * saturate(d / reach));
    float c = cos(a), s = sin(a);

    // rotate (outward, up) by a, so positive angles lift the tips on both sides
    float y = p.y;
    p.x = side * (_FlapRoot + d * c - y * s);
    p.y = d * s + y * c;

    float nOut = n.x * side;
    n.x = side * (nOut * c - n.y * s);
    n.y = nOut * s + n.y * c;
}

// Walking legs for MapFeature.shader; needs _Stride, _StridePhase, _StrideLegs and _StrideMode.
// The models are single static meshes, so everything below the hips (_StrideLegs.x, object space)
// is treated as legs: it swings about the hip line by up to _Stride radians, front/back by z.
// Legs are grouped into _StrideMode.x pairs along z (1 = biped, 2 = quadruped, 3 = insect...);
// neighbouring pairs and the left/right legs of a pair step in opposite phase, which gives a
// diagonal trot for four legs and a tripod gait for six. _StrideMode.y = 1 moves all legs together
// (hoppers). _StrideMode.z blends toward a bounding gallop (running big cats): the left and right
// legs of a pair land together and the hind pair follows the front pair. A leg swinging forward lifts its foot. _Stride = 0 leaves the mesh untouched.
void ApplyStride(inout float3 p)
{
    if (_Stride == 0) return;
    float hip   = _StrideLegs.x;
    float leg   = max(_StrideLegs.y, 1e-4);
    float below = hip - p.y;
    if (below <= 0) return;

    float pairs  = max(_StrideMode.x, 1);
    float zt     = saturate((p.z - _StrideLegs.z) / max(_StrideLegs.w - _StrideLegs.z, 1e-4));
    float bucket = min(floor(zt * pairs), pairs - 1);
    float side   = p.x >= 0 ? 0 : 1;
    float walk   = fmod(bucket + side, 2) * 3.14159265;
    float bound  = bucket * 3.14159265 * 0.7;
    float phase  = _StridePhase + (_StrideMode.y > 0.5 ? 0 : lerp(walk, bound, saturate(_StrideMode.z)));

    float a    = _Stride * sin(phase);
    float ease = smoothstep(0, leg * 0.25, below);  // the belly just under the hips barely moves
    float foot = saturate(below / leg);
    p.z += below * sin(a) * ease;
    p.y += below * (1 - cos(a)) * ease + leg * 0.12 * max(0, cos(phase)) * foot * foot * (_Stride / 0.5);
}

// Snakes and eels for MapFeature.shader; needs _Undulate, _UndulatePhase, _UndulateBody and _Coil.
// The model is a straight body facing +z (snout at _UndulateBody.y, tail tip at .x). Its centre
// line is re-laid along a curve of the same length, given by the heading of the body at each
// point, and every vertex keeps its offset from the centre line, so the body bends without
// stretching. The heading blends between two shapes by _Coil.x:
//   0: a sideways wave of _UndulateBody.z wavelengths running from the head to the tail as
//      _UndulatePhase grows; _Undulate = its heading amplitude in radians; the head stays nearly
//      straight and the swing grows toward the tail by _UndulateBody.w (0 = even, 1 = eel-like);
//   1: a flat resting coil (spiral, inner radius _Coil.y and ring spacing _Coil.z as fractions of
//      the length) with the head held up by _Coil.w lengths above the middle of it.
// In between the coil loosens into the wave, so a snake uncoils and sets off continuously.
float BodyHeading(float u) // u = 0 at the snout .. 1 at the tail tip
{
    float env  = smoothstep(0, 0.15, u) * (1 - _UndulateBody.w + _UndulateBody.w * u);
    float wave = _Undulate * env * sin(6.2831853 * _UndulateBody.z * u - _UndulatePhase);

    // neck: carries on curling from the inner end of the spiral, held up over the middle (rise)
    const float neck = 0.15;
    float ri   = max(_Coil.y, 1e-3), d = max(_Coil.z, 1e-3);
    float s    = max(u - neck, 0);
    float coil = 6.2831853 / d * (sqrt(ri * ri + d * s / 3.14159265) - ri)  // Archimedean spiral
               - max(neck - u, 0) / ri;
    return lerp(wave, coil, _Coil.x);
}

void ApplyUndulate(inout float3 p, inout float3 n)
{
    if (_Undulate == 0 && _Coil.x == 0) return;
    float len = max(_UndulateBody.y - _UndulateBody.x, 1e-4);
    float u   = saturate((_UndulateBody.y - p.z) / len);

    // Reference direction that faces +z: the body's average heading when stretched out, the
    // head's when coiled, so an uncoiling snake points its head the way it goes and the body
    // unwinds behind it instead of the whole coil spinning
    float mean = 0, head = 0;
    [unroll] for (int i = 0; i < 16; i++) mean += BodyHeading((i + 0.5) / 16);
    [unroll] for (int k = 0; k < 4; k++)  head += BodyHeading((k + 0.5) / 4 * 0.1);
    mean = lerp(mean / 16, head / 4, _Coil.x);

    // centre line from the middle of the body (which stays at the pivot) to this point
    const int steps = 20;
    float h = (u - 0.5) / steps;
    float2 c = 0; // (x, z)
    [unroll] for (int j = 0; j < steps; j++)
    {
        float a = BodyHeading(0.5 + (j + 0.5) * h) - mean;
        c += float2(sin(a), -cos(a)) * h * len;
    }
    float a  = BodyHeading(u) - mean;
    float2 t = float2(sin(a), -cos(a)); // along the body, toward the tail
    float2 side = float2(cos(a), sin(a));
    float2 q = c + side * p.x;
    float rise = _Coil.x * _Coil.w * len * (1 - smoothstep(0.02, 0.15, u));
    p = float3(q.x, p.y + rise, _UndulateBody.y - 0.5 * len + q.y);

    float3 m = n;
    n = normalize(float3(m.x * side.x - m.z * t.x, m.y, m.x * side.y - m.z * t.y));
}

// Gentle swaying in the water for MapFeature.shader; needs _Sway (amplitude, height of full sway,
// speed, wavelength in world units). Only vertices with flex (uv3.x, set by MapFeatureMeshes on tall,
// slender water plants: kelp, ribbon weeds, seagrass, feathery fronds; 0 at the foot, most at the
// top) move: sideways by amplitude × full-sway height × flex, so low algae, mats and stones stay
// still while tall fronds lean with the swell. The phase drifts across the map so neighbours
// don't move in step.
void ApplySway(inout float3 p, float flex)
{
    if (_Sway.x == 0 || flex <= 0.001) return;
    float  d  = _Sway.x * _Sway.y * flex;
    float3 w  = mul(unity_ObjectToWorld, float4(p, 1)).xyz;
    float  ph = (w.x * 0.8 + w.z * 0.6) / max(_Sway.w, 1e-4) * 6.2831853;
    float  t  = _Time.y * _Sway.z;
    p.x += d * sin(t + ph);
    p.z += d * 0.6 * sin(t * 0.77 + ph * 1.3 + 1.7);
}

// Wind on land plants: uv3.x (TEXCOORD3) is how much a vertex bends (0 = stiff, set by
// MapFeatureMeshes on slender plants: grasses, reeds, horsetails, Cooksonia, ferns, the tops most).
// _NHWind is global (Wind.cs): amplitude in world units, speed, gust wavelength in world units.
// The wind blows along world +x with gusts rolling across the map, plus a little side-to-side.
float4 _NHWind;
void ApplyWind(inout float3 p, float flex)
{
    if (flex <= 0.001 || _NHWind.x == 0 || _Sway.x != 0) return; // water plants sway instead
    float3 w  = mul(unity_ObjectToWorld, float4(p, 1)).xyz;
    float  ph = (w.x * 0.9 + w.z * 0.4) / max(_NHWind.z, 1e-4) * 6.2831853;
    float  t  = _Time.y * _NHWind.y;
    float  gust = 0.55 + 0.45 * sin(t * 0.37 - ph * 0.5);              // slow gusts rolling across
    float  d  = _NHWind.x * flex;
    float3 offsetWS = float3(d * gust * (0.6 + 0.4 * sin(t + ph)),       // leaning and bobbing downwind
                             0,
                             d * 0.3 * sin(t * 1.31 + ph * 1.7));        // and a little sideways
    p += mul((float3x3)unity_WorldToObject, offsetWS);
}

#endif

// Banded rock (Danxia rainbow hills, canyon and mesa strata): uv2.x is a band coordinate laid on
// each vertex by LandformMeshes (height plus the tilt of the beds), uv2.y which palette (1 = Danxia,
// 2 = strata; 0 = not banded). The colour is looked up per pixel, so the stripes follow smooth lines
// instead of the triangles, with a narrow soft edge between bands. Palettes are globals set by
// MapFeatureMeshes.SetBandPalettes.
float4 _NHBandsA[8];
float4 _NHBandsB[8];
float4 _NHBandCounts; // x = colours in A, y = colours in B

float3 BandPick(float k, float palette)
{
    float n = palette < 1.5 ? max(_NHBandCounts.x, 1) : max(_NHBandCounts.y, 1);
    int   i = (int)(k - n * floor(k / n));
    return palette < 1.5 ? _NHBandsA[i].rgb : _NHBandsB[i].rgb;
}

float3 BandMean(float palette)
{
    float  n = palette < 1.5 ? max(_NHBandCounts.x, 1) : max(_NHBandCounts.y, 1);
    float3 s = 0;
    [unroll] for (int i = 0; i < 8; i++) if (i < n) s += palette < 1.5 ? _NHBandsA[i].rgb : _NHBandsB[i].rgb;
    return s / n;
}

// Box-filtered over the pixel's footprint: each edge blends across exactly one pixel, centred on
// the edge, and where the bands get thinner than about a pixel (far away) they fade to the
// palette's average instead of sparkling and crawling as the camera moves.
float3 BandColor(float2 band)
{
    float k = floor(band.x);
    float f = band.x - k;
    float w = max(fwidth(band.x), 1e-4);
    float next = saturate((f + 0.5 * w - 1) / w); // share of the pixel past the upper edge
    float prev = saturate((0.5 * w - f) / w);     // share below the lower edge
    float3 c = BandPick(k, band.y) * (1 - next - prev)
             + BandPick(k + 1, band.y) * next
             + BandPick(k - 1, band.y) * prev;
    return lerp(c, BandMean(band.y), saturate((w - 0.35) / 0.5));
}
