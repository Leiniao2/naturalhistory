"""
Parametric archaeocete (early whale) swimmer for the Paleogene species in tools/blender/
(basilosaurus_cetoides.py, dorudon_atrox.py, rodhocetus_kasranii.py).

The body is a lofted tube along Y from a radius profile (snout at -Y, faces -Y),
with a long toothed jaw, pectoral flippers or legs, small or large hind limbs,
an optional horizontal tail fluke and dorsal fin. Parts are fused into one surface,
countershaded (dark back, pale belly), then crisp eyes and teeth are added.
Pivot at the body centre (Swim).
"""

import math
from dataclasses import dataclass, field

from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

import nh_model as nh

EYE = (0.03, 0.03, 0.03)
TOOTH = (0.92, 0.89, 0.80)


@dataclass
class Spec:
    name: str
    length: float = 2.0
    # (t along body 0 = snout tip .. 1 = tail tip, radius) control points; width = radius * flat
    profile: tuple = ((0.0, 0.02), (0.1, 0.07), (0.2, 0.13), (0.45, 0.17), (0.75, 0.1), (1.0, 0.03))
    flat: float = 0.9            # body width / height
    head_end: float = 0.2        # t where the skull ends (jaw line runs to here)
    jaw_open: float = 0.0
    teeth: int = 8               # per side, upper jaw
    tooth_len: float = 0.025
    flipper: tuple = (0.26, 0.28, 0.07)  # t, length, width of the pectoral flippers (0 length = none)
    flipper_legs: bool = False   # four-legged swimmer: front limbs are legs with feet
    hind: tuple = (0.62, 0.05, 0.02)     # t, length, foot size of the hind limbs
    fluke: float = 0.0           # half-span of the tail fluke (0 = none)
    dorsal: float = 0.0          # dorsal fin height (0 = none)
    dorsal_t: float = 0.55
    sag: float = 0.0             # tail curves down (fraction of length)
    back: tuple = (0.25, 0.27, 0.30)
    belly: tuple = (0.75, 0.74, 0.70)
    mid: tuple = None
    pattern: float = 0.0         # mottling strength
    eye_r: float = 0.012
    voxel: float = 0.012
    max_tris: int = 14000


