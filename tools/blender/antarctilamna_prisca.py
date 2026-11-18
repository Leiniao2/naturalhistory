"""
Procedural Antarctilamna prisca for the map: an early shark-like chondrichthyan from the
Middle Devonian (Givetian, about 385 million years ago) rivers and lakes of Antarctica and
south-eastern Australia; roughly a metre long.

One of the oldest well-preserved sharks, and a freshwater one: a slender, rather
elongated, almost eel-like body; a single long, stout, ribbed fin spine standing on the
shoulders just behind the head in front of the first dorsal fin; a long, low second dorsal
fin running along the back; and an upturned (heterocercal) tail. Its small teeth were
"diplodont", with two large diverging cusps for gripping slippery prey.

Smooth skin loft plus fin webs (nh_dev_fish). Colours are unknown: dark olive-brown
above, pale below.

Usage:
  blender --background --python tools/blender/antarctilamna_prisca.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Antarctilamna.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Antarctilamna"

BACK = (0.24, 0.22, 0.12)
FLANK = (0.46, 0.42, 0.26)
BELLY = (0.88, 0.84, 0.72)
BLOTCH = (0.14, 0.13, 0.07)
FIN = (0.28, 0.26, 0.15)
FIN_EDGE = (0.16, 0.15, 0.09)
MOUTH = (0.08, 0.05, 0.04)
GILL = (0.12, 0.11, 0.07)
SPINE = (0.82, 0.76, 0.60)
SPINE_RIDGE = (0.46, 0.40, 0.28)
TOOTH = (0.95, 0.92, 0.84)

PROF = ef.Profile([
    (-0.80, 0.008, 0.016, 0.012, -0.006),
    (-0.77, 0.040, 0.044, 0.034, -0.006),
    (-0.70, 0.066, 0.070, 0.058, -0.004),
    (-0.58, 0.080, 0.086, 0.074, 0.000),
    (-0.40, 0.080, 0.088, 0.076, 0.002),
    (-0.15, 0.070, 0.078, 0.068, 0.004),
    (0.10, 0.054, 0.060, 0.052, 0.006),
    (0.30, 0.036, 0.040, 0.034, 0.012),
    (0.46, 0.022, 0.024, 0.020, 0.026),
    (0.60, 0.013, 0.014, 0.012, 0.050),
    (0.72, 0.007, 0.008, 0.007, 0.075),
    (0.80, 0.002, 0.002, 0.002, 0.092),
], power=2.1)


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.35


def skin_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.3)
    if -0.62 < co.y < -0.50 and abs(u) > 0.55 and -0.6 < v < 0.3:
        ph = (co.y + 0.62) / 0.024
        c = nh.lerp(c, GILL, 0.85 * (1.0 - nh.smoothstep(0.08, 0.2, abs(ph - round(ph)))))
    return c


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, PROF.y1, skin_color, ny=60, na=24)
    plain = ef.ray_color(FIN, FIN, FIN_EDGE, 1, rays=False, edge_amount=0.8)
    # long, stout shoulder spine leaning back, with a small fin web behind it
    base = Vector((0.0, -0.46, PROF.top(-0.46) - 0.004))
    ef.spine(mb, base, base + Vector((0.0, 0.11, 0.20)), 0.016, SPINE, SPINE_RIDGE, sides=8)
    df.web(mb, PROF, -0.455, -0.32, lambda u: (0.10 * u + 0.10 * (1 - u), 0.17 * (1 - u) ** 1.2 + 0.01), plain,
           side=1, n=7, rows=2)
    # long, low second dorsal
    df.web(mb, PROF, -0.02, 0.36, lambda u: (0.04, 0.05 * df.bump(u, 0.4, 0.1) + 0.006), plain,
           side=1, n=13, rows=2)
    df.web(mb, PROF, 0.20, 0.36, lambda u: (0.03, -(0.04 * df.bump(u, 0.5, 0.1) + 0.004)), plain,
           side=-1, n=7, rows=2)
    # heterocercal tail: deep lower web under the upturned axis, thin upper fringe
    df.web(mb, PROF, 0.48, 0.80,
           lambda u: (0.08 * u, -(0.12 * math.exp(-((u - 0.35) / 0.30) ** 2) + 0.01)),
           plain, side=-1, n=11, rows=3)
    df.web(mb, PROF, 0.50, 0.80, lambda u: (0.02, 0.022 * df.bump(u, 0.6) + 0.003), plain,
           side=1, n=7, rows=2)
    for s in (1, -1):
        ef.paired_fin(mb, PROF, s, -0.52, -0.40, -0.70, lambda u: 0.13 * (1 - u) ** 0.9 + 0.02,
                      0.85, 0.35, 0.7, plain, cols=7, rows=2)
        ef.paired_fin(mb, PROF, s, 0.14, 0.22, -0.9, lambda u: 0.06 * (1 - u) ** 0.8 + 0.01,
                      0.7, 0.5, 0.7, plain, cols=5, rows=2)
        # two-cusped (diplodont) teeth at the front of the jaw
        for k in range(3):
            y = -0.785 + 0.018 * k
            z = mouth_z(y)
            x = s * (PROF.W(y) * 0.85)
            for c in (-1, 1):
                mb.add(nh.tube([(x, y, z + 0.002), (x, y + c * 0.006, z - 0.016)], [0.004, 0.0], sides=4), TOOTH)
    ef.mouth_line(mb, PROF, -0.79, -0.70, mouth_z, MOUTH, r=0.005, grow=0.003)
    ef.surface_eye(mb, PROF, -0.71, 0.35, 0.024, (0.95, -0.25, 0.15), iris=(0.60, 0.55, 0.35))
    return df.finish(mb, NAME, roughness=0.4)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
