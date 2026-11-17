"""
Procedural Coccosteus cuspidatus for the map: a small arthrodire placoderm from the
Middle Devonian (Givetian, about 385 million years ago) lake beds of the Orcadian Basin,
Scotland; about 40 cm long - a smaller, earlier relative of Dunkleosteus.

The head and the front of the trunk are boxed in bony armour: a head shield with big
orbits, joined by a ball-and-socket neck joint to a thoracic shield (the arthrodire
"jointed neck" let it lift the head to open the mouth wide). Instead of teeth it had
sharp, beak-like bony jaw plates. Behind the armour the body was naked and tapered into a
long tail with a low fin fold above and below, plus a single dorsal fin; the small
pectoral fins came out through notches in the armour. Its tubercle-covered plates gave it
its name ("berry bone").

Skin loft (nh_dev_fish) with the armour as a slightly proud second shell painted with
plate sutures and tubercles. Colours are unknown: pale, tuberculate armour, a darker
olive body.

Usage:
  blender --background --python tools/blender/coccosteus_cuspidatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Coccosteus.fbx (Swim: pivot at the body centre,
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

NAME = "Coccosteus"

ARMOUR = (0.70, 0.64, 0.50)
ARMOUR_DARK = (0.46, 0.40, 0.30)
TUBERCLE = (0.84, 0.80, 0.68)
SUTURE = (0.16, 0.13, 0.09)
BACK = (0.22, 0.22, 0.15)
FLANK = (0.40, 0.40, 0.28)
BELLY = (0.78, 0.74, 0.60)
BLOTCH = (0.13, 0.13, 0.09)
FIN = (0.32, 0.32, 0.22)
FIN_EDGE = (0.55, 0.53, 0.40)
RAY = (0.16, 0.16, 0.11)
BLADE = (0.88, 0.84, 0.72)
MOUTH = (0.07, 0.05, 0.04)

PROF = ef.Profile([
    (-0.80, 0.030, 0.035, 0.030, -0.010),
    (-0.77, 0.085, 0.075, 0.065, -0.010),
    (-0.70, 0.135, 0.115, 0.095, -0.004),
    (-0.58, 0.170, 0.150, 0.125, 0.004),
    (-0.42, 0.180, 0.170, 0.140, 0.008),
    (-0.26, 0.165, 0.160, 0.130, 0.008),
    (-0.14, 0.120, 0.130, 0.108, 0.008),
    (0.04, 0.080, 0.096, 0.080, 0.008),
    (0.22, 0.050, 0.062, 0.052, 0.008),
    (0.42, 0.028, 0.034, 0.028, 0.008),
    (0.62, 0.012, 0.014, 0.012, 0.008),
    (0.80, 0.002, 0.003, 0.002, 0.008),
], power=lambda y: 2.6 if y < -0.2 else 2.1)

Y_ARMOUR = -0.22          # back edge of the thoracic shield (dorsal midline)
Y_NECK = -0.50            # head / thoracic shield joint


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.25


def armour_end(v):
    # the shield reaches further back on the back than on the flanks
    return Y_ARMOUR - 0.10 * (1.0 - max(v, -0.2))


def armour_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(ARMOUR, ARMOUR_DARK, 0.4 * nh.smoothstep(-0.2, -0.9, v))
    c = nh.lerp(c, TUBERCLE, 0.5 * nh.smoothstep(0.15, 0.45, ef.mottle(co, 60.0, 1.0)))
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.3), (-0.62, 0.0), (-0.60, 0.6), (-0.70, 1.2), (-0.56, 1.6),
             (-0.38, 0.0), (-0.36, 0.9), (-0.40, 1.6), (-0.34, 2.4)]
    c = nh.lerp(c, SUTURE, 0.7 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    # the neck joint groove between head and thoracic shields
    c = nh.lerp(c, SUTURE, 0.9 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_NECK + 0.03 * abs(u))))))
    if co.y < -0.6 and abs(u) > 0.3:
        c = nh.lerp(c, MOUTH, 1.0 - nh.smoothstep(0.004, 0.010, abs(co.z - mouth_z(co.y))))
    return c


def skin_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.4)


def armour_shell(mb):
    """Second, slightly proud shell over the front, trimmed at the shield's back edge."""
    bm = ef.loft(PROF, PROF.y0, Y_ARMOUR + 0.02, 24, 30, grow=0.006, cap0=True, cap1=False)
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        u, v = PROF.rel(c)
        if c.y > armour_end(v):
            kill.append(f)
    import bmesh
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    mb.add(bm, armour_color)


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, PROF.y1, skin_color, ny=50, na=26)
    armour_shell(mb)
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, PROF, -0.14, 0.06, lambda u: (0.08 * u + 0.04, 0.12 * df.bump(u, 0.6, 0.15) + 0.006), rays(5),
           side=1, n=ef.ray_cols(5), rows=2)
    # long tail fringed above and below
    df.web(mb, PROF, 0.26, 0.80, lambda u: (0.04 * u, 0.06 * df.bump(u, 0.6, 0.05) + 0.004), rays(10),
           side=1, n=ef.ray_cols(10), rows=2)
    df.web(mb, PROF, 0.14, 0.80, lambda u: (0.04 * u, -(0.07 * df.bump(u, 0.6, 0.05) + 0.004)), rays(11),
           side=-1, n=ef.ray_cols(11), rows=2)
    for s in (1, -1):
        ef.paired_fin(mb, PROF, s, -0.26, -0.18, -0.6, lambda u: 0.11 * (1 - u) ** 0.6 + 0.01,
                      0.8, 0.4, 0.8, rays(4), cols=ef.ray_cols(4), rows=2)
        ef.paired_fin(mb, PROF, s, 0.02, 0.10, -1.1, lambda u: 0.06 * (1 - u) ** 0.6 + 0.01,
                      0.6, 0.6, 0.8, rays(3), cols=ef.ray_cols(3), rows=2)
        # pale beak-like jaw blades along the gape
        pts = []
        for k in range(6):
            y = -0.795 + 0.16 * k / 5
            z = mouth_z(y)
            best = min((abs(PROF.point(y, a).z - z), a) for a in [-math.pi / 2 + q / 80 * math.pi for q in range(81)])[1]
            p = PROF.point(y, best, 0.008)
            p.x *= s
            pts.append(p)
        mb.add(nh.tube(pts, [0.004, 0.009, 0.010, 0.009, 0.007, 0.003], sides=5, scale_xy=(0.6, 1.0)), BLADE)
    # big orbits high on the head
    ef.surface_eye(mb, PROF, -0.67, 0.55, 0.034, (0.85, -0.3, 0.4), iris=(0.75, 0.60, 0.25), ring=ARMOUR_DARK)
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
