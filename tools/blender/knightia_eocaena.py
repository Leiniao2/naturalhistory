"""
Procedural Knightia eocaena (early Eocene, ~52-50 Ma, Green River Formation lakes,
Wyoming) for map colonies. Built with nh_fish.py.

A small extinct herring-relative (Clupeidae), usually 10-15 cm long and one of the
most common fossil fish in the world; whole schools are preserved in the Green River
lake beds. Laterally compressed silvery body with a single dorsal fin over the middle,
a deeply forked tail and a keel of scutes along the belly. It fed on plankton and was
food for gars, Diplomystus and birds. Colour: blue-green back, silver flanks.
Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/knightia_eocaena.py -- [--render out.png]

Output: Assets/Resources/Models/Species/KnightiaEocaena.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fh  # noqa: E402

BACK = (0.18, 0.32, 0.36)
SILVER = (0.80, 0.83, 0.85)
BELLY = (0.93, 0.93, 0.92)
FIN = (0.62, 0.66, 0.66)
EYE_RING = (0.85, 0.85, 0.80)

Y0, Y1 = -0.8, 0.55


def top(y):
    t = max(0.0, min(1.0, (y - Y0) / (Y1 - Y0)))
    return 0.02 + 0.19 * math.sin(min(1.0, t) * math.pi) ** 0.8 - 0.03 * t


def bot(y):
    t = max(0.0, min(1.0, (y - Y0) / (Y1 - Y0)))
    return -0.02 - 0.20 * math.sin(min(1.0, t) * math.pi) ** 0.7 + 0.04 * t


def width(y):
    t = max(0.0, min(1.0, (y - Y0) / (Y1 - Y0)))
    return 0.012 + 0.075 * math.sin(min(1.0, t) * math.pi) ** 0.9


def color(co):
    zt, zb = top(co.y), bot(co.y)
    u = (co.z - zb) / max(zt - zb, 1e-4)
    c = nh.lerp(BELLY, SILVER, nh.smoothstep(0.1, 0.45, u))
    return nh.lerp(c, BACK, nh.smoothstep(0.6, 0.85, u))


def build():
    mb = nh.MeshBuilder()
    fh.body(mb, top, bot, width, Y0, Y1, color, stations=40, ring=24)
    fc = lambda u, v, p: nh.lerp(FIN, BACK, 0.2 * (1 - v))
    # forked tail
    base = [(0, Y1 - 0.04, top(Y1 - 0.04) - 0.005), (0, Y1, 0.0), (0, Y1 - 0.04, bot(Y1 - 0.04) + 0.005)]
    edge = [(0, Y1 + 0.28, 0.26), (0, Y1 + 0.1, 0.0), (0, Y1 + 0.28, -0.26)]
    fh.fin(mb, base, edge, fc, th0=0.01, th1=0.003)
    # dorsal fin over the middle
    ys = [-0.12, -0.04, 0.04]
    fh.fin(mb, [(0, y, top(y) - 0.01) for y in ys], [(0, -0.07, top(-0.12) + 0.13), (0, 0.0, top(-0.04) + 0.09),
                                                    (0, 0.07, top(0.04) + 0.02)], fc)
    # anal fin and pelvic fins
    ys = [0.28, 0.34, 0.40]
    fh.fin(mb, [(0, y, bot(y) + 0.008) for y in ys], [(0, y + 0.05, bot(y) - 0.06 + (y - 0.28) * 0.3) for y in ys], fc)
    for sx in (-1, 1):
        fh.fin(mb, [(sx * 0.03, -0.03, bot(-0.03) + 0.03), (sx * 0.03, 0.02, bot(0.02) + 0.03)],
               [(sx * 0.07, 0.08, bot(-0.03) - 0.03), (sx * 0.06, 0.1, bot(0.02) - 0.0)], fc)
        fh.fin(mb, [(sx * 0.06, -0.48, -0.08), (sx * 0.06, -0.44, -0.1)],
               [(sx * 0.11, -0.34, -0.15), (sx * 0.1, -0.33, -0.16)], fc)
    fh.eyes(mb, -0.62, 0.03, width(-0.62) * 0.95, 0.035, EYE_RING)
    obj = mb.to_object("KnightiaEocaena")
    vs = obj.data.vertices
    zc = (min(v.co.z for v in vs) + max(v.co.z for v in vs)) / 2
    yc = (min(v.co.y for v in vs) + max(v.co.y for v in vs)) / 2
    for v in vs:
        v.co.z -= zc
        v.co.y -= yc
    return obj


if __name__ == "__main__":
    nh.run(build, "KnightiaEocaena", background=(0.05, 0.22, 0.32), views=((35, 20), (-90, 5)))
