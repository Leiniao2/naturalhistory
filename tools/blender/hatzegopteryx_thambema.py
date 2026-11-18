"""
Procedural Hatzegopteryx thambema (latest Cretaceous azhdarchid pterosaur, Hateg Island, Romania).

A robust giant azhdarchid, soaring: a 10-12 metre wingspan, an enormous, broad, deep skull
with a long, straight, toothless dagger beak and a low rounded crest, carried on a short,
very thick neck; a compact furry body with heavy shoulders and hind legs trailing behind.
Dark brown pycnofibre coat with a pale throat, a bone-yellow beak, a red-and-black crest and
dark wing tips.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/hatzegopteryx_thambema.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hatzegopteryx.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_flier as fl  # noqa: E402

BODY = (0.34, 0.24, 0.17)
THROAT = (0.80, 0.72, 0.60)
WING = (0.38, 0.28, 0.20)
WING_TIP = (0.12, 0.09, 0.07)
BEAK = (0.86, 0.76, 0.52)
CREST = (0.70, 0.14, 0.08)


def body_paint(co, n):
    c = cc.countershade(n, THROAT, BODY, BODY)
    if co.y < -0.30:
        c = nh.lerp(c, BEAK, nh.smoothstep(-0.34, -0.48, co.y))
    return cc.mottle(c, co, 0.1)


def wing_col(co, n):
    x = abs(co.x)
    c = nh.lerp(WING, WING_TIP, nh.smoothstep(0.9, 1.5, x))
    if n.z < -0.3:
        c = nh.lerp(c, THROAT, 0.4)
    return cc.mottle(c, co, 0.1, 5.0)


def make():
    axis = [(0.24, 0.0, 0.0, 0.0), (0.20, 0.0, 0.02, 0.02), (0.12, 0.0, 0.08, 0.07),
            (0.0, 0.0, 0.10, 0.085), (-0.09, 0.02, 0.085, 0.075), (-0.15, 0.05, 0.065, 0.065),
            (-0.21, 0.08, 0.075, 0.075), (-0.27, 0.09, 0.10, 0.11), (-0.37, 0.085, 0.075, 0.085),
            (-0.50, 0.07, 0.042, 0.048), (-0.66, 0.055, 0.014, 0.016), (-0.74, 0.05, 0.0, 0.0)]
    f = fl.Flier(name="Hatzegopteryx", axis=axis, paint=body_paint, eye=(0.085, -0.30, 0.135, 0.012),
                 eye_col=(0.85, 0.6, 0.15), disp=cc.fuzz_disp(0.003, 60.0), voxel=0.011)
    f.blobs.append(((0.08, -0.06, 0.03), (0.08, 0.07, 0.05), True))      # heavy flight muscles
    lead = [(0.07, -0.07, 0.03), (0.33, -0.13, 0.06), (0.55, -0.10, 0.07), (1.0, -0.02, 0.09), (1.55, 0.12, 0.13)]
    trail = [(0.07, 0.16, 0.0), (0.30, 0.26, 0.02), (0.55, 0.24, 0.04), (1.0, 0.17, 0.08), (1.55, 0.13, 0.13)]
    f.wings.append(fl.Wing(lead, trail, wing_col, thickness=0.016, nv=8, billow=0.02,
                           bone=((0.30, 0.22, 0.16), 0.03)))
    f.tubes.append(([(0.07, 0.12, -0.01), (0.09, 0.24, -0.03), (0.09, 0.34, -0.03)], [0.03, 0.018, 0.012], True))

    def crisp(mb, f):
        crest = [((0, -0.36, 0.16), (0, -0.35, 0.17)), ((0, -0.31, 0.18), (0, -0.28, 0.22)),
                 ((0, -0.26, 0.18), (0, -0.22, 0.21)), ((0, -0.21, 0.15), (0, -0.19, 0.16))]
        mb.add(cc.ribbon(crest, 0.014, normal_hint=Vector((1, 0, 0))),
               lambda co, n: CREST if co.z < 0.195 else (0.08, 0.06, 0.05))
    f.crisp = crisp
    return f


if __name__ == "__main__":
    fl.run(make, "Hatzegopteryx")
