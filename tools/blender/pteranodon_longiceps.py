"""
Procedural Pteranodon longiceps (Late Cretaceous pteranodontid pterosaur, Western Interior
Seaway, North America), soaring.

A huge, toothless ocean-going pterosaur with a wingspan of about 6-7 metres: a long, pointed
beak, a tall backward-sweeping crest on the skull of the males, a short body with a stubby
tail, and long narrow wings of skin stretched from the enormous fourth finger to the ankles.
Pale grey-white head and body like a seabird, grey-brown wings with darker tips and trailing
edge, a red crest. Pivot at the body centre, faces -Y, wings spread.

Usage:
  blender --background --python tools/blender/pteranodon_longiceps.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pteranodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_flier as fl  # noqa: E402

BODY = (0.86, 0.86, 0.84)
BACK = (0.58, 0.58, 0.58)
WING = (0.46, 0.40, 0.34)
WING_TIP = (0.16, 0.14, 0.13)
CREST = (0.78, 0.20, 0.10)
BEAK = (0.90, 0.78, 0.50)


def body_paint(co, n):
    c = cc.countershade(n, BODY, BODY, BACK)
    if co.y < -0.22:
        t = nh.smoothstep(-0.25, -0.55, co.y)
        c = nh.lerp(c, BEAK, t)
    return cc.mottle(c, co, 0.06)


def wing_col(co, n):
    x = abs(co.x)
    c = nh.lerp(WING, WING_TIP, nh.smoothstep(1.0, 1.55, x))
    if n.z < -0.3:
        c = nh.lerp(c, (0.80, 0.78, 0.74), 0.5)
    return cc.mottle(c, co, 0.08, 5.0)


def make():
    axis = [(0.26, 0.0, 0.0, 0.0), (0.22, 0.0, 0.012, 0.012), (0.14, 0.0, 0.05, 0.045),
            (0.02, 0.0, 0.07, 0.06), (-0.08, 0.01, 0.06, 0.055), (-0.14, 0.03, 0.03, 0.03),
            (-0.20, 0.05, 0.028, 0.028), (-0.24, 0.06, 0.03, 0.04), (-0.30, 0.055, 0.022, 0.03),
            (-0.45, 0.045, 0.012, 0.016), (-0.62, 0.035, 0.0, 0.0)]
    f = fl.Flier(name="Pteranodon", axis=axis, paint=body_paint,
                 eye=(0.02, -0.255, 0.075, 0.008), eye_col=(0.05, 0.04, 0.03))
    f.blobs.append(((0.06, -0.06, 0.02), (0.05, 0.05, 0.035), True))      # shoulder muscles
    lead = [(0.05, -0.06, 0.02), (0.35, -0.10, 0.06), (0.55, -0.06, 0.07), (1.0, 0.02, 0.10), (1.6, 0.12, 0.16)]
    trail = [(0.05, 0.12, 0.0), (0.30, 0.16, 0.03), (0.55, 0.13, 0.05), (1.0, 0.10, 0.09), (1.6, 0.13, 0.16)]
    f.wings.append(fl.Wing(lead, trail, wing_col, thickness=0.012, nv=7, billow=0.015,
                           bone=((0.40, 0.36, 0.32), 0.022)))
    # legs trailing behind
    f.tubes.append(([(0.05, 0.10, -0.01), (0.07, 0.22, -0.02), (0.07, 0.32, -0.02)], [0.02, 0.012, 0.008], True))

    def crisp(mb, f):
        crest = [((0, -0.26, 0.08), (0, -0.24, 0.10)), ((0, -0.20, 0.09), (0, -0.14, 0.14)),
                 ((0, -0.17, 0.08), (0, -0.02, 0.15)), ((0, -0.16, 0.07), (0, 0.06, 0.13))]
        mb.add(cc.ribbon(crest, 0.012, normal_hint=Vector((1, 0, 0))), CREST)
    f.crisp = crisp
    return f


if __name__ == "__main__":
    fl.run(make, "Pteranodon")
