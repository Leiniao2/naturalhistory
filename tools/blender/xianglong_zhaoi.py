"""
Procedural Xianglong zhaoi (Early Cretaceous gliding lizard, Yixian Formation, Liaoning, China).

A small acrodontan lizard about 15 centimetres long with a gliding membrane (patagium)
stretched over eight greatly elongated ribs on each side, spread like the wings of a
living Draco "flying dragon": a short triangular head with big eyes, a slim body, four
slender sprawling legs and a very long, whip-like tail. Green-brown above with dark cross
bars, the wing membranes barred orange and dark brown, a pale belly (colours conjectural).
Faces -Y, pivot at the body centre (Soar style, gliding).

Usage:
  blender --background --python tools/blender/xianglong_zhaoi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Xianglong.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_flier as fl  # noqa: E402

BACK = (0.30, 0.36, 0.20)
FLANK = (0.48, 0.50, 0.32)
BELLY = (0.88, 0.86, 0.74)
BAR = (0.16, 0.18, 0.10)
WING = (0.86, 0.50, 0.14)
WING_BAR = (0.26, 0.15, 0.08)
RIB = (0.40, 0.26, 0.12)


def body_paint(co, n):
    c = cc.countershade(n, BELLY, FLANK, BACK)
    bar = cc.stripes(co, 28.0, warp=0.6) * nh.smoothstep(0.0, 0.6, n.z)
    return cc.mottle(nh.lerp(c, BAR, 0.6 * bar), co, 0.1)


def wing_col(co, n):
    r = math.hypot(co.x, co.y + 0.02)
    c = nh.lerp(WING, WING_BAR, nh.smoothstep(0.55, 0.85, 0.5 + 0.5 * math.sin(r * 38.0)))
    if n.z < -0.3:
        c = nh.lerp(c, BELLY, 0.5)
    return c


def make():
    axis = [(1.05, 0.0, 0.0, 0.0), (0.95, 0.0, 0.006, 0.006), (0.60, 0.0, 0.012, 0.012), (0.30, 0.0, 0.022, 0.02),
            (0.14, 0.0, 0.045, 0.035), (0.0, 0.0, 0.055, 0.04), (-0.14, 0.0, 0.05, 0.038),
            (-0.22, 0.005, 0.035, 0.03), (-0.27, 0.01, 0.045, 0.035), (-0.34, 0.008, 0.035, 0.026),
            (-0.40, 0.0, 0.015, 0.012), (-0.42, -0.002, 0.0, 0.0)]
    f = fl.Flier(name="Xianglong", axis=axis, paint=body_paint, eye=(0.036, -0.31, 0.022, 0.013),
                 eye_col=(0.85, 0.55, 0.12), disp=cc.scales_disp(0.0015, 60.0), voxel=0.007)
    # the patagium: spread on the elongated ribs from the flank
    lead = [(0.04, -0.11, 0.005), (0.16, -0.135, 0.01), (0.29, -0.11, 0.013), (0.37, -0.05, 0.015), (0.40, 0.01, 0.015)]
    trail = [(0.04, 0.11, 0.0), (0.16, 0.13, 0.005), (0.29, 0.105, 0.01), (0.37, 0.05, 0.013), (0.40, 0.015, 0.015)]
    f.wings.append(fl.Wing(lead, trail, wing_col, thickness=0.008, nv=6, billow=0.006))
    # four slender sprawling legs
    f.tubes.append(([(0.04, -0.16, -0.005), (0.10, -0.18, -0.02), (0.14, -0.24, -0.03)], [0.012, 0.008, 0.005], True))
    f.tubes.append(([(0.04, 0.14, -0.005), (0.11, 0.18, -0.02), (0.14, 0.26, -0.03)], [0.014, 0.009, 0.005], True))

    def crisp(mb, f):
        # the eight long ribs through the membrane
        for sx in (1, -1):
            for k in range(8):
                yb = -0.09 + 0.18 * k / 7
                base = Vector((sx * 0.04, yb, 0.006))
                tip = Vector((sx * (0.04 + 0.33 * math.sqrt(1 - (yb / 0.13) ** 2)), yb * 0.9, 0.014))
                mb.add(nh.tube([base, tip], [0.004, 0.0015], sides=4), RIB)
            for y in (-0.24, 0.26):
                foot = Vector((sx * 0.14, y, -0.03))
                for k in range(5):
                    d = Vector((sx * math.cos(math.radians(-60 + 30 * k)), -math.sin(math.radians(-60 + 30 * k)) * sx * 0.0 - 0.6 + 0.3 * k, 0)).normalized()
                    mb.add(nh.tube([foot, foot + d * 0.03], [0.003, 0.0], sides=4), BACK)
    f.crisp = crisp
    return f


if __name__ == "__main__":
    fl.run(make, "Xianglong")
