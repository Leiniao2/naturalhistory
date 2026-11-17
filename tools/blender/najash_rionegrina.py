"""
Procedural Najash rionegrina (Late Cretaceous, ~95-92 Ma, Candeleros Formation,
Rio Negro, Argentina) for map colonies. Built on nh_pal_snake.py.

One of the earliest known snakes and a transitional form: a long snake body, but
with a skull still close to a lizard's (a cheek bone, jugal, that later snakes lost)
and a small pair of hind legs with a pelvis attached to the spine, sitting beside the
vent. About 2 m long; it lived in a dry, desert-like setting and probably burrowed.
Pattern: sandy tan with faint darker blotches and a pale belly (colour unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/najash_rionegrina.py -- [--render out.png]

Output: Assets/Resources/Models/Species/NajashRionegrina.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_pal_snake as sn  # noqa: E402

SPEC = sn.Spec(
    name="NajashRionegrina",
    length=2.4, girth=0.075, head_len=0.17, head_w=0.07, neck=0.62, tail=0.2,
    base=(0.66, 0.55, 0.38), saddle=(0.40, 0.31, 0.20), belly=(0.86, 0.80, 0.66),
    saddles=18, saddle_w=0.35, side_spots=0.45, head_col=(0.52, 0.42, 0.28),
)
LEG = (0.55, 0.45, 0.31)
CLAW = (0.20, 0.17, 0.13)


def build(s):
    b = nh.MeshBuilder()
    n = 50
    y0 = -s.length / 2 + s.head_len * 0.6
    pts, rr = [], []
    for i in range(n + 1):
        t = i / n
        y = y0 + (s.length / 2 - y0) * t
        r = s.girth * (s.neck + (1 - s.neck) * nh.smoothstep(0.0, 0.25, t))
        r *= 1.0 - nh.smoothstep(1 - s.tail - 0.05, 1.0, t) * 0.92
        r = max(r, s.voxel * 1.2)
        pts.append((0, y, r * 0.88))
        rr.append(r)
    b.add(nh.tube(pts, rr, sides=16, scale_xy=(1.12, 0.88)), s.base)
    # a lizard-like head: longer, with a distinct snout and cheeks wider than the neck
    hy = -s.length / 2 + s.head_len * 0.5
    hz = rr[0] * 0.85
    b.add(nh.ellipsoid((0, hy + s.head_len * 0.1, hz), (s.head_w, s.head_len * 0.45, s.head_w * 0.66)), s.base)
    b.add(nh.ellipsoid((0, hy - s.head_len * 0.32, hz - s.head_w * 0.05), (s.head_w * 0.62, s.head_len * 0.3, s.head_w * 0.45)), s.base)
    fused = b.fuse(voxel=s.voxel, smooth=4, smooth_factor=0.5)

    period = (s.length - s.head_len) / s.saddles

    def paint(co, nrm):
        c = s.base
        u = (co.y - (-s.length / 2 + s.head_len)) / period
        if co.y > -s.length / 2 + s.head_len * 1.1:
            ph = (u + 0.25 * noise.noise(co * 6)) % 1.0
            top = nh.smoothstep(0.1, 0.6, nrm.z)
            dark = 1.0 - nh.smoothstep(s.saddle_w - 0.08, s.saddle_w + 0.08, ph)
            c = nh.lerp(c, s.saddle, dark * top * 0.8)
            side = nh.smoothstep(0.55, 0.15, abs(nrm.z)) * s.side_spots
            ph2 = (u + 0.5) % 1.0
            c = nh.lerp(c, s.saddle, side * (1.0 - nh.smoothstep(0.2, 0.3, abs(ph2 - 0.5))))
        else:
            c = nh.lerp(c, s.head_col, nh.smoothstep(0.0, 0.5, nrm.z))
        return nh.lerp(c, s.belly, nh.smoothstep(-0.2, -0.6, nrm.z))

    mb = nh.MeshBuilder()
    mb.add(fused, color=paint)
    for sx in (-1, 1):
        e = Vector((sx * s.head_w * 0.8, hy - s.head_len * 0.12, hz + s.head_w * 0.25))
        mb.add(nh.ellipsoid(tuple(e), (s.head_w * 0.17,) * 3, subdivisions=2), sn.EYE)
        mb.add(nh.ellipsoid(tuple(e + Vector((sx * s.head_w * 0.1, 0, 0))), (s.head_w * 0.05, s.head_w * 0.1, s.head_w * 0.13),
                            subdivisions=1), sn.PUPIL)

    # the small hind legs beside the vent: thigh out from the flank, shin back and down, a clawed foot
    vy = -s.length / 2 + (s.length - s.head_len * 0.6) * (1 - s.tail) + s.head_len * 0.6
    i = min(n, int(n * (1 - s.tail)))
    r = rr[i]
    for sx in (-1, 1):
        hip = Vector((sx * r * 0.9, vy - 0.02, r * 0.55))
        knee = hip + Vector((sx * r * 1.15, 0.05, -r * 0.3))
        foot = knee + Vector((sx * r * 0.3, 0.11, -r * 0.4))
        mb.add(nh.tube([tuple(hip), tuple(knee), tuple(foot)], [r * 0.3, r * 0.2, r * 0.13], sides=7), LEG)
        for k in (-1, 0, 1):
            tip = foot + Vector((sx * r * 0.12 + k * r * 0.1, 0.07, -r * 0.05))
            mb.add(nh.tube([tuple(foot), tuple(tip)], [r * 0.07, 0.0], sides=4), CLAW)

    tip = Vector((0, -s.length / 2 - s.head_len * 0.15, hz - s.head_w * 0.3))
    fork = tip + Vector((0, -s.head_len * 0.35, -s.head_w * 0.1))
    mb.add(nh.tube([tuple(tip + Vector((0, s.head_len * 0.1, 0))), tuple(fork)], [s.head_w * 0.05, s.head_w * 0.04], sides=5),
           sn.TONGUE)
    for sx in (-1, 1):
        mb.add(nh.tube([tuple(fork), tuple(fork + Vector((sx * s.head_w * 0.18, -s.head_len * 0.12, 0)))],
                       [s.head_w * 0.035, 0.0], sides=5), sn.TONGUE)
    obj = mb.to_object(s.name)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(lambda: build(SPEC), SPEC.name, ground=(0.72, 0.62, 0.45), views=((35, 30), (-90, 8), (0, 75)))
