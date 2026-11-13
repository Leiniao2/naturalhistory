"""
Procedural ornate butterflyfish (Chaetodon ornatissimus) for the map.

A small, thin, disc-shaped reef fish with a short pointed snout: white body
with diagonal orange stripes, black bars through the eye, across the snout and
at the tail base, and yellow-orange fins with black margins.

Usage:
  blender --background --python tools/blender/ornate_butterflyfish.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OrnateButterflyfish.fbx (map style
Swim: pivot at the body centre, facing -Y, dorsal fin up).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402

WHITE = (0.96, 0.96, 0.92)
ORANGE = (1.00, 0.50, 0.10)
YELLOW = (1.00, 0.76, 0.10)
BLACK = (0.05, 0.05, 0.06)
FIN_CLEAR = (0.84, 0.88, 0.88)

EYE = (-0.27, 0.05)
TAIL_Y = 0.265


def half_height(y):
    disc = 0.34 * math.sqrt(max(0.0, 1.0 - ((y + 0.04) / 0.34) ** 2))
    snout = 0.05 * nh.smoothstep(-0.465, -0.39, y)
    peduncle = 0.075 * nh.smoothstep(0.05, 0.2, y)
    return fish.smax(fish.smax(disc, snout, 60), peduncle, 60)


def top(y):
    return half_height(y) + 0.01 * nh.smoothstep(-0.4, -0.1, y)


def bot(y):
    return -half_height(y)


def width(y):
    return 0.07 * (half_height(y) / 0.34) ** 0.6


def bar(y, center, half_width, soft=0.008):
    return 1.0 - nh.smoothstep(half_width - soft, half_width + soft, abs(y - center))


def pattern(y, z):
    """Side-view colour of the body (also used for the fin bases)."""
    col = WHITE  # the diagonal orange stripes are separate strips, see stripes()
    # head: yellow-bordered black bar through the eye, a thin black bar over the snout
    eye_c = EYE[0] + 0.06 * (z - EYE[1])
    col = nh.lerp(col, YELLOW, bar(y, eye_c, 0.06))
    col = nh.lerp(col, BLACK, bar(y, eye_c, 0.033))
    snout_c = -0.37 + 0.05 * z
    col = nh.lerp(col, YELLOW, bar(y, snout_c, 0.03) * (y > -0.44))
    col = nh.lerp(col, BLACK, bar(y, snout_c, 0.014))
    col = nh.lerp(col, (0.55, 0.40, 0.18), nh.smoothstep(-0.43, -0.46, y))  # mouth
    # tail base: yellow-bordered black bar, yellow peduncle behind it
    col = nh.lerp(col, YELLOW, nh.smoothstep(0.17, 0.19, y))
    col = nh.lerp(col, BLACK, bar(y, 0.215, 0.028))
    return col


def stripes(mb):
    """Diagonal orange stripes across the flank, rising toward the tail."""
    n = (-0.57, 0.82)   # across the stripes (side view y, z)
    d = (0.82, 0.57)    # along them
    for k in range(-3, 4):
        s = k * 0.112 + 0.02
        line = []
        for i in range(46):
            t = -0.6 + 1.2 * i / 45
            y, z = s * n[0] + t * d[0], s * n[1] + t * d[1]
            if -0.19 < y < 0.165:
                line.append((y, z))
        if len(line) > 2:
            fish.stripe(mb, top, bot, width, line, 0.027,
                        lambda across, along: nh.lerp(ORANGE, YELLOW, abs(across) * 0.6),
                        offset=0.0035, inset=0.96)


def fin_color(u, v, co):
    col = pattern(co.y, co.z)
    col = nh.lerp(col, YELLOW, nh.smoothstep(0.2, 0.35, v))
    col = nh.lerp(col, ORANGE, nh.smoothstep(0.4, 0.65, v) * 0.7)
    col = BLACK if 0.74 < v < 0.9 else col  # crisp black margin line (rows land on these values)
    return YELLOW if v >= 0.9 else col


def median_fin(y_a, y_b, sign, reach, sweep, cols=17):
    edge_z = top if sign > 0 else bot
    base, edge = [], []
    for i in range(cols):
        u = i / (cols - 1)
        y = y_a + (y_b - y_a) * u
        z = edge_z(y) - sign * 0.015
        base.append((0.0, y, z))
        h = 0.035 + reach * math.sin(math.pi * u) ** 0.5 * (0.6 + 0.4 * u)
        edge.append((0.0, y + sweep * u * u, z + sign * h))
    return base, edge


def build():
    mb = nh.MeshBuilder()
    fish.body(mb, top, bot, width, -0.46, TAIL_Y + 0.015, lambda co: pattern(co.y, co.z),
              stations=40, ring=32, close_end=False)
    stripes(mb)

    base, edge = median_fin(-0.22, 0.2, 1, 0.11, 0.07, cols=15)
    fish.fin(mb, base, edge, fin_color, rows=5, th0=0.02, th1=0.004)
    base, edge = median_fin(-0.02, 0.2, -1, 0.10, 0.06, cols=11)
    fish.fin(mb, base, edge, fin_color, rows=5, th0=0.02, th1=0.004)

    # Tail: yellow base, black band, clear margin
    base, edge = [], []
    for i in range(11):
        u = i / 10
        base.append((0.0, TAIL_Y, -0.07 + 0.14 * u))
        edge.append((0.0, TAIL_Y + 0.17 + 0.02 * math.sin(math.pi * u), -0.15 + 0.30 * u))

    def tail_color(u, v, co):
        if v < 0.3:
            return YELLOW
        return BLACK if v < 0.55 else FIN_CLEAR

    fish.fin(mb, base, edge, tail_color, rows=5, th0=0.016, th1=0.004)

    # Pectoral and pelvic fins
    for sx in (1, -1):
        x = fish.surface_x(top, bot, width, -0.16, -0.06)
        base = [(sx * x, -0.16, -0.03 - 0.06 * u) for u in (i / 4 for i in range(5))]
        edge = [(sx * (x + 0.03), -0.16 + 0.08 + 0.04 * math.sin(math.pi * u), -0.05 - 0.07 * u) for u in (i / 4 for i in range(5))]
        fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(YELLOW, FIN_CLEAR, v), rows=2, th0=0.008, th1=0.003)
        bx = fish.surface_x(top, bot, width, -0.12, -0.28) * 0.6
        base = [(sx * bx, -0.14 + 0.04 * u, bot(-0.14 + 0.04 * u) + 0.02) for u in (i / 3 for i in range(4))]
        edge = [(sx * (bx + 0.025), -0.10 + 0.05 * u, bot(-0.12) - 0.08 + 0.03 * u) for u in (i / 3 for i in range(4))]
        fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(WHITE, YELLOW, v), rows=2, th0=0.008, th1=0.003)

    ex = fish.surface_x(top, bot, width, *EYE)
    fish.eyes(mb, EYE[0], EYE[1], ex, 0.028, (0.30, 0.26, 0.14))

    return mb.to_object("OrnateButterflyfish", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "OrnateButterflyfish", **fish.PREVIEW)
