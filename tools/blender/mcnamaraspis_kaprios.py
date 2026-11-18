"""
Procedural Mcnamaraspis kaprios for the map: a small, sleek arthrodire placoderm from the
Late Devonian (Frasnian, about 380 million years ago) Gogo reef of Western Australia;
about 25 cm long (the state fossil emblem of Western Australia).

A fast little hunter on the reef: a head shield drawn out into a pointed snout, very
large orbits, sharp bony jaw blades with pointed tips, and a deep thoracic shield joined
to the head by the arthrodire neck joint. Behind the armour the naked body tapers into a
long tail with low fin folds.

Skin loft (nh_dev_fish) with the armour as a slightly proud second shell painted with
plate sutures and tubercles. Colours are unknown: bronze armour, dark olive-brown body.

Usage:
  blender --background --python tools/blender/mcnamaraspis_kaprios.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mcnamaraspis.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bmesh  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Mcnamaraspis"

ARMOUR = (0.74, 0.52, 0.26)
ARMOUR_DARK = (0.46, 0.30, 0.14)
TUBERCLE = (0.92, 0.76, 0.48)
SUTURE = (0.18, 0.10, 0.05)
BACK = (0.16, 0.13, 0.08)
FLANK = (0.36, 0.28, 0.16)
BELLY = (0.84, 0.74, 0.56)
BLOTCH = (0.08, 0.07, 0.04)
FIN = (0.30, 0.22, 0.12)
FIN_EDGE = (0.62, 0.46, 0.24)
RAY = (0.14, 0.10, 0.05)
BLADE = (0.94, 0.90, 0.78)
MOUTH = (0.07, 0.04, 0.03)

PROF = ef.Profile([
    (-0.80, 0.006, 0.010, 0.008, -0.020),
    (-0.75, 0.035, 0.040, 0.034, -0.016),
    (-0.68, 0.075, 0.080, 0.068, -0.010),
    (-0.56, 0.118, 0.125, 0.105, -0.002),
    (-0.40, 0.140, 0.155, 0.135, 0.006),
    (-0.24, 0.138, 0.152, 0.130, 0.008),
    (-0.10, 0.105, 0.120, 0.100, 0.008),
    (0.06, 0.070, 0.082, 0.068, 0.008),
    (0.24, 0.042, 0.050, 0.042, 0.008),
    (0.44, 0.022, 0.026, 0.022, 0.008),
    (0.64, 0.009, 0.011, 0.009, 0.008),
    (0.80, 0.002, 0.003, 0.002, 0.008),
], power=lambda y: 2.5 if y < -0.2 else 2.1)

Y_ARMOUR = -0.16
Y_NECK = -0.46


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.30


def armour_end(v):
    return Y_ARMOUR - 0.10 * (1.0 - max(v, -0.2))


def armour_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(ARMOUR, ARMOUR_DARK, 0.4 * nh.smoothstep(-0.2, -0.9, v) + 0.3 * nh.smoothstep(0.3, 1.0, v))
    c = nh.lerp(c, TUBERCLE, 0.55 * nh.smoothstep(0.15, 0.45, ef.mottle(co, 70.0, 1.0)))
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.72, 0.2), (-0.60, 0.0), (-0.58, 0.6), (-0.66, 1.2), (-0.52, 1.6),
             (-0.32, 0.0), (-0.30, 0.9), (-0.34, 1.6), (-0.28, 2.4)]
    c = nh.lerp(c, SUTURE, 0.7 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    c = nh.lerp(c, SUTURE, 0.9 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_NECK + 0.03 * abs(u))))))
    if co.y < -0.58 and abs(u) > 0.3:
        c = nh.lerp(c, MOUTH, 1.0 - nh.smoothstep(0.004, 0.010, abs(co.z - mouth_z(co.y))))
    return c


def skin_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.4)


def armour_shell(mb):
    bm = ef.loft(PROF, PROF.y0, Y_ARMOUR + 0.02, 26, 30, grow=0.006, cap0=True, cap1=False)
    kill = [f for f in bm.faces
            if f.calc_center_median().y > armour_end(PROF.rel(f.calc_center_median())[1])]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    mb.add(bm, armour_color)


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, PROF.y1, skin_color, ny=50, na=26)
    armour_shell(mb)
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, PROF, -0.08, 0.10, lambda u: (0.08 * u + 0.04, 0.13 * df.bump(u, 0.6, 0.15) + 0.006), rays(5),
           side=1, n=ef.ray_cols(5), rows=2)
    df.web(mb, PROF, 0.28, 0.80, lambda u: (0.04 * u, 0.05 * df.bump(u, 0.6, 0.05) + 0.004), rays(10),
           side=1, n=ef.ray_cols(10), rows=2)
    df.web(mb, PROF, 0.16, 0.80, lambda u: (0.04 * u, -(0.07 * df.bump(u, 0.6, 0.05) + 0.004)), rays(11),
           side=-1, n=ef.ray_cols(11), rows=2)
    for s in (1, -1):
        ef.paired_fin(mb, PROF, s, -0.22, -0.12, -0.6, lambda u: 0.12 * (1 - u) ** 0.6 + 0.01,
                      0.8, 0.4, 0.8, rays(4), cols=ef.ray_cols(4), rows=2)
        ef.paired_fin(mb, PROF, s, 0.06, 0.14, -1.1, lambda u: 0.06 * (1 - u) ** 0.6 + 0.01,
                      0.6, 0.6, 0.8, rays(3), cols=ef.ray_cols(3), rows=2)
        pts = []
        for k in range(7):
            y = -0.76 + 0.18 * k / 6
            z = mouth_z(y)
            best = min((abs(PROF.point(y, a).z - z), a) for a in [-math.pi / 2 + q / 80 * math.pi for q in range(81)])[1]
            p = PROF.point(y, best, 0.008)
            p.x *= s
            pts.append(p)
        mb.add(nh.tube(pts, [0.003, 0.009, 0.011, 0.010, 0.009, 0.007, 0.003], sides=5, scale_xy=(0.6, 1.0)), BLADE)
        # pointed tooth-like cusp at the front of each jaw blade
        p0 = pts[1]
        mb.add(nh.tube([tuple(p0), (p0.x, p0.y, p0.z - 0.03)], [0.007, 0.0], sides=5), BLADE)
    # very large orbits
    ef.surface_eye(mb, PROF, -0.62, 0.50, 0.040, (0.85, -0.3, 0.4), iris=(0.85, 0.62, 0.20), ring=ARMOUR_DARK)
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
