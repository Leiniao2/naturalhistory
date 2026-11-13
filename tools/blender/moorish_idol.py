"""
Procedural Moorish idol (Zanclus cornutus) for the map.

A tall, very thin disc with a long tube snout, a high dorsal fin that runs out
into a long white sickle-shaped filament, a big swept anal fin and a lunate
tail. Bold vertical bands: cream-yellow body with two broad black bands, an
orange saddle on the snout, and a black tail with a white rim.

Usage:
  blender --background --python tools/blender/moorish_idol.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MoorishIdol.fbx (map style Swim:
pivot at the body centre, facing -Y, dorsal fin up).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402

CREAM = (0.98, 0.95, 0.80)
YELLOW = (1.00, 0.78, 0.12)
BLACK = (0.05, 0.05, 0.06)
ORANGE = (1.00, 0.48, 0.10)
WHITE = (0.97, 0.97, 0.95)

TAIL_Y = 0.235
SNOUT_Z = -0.06    # the snout sticks out below the middle of the face
EYE = (-0.2, 0.06)
FILAMENT_START = (-0.05, 0.80)


def _disc(y):
    """Signed half height of the main disc (negative outside it, for smooth blending)."""
    q = 1.0 - ((y + 0.06) / 0.29) ** 2
    return 0.36 * math.copysign(math.sqrt(abs(q)), q)


def _snout(y):
    return 0.034 * nh.smoothstep(-0.528, -0.49, y)


def _peduncle(y):
    return 0.045 * nh.smoothstep(0.08, 0.2, y)


def top(y):
    return fish.smax(fish.smax(_disc(y) + 0.02, SNOUT_Z + _snout(y), 50), _peduncle(y), 50)


def bot(y):
    return -fish.smax(fish.smax(_disc(y), -(SNOUT_Z - _snout(y)), 50), _peduncle(y), 50)


def width(y):
    return 0.06 * (max(0.0, top(y) - bot(y)) * 0.5 / 0.37) ** 0.6


def band_coord(y, z):
    return y + 0.08 * z  # bands lean back toward the belly


def in_band(y_t, a, b, soft=0.008):
    return nh.smoothstep(a - soft, a + soft, y_t) * (1.0 - nh.smoothstep(b - soft, b + soft, y_t))


def pattern(y, z):
    y_t = band_coord(y, z)
    col = nh.lerp(CREAM, YELLOW, nh.smoothstep(-0.02, 0.09, y_t))   # yellow wash on the rear half
    col = nh.lerp(col, CREAM, nh.smoothstep(0.17, 0.2, y_t))         # pale tail stalk
    if y < -0.3:                                                     # snout: orange saddle, black tip
        saddle = nh.smoothstep(SNOUT_Z - 0.005, SNOUT_Z + 0.01, z) * (1.0 - nh.smoothstep(SNOUT_Z + 0.05, SNOUT_Z + 0.08, z))
        col = nh.lerp(col, ORANGE, saddle * nh.smoothstep(-0.29, -0.33, y))
        col = nh.lerp(col, BLACK, nh.smoothstep(-0.485, -0.5, y))
    col = nh.lerp(col, BLACK, in_band(y_t, -0.24, -0.04))
    col = nh.lerp(col, BLACK, in_band(y_t, 0.09, 0.19))
    return nh.lerp(col, WHITE, in_band(y_t, 0.115, 0.128, 0.004))   # thin white line in the rear band


def build():
    mb = nh.MeshBuilder()
    fish.body(mb, top, bot, width, -0.53, TAIL_Y + 0.01, lambda co: pattern(co.y, co.z),
              stations=44, ring=28, close_end=False)

    # Dorsal fin: tall leading edge up to the filament, concave trailing edge down to the stalk
    y_a, y_b, split = -0.15, 0.17, 0.28
    base, edge = [], []
    for i in range(19):
        u = i / 18
        y = y_a + (y_b - y_a) * u
        base.append((0.0, y, top(y) - 0.02))
        if u <= split:
            p = fish.bezier((0, y_a, top(y_a)), (0, -0.14, 0.55), (0, *FILAMENT_START), u / split)
        else:
            p = fish.bezier((0, *FILAMENT_START), (0, 0.14, 0.55), (0, y_b + 0.03, top(y_b) + 0.03),
                            (u - split) / (1 - split))
        edge.append(tuple(p))

    def dorsal_color(u, v, co):
        return nh.lerp(pattern(co.y, co.z), WHITE, nh.smoothstep(0.6, 1.0, v) * (1.0 - in_band(band_coord(co.y, co.z), -0.24, -0.04)))

    fish.fin(mb, base, edge, dorsal_color, rows=5, th0=0.02, th1=0.004)

    # The long white sickle filament trailing from the dorsal fin
    pts = [tuple(fish.bezier((0, *FILAMENT_START), (0, 0.22, 0.95), (0, 0.66, 0.52), i / 11)) for i in range(12)]
    radii = [0.019 * (1 - i / 11) ** 0.8 + 0.003 for i in range(12)]
    radii[-1] = 0.0
    mb.add(nh.tube(pts, radii, sides=5, cap_start=False), WHITE)

    # Anal fin: big, swept back
    y_a, y_b, split = -0.08, 0.16, 0.38
    tip = (0, 0.05, -0.68)
    base, edge = [], []
    for i in range(15):
        u = i / 14
        y = y_a + (y_b - y_a) * u
        base.append((0.0, y, bot(y) + 0.02))
        if u <= split:
            p = fish.bezier((0, y_a, bot(y_a)), (0, -0.07, -0.5), tip, u / split)
        else:
            p = fish.bezier(tip, (0, 0.1, -0.42), (0, y_b + 0.03, bot(y_b) - 0.03), (u - split) / (1 - split))
        edge.append(tuple(p))
    fish.fin(mb, base, edge,
             lambda u, v, co: nh.lerp(pattern(co.y, co.z), BLACK, nh.smoothstep(0.75, 0.9, v)),
             rows=5, th0=0.02, th1=0.004)

    # Lunate tail: black with a white rim
    base, edge = [], []
    for i in range(11):
        u = i / 10
        base.append((0.0, TAIL_Y, -0.045 + 0.09 * u))
        edge.append((0.0, TAIL_Y + 0.12 + 0.07 * abs(2 * u - 1) ** 1.5, -0.17 + 0.34 * u))
    fish.fin(mb, base, edge,
             lambda u, v, co: CREAM if v < 0.2 else (BLACK if v < 0.8 else WHITE),
             rows=5, th0=0.016, th1=0.004)

    # Black pelvic fins and small clear pectorals
    for sx in (1, -1):
        bx = fish.surface_x(top, bot, width, -0.13, -0.3) * 0.6
        base = [(sx * bx, -0.15 + 0.05 * u, bot(-0.15 + 0.05 * u) + 0.03) for u in (i / 3 for i in range(4))]
        edge = [(sx * (bx + 0.03), -0.09 + 0.06 * u, bot(-0.12) - 0.13 + 0.05 * u) for u in (i / 3 for i in range(4))]
        fish.fin(mb, base, edge, lambda u, v, co: BLACK, rows=2, th0=0.008, th1=0.003)
        x = fish.surface_x(top, bot, width, -0.1, -0.06)
        base = [(sx * x, -0.1, -0.03 - 0.06 * u) for u in (i / 4 for i in range(5))]
        edge = [(sx * (x + 0.03), -0.02 + 0.03 * math.sin(math.pi * u), -0.05 - 0.07 * u) for u in (i / 4 for i in range(5))]
        fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(YELLOW, (0.85, 0.88, 0.86), v), rows=2, th0=0.008, th1=0.003)

    ex = fish.surface_x(top, bot, width, *EYE)
    fish.eyes(mb, EYE[0], EYE[1], ex, 0.03, (0.78, 0.62, 0.20))

    return mb.to_object("MoorishIdol", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "MoorishIdol", **fish.PREVIEW)
