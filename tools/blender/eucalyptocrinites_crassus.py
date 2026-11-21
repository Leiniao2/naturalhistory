"""
Procedural Eucalyptocrinites crassus (a large camerate crinoid - a sea lily - from the
Silurian reefs of North America)
for map colonies (Fixed).

A heavy, armoured sea lily: a long, round stem of disc-like columnals anchored by roots;
a big, bowl-shaped cup (calyx) of thick, rigid, knobbly plates; and ten arms which,
when closed, packed upright into ten slots round a tall, stout central column (the
anal tube) to form a tight, ribbed, bud-like crown with the tube's tip poking out at
the top. When feeding, the arms opened out, their fine side branches (pinnules)
forming a filter. Pinkish-grey stem and cup, paler arms.
Fixed style: pivot on the sea floor, facing -Y.

Usage:
  blender --background --python tools/blender/eucalyptocrinites_crassus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EucalyptocrinitesCrassus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

NAME = "EucalyptocrinitesCrassus"
STEM = (0.64, 0.56, 0.54)
STEM_DARK = (0.40, 0.33, 0.32)
CUP = (0.58, 0.48, 0.46)
CUP_DARK = (0.36, 0.28, 0.27)
ARM = (0.80, 0.70, 0.64)
ARM_DARK = (0.50, 0.40, 0.38)
TUBE = (0.52, 0.42, 0.40)

STEM_H = 0.85


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 0.35, ((0.40, 0.39, 0.35), (0.54, 0.52, 0.46)))
    # roots
    for k in range(6):
        a = k / 6 * math.tau + 0.3
        d = Vector((math.cos(a), math.sin(a), 0))
        mb.add(nh.tube([Vector((0, 0, 0.06)), d * 0.12 + Vector((0, 0, 0.015)), d * 0.24],
               [0.035, 0.022, 0.0], sides=6), STEM_DARK)
    # stem: round, of disc columnals
    pts = [Vector((0.04 * math.sin(t * 2.0), 0.02 * math.sin(t * 1.4), STEM_H * t)) for t in [i / 12 for i in range(13)]]
    mb.add(nh.tube(pts, [0.045] * 13, sides=10),
           lambda co, n: STEM_DARK if math.cos(co.z * 140.0) > 0.55 else STEM)
    top = pts[-1]
    # calyx: deep, broad bowl of knobbly plates
    cz = top.z

    def cup_col(co, n):
        a = math.atan2(co.y - top.y, co.x - top.x)
        k = 0.5 + 0.5 * math.cos(a * 10) * math.cos((co.z - cz) * 60)
        return nh.lerp(CUP, CUP_DARK, 0.5 * nh.smoothstep(0.75, 1.0, k))

    mb.add(nh.tube([top, top + Vector((0, 0, 0.05)), top + Vector((0, 0, 0.14)), top + Vector((0, 0, 0.22))],
                   [0.05, 0.15, 0.20, 0.19], sides=20), cup_col)
    # tall stout anal tube in the centre
    base = top + Vector((0, 0, 0.20))
    mb.add(nh.tube([base, base + Vector((0, 0, 0.40)), base + Vector((0, 0, 0.62))], [0.07, 0.065, 0.05], sides=10),
           TUBE)
    mb.add(nh.ellipsoid(tuple(base + Vector((0, 0, 0.62))), (0.05, 0.05, 0.03), subdivisions=2), CUP_DARK)
    # ten arms packed upright around the tube into a ribbed bud, tips curling in
    for k in range(10):
        a = k / 10 * math.tau
        d = Vector((math.cos(a), math.sin(a), 0))
        p0 = base + d * 0.16
        arm = [p0, p0 + d * 0.02 + Vector((0, 0, 0.18)), p0 + d * 0.01 + Vector((0, 0, 0.36)),
               p0 - d * 0.04 + Vector((0, 0, 0.50)), p0 - d * 0.10 + Vector((0, 0, 0.56))]

        def arm_col(co, n, a=a):
            ridge = math.cos((math.atan2(co.y - top.y, co.x - top.x) - a) * 10)
            c = nh.lerp(ARM_DARK, ARM, 0.5 + 0.5 * ridge)
            return nh.lerp(c, ARM_DARK, 0.4 * nh.smoothstep(0.7, 1.0, math.cos(co.z * 110)))
        mb.add(nh.tube(arm, [0.052, 0.058, 0.055, 0.042, 0.0], sides=8), arm_col)
    obj = mb.to_object(NAME, roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.40, 0.39, 0.35), background=(0.05, 0.14, 0.18), views=((30, 25), (0, 70), (-90, 5)))
