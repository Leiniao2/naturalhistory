"""
Procedural Megapiranha paranensis (Late Miocene of the Parana basin, Argentina)
for map colonies: a giant piranha-like serrasalmid known from a jaw with a
zig-zag row of teeth intermediate between those of pacus and piranhas.

Estimated at roughly 70 cm to 1 m long: the deep, disc-like, laterally
compressed body of a piranha with a blunt head, a deep lower jaw jutting
forward with interlocking triangular teeth, a small adipose fin behind the
dorsal fin and a forked tail. Shown silvery grey with a darker back and the
red throat and belly of the red-bellied piranha (a reconstruction choice).
Built with nh_fish.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/megapiranha_paranensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MegapiranhaParanensis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_fish as fish  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import noise, Vector  # noqa: E402

SILVER = (0.62, 0.64, 0.64)
BACK = (0.26, 0.29, 0.30)
RED = (0.78, 0.26, 0.14)
FIN = (0.30, 0.30, 0.30)
TOOTH = (0.94, 0.92, 0.86)
TAIL_Y = 0.40


def half_height(y):
    disc = 0.24 * max(0.0, 1 - ((y + 0.02) / 0.43) ** 2) ** 0.55
    ped = 0.055
    return fish.smax(disc, ped * nh.smoothstep(0.1, 0.35, y), 60)


def top(y):
    return 0.02 + half_height(y) * 1.05


def bot(y):
    return 0.02 - half_height(y) * 1.0 - 0.03 * nh.smoothstep(-0.30, -0.42, y)


def width(y):
    return 0.075 * max(0.05, 1 - ((y + 0.05) / 0.46) ** 2) ** 0.6


def pattern(co):
    y, z = co.y, co.z
    mid = (top(y) + bot(y)) * 0.5
    c = nh.lerp(SILVER, BACK, nh.smoothstep(mid + 0.02, top(y), z))
    c = nh.lerp(c, RED, 0.85 * nh.smoothstep(mid - 0.03, bot(y) + 0.02, z) * nh.smoothstep(0.25, -0.05, y))
    c = nh.lerp(c, nh.lerp(c, (1, 1, 1), 0.3), 0.4 * max(0.0, noise.noise(Vector((y * 50, z * 50, 0)))))
    return c


def median_fin(y_a, y_b, sign, reach, sweep, cols=13):
    edge_z = top if sign > 0 else bot
    base, edge = [], []
    for i in range(cols):
        u = i / (cols - 1)
        y = y_a + (y_b - y_a) * u
        z = edge_z(y) - sign * 0.012
        base.append((0.0, y, z))
        h = 0.02 + reach * math.sin(math.pi * u) ** 0.6 * (1.0 - 0.4 * u)
        edge.append((0.0, y + sweep * u, z + sign * h))
    return base, edge


def build():
    mb = nh.MeshBuilder()
    fish.body(mb, top, bot, width, -0.45, TAIL_Y + 0.01, pattern, stations=36, ring=24, close_end=False)
    base, edge = median_fin(-0.05, 0.14, 1, 0.12, 0.08)
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(BACK, FIN, v), rows=4, th0=0.016, th1=0.004)
    base, edge = median_fin(0.24, 0.30, 1, 0.035, 0.02, cols=5)       # adipose fin
    fish.fin(mb, base, edge, lambda u, v, co: BACK, rows=2, th0=0.014, th1=0.006)
    base, edge = median_fin(0.06, 0.30, -1, 0.09, 0.06)
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(RED, FIN, v), rows=4, th0=0.016, th1=0.004)
    base, edge = [], []
    for i in range(11):
        u = i / 10
        base.append((0.0, TAIL_Y, -0.05 + 0.12 * u))
        fork = 0.06 * (1 - abs(u - 0.5) * 2)
        edge.append((0.0, TAIL_Y + 0.17 - fork * 1.6, -0.18 + 0.40 * u))
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(FIN, (0.12, 0.12, 0.12), v), rows=4, th0=0.016, th1=0.004)
    for sx in (1, -1):
        x = fish.surface_x(top, bot, width, -0.25, -0.08)
        base = [(sx * x * 0.9, -0.26 + 0.03 * u, -0.08) for u in (i / 3 for i in range(4))]
        edge = [(sx * (x + 0.03), -0.17 + 0.03 * u, -0.14) for u in (i / 3 for i in range(4))]
        fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(RED, FIN, v), rows=2, th0=0.008, th1=0.003)
    # teeth: zig-zag row on both jaws at the front
    for i in range(7):
        u = i / 6
        y = -0.445 + 0.09 * u
        for sx in (1, -1):
            x = fish.surface_x(top, bot, width, y, -0.03) * 0.8 + 0.004
            z0 = -0.03 - 0.005 * (i % 2)
            mb.add(nh.tube([(sx * x, y, z0 - 0.012), (sx * x, y, z0 + 0.022)], [0.008, 0.0], sides=5), TOOTH)
            mb.add(nh.tube([(sx * x, y, z0 + 0.03), (sx * x, y, z0 - 0.005)], [0.007, 0.0], sides=5), TOOTH)
    ex = fish.surface_x(top, bot, width, -0.33, 0.07)
    fish.eyes(mb, -0.33, 0.07, ex, 0.026, (0.70, 0.45, 0.15))
    return mb.to_object("MegapiranhaParanensis")


if __name__ == "__main__":
    nh.run(build, "MegapiranhaParanensis", **fish.PREVIEW)
