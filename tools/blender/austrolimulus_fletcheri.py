"""
Procedural Austrolimulus fletcheri (Middle Triassic freshwater horseshoe crab, ~8 cm).

A strange horseshoe crab from the Hawkesbury Sandstone near Sydney, Australia, that lived
in fresh water: the corners of its broad head shield were drawn out into enormous,
sweeping horn-like spines curving back past the body, perhaps to keep it from sinking into
soft mud or to stabilise it in the current; behind sat a small, spiny rear shield and a
spike-like tail. Faces -Y, pivot at the body centre.

Output: Assets/Resources/Models/Species/Austrolimulus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402

SHELL = (0.40, 0.30, 0.18)
RIM = (0.66, 0.52, 0.32)
DARK = (0.16, 0.12, 0.08)
EYE = (0.06, 0.05, 0.04)
LEG = (0.48, 0.38, 0.24)


def shell_col(cy, rx, ry):
    def fn(co, n):
        r = math.hypot(co.x / rx, (co.y - cy) / ry)
        c = nh.lerp(SHELL, RIM, nh.smoothstep(0.75, 0.98, r))
        if abs(co.x) < 0.02:
            c = nh.lerp(c, DARK, 0.4)
        return c
    return fn


def dome(cy, rx, ry, h):
    bm = nh.ellipsoid((0, cy, 0), (rx, ry, h), subdivisions=4)
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z *= 0.15
        x = abs(v.co.x)
        if v.co.z > 0:
            v.co.z += 0.012 * math.exp(-(x / 0.02) ** 2) + 0.008 * math.exp(-((x - rx * 0.45) / 0.02) ** 2)
    return bm


def build():
    mb = nh.MeshBuilder()
    p = dome(-0.12, 0.30, 0.24, 0.10)
    for v in p.verts:
        if v.co.y > -0.02:
            v.co.y = -0.02 + (v.co.y + 0.02) * 0.25
    mb.add(p, shell_col(-0.12, 0.30, 0.24))
    # the huge genal spines sweeping out and back
    for sx in (1, -1):
        pts = [Vector((sx * (0.24 + 0.04 * t + 0.20 * math.sin(t * 1.4)), -0.06 + 0.62 * t * t + 0.10 * t, -0.005 * t))
               for t in [k / 10 for k in range(11)]]
        mb.add(nh.tube(pts, [0.055 * (1.0 - t) + 0.002 for t in [k / 10 for k in range(11)]], sides=8,
                       scale_xy=(1.0, 0.35)), RIM)
    o = dome(0.10, 0.16, 0.12, 0.06)
    mb.add(o, shell_col(0.10, 0.16, 0.12))
    for i in range(5):
        y = 0.03 + i * 0.035
        for sx in (1, -1):
            x = 0.16 * math.sqrt(max(0.0, 1 - ((y - 0.10) / 0.12) ** 2)) * 0.95
            b = Vector((sx * x, y, 0.0))
            mb.add(kit.cone(b, b + Vector((sx * 0.04, 0.03, -0.004)), 0.009, sides=4), RIM, smooth=False)
    mb.add(nh.tube([(0, 0.21, 0.01), (0, 0.40, 0.0), (0, 0.56, -0.02)], [0.02, 0.012, 0.0], sides=6), SHELL)
    for sx in (1, -1):
        mb.add(nh.ellipsoid((sx * 0.14, -0.15, 0.085), (0.016, 0.04, 0.010), subdivisions=2), EYE)
    for i in range(5):
        for sx in (1, -1):
            b = Vector((sx * 0.06, -0.18 + i * 0.04, -0.01))
            mb.add(nh.tube([b, b + Vector((sx * 0.12, -0.02, -0.03)), b + Vector((sx * 0.18, 0.0, -0.045))],
                           [0.010, 0.008, 0.004], sides=5), LEG)
    return kit.finish(mb, "Austrolimulus", pivot="center", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Austrolimulus", background=(0.06, 0.12, 0.10), views=((35, 35), (-90, 5), (0, 89)))
