"""
Procedural Thectardis avalonensis (Ediacaran possible sponge) for the map, Fixed style.

Tall, slender inverted cones, point down in the sediment and widening upward to an open,
rimmed top, a simple sponge-like shape that may have pumped water up through its walls and
out of the top. A stand of three cones; olive-grey with fine pores, dark open top.
Pivot at the base (z = 0), faces -Y.

Output: Assets/Resources/Models/Species/Thectardis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_b2_ediacaran_plan as ep  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

WALL = (0.64, 0.62, 0.50)
WALL_DARK = (0.44, 0.42, 0.34)
RIM = (0.80, 0.78, 0.66)
INSIDE = (0.16, 0.14, 0.12)


def cone(H, R):
    def shape(u, v):
        th = u * math.tau
        flat = 1.0 + 0.12 * math.cos(2 * th)          # slightly flattened, triangular in side view
        if v <= 0.8:
            t = v / 0.8
            return (0.012 + R * t ** 0.9) * flat, H * t
        if v <= 0.88:
            t = (v - 0.8) / 0.08
            return (R * (1 + 0.06 * math.sin(math.pi * t)) - R * 0.12 * t) * flat, H + H * 0.02 * math.sin(math.pi * t)
        t = (v - 0.88) / 0.12
        return R * (0.88 - 0.25 * t) * flat, H * (1 - 0.15 * t)

    def color(u, v, co):
        if v > 0.86:
            return nh.lerp(RIM, INSIDE, nh.smoothstep(0.86, 0.92, v))
        pore = noise.noise(Vector(co) * 40.0)
        c = nh.lerp(WALL, WALL_DARK, nh.smoothstep(0.2, 0.5, pore))
        c = nh.lerp(c, RIM, nh.smoothstep(0.74, 0.82, v) * 0.7)
        return nh.lerp(c, WALL_DARK, nh.smoothstep(0.15, 0.0, v))

    return ep.lathe(40, 20, shape, color, cap_start=True, cap_end=True)


def build():
    mb = nh.MeshBuilder()
    ep.mat(mb, 0.55)
    for x, y, H, R, yaw, lean in [(0.0, 0.05, 1.5, 0.24, 0, 4), (0.3, -0.18, 1.0, 0.17, 30, -8), (-0.28, -0.12, 0.72, 0.13, 60, 10)]:
        p = cone(H, R)
        ep.place(p[0], x, y, yaw, lean, z=-0.05)
        ep.add(mb, p)
    return ep.finish(mb, "Thectardis")


if __name__ == "__main__":
    ep.export(build, "Thectardis")
