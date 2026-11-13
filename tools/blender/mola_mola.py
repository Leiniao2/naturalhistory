"""
Procedural ocean sunfish (Mola mola) for the map.

A tall, flat, oval disc that ends abruptly in the scalloped clavus instead of a
tail, with long swept dorsal and anal fins, a small beak-like mouth, a round
eye and small pectoral fins. Silvery grey-blue above, mottled pale below.

Usage:
  blender --background --python tools/blender/mola_mola.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OceanSunfish.fbx (map style Swim:
pivot at the body centre, facing -Y, dorsal fin up).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402

BACK_Y = 0.42     # where the body ends in the clavus
TOP = (0.42, 0.48, 0.55)
BELLY = (0.80, 0.82, 0.83)
FIN = (0.38, 0.42, 0.47)
FIN_TIP = (0.27, 0.30, 0.34)
CLAVUS_EDGE = (0.62, 0.66, 0.70)


def half_height(y):
    return 0.41 * math.sqrt(max(0.0, 1.0 - ((y - 0.06) / 0.56) ** 2))


def top(y):
    return half_height(y) + 0.01


def bot(y):
    return -half_height(y)


def width(y):
    return 0.085 * (half_height(y) / 0.41) ** 0.8 * (1.0 - 0.5 * nh.smoothstep(0.0, BACK_Y, y))


def body_color(co):
    shade = nh.smoothstep(-0.28, 0.3, co.z)
    col = nh.lerp(BELLY, TOP, shade)
    blotch = nh.smoothstep(-0.05, 0.45, noise.noise(Vector((co.y * 6.0, co.z * 6.0, 3.3))))
    col = nh.lerp(col, (0.93, 0.94, 0.95), blotch * (0.85 - shade * 0.5))
    freckle = nh.smoothstep(0.2, 0.55, noise.noise(Vector((co.y * 11.0, co.z * 11.0, 8.1))))
    col = nh.lerp(col, (0.30, 0.35, 0.41), freckle * 0.35 * shade)
    return nh.lerp(col, FIN, nh.smoothstep(0.30, BACK_Y, co.y) * 0.5)  # darker toward the clavus


def swept_fin(sign):
    """Dorsal (sign=1) or anal (sign=-1) fin: long, swept back, pointed."""
    edge_z = top if sign > 0 else bot
    y_a, y_b = 0.08, 0.34
    tip = (0.0, 0.43 if sign > 0 else 0.41, sign * 1.02)
    base, edge = [], []
    n, split = 15, 0.6
    for i in range(n):
        u = i / (n - 1)
        y = y_a + (y_b - y_a) * u
        base.append((0.0, y, edge_z(y) - sign * 0.02))
        if u <= split:
            p = fish.bezier((0, y_a, edge_z(y_a)), (0, 0.17, sign * 0.78), tip, u / split)
        else:
            p = fish.bezier(tip, (0, 0.36, sign * 0.6), (0, y_b + 0.02, edge_z(y_b) + sign * 0.02),
                            (u - split) / (1 - split))
        edge.append(tuple(p))

    def color(u, v, co):
        return nh.lerp(FIN, FIN_TIP, v)

    return base, edge, color


def build():
    mb = nh.MeshBuilder()
    fish.body(mb, top, bot, width, -0.5, BACK_Y, body_color, stations=36, ring=24, close_end=False)

    for sign in (1, -1):
        base, edge, color = swept_fin(sign)
        fish.fin(mb, base, edge, color, rows=4, th0=0.03, th1=0.006)

    # Clavus: the scalloped rudder that replaces a tail
    base, edge = [], []
    n = 49
    for i in range(n):
        u = i / (n - 1)
        z = -0.355 + 0.71 * u
        base.append((0.0, BACK_Y - 0.03, z))
        lobe = abs(math.sin(math.pi * 8 * u)) ** 0.7
        edge.append((0.0, BACK_Y + 0.05 + 0.04 * math.sin(math.pi * u) + 0.035 * lobe, z * 1.05))
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(FIN, CLAVUS_EDGE, nh.smoothstep(0.4, 1.0, v)),
             rows=3, th0=0.03, th1=0.006)

    # Small rounded pectoral fins behind the eye, and the gill slit in front of them
    for sx in (1, -1):
        # paddle sticking back and out from a short vertical base
        x = fish.surface_x(top, bot, width, -0.14, -0.03)
        base, edge = [], []
        for i in range(9):
            u = i / 8
            z = 0.015 - 0.07 * u
            base.append((sx * x * 0.85, -0.14, z))
            reach = 0.05 + 0.08 * math.sin(math.pi * u) ** 0.7
            edge.append((sx * (x * 0.85 + reach * 0.35), -0.14 + reach, -0.03 + (z + 0.03) * 1.6))
        fish.fin(mb, base, edge, lambda u, v, co: nh.lerp((0.62, 0.66, 0.70), FIN, v), rows=3, th0=0.012, th1=0.004)
        gx = fish.surface_x(top, bot, width, -0.165, -0.025)
        mb.add(nh.ellipsoid((sx * gx, -0.165, -0.025), (0.008, 0.01, 0.04), subdivisions=1), (0.30, 0.33, 0.37))

    # Eye and the small beak-like mouth
    ex = fish.surface_x(top, bot, width, -0.34, 0.09)
    fish.eyes(mb, -0.34, 0.09, ex, 0.034, (0.78, 0.80, 0.82))
    mb.add(nh.ellipsoid((0, -0.49, -0.015), (0.03, 0.035, 0.03), subdivisions=2), (0.55, 0.58, 0.62))
    mb.add(nh.ellipsoid((0, -0.52, -0.015), (0.014, 0.01, 0.012), subdivisions=1), (0.08, 0.08, 0.09))

    return mb.to_object("OceanSunfish", roughness=0.45)


if __name__ == "__main__":
    nh.run(build, "OceanSunfish", **fish.PREVIEW)
