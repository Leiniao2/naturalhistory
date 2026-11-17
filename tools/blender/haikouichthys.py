"""
Procedural Haikouichthys ercaicunensis for the map: one of the earliest known vertebrates, from
the early Cambrian Chengjiang biota of Yunnan, China (~518 million years ago).

Built on the Myllokunmingia script (myllokunmingia_fengjiaoa.py): a tiny (~2.5 cm), jawless,
fish-shaped animal, slimmer, with a distinct rounded head carrying big paired eyes, a row of
seven or more gill pouches behind it, a low dorsal fin fold with fine fin radials running along
most of the back (rising a little toward the front), a ventral fin fold under the rear belly and
a fin fold round the pointed tail. Zig-zag myomeres along the flanks. Pale grey-olive above,
silvery-pale below, reddish gill pouches.

Usage:
  blender --background --python tools/blender/haikouichthys.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Haikouichthys.fbx (map style Swim: pivot at the body
centre, facing -Y, dorsal fin up). About 1 unit long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402

BACK = (0.36, 0.38, 0.33)
FLANK = (0.62, 0.64, 0.56)
BELLY = (0.88, 0.88, 0.82)
MYOMERE = (0.36, 0.34, 0.25)
FIN = (0.72, 0.70, 0.60)
RADIAL = (0.48, 0.45, 0.36)
GILL = (0.62, 0.32, 0.27)
GILL_DARK = (0.40, 0.18, 0.16)
MOUTH = (0.10, 0.07, 0.06)
EYE_RING = (0.30, 0.28, 0.22)

Y_SNOUT, Y_TAIL = -0.50, 0.55
EYE = (-0.425, 0.03)
GILL_YS = [-0.35, -0.328, -0.306, -0.284, -0.262, -0.24, -0.218, -0.196]
MYOMERES = 24


def half_h(y):
    """Spindle profile: blunt head, deepest a third of the way back, long tapering tail."""
    t = (y - Y_SNOUT) / (Y_TAIL - Y_SNOUT)
    body = 0.095 * min(1.0, (t / 0.3)) ** 0.55 * (1.0 - nh.smoothstep(0.3, 1.0, t) * 0.92) * (1.0 - t ** 6)
    head = 0.08 * min(1.0, t / 0.05) ** 0.5 * (1.0 - nh.smoothstep(0.06, 0.32, t))  # rounded head
    return max(body, head)


def top(y):
    return half_h(y) + 0.008


def bot(y):
    return -half_h(y) * 0.95


def width(y):
    return 0.055 * (half_h(y) / 0.115) ** 0.8


def rel(y, z):
    zt, zb = top(y), bot(y)
    return (z - (zt + zb) * 0.5) / max((zt - zb) * 0.5, 1e-4)


def body_color(co):
    r = rel(co.y, co.z)
    col = nh.lerp(FLANK, BELLY, nh.smoothstep(-0.1, -0.7, r))
    col = nh.lerp(col, BACK, nh.smoothstep(0.2, 0.8, r))
    # a faint darker notochord band along the middle of the flank
    col = nh.lerp(col, (0.55, 0.52, 0.40), (1.0 - nh.smoothstep(0.05, 0.18, abs(r - 0.12))) * 0.4
                  * nh.smoothstep(-0.3, -0.2, co.y))
    mott = noise.noise(Vector((co.y * 25.0, co.z * 25.0, 3.3)))
    return nh.lerp(col, (col[0] * 0.85, col[1] * 0.85, col[2] * 0.82), max(0.0, mott) * 0.5)


def fold(mb, y0, y1, height, sign, rows=4, cols=40, radials=True):
    """Midline fin fold along the back (sign=1) or belly (sign=-1); height(u) above the body."""
    edge_z = top if sign > 0 else bot
    base, edge = [], []
    for i in range(cols):
        u = i / (cols - 1)
        y = y0 + (y1 - y0) * u
        base.append((0.0, y, edge_z(y) - sign * 0.006))
        edge.append((0.0, y + 0.03 * height(u) / 0.2, edge_z(y) + sign * height(u)))

    def color(u, v, co):
        ray = 0.5 + 0.5 * math.cos(u * (cols - 1) * math.pi) if radials else 0.0
        col = nh.lerp(nh.lerp(FLANK, BACK, 0.4) if sign > 0 else BELLY, FIN, nh.smoothstep(0.0, 0.3, v))
        return nh.lerp(col, RADIAL, ray * 0.55 * (1.0 - nh.smoothstep(0.6, 1.0, v)))
    fish.fin(mb, base, edge, color, rows=rows, th0=0.008, th1=0.003)


def myomere_line(k):
    """W-shaped (zig-zag) myomere boundary k, as side-view (y, z) points."""
    t = k / (MYOMERES - 1)
    y_mid = -0.22 + 0.70 * t
    a = 0.028 * (1.0 - 0.4 * t)
    pts = []
    for i in range(21):
        r = -0.92 + 1.84 * i / 20
        y = y_mid + a * abs(abs(r) * 2.0 - 1.0) - 0.01
        zt, zb = top(y), bot(y)
        pts.append((y, (zt + zb) * 0.5 + r * (zt - zb) * 0.5))
    return pts


def build():
    mb = nh.MeshBuilder()
    fish.body(mb, top, bot, width, Y_SNOUT, Y_TAIL, body_color, stations=64, ring=28)

    # Tall sail-like dorsal fin over the front half, lowering into a low fold toward the tail
    fold(mb, -0.22, 0.53,
         lambda u: 0.075 * math.sin(math.pi * min(1.0, u / 0.25)) ** 0.6 * (1 - nh.smoothstep(0.2, 0.55, u) * 0.5)
         * (1 - nh.smoothstep(0.86, 1.0, u)) + 0.006,
         sign=1, cols=56)
    # Ventral fin fold along the rear belly, into the tail fold
    fold(mb, -0.02, 0.53,
         lambda u: 0.06 * math.sin(math.pi * min(1.0, u / 0.35)) ** 0.6 * (1 - nh.smoothstep(0.55, 1.0, u) * 0.6)
         * (1 - nh.smoothstep(0.88, 1.0, u)) + 0.004,
         sign=-1, cols=36)

    # Zig-zag myomeres on both flanks
    for k in range(MYOMERES):
        fish.stripe(mb, top, bot, width, myomere_line(k), 0.003,
                    lambda across, along: MYOMERE, offset=0.003, inset=0.9)

    # Six gill pouches in a row behind the head
    for sx in (1, -1):
        for i, gy in enumerate(GILL_YS):
            gz = -0.02 - 0.003 * i
            x = fish.surface_x(top, bot, width, gy, gz)
            mb.add(nh.ellipsoid((sx * (x - 0.004), gy, gz), (0.007, 0.0085, 0.022), subdivisions=2),
                   lambda co, n: nh.lerp(GILL, GILL_DARK, nh.smoothstep(0.3, -0.6, n.z)))

    # Small round jawless mouth under the snout tip
    mb.add(nh.ellipsoid((0.0, Y_SNOUT + 0.014, -0.012), (0.011, 0.008, 0.009), subdivisions=2), MOUTH)

    ex = fish.surface_x(top, bot, width, *EYE)
    fish.eyes(mb, EYE[0], EYE[1], ex, 0.022, EYE_RING)  # big eyes

    return mb.to_object("Haikouichthys", roughness=0.4)


if __name__ == "__main__":
    nh.run(build, "Haikouichthys", background=(0.04, 0.10, 0.13),
           views=((35, 25), (-90, 4), (30, 50), (-60, 12)))
