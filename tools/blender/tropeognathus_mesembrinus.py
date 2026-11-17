"""
Procedural Tropeognathus mesembrinus (Early Cretaceous anhanguerid pterosaur, Romualdo
Formation, Brazil), soaring.

One of the largest toothed pterosaurs, with a wingspan of about 8 metres: a long head whose
upper and lower jaw tips each carry a tall, rounded, keel-like crest, a rosette of long
interlocking fish-grabbing teeth at the front of the jaws, a robust body and broad wings.
Warm brown body and pycnofibre coat, rusty-brown wings with darker tips, the jaw crests
yellow-orange. Pivot at the body centre, faces -Y, wings spread.

Usage:
  blender --background --python tools/blender/tropeognathus_mesembrinus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tropeognathus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_flier as fl  # noqa: E402

BODY = (0.52, 0.38, 0.26)
BELLY = (0.78, 0.68, 0.54)
WING = (0.52, 0.28, 0.18)
WING_TIP = (0.20, 0.12, 0.08)
CREST = (0.92, 0.66, 0.16)
HEAD = (0.70, 0.62, 0.52)


def body_paint(co, n):
    c = cc.countershade(n, BELLY, BODY, BODY)
    if co.y < -0.2:
        c = nh.lerp(c, HEAD, nh.smoothstep(-0.2, -0.3, co.y))
    return cc.mottle(c, co, 0.1)


def wing_col(co, n):
    x = abs(co.x)
    c = nh.lerp(WING, WING_TIP, nh.smoothstep(1.0, 1.6, x))
    if n.z < -0.3:
        c = nh.lerp(c, BELLY, 0.45)
    return cc.mottle(c, co, 0.1, 5.0)


def make():
    axis = [(0.24, 0.0, 0.0, 0.0), (0.20, 0.0, 0.015, 0.015), (0.12, 0.0, 0.065, 0.055),
            (0.0, 0.0, 0.085, 0.07), (-0.09, 0.01, 0.07, 0.06), (-0.15, 0.03, 0.04, 0.04),
            (-0.21, 0.05, 0.035, 0.035), (-0.26, 0.06, 0.035, 0.045), (-0.33, 0.055, 0.025, 0.032),
            (-0.48, 0.045, 0.016, 0.02), (-0.60, 0.04, 0.0, 0.0)]
    f = fl.Flier(name="Tropeognathus", axis=axis, paint=body_paint, eye=(0.026, -0.27, 0.08, 0.009),
                 disp=cc.fuzz_disp(0.003, 60.0))
    f.blobs.append(((0.07, -0.06, 0.02), (0.06, 0.06, 0.04), True))
    lead = [(0.06, -0.07, 0.02), (0.35, -0.13, 0.05), (0.60, -0.09, 0.06), (1.1, 0.0, 0.08), (1.7, 0.14, 0.12)]
    trail = [(0.06, 0.15, 0.0), (0.30, 0.24, 0.02), (0.60, 0.22, 0.04), (1.1, 0.16, 0.07), (1.7, 0.15, 0.12)]
    f.wings.append(fl.Wing(lead, trail, wing_col, thickness=0.014, nv=8, billow=0.02,
                           bone=((0.36, 0.24, 0.16), 0.026)))
    f.tubes.append(([(0.06, 0.12, -0.01), (0.08, 0.24, -0.02), (0.08, 0.34, -0.02)], [0.024, 0.014, 0.009], True))

    def crisp(mb, f):
        up = [((0, -0.42, 0.05), (0, -0.42, 0.06)), ((0, -0.48, 0.06), (0, -0.47, 0.11)),
              ((0, -0.54, 0.05), (0, -0.54, 0.10)), ((0, -0.59, 0.042), (0, -0.59, 0.05))]
        lo = [((0, -0.44, 0.03), (0, -0.44, 0.025)), ((0, -0.50, 0.028), (0, -0.50, -0.02)),
              ((0, -0.56, 0.032), (0, -0.56, -0.01)), ((0, -0.595, 0.037), (0, -0.595, 0.03))]
        mb.add(cc.ribbon(up, 0.01, normal_hint=Vector((1, 0, 0))), CREST)
        mb.add(cc.ribbon(lo, 0.01, normal_hint=Vector((1, 0, 0))), CREST)
        teeth = []
        for k in range(5):
            y = -0.58 + k * 0.03
            for sx in (1, -1):
                teeth.append((sx * 0.012, y, 0.035))
        cc.teeth_row(mb, teeth, 0.03, 0.004, down=True)
    f.crisp = crisp
    return f


if __name__ == "__main__":
    fl.run(make, "Tropeognathus")
