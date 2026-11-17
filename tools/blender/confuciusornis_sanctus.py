"""
Procedural Confuciusornis sanctus (Early Cretaceous bird, Jehol Biota, north-eastern China), flying.

A crow-sized early bird and the oldest known with a toothless horny beak. Its wings still
carried three clawed fingers (the big thumb claw shows at the wrist), it had a short tail
stump (pygostyle) and many specimens, probably males, bear a pair of very long ribbon-like
tail feathers. Melanosomes suggest a patchwork of dark and brownish plumage with paler
spots on the wings and neck.
Pivot at the body centre, faces -Y, wings spread.

Usage:
  blender --background --python tools/blender/confuciusornis_sanctus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Confuciusornis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_flier as fl  # noqa: E402

DARK = (0.14, 0.11, 0.09)
BROWN = (0.42, 0.28, 0.17)
PALE = (0.82, 0.76, 0.66)
BEAK = (0.20, 0.18, 0.16)


def body_paint(co, n):
    c = cc.countershade(n, BROWN, BROWN, DARK)
    c = nh.lerp(c, PALE, 0.7 * cc.spots(co, 18.0, 0.18) * nh.smoothstep(-0.2, 0.3, co.y * -1))
    return cc.mottle(c, co, 0.1)


def wing_col(co, n):
    x = abs(co.x)
    c = nh.lerp(BROWN, DARK, nh.smoothstep(0.25, 0.6, x))
    c = nh.lerp(c, PALE, 0.6 * cc.spots(co, 14.0, 0.15) * (1 - nh.smoothstep(0.3, 0.5, x)))
    k = 0.5 + 0.5 * math.sin(x * 60.0)
    return tuple(v * (0.85 + 0.25 * k) for v in c)


def make():
    axis = [(0.20, 0.0, 0.0, 0.0), (0.17, 0.0, 0.02, 0.015), (0.10, 0.0, 0.06, 0.055),
            (-0.02, 0.0, 0.075, 0.075), (-0.12, 0.02, 0.06, 0.06), (-0.18, 0.05, 0.035, 0.035),
            (-0.23, 0.07, 0.04, 0.04), (-0.28, 0.065, 0.03, 0.03), (-0.33, 0.055, 0.0, 0.0)]
    f = fl.Flier(name="Confuciusornis", axis=axis, paint=body_paint, eye=(0.028, -0.245, 0.085, 0.009),
                 eye_col=(0.2, 0.12, 0.06), disp=cc.fuzz_disp(0.003, 60.0), voxel=0.008)
    lead = [(0.04, -0.08, 0.03), (0.22, -0.10, 0.06), (0.40, -0.12, 0.07), (0.72, -0.04, 0.09)]
    trail = [(0.04, 0.08, 0.02), (0.25, 0.16, 0.04), (0.50, 0.15, 0.06), (0.74, 0.04, 0.09)]
    f.wings.append(fl.Wing(lead, trail, wing_col, thickness=0.009, nv=6))

    def crisp(mb, f):
        mb.add(nh.ellipsoid((0, -0.31, 0.055), (0.016, 0.04, 0.016), subdivisions=2), BEAK)
        # tail fan stub and the two long ribbon feathers
        mb.add(cc.ribbon([((-0.03, 0.16, 0.0), (0.03, 0.16, 0.0)), ((-0.05, 0.26, 0.0), (0.05, 0.26, 0.0))],
                         0.006), DARK)
        for sx in (1, -1):
            pts = cc.bezier_pts((sx * 0.01, 0.17, 0.0), (sx * 0.03, 0.45, -0.02), (sx * 0.05, 0.80, 0.01), 12)
            pairs = []
            for i, p in enumerate(pts):
                w = 0.004 if i < 9 else 0.016
                pairs.append((p - Vector((w, 0, 0)), p + Vector((w, 0, 0))))
            mb.add(cc.ribbon(pairs, 0.004), DARK)
            base = Vector((sx * 0.22, -0.11, 0.06))
            mb.add(cc.cone(base, base + Vector((0, -0.03, -0.01)), 0.006, sides=4), cc.CLAW)
    f.crisp = crisp
    return f


if __name__ == "__main__":
    fl.run(make, "Confuciusornis")
