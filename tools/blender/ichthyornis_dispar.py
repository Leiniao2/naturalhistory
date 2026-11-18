"""
Procedural Ichthyornis dispar (Late Cretaceous toothed seabird, Western Interior Seaway).

A tern-like seabird, in flight: a large head with a long, pointed beak whose jaws still carry
small, curved teeth, a compact body with a deep keel, long, narrow, pointed wings and a short
fanned tail. White underneath and on the head, pale grey back and wings with black
primaries and a dark eye smudge; the beak yellowish.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/ichthyornis_dispar.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ichthyornis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_flier as fl  # noqa: E402

WHITE = (0.94, 0.94, 0.92)
GREY = (0.62, 0.64, 0.66)
BLACK = (0.08, 0.08, 0.09)
BEAK = (0.78, 0.62, 0.30)


def body_paint(co, n):
    c = cc.countershade(n, WHITE, WHITE, GREY, lo=-0.4, mid=0.1, hi=0.7)
    if co.y < -0.20:
        c = nh.lerp(c, WHITE, 0.7)
        if co.y < -0.30:
            c = nh.lerp(c, BEAK, nh.smoothstep(-0.30, -0.33, co.y))
    return cc.mottle(c, co, 0.04)


def wing_col(co, n):
    x = abs(co.x)
    c = nh.lerp(GREY, BLACK, nh.smoothstep(0.50, 0.62, x))
    if n.z < -0.3:
        c = nh.lerp(c, WHITE, 0.6 if x < 0.5 else 0.2)
    return cc.mottle(c, co, 0.04)


def make():
    axis = [(0.20, 0.0, 0.0, 0.0), (0.16, 0.0, 0.025, 0.015), (0.10, 0.0, 0.055, 0.05),
            (-0.02, 0.0, 0.07, 0.07), (-0.12, 0.02, 0.055, 0.055), (-0.18, 0.045, 0.035, 0.035),
            (-0.24, 0.065, 0.042, 0.042), (-0.30, 0.062, 0.03, 0.03), (-0.36, 0.055, 0.012, 0.012),
            (-0.43, 0.05, 0.0, 0.0)]
    f = fl.Flier(name="Ichthyornis", axis=axis, paint=body_paint, eye=(0.032, -0.262, 0.08, 0.009),
                 eye_col=(0.12, 0.08, 0.05), disp=cc.fuzz_disp(0.002, 60.0), voxel=0.007)
    lead = [(0.04, -0.07, 0.03), (0.22, -0.10, 0.06), (0.38, -0.09, 0.07), (0.72, 0.02, 0.10)]
    trail = [(0.04, 0.07, 0.02), (0.22, 0.10, 0.04), (0.42, 0.07, 0.06), (0.73, 0.03, 0.10)]
    f.wings.append(fl.Wing(lead, trail, wing_col, thickness=0.008, nv=6))

    def crisp(mb, f):
        mb.add(cc.ribbon([((-0.025, 0.16, 0.0), (0.025, 0.16, 0.0)), ((-0.06, 0.25, 0.0), (0.06, 0.25, 0.0))],
                         0.006), GREY)
        for sx in (1, -1):   # dark smudge behind the eye
            mb.add(nh.ellipsoid((sx * 0.036, -0.245, 0.083), (0.004, 0.018, 0.008), subdivisions=1), BLACK)
        teeth = [(sx * 0.008, -0.34 - 0.016 * k, 0.045) for k in range(4) for sx in (1, -1)]
        cc.teeth_row(mb, teeth, 0.006, 0.002, down=True)
    f.crisp = crisp
    return f


if __name__ == "__main__":
    fl.run(make, "Ichthyornis")
