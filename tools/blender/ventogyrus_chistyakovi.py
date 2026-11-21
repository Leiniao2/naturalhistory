"""
Procedural Ventogyrus chistyakovi (Ediacaran petalonamid) for the map, Fixed style.

A boat- or egg-shaped body with three-fold symmetry, standing half buried in the sand: three
deep lengthwise grooves split it into three bulging vanes, and each vane is quilted into
stacked, tube-like chambers that run around the body. Two individuals. Ochre-orange chambers,
dark seams. Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Ventogyrus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402

CELL = (0.90, 0.64, 0.38)
CELL_DARK = (0.70, 0.44, 0.24)
SEAM = (0.36, 0.20, 0.12)
CHAMBERS = 11


def groove(th):
    best = 0.0
    for k in range(3):
        d = math.atan2(math.sin(th - k * math.tau / 3 - math.pi / 3), math.cos(th - k * math.tau / 3 - math.pi / 3))
        best = max(best, math.exp(-(d / 0.14) ** 2))
    return best


def body(H, R):
    def shape(u, v):
        th = u * math.tau
        prof = math.sin(math.pi * v) ** 0.75
        vane = math.floor(((th + math.pi / 3) % math.tau) / (math.tau / 3))
        q = 0.5 + 0.5 * math.cos((v * CHAMBERS + vane * 0.5) * math.tau)
        r = R * prof * (1 - 0.28 * groove(th)) * (0.94 + 0.06 * q)
        return max(r, 0.004), H * (v - 0.25)

    def color(u, v, co):
        th = u * math.tau
        vane = math.floor(((th + math.pi / 3) % math.tau) / (math.tau / 3))
        t = (v * CHAMBERS + vane * 0.5) % 1.0
        seam = 1 - nh.smoothstep(0.0, 0.14, min(t, 1 - t))
        c = nh.lerp(CELL, CELL_DARK, 0.3 * vane / 2)
        c = nh.lerp(c, SEAM, max(seam * 0.75, groove(th) * 0.9))
        return ep.mottle(c, co)

    return ep.lathe(60, 42, shape, color)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.7)
    for x, y, H, R, yaw, lean in [(-0.05, 0.05, 1.5, 0.36, 0, 18), (0.45, -0.2, 0.9, 0.22, 70, -25)]:
        p = body(H, R)
        ep.place(p[0], x, y, yaw, lean)
        ep.add(mb, p)
    return ep.finish(mb, "Ventogyrus")


if __name__ == "__main__":
    ep.export(build, "Ventogyrus")
