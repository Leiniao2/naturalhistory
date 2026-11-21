"""
Procedural Namalia villiersiensis (Ediacaran petalonamid) for the map, Fixed style.

Small, upright, cup- to bag-shaped animals partly buried in the sand, their walls quilted
into narrow, tube-like chambers that zig-zag in chevrons up the sides, open at the top.
A cluster of four. Sandy grey-tan with darker chamber seams. Pivot at the base (z = 0),
faces -Y.

Output: Assets/Resources/Models/Species/Namalia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

CELL = (0.84, 0.66, 0.48)
SEAM = (0.40, 0.32, 0.24)
RIM = (0.92, 0.80, 0.64)
INSIDE = (0.22, 0.17, 0.13)
ROWS = 9


def chevron(u, v):
    th = u * math.tau
    return v * ROWS + 0.9 * abs(math.sin(th * 3))


def cup(H, R):
    def shape(u, v):
        if v <= 0.85:
            t = v / 0.85
            prof = (0.35 + 0.65 * math.sin(math.pi * 0.5 * min(1.0, t * 1.4))) * (1 - 0.15 * t)
            q = chevron(u, t) % 1.0
            bump = 0.05 * math.sin(math.pi * q)
            return R * prof * (1 + bump), H * t
        t = (v - 0.85) / 0.15
        return R * 0.85 * (1 - 0.18 * t), H * (1 - 0.12 * t)

    def color(u, v, co):
        if v > 0.86:
            return nh.lerp(RIM, INSIDE, nh.smoothstep(0.86, 0.93, v))
        t = v / 0.85
        q = chevron(u, t) % 1.0
        seam = 1 - nh.smoothstep(0.0, 0.15, min(q, 1 - q))
        return ep.mottle(nh.lerp(CELL, SEAM, seam * 0.8), co)

    return ep.lathe(40, 30, shape, color)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.65)
    for x, y, H, R, yaw, lean in [(0, 0.05, 1.0, 0.3, 0, 4), (0.4, -0.15, 0.7, 0.22, 40, -10),
                                  (-0.38, -0.12, 0.6, 0.2, 80, 12), (0.05, 0.42, 0.5, 0.16, 20, 8)]:
        p = cup(H, R)
        ep.place(p[0], x, y, yaw, lean, z=-0.06)
        ep.add(mb, p)
    return ep.finish(mb, "Namalia")


if __name__ == "__main__":
    ep.export(build, "Namalia")
