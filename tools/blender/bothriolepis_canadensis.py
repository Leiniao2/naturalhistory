"""
Procedural Bothriolepis canadensis for the map: an antiarch placoderm from the Late
Devonian (Frasnian, about 380 million years ago) Escuminac Formation at Miguasha, Quebec;
usually about 30-40 cm long. Bothriolepis is the most species-rich placoderm genus, found
on every continent in Middle and Late Devonian rivers, lakes and estuaries.

The front half is a box of bony plates: a small head shield with the eyes and nostrils
together in a single opening on top, and a long, high-backed trunk armour with a flat
belly. From its sides stick out the antiarch "arms": jointed, armour-plated pectoral
appendages with serrated edges, perhaps used to prop itself up, dig or push off from the
bottom. Behind the armour the body was naked and scaleless, with one dorsal fin and a
heterocercal tail. It probably grubbed for food in the mud.

Lofted armour and skin (nh_dev_fish), tube-built arms. Colours are unknown: pale grey-
brown, tuberculate armour, olive body.

Usage:
  blender --background --python tools/blender/bothriolepis_canadensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Bothriolepis.fbx (Swim: pivot at the body
centre, facing -Y). About 1.6 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Bothriolepis"

ARMOUR = (0.68, 0.62, 0.50)
ARMOUR_DARK = (0.44, 0.39, 0.30)
TUBERCLE = (0.82, 0.78, 0.66)
SUTURE = (0.17, 0.14, 0.10)
BACK = (0.26, 0.26, 0.17)
FLANK = (0.42, 0.42, 0.29)
BELLY = (0.76, 0.72, 0.58)
FIN = (0.32, 0.32, 0.22)
FIN_EDGE = (0.56, 0.54, 0.40)
RAY = (0.17, 0.17, 0.11)
EYE_PIT = (0.10, 0.08, 0.06)

# boxy armour (high superellipse power) then a slim naked tail
PROF = ef.Profile([
    (-0.80, 0.040, 0.030, 0.025, -0.040),
    (-0.77, 0.100, 0.060, 0.045, -0.040),
    (-0.68, 0.140, 0.090, 0.060, -0.035),
    (-0.56, 0.155, 0.130, 0.070, -0.030),
    (-0.40, 0.165, 0.175, 0.075, -0.025),
    (-0.24, 0.160, 0.170, 0.075, -0.025),
    (-0.10, 0.130, 0.130, 0.072, -0.020),
    (0.02, 0.080, 0.090, 0.060, -0.010),
    (0.20, 0.050, 0.060, 0.045, 0.000),
    (0.40, 0.030, 0.034, 0.026, 0.020),
    (0.60, 0.014, 0.015, 0.012, 0.055),
    (0.80, 0.002, 0.002, 0.002, 0.090),
], power=lambda y: 3.6 if y < -0.1 else 2.1)

Y_ARMOUR = -0.06
Y_HEAD = -0.60


def armour_color(co, u, v):
    c = nh.lerp(ARMOUR, ARMOUR_DARK, 0.3 * nh.smoothstep(-0.2, -0.9, v))
    c = nh.lerp(c, TUBERCLE, 0.45 * nh.smoothstep(0.15, 0.45, ef.mottle(co, 55.0, 1.0)))
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.72, 0.0), (-0.66, 0.9), (-0.44, 0.0), (-0.20, 0.0), (-0.40, 1.1), (-0.18, 1.1),
             (-0.40, 2.2), (-0.18, 2.2), (-0.30, 3.0)]
    c = nh.lerp(c, SUTURE, 0.7 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.07, width=0.012))
    return nh.lerp(c, SUTURE, 0.9 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - Y_HEAD))))


def skin_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY)


def arm(mb, s):
    """Jointed, plated pectoral appendage: proximal segment out and back, distal segment back."""
    root = Vector((s * PROF.W(-0.50) * 0.95, -0.50, PROF.CZ(-0.50) - 0.01))
    elbow = root + Vector((s * 0.16, 0.10, -0.03))
    tip = elbow + Vector((s * 0.06, 0.24, -0.02))
    seg = lambda co, n: nh.lerp(ARMOUR, ARMOUR_DARK, 0.5 * (1 - n.z) * 0.5)  # noqa: E731
    mb.add(nh.tube([root, root.lerp(elbow, 0.5), elbow], [0.030, 0.032, 0.026], sides=7, scale_xy=(1.0, 0.6)), seg)
    mb.add(nh.ellipsoid(elbow, (0.028, 0.028, 0.02), 1), SUTURE)
    mb.add(nh.tube([elbow, elbow.lerp(tip, 0.5), tip], [0.026, 0.022, 0.0], sides=7, scale_xy=(1.0, 0.55)), seg)
    # serrated outer edge
    for k in range(5):
        p = elbow.lerp(tip, 0.1 + 0.17 * k) + Vector((s * 0.022 * (1 - 0.15 * k), 0, 0))
        mb.add(nh.tube([p, p + Vector((s * 0.018, 0.012, 0))], [0.006, 0.0], sides=4), ARMOUR_DARK)


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, Y_ARMOUR, armour_color, ny=36, na=32, grow=0.003, cap1=False)
    df.skin(mb, PROF, Y_ARMOUR - 0.03, PROF.y1, skin_color, ny=30, na=20, cap0=False)
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, PROF, 0.02, 0.18, lambda u: (0.06 * u + 0.04, 0.11 * df.bump(u, 0.6, 0.15) + 0.006), rays(5),
           side=1, n=ef.ray_cols(5), rows=2)
    df.web(mb, PROF, 0.36, 0.80, lambda u: (0.08 * u, -(0.12 * df.bump(u, 0.8, 0.05) * (1 - 0.3 * u) + 0.004)),
           rays(7), side=-1, n=ef.ray_cols(7), rows=3)
    df.web(mb, PROF, 0.40, 0.80, lambda u: (0.02, 0.03 * df.bump(u, 0.6) + 0.003), rays(3),
           side=1, n=ef.ray_cols(3), rows=2)
    for s in (1, -1):
        arm(mb, s)
    # single orbital opening on top of the head with both eyes in it
    top = PROF.top(-0.70)
    mb.add(nh.uv_ellipsoid((0, -0.70, top - 0.004), (0.050, 0.035, 0.010), 10, 5), EYE_PIT)
    for s in (1, -1):
        ef.eye(mb, (s * 0.024, -0.70, top + 0.002), (s * 0.3, -0.2, 0.9), 0.016, iris=(0.65, 0.55, 0.30))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
