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
// (hoppers). A leg swinging forward lifts its foot. _Stride = 0 leaves the mesh untouched.
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
    float phase  = _StridePhase + (_StrideMode.y > 0.5 ? 0 : fmod(bucket + side, 2) * 3.14159265);

    float a    = _Stride * sin(phase);
    float ease = smoothstep(0, leg * 0.25, below);  // the belly just under the hips barely moves
    float foot = saturate(below / leg);
    p.z += below * sin(a) * ease;
    p.y += below * (1 - cos(a)) * ease + leg * 0.12 * max(0, cos(phase)) * foot * foot * (_Stride / 0.5);
}

#endif
