"""
Procedural Oncorhynchus rastrosus (Late Miocene to Pliocene of the North
Pacific coast) for map colonies: the "spike-toothed" or sabre-toothed salmon.

The largest salmon known, up to about 2.5 m long: a plankton-straining fish
with many gill rakers, which as a spawning adult grew a pair of big tusk-like
teeth that stuck out sideways from the tip of the snout, used in fights or nest
digging. Shown in spawning colours like a sockeye: red flanks, dark olive head
and a hooked jaw. Built with nh_fish.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/oncorhynchus_rastrosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OncorhynchusRastrosus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_fish as fish  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import noise, Vector  # noqa: E402

RED = (0.70, 0.18, 0.12)
BACK = (0.38, 0.12, 0.09)
HEAD = (0.20, 0.27, 0.18)
BELLY = (0.85, 0.80, 0.72)
FIN = (0.25, 0.22, 0.18)
TOOTH = (0.94, 0.92, 0.86)
TAIL_Y = 0.46


def half_height(y):
    body = 0.12 * max(0.0, 1 - ((y + 0.04) / 0.50) ** 2) ** 0.6
    hump = 0.03 * math.exp(-((y + 0.18) / 0.12) ** 2)
    return fish.smax(body + hump, 0.045 * nh.smoothstep(0.2, 0.42, y), 60)


def top(y):
    return half_height(y) * 1.05


def bot(y):
    return -half_height(y) * 0.95


def width(y):
    return 0.06 * max(0.05, 1 - ((y + 0.06) / 0.52) ** 2) ** 0.6


def pattern(co):
    y, z = co.y, co.z
    mid = (top(y) + bot(y)) * 0.5
    c = nh.lerp(RED, BACK, nh.smoothstep(mid + 0.02, top(y), z))
    c = nh.lerp(c, BELLY, 0.6 * nh.smoothstep(mid - 0.02, bot(y), z) * nh.smoothstep(-0.25, -0.38, y))
    c = nh.lerp(c, HEAD, nh.smoothstep(-0.28, -0.36, y))
    c = nh.lerp(c, (0.10, 0.08, 0.07), 0.6 * nh.smoothstep(0.55, 0.75, noise.noise(Vector((y * 60, z * 60, 0)))) *
                nh.smoothstep(mid, top(y), z))
    return c


def median_fin(y_a, y_b, sign, reach, sweep, cols=11):
    edge_z = top if sign > 0 else bot
    base, edge = [], []
    for i in range(cols):
        u = i / (cols - 1)
        y = y_a + (y_b - y_a) * u
        z = edge_z(y) - sign * 0.01
        base.append((0.0, y, z))
        h = 0.015 + reach * math.sin(math.pi * u) ** 0.6 * (1.0 - 0.4 * u)
        edge.append((0.0, y + sweep * u, z + sign * h))
    return base, edge


def build():
    mb = nh.MeshBuilder()
    fish.body(mb, top, bot, width, -0.52, TAIL_Y + 0.01, pattern, stations=36, ring=24, close_end=False)
    base, edge = median_fin(-0.08, 0.08, 1, 0.09, 0.06)
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(BACK, FIN, v), rows=4, th0=0.014, th1=0.004)
    base, edge = median_fin(0.28, 0.33, 1, 0.025, 0.02, cols=5)       # adipose fin
    fish.fin(mb, base, edge, lambda u, v, co: BACK, rows=2, th0=0.012, th1=0.005)
    base, edge = median_fin(0.18, 0.32, -1, 0.06, 0.05)
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(RED, FIN, v), rows=3, th0=0.014, th1=0.004)
    base, edge = median_fin(0.0, 0.08, -1, 0.05, 0.04, cols=5)        # pelvic fins (as one)
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(RED, FIN, v), rows=2, th0=0.012, th1=0.004)
    base, edge = [], []
    for i in range(11):
        u = i / 10
        base.append((0.0, TAIL_Y, -0.04 + 0.08 * u))
        fork = 0.04 * (1 - abs(u - 0.5) * 2)
        edge.append((0.0, TAIL_Y + 0.15 - fork * 1.4, -0.15 + 0.30 * u))
    fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(FIN, (0.12, 0.10, 0.09), v), rows=4, th0=0.014, th1=0.004)
    for sx in (1, -1):
        x = fish.surface_x(top, bot, width, -0.30, -0.06)
        base = [(sx * x * 0.9, -0.30 + 0.03 * u, -0.06) for u in (i / 3 for i in range(4))]
        edge = [(sx * (x + 0.03), -0.22 + 0.03 * u, -0.11) for u in (i / 3 for i in range(4))]
        fish.fin(mb, base, edge, lambda u, v, co: nh.lerp(RED, FIN, v), rows=2, th0=0.008, th1=0.003)
    # kype: hooked tip of the upper jaw
    mb.add(nh.tube([(0, -0.50, 0.01), (0, -0.545, 0.0), (0, -0.55, -0.03)], [0.022, 0.016, 0.006], sides=8), HEAD)
    # the "spikes": a pair of tusks jutting sideways out of the snout tip
    for sx in (1, -1):
        r0 = Vector((sx * 0.012, -0.505, 0.0))
        mb.add(nh.tube([tuple(r0), tuple(r0 + Vector((sx * 0.05, -0.012, -0.012))), tuple(r0 + Vector((sx * 0.085, -0.01, -0.03)))],
                       [0.008, 0.006, 0.0], sides=6), TOOTH)
    ex = fish.surface_x(top, bot, width, -0.40, 0.03)
    fish.eyes(mb, -0.40, 0.03, ex, 0.016, (0.70, 0.55, 0.20))
    return mb.to_object("OncorhynchusRastrosus")


if __name__ == "__main__":
    nh.run(build, "OncorhynchusRastrosus", **fish.PREVIEW)
