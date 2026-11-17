"""
Procedural Acanthostega gunnari for the map: one of the earliest four-limbed vertebrates,
from the Late Devonian (Famennian, about 365 million years ago) Britta Dal Formation of
East Greenland; about 60 cm long.

A tetrapod that still lived like a fish: it had internal gills as well as lungs, a
broad, flat skull with the eyes on top, a slim body, and a long, deep tail fringed above
and below by a tall fin supported by bony rays. Its limbs were short, paddle-like and
could hardly bear its weight on land; each forelimb ended in eight digits (more than the
five of later tetrapods), the hind limbs too had eight. It probably lived in shallow,
weedy river channels, ambushing prey.

Smooth skin loft (nh_dev_fish), tail fin webs, tube limbs with fanned digits. Colours are
unknown: mottled olive-brown with a pale belly.

Usage:
  blender --background --python tools/blender/acanthostega_gunnari.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Acanthostega.fbx (Swim: pivot at the body centre,
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

NAME = "Acanthostega"

BACK = (0.24, 0.25, 0.14)
FLANK = (0.44, 0.42, 0.26)
BELLY = (0.84, 0.78, 0.58)
BLOTCH = (0.12, 0.12, 0.07)
FIN = (0.34, 0.32, 0.20)
FIN_EDGE = (0.60, 0.56, 0.38)
RAY = (0.18, 0.17, 0.10)
MOUTH = (0.09, 0.06, 0.05)
TOOTH = (0.92, 0.88, 0.76)
LIMB = (0.40, 0.38, 0.23)

PROF = ef.Profile([
    (-0.80, 0.030, 0.012, 0.010, 0.000),
    (-0.77, 0.070, 0.026, 0.022, 0.000),
    (-0.70, 0.105, 0.040, 0.034, 0.002),
    (-0.60, 0.130, 0.052, 0.044, 0.004),
    (-0.50, 0.128, 0.060, 0.052, 0.006),
    (-0.40, 0.100, 0.066, 0.060, 0.006),
    (-0.20, 0.092, 0.070, 0.064, 0.006),
    (0.00, 0.082, 0.068, 0.062, 0.006),
    (0.12, 0.066, 0.060, 0.054, 0.006),
    (0.30, 0.036, 0.050, 0.044, 0.006),
    (0.50, 0.020, 0.036, 0.030, 0.006),
    (0.70, 0.010, 0.018, 0.015, 0.006),
    (0.80, 0.002, 0.003, 0.003, 0.006),
], power=lambda y: 2.6 if y < -0.45 else 2.1)


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.10


def skin_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.55)
    if co.y < -0.62 and abs(u) > 0.5:
        c = nh.lerp(c, MOUTH, 1.0 - nh.smoothstep(0.003, 0.008, abs(co.z - mouth_z(co.y))))
    return c


def limb(mb, s, y, out, down, back, length, r0):
    root = PROF.point(y, -0.5, -0.01)
    root.x *= s
    knee = root + Vector((s * out * 0.55, back * 0.2, -down * 0.4)) * length
    foot = knee + Vector((s * out * 0.35, back * 0.55, -down * 0.5)) * length
    col = lambda co, n: nh.lerp(BELLY, LIMB, nh.smoothstep(-0.6, 0.4, n.z))  # noqa: E731
    mb.add(nh.tube([root, root.lerp(knee, 0.5), knee], [r0, r0 * 0.9, r0 * 0.8], sides=8), col)
    mb.add(nh.tube([knee, knee.lerp(foot, 0.5), foot], [r0 * 0.8, r0 * 0.7, r0 * 0.6], sides=8), col)
    # eight short digits fanned out like a paddle
    d = (foot - knee).normalized()
    side = Vector((s, 0, 0))
    for k in range(8):
        a = -0.75 + 1.5 * k / 7
        dirv = (d * math.cos(a) + side * math.sin(a) * 0.9).normalized()
        tip = foot + dirv * length * 0.22 * (0.8 + 0.2 * math.cos(a))
        mb.add(nh.tube([foot, tip], [r0 * 0.28, r0 * 0.12], sides=5), LIMB)


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, PROF.y1, skin_color, ny=60, na=28)
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # tall tail fin above and below, supported by rays
    df.web(mb, PROF, 0.05, 0.80, lambda u: (0.05 * u, 0.11 * df.bump(u, 0.6, 0.05) + 0.004), rays(16),
           side=1, n=ef.ray_cols(16), rows=2)
    df.web(mb, PROF, 0.30, 0.80, lambda u: (0.05 * u, -(0.09 * df.bump(u, 0.6, 0.05) + 0.004)), rays(12),
           side=-1, n=ef.ray_cols(12), rows=2)
    for s in (1, -1):
        limb(mb, s, -0.40, 0.9, 0.5, 0.3, 0.20, 0.022)
        limb(mb, s, 0.08, 0.9, 0.5, 0.45, 0.22, 0.024)
    df.teeth(mb, PROF, -0.78, -0.64, mouth_z, 7, 0.010, TOOTH)
    ef.surface_eye(mb, PROF, -0.62, 1.05, 0.024, (0.4, -0.2, 0.9), iris=(0.72, 0.60, 0.25))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
