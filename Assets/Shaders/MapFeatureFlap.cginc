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

#endif
