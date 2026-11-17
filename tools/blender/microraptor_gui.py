"""
Procedural Microraptor gui (Early Cretaceous dromaeosaurid, Jiufotang Formation, China), gliding.

A crow-sized 'four-winged' dinosaur: long flight feathers on the arms and also on the legs,
which it held out to the sides as a second pair of wings, and a long tail ending in a
diamond-shaped feather fan. Melanosomes show the plumage was glossy iridescent black like a
crow's. Small toothed head, sickle claw on each foot.
Pivot at the body centre, faces -Y, wings spread.

Usage:
  blender --background --python tools/blender/microraptor_gui.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Microraptor.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_flier as fl  # noqa: E402

BLACK = (0.05, 0.05, 0.07)
SHEEN = (0.10, 0.14, 0.24)


def gloss(co, n):
    c = nh.lerp(BLACK, SHEEN, max(0.0, n.z) * 0.8 * (0.5 + 0.5 * math.sin(co.x * 9.0 + co.y * 7.0)))
    return cc.mottle(c, co, 0.15, 8.0)


def feather_col(co, n):
    c = gloss(co, n)
    # faint quill lines along the span
    k = 0.5 + 0.5 * math.sin(abs(co.x) * 70.0)
    return tuple(v * (0.85 + 0.25 * k) for v in c)


def make():
    axis = [(0.80, 0.0, 0.0, 0.0), (0.70, 0.0, 0.008, 0.008), (0.45, 0.0, 0.015, 0.014),
            (0.20, 0.0, 0.03, 0.028), (0.08, 0.0, 0.06, 0.06), (-0.06, 0.0, 0.07, 0.07),
            (-0.17, 0.01, 0.055, 0.06), (-0.24, 0.04, 0.03, 0.03), (-0.30, 0.06, 0.03, 0.03),
            (-0.35, 0.07, 0.035, 0.035), (-0.42, 0.065, 0.025, 0.025), (-0.50, 0.055, 0.012, 0.012),
            (-0.53, 0.05, 0.0, 0.0)]
    f = fl.Flier(name="Microraptor", axis=axis, paint=gloss, eye=(0.025, -0.38, 0.08, 0.009),
                 eye_col=(0.75, 0.55, 0.15), disp=cc.fuzz_disp(0.003, 60.0), voxel=0.008)
    # arms spread
    f.tubes.append(([(0.03, -0.12, 0.01), (0.22, -0.08, 0.03), (0.42, -0.14, 0.04), (0.55, -0.16, 0.04)],
                    [0.025, 0.018, 0.012, 0.006], True))
    # legs held out back and to the side
    f.tubes.append(([(0.04, 0.08, -0.02), (0.14, 0.16, -0.04), (0.24, 0.26, -0.05), (0.30, 0.34, -0.05)],
                    [0.03, 0.018, 0.01, 0.006], True))
    fore_lead = [(0.03, -0.12, 0.01), (0.22, -0.09, 0.03), (0.42, -0.14, 0.04), (0.80, -0.10, 0.06)]
    fore_trail = [(0.04, 0.04, 0.0), (0.25, 0.14, 0.02), (0.50, 0.12, 0.04), (0.82, -0.04, 0.06)]
    f.wings.append(fl.Wing(fore_lead, fore_trail, feather_col, thickness=0.008, nv=6))
    hind_lead = [(0.06, 0.10, -0.02), (0.18, 0.16, -0.04), (0.30, 0.30, -0.05), (0.36, 0.38, -0.05)]
    hind_trail = [(0.03, 0.22, -0.02), (0.12, 0.34, -0.04), (0.22, 0.44, -0.05), (0.34, 0.44, -0.05)]
    f.wings.append(fl.Wing(hind_lead, hind_trail, feather_col, thickness=0.007, nv=5))

    def crisp(mb, f):
        # diamond tail fan around the distal tail
        pts = []
        for i in range(8):
            u = i / 7
            y = 0.45 + 0.42 * u
            w = 0.075 * math.sin(math.pi * min(1.0, u * 1.05)) + 0.005
            pts.append(((-w, y, 0.0), (w, y, 0.0)))
        mb.add(cc.ribbon(pts, 0.006, normal_hint=Vector((0, 0, 1))), feather_col)
        for sx in (1, -1):
            for k in range(3):
                base = Vector((sx * 0.55, -0.16 + 0.01 * k, 0.04))
                mb.add(cc.cone(base, base + Vector((sx * 0.02, -0.025, -0.01)), 0.004, sides=4), cc.CLAW)
    f.crisp = crisp
    return f


if __name__ == "__main__":
    fl.run(make, "Microraptor")
