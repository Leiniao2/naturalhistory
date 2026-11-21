"""
Procedural Encrinus liliiformis (Middle Triassic sea lily, ~1 m tall) for map colonies.

The classic "stone lily" of the German Muschelkalk sea, about 240 million years old: a long
stem of round, coin-like columnals, a small bowl-shaped cup and a crown of ten thick arms,
each made of a double zig-zag row of plates, which closed together into a tulip-like bud and
opened into a fan to strain food from the current. Shown half open. Fixed, pivot on the
ground (on a patch of shelly mud).

Output: Assets/Resources/Models/Species/Encrinus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

STEM = (0.78, 0.70, 0.56)
STEM_DARK = (0.50, 0.42, 0.30)
CUP = (0.70, 0.58, 0.42)
ARM = (0.86, 0.76, 0.58)
ARM_DARK = (0.58, 0.46, 0.32)
PINNULE = (0.92, 0.84, 0.68)


def arm_col(co, n):
    # biserial arms: alternating plates, a zig-zag of seams
    k = 0.5 + 0.5 * math.sin(co.z * 260.0 + math.atan2(co.y, co.x) * 40.0)
    return nh.lerp(ARM, ARM_DARK, 0.6 * nh.smoothstep(0.7, 1.0, k))


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 0.32, ((0.40, 0.37, 0.30), (0.58, 0.54, 0.44)))
    for k in range(4):        # small holdfast
        a = k / 4 * math.tau + 0.4
        mb.add(nh.tube([(0, 0, 0.03), (math.cos(a) * 0.08, math.sin(a) * 0.08, 0.015),
                        (math.cos(a + 0.4) * 0.15, math.sin(a + 0.4) * 0.15, 0.005)], [0.028, 0.016, 0.0], sides=6),
               STEM_DARK)
    n = 20
    stem_h = 0.85
    pts = [Vector((0.10 * math.sin(t * 2.0) * t, 0.04 * math.sin(t * 3.1) * t, 0.02 + stem_h * t))
           for t in [i / n for i in range(n + 1)]]
    mb.add(nh.tube(pts, [0.032 * (1.05 - 0.15 * i / n) for i in range(n + 1)], sides=12), ec._columnal_color(STEM, STEM_DARK))
    top = pts[-1]
    up = (pts[-1] - pts[-2]).normalized()
    # cup
    mb.add(nh.tube([top, top + up * 0.05, top + up * 0.10], [0.035, 0.065, 0.085], sides=10), CUP)
    base = top + up * 0.10
    # ten thick arms, rising and bending inward a little at the tips: a half-open tulip crown
    for k in range(10):
        a = k / 10 * math.tau
        out = Vector((math.cos(a), math.sin(a), 0.0))
        p = base + out * 0.07
        arm_pts, rad = [p.copy()], [0.032]
        steps = 7
        for i in range(1, steps + 1):
            t = i / steps
            d = (out * (0.42 - 0.70 * t) + Vector((0, 0, 1.0))).normalized()
            p = p + d * 0.06
            arm_pts.append(p.copy())
            rad.append(0.032 * (1.0 - 0.45 * t))
        rad[-1] = 0.006
        mb.add(nh.tube(arm_pts, rad, sides=8), arm_col)
        # pinnules on the inner side, a fringe
        for i in range(1, steps):
            b = arm_pts[i]
            mb.add(nh.tube([b, b - out * 0.045 + Vector((0, 0, 0.03))], [0.006, 0.0], sides=3), PINNULE, smooth=False)
    return ec._finish(mb, "Encrinus")


if __name__ == "__main__":
    nh.run(build, "Encrinus", **ec.VIEWS)
