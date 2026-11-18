"""
Procedural Titanichthys agassizi for the map: a giant arthrodire placoderm from the Late
Devonian (Famennian, about 370-360 million years ago) seas of Ohio and Morocco; perhaps
5-7 m long, one of the largest animals of its time.

Built like its relative Dunkleosteus but a gentle giant: a long, low, rather flat head
shield joined to a short thoracic shield, small eyes, and long, slender lower jaws with
no cutting blades or fangs - just smooth, blunt edges. It probably swam slowly through
open water with its mouth open, sieving small prey such as plankton and shrimp, like a
basking shark. Behind the armour the huge body was naked and tapered into a long tail.

Skin loft (nh_dev_fish) with the armour as a slightly proud second shell painted with
plate sutures. Colours are unknown: dark slate-blue body, paler belly, grey armour.

Usage:
  blender --background --python tools/blender/titanichthys_agassizi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Titanichthys.fbx (Swim: pivot at the body centre,
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

NAME = "Titanichthys"

ARMOUR = (0.48, 0.52, 0.56)
ARMOUR_DARK = (0.28, 0.31, 0.35)
SUTURE = (0.10, 0.11, 0.13)
BACK = (0.13, 0.17, 0.24)
FLANK = (0.26, 0.32, 0.42)
BELLY = (0.78, 0.80, 0.82)
BLOTCH = (0.08, 0.10, 0.15)
FIN = (0.16, 0.20, 0.27)
FIN_EDGE = (0.34, 0.40, 0.48)
RAY = (0.09, 0.11, 0.15)
LIP = (0.62, 0.62, 0.58)
MOUTH = (0.05, 0.04, 0.05)

PROF = ef.Profile([
    (-0.80, 0.040, 0.030, 0.040, -0.020),
    (-0.77, 0.095, 0.060, 0.075, -0.020),
    (-0.68, 0.140, 0.090, 0.110, -0.012),
    (-0.54, 0.170, 0.120, 0.140, -0.002),
    (-0.38, 0.182, 0.150, 0.160, 0.006),
    (-0.20, 0.170, 0.160, 0.155, 0.010),
    (-0.02, 0.140, 0.145, 0.135, 0.010),
    (0.18, 0.098, 0.108, 0.098, 0.010),
    (0.38, 0.058, 0.064, 0.058, 0.012),
    (0.58, 0.026, 0.030, 0.026, 0.014),
    (0.72, 0.010, 0.012, 0.010, 0.016),
    (0.80, 0.002, 0.003, 0.002, 0.016),
], power=lambda y: 2.7 if y < -0.25 else 2.1)

Y_ARMOUR = -0.30
Y_NECK = -0.52


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.15


def armour_end(v):
    return Y_ARMOUR - 0.10 * (1.0 - max(v, -0.2))


def armour_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(ARMOUR, ARMOUR_DARK, 0.5 * nh.smoothstep(-0.2, -0.9, v) + 0.25 * nh.smoothstep(0.2, 0.9, v))
    c = nh.lerp(c, ARMOUR_DARK, 0.3 * nh.smoothstep(0.1, 0.45, ef.mottle(co, 25.0, 3.0)))
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.75, 0.3), (-0.66, 0.0), (-0.64, 0.7), (-0.72, 1.3), (-0.60, 1.7),
             (-0.44, 0.0), (-0.42, 0.9), (-0.44, 1.7), (-0.40, 2.4)]
    c = nh.lerp(c, SUTURE, 0.7 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    c = nh.lerp(c, SUTURE, 0.9 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_NECK + 0.03 * abs(u))))))
    return c


def skin_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.35)


def armour_shell(mb):
    bm = ef.loft(PROF, PROF.y0, Y_ARMOUR + 0.02, 26, 30, grow=0.006, cap0=True, cap1=False)
    kill = [f for f in bm.faces
            if f.calc_center_median().y > armour_end(PROF.rel(f.calc_center_median())[1])]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    mb.add(bm, armour_color)


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, PROF.y1, skin_color, ny=54, na=26)
    armour_shell(mb)
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, PROF, -0.18, 0.04, lambda u: (0.10 * u + 0.05, 0.15 * df.bump(u, 0.6, 0.15) + 0.006), rays(5),
           side=1, n=ef.ray_cols(5), rows=2)
    # long tail with a deeper lower lobe (hypocercal-ish fringe)
    df.web(mb, PROF, 0.30, 0.80, lambda u: (0.04 * u, 0.06 * df.bump(u, 0.6, 0.05) + 0.004), rays(9),
           side=1, n=ef.ray_cols(9), rows=2)
    df.web(mb, PROF, 0.22, 0.80, lambda u: (0.06 * u, -(0.11 * df.bump(u, 0.6, 0.05) + 0.004)), rays(11),
           side=-1, n=ef.ray_cols(11), rows=2)
    for s in (1, -1):
        ef.paired_fin(mb, PROF, s, -0.32, -0.20, -0.6, lambda u: 0.16 * (1 - u) ** 0.6 + 0.01,
                      0.8, 0.4, 0.8, rays(4), cols=ef.ray_cols(4), rows=2)
        ef.paired_fin(mb, PROF, s, 0.04, 0.12, -1.1, lambda u: 0.07 * (1 - u) ** 0.6 + 0.01,
                      0.6, 0.6, 0.8, rays(3), cols=ef.ray_cols(3), rows=2)
        # long, smooth, bladeless jaw edge: a pale blunt lip running far back
        pts = []
        for k in range(8):
            y = -0.795 + 0.26 * k / 7
            z = mouth_z(y)
            best = min((abs(PROF.point(y, a).z - z), a) for a in [-math.pi / 2 + q / 80 * math.pi for q in range(81)])[1]
            p = PROF.point(y, best, 0.006)
            p.x *= s
            pts.append(p)
        mb.add(nh.tube(pts, [0.004, 0.008, 0.008, 0.008, 0.008, 0.007, 0.006, 0.003], sides=5,
                       scale_xy=(0.6, 1.0)), LIP)
    ef.mouth_line(mb, PROF, -0.795, -0.53, lambda y: mouth_z(y) + 0.012, MOUTH, r=0.005, grow=0.007)
    # small eyes, far forward
    ef.surface_eye(mb, PROF, -0.72, 0.45, 0.018, (0.85, -0.3, 0.4), iris=(0.60, 0.55, 0.35), ring=ARMOUR_DARK)
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
