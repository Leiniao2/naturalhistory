"""
Procedural Leptolepis coryphaenoides (Early Jurassic, Toarcian, ~180 Ma; the Posidonia Shale of
Holzmaden and other Lias beds of Europe) for map colonies. Built with nh_fish.py.

One of the earliest teleosts, the group that now makes up almost all living fish: a small,
slender, herring-like fish usually 10-15 cm long, with thin round (cycloid) scales instead of
the heavy enamel scales of older ray-finned fish, a symmetrical forked tail and a single dorsal
fin over the middle of the back. It swam in great shoals in the open sea, eating plankton and
tiny prey, and was in turn food for ichthyosaurs, pterosaurs and larger fish.
Colour: blue-grey back, silvery flanks and belly.
Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/leptolepis_coryphaenoides.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Leptolepis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fh  # noqa: E402

BACK = (0.22, 0.30, 0.40)
SILVER = (0.82, 0.85, 0.88)
BELLY = (0.94, 0.94, 0.93)
FIN = (0.66, 0.70, 0.72)
EYE_RING = (0.88, 0.86, 0.78)

Y0, Y1 = -0.8, 0.55


def top(y):
    t = max(0.0, min(1.0, (y - Y0) / (Y1 - Y0)))
    return 0.015 + 0.14 * math.sin(min(1.0, t) * math.pi) ** 0.85 - 0.02 * t


def bot(y):
    t = max(0.0, min(1.0, (y - Y0) / (Y1 - Y0)))
    return -0.015 - 0.13 * math.sin(min(1.0, t) * math.pi) ** 0.8 + 0.025 * t


def width(y):
    t = max(0.0, min(1.0, (y - Y0) / (Y1 - Y0)))
    return 0.012 + 0.065 * math.sin(min(1.0, t) * math.pi) ** 0.9


def color(co):
    zt, zb = top(co.y), bot(co.y)
    u = (co.z - zb) / max(zt - zb, 1e-4)
    c = nh.lerp(BELLY, SILVER, nh.smoothstep(0.1, 0.45, u))
    c = nh.lerp(c, BACK, nh.smoothstep(0.62, 0.88, u))
    # a faint lateral line of darker scales
    return nh.lerp(c, (0.45, 0.52, 0.58), 0.35 * (1.0 - nh.smoothstep(0.0, 0.035, abs(u - 0.58))))


def build():
    mb = nh.MeshBuilder()
    fh.body(mb, top, bot, width, Y0, Y1, color, stations=40, ring=24)
    fc = lambda u, v, p: nh.lerp(FIN, BACK, 0.2 * (1 - v))
    # symmetrical forked tail
    base = [(0, Y1 - 0.04, top(Y1 - 0.04) - 0.005), (0, Y1, 0.0), (0, Y1 - 0.04, bot(Y1 - 0.04) + 0.005)]
    edge = [(0, Y1 + 0.30, 0.22), (0, Y1 + 0.09, 0.0), (0, Y1 + 0.30, -0.22)]
    fh.fin(mb, base, edge, fc, th0=0.01, th1=0.003)
    # single dorsal fin mid-back
    ys = [-0.10, -0.03, 0.04]
    fh.fin(mb, [(0, y, top(y) - 0.01) for y in ys], [(0, -0.05, top(-0.10) + 0.11), (0, 0.02, top(-0.03) + 0.08),
                                                    (0, 0.08, top(0.04) + 0.02)], fc)
    # anal fin, pelvic and pectoral fins
    ys = [0.26, 0.32, 0.38]
    fh.fin(mb, [(0, y, bot(y) + 0.008) for y in ys], [(0, y + 0.05, bot(y) - 0.05 + (y - 0.26) * 0.3) for y in ys], fc)
    for sx in (-1, 1):
        fh.fin(mb, [(sx * 0.03, -0.02, bot(-0.02) + 0.025), (sx * 0.03, 0.03, bot(0.03) + 0.025)],
               [(sx * 0.07, 0.09, bot(-0.02) - 0.03), (sx * 0.06, 0.11, bot(0.03) - 0.0)], fc)
        fh.fin(mb, [(sx * 0.055, -0.50, -0.06), (sx * 0.055, -0.46, -0.08)],
               [(sx * 0.10, -0.36, -0.12), (sx * 0.09, -0.35, -0.13)], fc)
    fh.eyes(mb, -0.64, 0.02, width(-0.64) * 0.95, 0.034, EYE_RING)
    obj = mb.to_object("Leptolepis")
    vs = obj.data.vertices
    zc = (min(v.co.z for v in vs) + max(v.co.z for v in vs)) / 2
    yc = (min(v.co.y for v in vs) + max(v.co.y for v in vs)) / 2
    for v in vs:
        v.co.z -= zc
        v.co.y -= yc
    return obj


if __name__ == "__main__":
    nh.run(build, "Leptolepis", background=(0.05, 0.22, 0.32), views=((35, 20), (-90, 5)))
