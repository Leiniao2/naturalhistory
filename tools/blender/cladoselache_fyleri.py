"""
Procedural Cladoselache fyleri for the map: one of the earliest well-known sharks, from
the Late Devonian (Famennian, about 370-360 million years ago) Cleveland Shale of Ohio;
up to about 1.8 m long.

A sleek, fast open-water hunter: a blunt snout with the mouth at the front (not
underneath as in modern sharks), large eyes, two dorsal fins with a stout spine in front
of the first, big broad-based triangular pectoral fins, small pelvic fins and no anal
fin, a pair of strong horizontal keels on the tail stalk and a tall, crescent-shaped
(lunate) tail with nearly equal lobes. Its skin was almost naked, with scales only on
the fins, around the eyes and along the edges. Stomach contents show it swallowed
fishes and shrimp tail-first, suggesting it chased them down.

Smooth skin loft plus fin webs (nh_dev_fish). Colours are unknown: shark-like dark grey
above, white below.

Usage:
  blender --background --python tools/blender/cladoselache_fyleri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cladoselache.fbx (Swim: pivot at the body centre,
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

NAME = "Cladoselache"

BACK = (0.22, 0.25, 0.29)
FLANK = (0.42, 0.45, 0.48)
BELLY = (0.90, 0.90, 0.88)
FIN = (0.26, 0.29, 0.33)
FIN_EDGE = (0.16, 0.18, 0.21)
MOUTH = (0.08, 0.05, 0.05)
SPINE = (0.80, 0.76, 0.66)
SPINE_RIDGE = (0.45, 0.42, 0.36)
GILL = (0.12, 0.13, 0.15)

PROF = ef.Profile([
    (-0.80, 0.010, 0.020, 0.014, -0.010),
    (-0.77, 0.050, 0.060, 0.045, -0.010),
    (-0.68, 0.090, 0.098, 0.080, -0.006),
    (-0.52, 0.118, 0.130, 0.110, 0.000),
    (-0.30, 0.122, 0.140, 0.118, 0.004),
    (-0.06, 0.100, 0.118, 0.098, 0.010),
    (0.16, 0.064, 0.074, 0.060, 0.020),
    (0.32, 0.036, 0.040, 0.032, 0.034),
    (0.42, 0.026, 0.028, 0.024, 0.052),
    (0.52, 0.020, 0.022, 0.018, 0.100),
    (0.64, 0.013, 0.014, 0.012, 0.180),
    (0.74, 0.007, 0.008, 0.007, 0.250),
    (0.80, 0.002, 0.002, 0.002, 0.290),
], power=2.1)


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.35


def skin_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY)
    # five gill slits
    if -0.58 < co.y < -0.42 and abs(u) > 0.55 and -0.6 < v < 0.3:
        ph = (co.y + 0.58) / 0.032
        c = nh.lerp(c, GILL, 0.85 * (1.0 - nh.smoothstep(0.08, 0.2, abs(ph - round(ph)))))
    return c


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, PROF.y1, skin_color, ny=56, na=28)
    plain = ef.ray_color(FIN, FIN, FIN_EDGE, 1, rays=False, edge_amount=0.8)
    # first dorsal with its spine, second dorsal smaller
    df.web(mb, PROF, -0.24, -0.06, lambda u: (0.14 * u + 0.06, 0.20 * (1 - u) ** 0.8 + 0.01), plain,
           side=1, n=8, rows=3)
    base = Vector((0.0, -0.245, PROF.top(-0.245) - 0.004))
    ef.spine(mb, base, base + Vector((0.0, 0.06, 0.17)), 0.016, SPINE, SPINE_RIDGE, sides=8)
    df.web(mb, PROF, 0.12, 0.24, lambda u: (0.08 * u + 0.04, 0.11 * (1 - u) ** 0.8 + 0.01), plain,
           side=1, n=7, rows=2)
    # lunate tail: lower lobe off the upturned axis, thin upper fringe
    df.web(mb, PROF, 0.42, 0.80,
           lambda u: (0.16 * math.exp(-((u - 0.25) / 0.22) ** 2),
                      -(0.30 * math.exp(-((u - 0.22) / 0.17) ** 2) + 0.03 * (1 - u) + 0.004)),
           plain, side=-1, n=13, rows=3)
    df.web(mb, PROF, 0.44, 0.80, lambda u: (0.02, 0.03 * df.bump(u, 0.6) + 0.003), plain,
           side=1, n=7, rows=2)
    for s in (1, -1):
        # big broad-based pectorals
        ef.paired_fin(mb, PROF, s, -0.48, -0.30, -0.70, lambda u: 0.26 * (1 - u) ** 0.9 + 0.03,
                      0.85, 0.35, 0.6, plain, cols=8, rows=3)
        ef.paired_fin(mb, PROF, s, 0.10, 0.18, -0.9, lambda u: 0.07 * (1 - u) ** 0.8 + 0.01,
                      0.7, 0.5, 0.7, plain, cols=5, rows=2)
        # horizontal keel on the tail stalk
        pts = []
        for k in range(7):
            y = 0.30 + 0.16 * k / 6
            w = PROF.W(y) + 0.035 * math.sin(math.pi * k / 6)
            pts.append((s * w, y, PROF.CZ(y)))
        base_pts = [(s * PROF.W(0.30 + 0.16 * k / 6) * 0.5, 0.30 + 0.16 * k / 6, PROF.CZ(0.30 + 0.16 * k / 6))
                    for k in range(7)]
        import nh_fish as fish
        fish.fin(mb, base_pts, pts, plain, rows=1, th0=0.01, th1=0.004, normal=(0, 0, 1))
    ef.mouth_line(mb, PROF, -0.79, -0.68, mouth_z, MOUTH, r=0.006, grow=0.003)
    ef.surface_eye(mb, PROF, -0.70, 0.35, 0.030, (0.95, -0.25, 0.15), iris=(0.55, 0.55, 0.45))
    return df.finish(mb, NAME, roughness=0.35)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