def radius(s, t):
    pts = s.profile
    for (t0, r0), (t1, r1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / max(t1 - t0, 1e-6)
            u = u * u * (3 - 2 * u)
            return r0 + (r1 - r0) * u
    return pts[-1][1]


def axis(s, t):
    """Centre line point at t."""
    y = -s.length / 2 + s.length * t
    z = -s.sag * s.length * max(0.0, t - 0.55) ** 2 * 4
    return Vector((0, y, z))


def build(s, extra=None):
    b = nh.MeshBuilder()
    n = 40
    pts = [axis(s, i / n) for i in range(n + 1)]
    rr = [max(radius(s, i / n), s.voxel * 1.2) for i in range(n + 1)]
    rr[0] = s.voxel
    b.add(nh.tube([tuple(p) for p in pts], rr, sides=18, scale_xy=(s.flat, 1.0)), s.back)
    # lower jaw: slim tube under the snout
    he = s.head_end
    j0, j1 = axis(s, 0.015), axis(s, he)
    b.add(nh.tube([tuple(j0 + Vector((0, 0, -radius(s, 0.03) * 0.6))),
                   tuple(j1 + Vector((0, 0, -radius(s, he) * 0.55)))],
                  [radius(s, 0.03) * 0.55, radius(s, he) * 0.55], sides=12, scale_xy=(s.flat, 1.0)), s.back)
    # pectoral limbs
    ft, fl, fw = s.flipper
    if fl > 0:
        for sx in (-1, 1):
            root = axis(s, ft) + Vector((sx * radius(s, ft) * s.flat * 0.6, 0, -radius(s, ft) * 0.55))
            if s.flipper_legs:
                knee = root + Vector((sx * fl * 0.25, fl * 0.15, -fl * 0.55))
                tip = knee + Vector((sx * fl * 0.05, fl * 0.45, -fl * 0.2))
                b.add(nh.tube([tuple(root), tuple(knee), tuple(tip)], [fw * 0.7, fw * 0.5, fw * 0.4], sides=10), s.back)
                b.add(nh.ellipsoid(tuple(tip + Vector((0, fw * 0.8, 0))), (fw * 0.9, fw * 1.4, fw * 0.25)), s.back)
            else:
                tip = root + Vector((sx * fl * 0.75, fl * 0.55, -fl * 0.35))
                mid = root.lerp(tip, 0.45)
                b.add(nh.tube([tuple(root), tuple(mid), tuple(tip)], [fw * 0.8, fw, fw * 0.3], sides=10,
                              scale_xy=(1.0, 0.32)), s.back)
    # hind limbs
    ht, hl, hf = s.hind
    if hl > 0:
        for sx in (-1, 1):
            root = axis(s, ht) + Vector((sx * radius(s, ht) * s.flat * 0.5, 0, -radius(s, ht) * 0.6))
            tip = root + Vector((sx * hl * 0.3, hl * 0.8, -hl * 0.4))
            b.add(nh.tube([tuple(root), tuple(tip)], [max(hf * 0.5, s.voxel * 1.3), max(hf * 0.4, s.voxel * 1.2)],
                          sides=8), s.back)
            if hf > 0.02:
                b.add(nh.ellipsoid(tuple(tip + Vector((0, hf * 1.2, -hf * 0.1))), (hf * 0.9, hf * 1.8, hf * 0.22)),
                      s.back)
    # fluke
    if s.fluke > 0:
        tail = axis(s, 0.97)
        for sx in (-1, 1):
            tip = tail + Vector((sx * s.fluke, s.fluke * 0.55, 0))
            b.add(nh.tube([tuple(tail + Vector((0, -s.fluke * 0.25, 0))), tuple(tail.lerp(tip, 0.5) + Vector((0, -s.fluke * 0.05, 0))),
                           tuple(tip)], [s.fluke * 0.32, s.fluke * 0.26, s.voxel * 1.2], sides=10,
                          scale_xy=(1.0, 0.18)), s.back)
    if s.dorsal > 0:
        base = axis(s, s.dorsal_t) + Vector((0, 0, radius(s, s.dorsal_t) * 0.8))
        tip = base + Vector((0, s.dorsal * 0.7, s.dorsal))
        b.add(nh.tube([tuple(base + Vector((0, -s.dorsal * 0.4, 0))), tuple(base.lerp(tip, 0.5)), tuple(tip)],
                      [s.dorsal * 0.45, s.dorsal * 0.3, s.voxel], sides=10, scale_xy=(0.25, 1.0)), s.back)
    if extra:
        extra(b, s)
    fused = b.fuse(voxel=s.voxel, smooth=5, smooth_factor=0.5, max_tris=s.max_tris)

    def paint(co, nrm):
        c0 = axis(s, max(0.0, min(1.0, (co.y + s.length / 2) / s.length)))
        dz = co.z - c0.z
        r = max(radius(s, (co.y + s.length / 2) / s.length), 1e-3)
        u = nh.smoothstep(-0.55, 0.35, dz / r)
        c = nh.lerp(s.belly, s.mid or nh.lerp(s.back, s.belly, 0.4), nh.smoothstep(0.0, 0.5, u))
        c = nh.lerp(c, s.back, nh.smoothstep(0.5, 1.0, u))
        if s.pattern > 0:
            c = nh.lerp(c, s.back, s.pattern * nh.smoothstep(0.25, 0.45, noise.noise(co * 9.0)))
        return c

    tree = BVHTree.FromBMesh(fused)
    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    # eyes on the sides of the skull, just above the jaw line
    et = s.head_end * 0.85
    for sx in (-1, 1):
        c0 = axis(s, et) + Vector((0, 0, radius(s, et) * 0.15))
        loc, nrm, _i, _d = tree.ray_cast(c0 + Vector((sx * 2, 0, 0)), Vector((-sx, 0, 0)))
        if loc is None:
            continue
        mb.add(nh.ellipsoid(tuple(loc - nrm * s.eye_r * 0.3), (s.eye_r,) * 3, subdivisions=2), EYE)
    # teeth along the upper jaw line
    for i in range(s.teeth):
        t = 0.02 + (s.head_end * 0.75 - 0.02) * i / max(1, s.teeth - 1)
        for sx in (-1, 1):
            c0 = axis(s, t) + Vector((0, 0, -radius(s, t) * 0.35))
            loc, nrm, _i, _d = tree.ray_cast(c0 + Vector((sx * 2, 0, 0)), Vector((-sx, 0, 0)))
            if loc is None:
                continue
            L = s.tooth_len * (1.3 if i < 3 else 1.0)
            mb.add(nh.tube([tuple(loc - nrm * 0.004), tuple(loc + Vector((sx * 0.003, 0, -L)))],
                           [L * 0.28, 0.0], sides=6), TOOTH)
    obj = mb.to_object(s.name)
    # pivot at the body centre
    vs = obj.data.vertices
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (lo + hi) / 2
    for v in vs:
        v.co -= c
    return obj


def main(spec, extra=None):
    nh.run(lambda: build(spec, extra), spec.name, background=(0.05, 0.22, 0.32),
           views=((35, 25), (-90, 5), (0, 80)))
