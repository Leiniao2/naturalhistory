"""
Procedural Fanjingshania renovata for the map: an early spiny jawed fish (a climatiid
"acanthodian", a stem relative of sharks) from the early Silurian (Telychian, about 439
million years ago) of Guizhou, China; a small fish a few centimetres long and one of
the oldest jawed vertebrates known from more than isolated scales.

Bristling with defensive spines: tall, ridged spines in front of both dorsal fins and
the anal fin; big pectoral spines set in a bony shoulder girdle of plates on the chest;
a long row of extra paired spines along the belly between the pectoral and pelvic fins;
and pelvic spines. Small scales, large eyes, a heterocercal tail.

Adapted from climatius_reticulatus.py (nh_dev_fish skin/webs + nh_early_fish spines).
Colours are unknown: bronze-olive with a pale belly and ivory spines.

Usage:
  blender --background --python tools/blender/fanjingshania_renovata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/FanjingshaniaRenovata.fbx (Swim: pivot at the body
centre, facing -Y).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "FanjingshaniaRenovata"

BACK = (0.34, 0.26, 0.12)
FLANK = (0.60, 0.48, 0.26)
BELLY = (0.86, 0.82, 0.68)
NET = (0.24, 0.17, 0.08)
FIN = (0.44, 0.34, 0.18)
FIN_EDGE = (0.22, 0.20, 0.13)
MOUTH = (0.08, 0.05, 0.04)
SPINE = (0.92, 0.88, 0.74)
SPINE_RIDGE = (0.56, 0.46, 0.30)
GILL = (0.14, 0.13, 0.09)

# (y, half-width, top, bottom, centre z)
PROF = ef.Profile([
    (-0.70, 0.010, 0.020, 0.016, -0.010),
    (-0.66, 0.060, 0.075, 0.060, -0.010),
    (-0.56, 0.100, 0.130, 0.105, -0.004),
    (-0.40, 0.118, 0.170, 0.140, 0.000),
    (-0.20, 0.112, 0.175, 0.140, 0.006),
    (0.00, 0.090, 0.140, 0.110, 0.014),
    (0.18, 0.060, 0.090, 0.070, 0.030),
    (0.32, 0.036, 0.050, 0.040, 0.055),
    (0.44, 0.022, 0.030, 0.024, 0.100),
    (0.56, 0.012, 0.016, 0.013, 0.160),
    (0.68, 0.005, 0.006, 0.005, 0.220),
    (0.74, 0.002, 0.002, 0.002, 0.250),
], power=2.1)


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.45


def skin_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY)
    # fine net of diagonal scale rows
    a = math.sin((co.y + co.z) * 95.0) * math.sin((co.y - co.z) * 95.0)
    c = nh.lerp(c, NET, 0.35 * nh.smoothstep(0.75, 0.95, abs(a)) * (1.0 - nh.smoothstep(-0.2, -0.6, v)))
    # gill region behind the head
    if -0.50 < co.y < -0.42 and abs(u) > 0.5 and -0.6 < v < 0.4:
        c = nh.lerp(c, GILL, 0.5)
    return c


def spine_at(mb, y, side_x, down, length, lean=0.55, r=0.010):
    """A stout fin spine rooted on the body at y, pointing back and out or down."""
    if side_x == 0:
        base = Vector((0.0, y, PROF.top(y) - 0.004))
        tip = base + Vector((0.0, length * lean, length))
    else:
        w = PROF.W(y)
        base = Vector((side_x * w * 0.85, y, PROF.CZ(y) - PROF.HB(y) * down))
        tip = base + Vector((side_x * length * 0.45, length * lean, -length * 0.75))
    ef.spine(mb, base, tip, r, SPINE, SPINE_RIDGE, sides=7)
    return base, tip


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, PROF.y1, skin_color, ny=52, na=26)
    plain = ef.ray_color(FIN, FIN, FIN_EDGE, 1, rays=False, edge_amount=0.8)

    # two dorsal fins, each behind a tall spine
    for y0, y1, h in ((-0.18, -0.06, 0.13), (0.16, 0.26, 0.09)):
        df.web(mb, PROF, y0, y1, lambda u, h=h: (0.06 * u + 0.03, h * (1 - u) ** 0.9 + 0.008), plain,
               side=1, n=7, rows=2)
        spine_at(mb, y0 - 0.01, 0, 0, h * 1.5, lean=0.40, r=0.013)
    # anal fin with its spine
    df.web(mb, PROF, 0.20, 0.28, lambda u: (0.05 * u + 0.02, -(0.07 * (1 - u) ** 0.9 + 0.006)), plain,
           side=-1, n=6, rows=2)
    base = Vector((0.0, 0.195, PROF.CZ(0.195) - PROF.HB(0.195)))
    ef.spine(mb, base, base + Vector((0.0, 0.06, -0.085)), 0.009, SPINE, SPINE_RIDGE, sides=7)
    # heterocercal tail: the axis turns up into the upper lobe, a broad web below it
    df.web(mb, PROF, 0.34, 0.74,
           lambda u: (0.10 * math.exp(-((u - 0.25) / 0.25) ** 2),
                      -(0.16 * math.exp(-((u - 0.25) / 0.2) ** 2) + 0.03 * (1 - u) + 0.004)),
           plain, side=-1, n=12, rows=3)
    df.web(mb, PROF, 0.40, 0.74, lambda u: (0.015, 0.025 * df.bump(u, 0.6) + 0.003), plain, side=1, n=7, rows=2)

    for s in (1, -1):
        # pectoral fins behind big spines
        ef.paired_fin(mb, PROF, s, -0.42, -0.32, -0.75, lambda u: 0.10 * (1 - u) ** 0.9 + 0.012,
                      0.8, 0.45, 0.6, plain, cols=6, rows=2)
        spine_at(mb, -0.43, s, 0.55, 0.17, lean=0.75, r=0.012)
        # the row of extra paired spines along the belly, then the pelvic fins with theirs
        for k, y in enumerate((-0.34, -0.27, -0.20, -0.13, -0.06, 0.01)):
            spine_at(mb, y, s, 0.85, 0.075 + 0.015 * (k % 2), lean=0.8, r=0.008)
        # bony shoulder-girdle plates on the chest round the pectoral spine
        for k, (y, dn) in enumerate(((-0.47, 0.65), (-0.42, 0.85), (-0.36, 0.98))):
            w = PROF.W(y)
            mb.add(nh.uv_ellipsoid((s * w * (0.75 - 0.25 * k), y, PROF.CZ(y) - PROF.HB(y) * dn), (0.035, 0.04, 0.012), 8, 5),
                   SPINE_RIDGE)
        ef.paired_fin(mb, PROF, s, 0.06, 0.14, -0.9, lambda u: 0.06 * (1 - u) ** 0.8 + 0.008,
                      0.7, 0.55, 0.7, plain, cols=5, rows=2)
        spine_at(mb, 0.05, s, 0.85, 0.11, lean=0.75, r=0.009)

    ef.mouth_line(mb, PROF, -0.69, -0.60, mouth_z, MOUTH, r=0.006, grow=0.003)
    ef.surface_eye(mb, PROF, -0.60, 0.30, 0.045, (0.95, -0.25, 0.15), iris=(0.75, 0.65, 0.35))
    return df.finish(mb, NAME, roughness=0.40)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
