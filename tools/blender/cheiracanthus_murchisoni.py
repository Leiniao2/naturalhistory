"""
Procedural Cheiracanthus murchisoni for the map: an acanthodian ("spiny shark") from the
Middle Devonian (about 390 million years ago) lake beds of the Orcadian Basin, Scotland;
about 30 cm long.

Unlike the deep-bodied Climatius, Cheiracanthus was slender and streamlined, with a single
dorsal fin set far back above the anal fin, a slim spine in front of every fin, no extra
belly spines, large eyes, a big wide toothless mouth for gulping small prey from open
water, and a shark-like heterocercal tail. Tiny ornamented scales cover the body.

Smooth skin loft plus fin webs (nh_dev_fish), spines from nh_early_fish. Colours unknown:
dark blue-grey back, silvery flanks.

Usage:
  blender --background --python tools/blender/cheiracanthus_murchisoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cheiracanthus.fbx (Swim: pivot at the body centre,
facing -Y). About 1.5 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Cheiracanthus"

BACK = (0.16, 0.20, 0.26)
FLANK = (0.62, 0.66, 0.68)
BELLY = (0.90, 0.90, 0.86)
NET = (0.24, 0.28, 0.32)
FIN = (0.30, 0.34, 0.40)
FIN_EDGE = (0.14, 0.17, 0.22)
MOUTH = (0.08, 0.05, 0.04)
SPINE = (0.86, 0.84, 0.74)
SPINE_RIDGE = (0.48, 0.48, 0.42)
GILL = (0.14, 0.13, 0.09)

# (y, half-width, top, bottom, centre z)
PROF = ef.Profile([
    (-0.76, 0.012, 0.022, 0.020, -0.004),
    (-0.72, 0.050, 0.060, 0.056, -0.004),
    (-0.62, 0.080, 0.092, 0.086, 0.000),
    (-0.46, 0.090, 0.108, 0.100, 0.004),
    (-0.24, 0.084, 0.104, 0.096, 0.008),
    (0.00, 0.066, 0.084, 0.076, 0.014),
    (0.18, 0.048, 0.060, 0.054, 0.026),
    (0.32, 0.032, 0.040, 0.034, 0.048),
    (0.44, 0.020, 0.024, 0.020, 0.084),
    (0.56, 0.011, 0.013, 0.011, 0.130),
    (0.68, 0.005, 0.006, 0.005, 0.180),
    (0.74, 0.002, 0.002, 0.002, 0.205),
], power=2.1)


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * (0.05 + 0.35 * nh.smoothstep(-0.76, -0.62, y))


def skin_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY)
    # fine net of diagonal scale rows
    a = math.sin((co.y + co.z) * 95.0) * math.sin((co.y - co.z) * 95.0)
    c = nh.lerp(c, NET, 0.35 * nh.smoothstep(0.75, 0.95, abs(a)) * (1.0 - nh.smoothstep(-0.2, -0.6, v)))
    # gill region behind the head
    if -0.56 < co.y < -0.48 and abs(u) > 0.5 and -0.6 < v < 0.4:
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

    # a single dorsal fin far back, behind its spine
    df.web(mb, PROF, 0.14, 0.25, lambda u: (0.06 * u + 0.03, 0.10 * (1 - u) ** 0.9 + 0.008), plain,
           side=1, n=7, rows=2)
    spine_at(mb, 0.13, 0, 0, 0.12, lean=0.55, r=0.008)
    # anal fin opposite it
    df.web(mb, PROF, 0.16, 0.26, lambda u: (0.05 * u + 0.02, -(0.08 * (1 - u) ** 0.9 + 0.006)), plain,
           side=-1, n=6, rows=2)
    base = Vector((0.0, 0.155, PROF.CZ(0.155) - PROF.HB(0.155)))
    ef.spine(mb, base, base + Vector((0.0, 0.07, -0.08)), 0.007, SPINE, SPINE_RIDGE, sides=7)
    # heterocercal tail
    df.web(mb, PROF, 0.32, 0.74,
           lambda u: (0.10 * math.exp(-((u - 0.25) / 0.25) ** 2),
                      -(0.15 * math.exp(-((u - 0.25) / 0.2) ** 2) + 0.03 * (1 - u) + 0.004)),
           plain, side=-1, n=12, rows=3)
    df.web(mb, PROF, 0.40, 0.74, lambda u: (0.015, 0.022 * df.bump(u, 0.6) + 0.003), plain, side=1, n=7, rows=2)

    for s in (1, -1):
        ef.paired_fin(mb, PROF, s, -0.46, -0.36, -0.75, lambda u: 0.10 * (1 - u) ** 0.9 + 0.012,
                      0.8, 0.45, 0.6, plain, cols=6, rows=2)
        spine_at(mb, -0.47, s, 0.55, 0.15, lean=0.8, r=0.008)
        ef.paired_fin(mb, PROF, s, -0.04, 0.04, -0.9, lambda u: 0.05 * (1 - u) ** 0.8 + 0.008,
                      0.7, 0.55, 0.7, plain, cols=5, rows=2)
        spine_at(mb, -0.05, s, 0.85, 0.09, lean=0.8, r=0.006)

    # big gape
    ef.mouth_line(mb, PROF, -0.755, -0.58, mouth_z, MOUTH, r=0.007, grow=0.003)
    ef.surface_eye(mb, PROF, -0.66, 0.30, 0.038, (0.95, -0.25, 0.15), iris=(0.80, 0.78, 0.60))
    return df.finish(mb, NAME, roughness=0.40)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
