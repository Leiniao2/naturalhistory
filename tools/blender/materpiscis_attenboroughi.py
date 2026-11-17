"""
Procedural Materpiscis attenboroughi for the map: a ptyctodontid placoderm from the Late
Devonian (Frasnian, about 380 million years ago) Gogo Formation reef of Western
Australia; about 25 cm long. Named for David Attenborough, it is the "mother fish": the
holotype contains an embryo still attached by a mineralised umbilical cord, the oldest
known evidence of live birth (and so of internal fertilisation) in any vertebrate.

Ptyctodonts look rather like modern chimaeras: a short, blunt, high head with very large
eyes, beak-like crushing tooth plates for cracking shellfish, only a short ring of
armour round the head and shoulders, a tall dorsal fin with a spine, large pectoral fins,
and a long body tapering into a whip-like tail with low fin folds.

Skin loft with a short proud armour shell (nh_dev_fish). Colours are unknown: a mottled
reef-brown with a pale belly.

Usage:
  blender --background --python tools/blender/materpiscis_attenboroughi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Materpiscis.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Materpiscis"

ARMOUR = (0.62, 0.50, 0.36)
ARMOUR_DARK = (0.40, 0.30, 0.20)
SUTURE = (0.16, 0.11, 0.07)
BACK = (0.38, 0.24, 0.14)
FLANK = (0.62, 0.44, 0.28)
BELLY = (0.90, 0.82, 0.66)
BLOTCH = (0.24, 0.14, 0.08)
FIN = (0.46, 0.32, 0.20)
FIN_EDGE = (0.72, 0.56, 0.38)
RAY = (0.26, 0.16, 0.10)
BEAK = (0.90, 0.86, 0.76)
SPINE = (0.80, 0.74, 0.60)
SPINE_RIDGE = (0.45, 0.38, 0.28)

PROF = ef.Profile([
    (-0.80, 0.030, 0.050, 0.030, -0.040),
    (-0.78, 0.075, 0.110, 0.070, -0.030),
    (-0.72, 0.110, 0.165, 0.110, -0.010),
    (-0.62, 0.130, 0.195, 0.140, 0.000),
    (-0.48, 0.128, 0.190, 0.145, 0.004),
    (-0.30, 0.105, 0.150, 0.120, 0.006),
    (-0.10, 0.075, 0.100, 0.082, 0.006),
    (0.10, 0.048, 0.060, 0.050, 0.006),
    (0.30, 0.028, 0.032, 0.028, 0.006),
    (0.55, 0.012, 0.013, 0.011, 0.006),
    (0.80, 0.002, 0.002, 0.002, 0.006),
], power=lambda y: 2.4 if y < -0.4 else 2.1)

Y_ARMOUR = -0.50


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.45


def armour_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(ARMOUR, ARMOUR_DARK, 0.4 * nh.smoothstep(0.2, 0.9, v))
    c = nh.lerp(c, BLOTCH, 0.3 * nh.smoothstep(0.15, 0.45, ef.mottle(co, 18.0, 2.0)))
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.4), (-0.64, 0.0), (-0.64, 1.0), (-0.56, 1.8), (-0.54, 0.5)]
    return nh.lerp(c, SUTURE, 0.6 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))


def skin_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.6)


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, PROF.y1, skin_color, ny=50, na=26)
    bm = ef.loft(PROF, PROF.y0, Y_ARMOUR + 0.02, 18, 28, grow=0.005, cap0=True, cap1=False)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().y > Y_ARMOUR
                               - 0.06 * (1 - PROF.rel(f.calc_center_median())[1])], context="FACES")
    mb.add(bm, armour_color)
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # tall spined first dorsal, long low second dorsal
    df.web(mb, PROF, -0.46, -0.32, lambda u: (0.10 * u + 0.05, 0.20 * (1 - u) ** 0.7 + 0.01), rays(4),
           side=1, n=ef.ray_cols(4), rows=3)
    base = Vector((0.0, -0.465, PROF.top(-0.465) - 0.004))
    ef.spine(mb, base, base + Vector((0.0, 0.07, 0.21)), 0.016, SPINE, SPINE_RIDGE, sides=8)
    df.web(mb, PROF, -0.10, 0.70, lambda u: (0.03, 0.05 * df.bump(u, 0.5, 0.05) + 0.004), rays(12),
           side=1, n=ef.ray_cols(12), rows=2)
    df.web(mb, PROF, 0.05, 0.75, lambda u: (0.03, -(0.045 * df.bump(u, 0.5, 0.05) + 0.004)), rays(10),
           side=-1, n=ef.ray_cols(10), rows=2)
    for s in (1, -1):
        ef.paired_fin(mb, PROF, s, -0.50, -0.36, -0.55, lambda u: 0.20 * (1 - u) ** 0.7 + 0.02,
                      0.85, 0.35, 0.6, rays(5), cols=ef.ray_cols(5), rows=3)
        ef.paired_fin(mb, PROF, s, -0.20, -0.10, -1.0, lambda u: 0.08 * (1 - u) ** 0.6 + 0.01,
                      0.6, 0.6, 0.8, rays(3), cols=ef.ray_cols(3), rows=2)
    # beak-like tooth plates at the snout
    mb.add(nh.uv_ellipsoid((0.0, -0.795, mouth_z(-0.79) + 0.012), (0.035, 0.022, 0.016), 10, 6), BEAK)
    mb.add(nh.uv_ellipsoid((0.0, -0.785, mouth_z(-0.79) - 0.012), (0.030, 0.020, 0.013), 10, 6), BEAK)
    ef.surface_eye(mb, PROF, -0.66, 0.45, 0.050, (0.85, -0.3, 0.35), iris=(0.40, 0.55, 0.45))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
