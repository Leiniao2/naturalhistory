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
// speed, wavelength in world units). Each point moves sideways by amplitude × height-of-full-sway
// × (its height / that height)², capped at the full height, so low algae barely stir while tall
// fronds lean with the swell. The phase drifts across the map so neighbours don't move in step.
void ApplySway(inout float3 p)
{
    if (_Sway.x == 0) return;
    float  k  = saturate(p.y / max(_Sway.y, 1e-4));
    float  d  = _Sway.x * _Sway.y * k * k;
    float3 w  = mul(unity_ObjectToWorld, float4(p, 1)).xyz;
    float  ph = (w.x * 0.8 + w.z * 0.6) / max(_Sway.w, 1e-4) * 6.2831853;
    float  t  = _Time.y * _Sway.z;
    p.x += d * sin(t + ph);
    p.z += d * 0.6 * sin(t * 0.77 + ph * 1.3 + 1.7);
}

#endif
