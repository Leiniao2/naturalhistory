"""
Procedural Panderichthys rhombolepis for the map: an elpistostegalian lobe-finned fish,
one of the closest fish relatives of the four-legged animals, from the Late Devonian
(Frasnian, about 380 million years ago) of Latvia and Estonia; about 1-1.3 m long.

What makes it look so unlike Eusthenopteron and so like an early tetrapod: a broad, flat,
crocodile-like head with the eyes on top, a dorsoventrally flattened front body, no dorsal
or anal fins at all, and a long tail with only a low diphycercal fin fold around its tip.
The pectoral fins are strong and lobed, the pelvic fins small. Rhombic scales cover
the trunk (hence "rhombolepis").

Built from nh_dev_fish / nh_early_fish pieces. Colours are unknown: muddy olive with darker
blotches, pale belly.

Usage:
  blender --background --python tools/blender/panderichthys_rhombolepis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Panderichthys.fbx (Swim: pivot at the body
centre, facing -Y). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Panderichthys"

BACK = (0.26, 0.27, 0.16)
FLANK = (0.48, 0.47, 0.30)
BELLY = (0.86, 0.82, 0.66)
BLOTCH = (0.14, 0.14, 0.08)
HEAD = (0.44, 0.42, 0.27)
HEAD_TOP = (0.30, 0.30, 0.18)
SUTURE = (0.14, 0.13, 0.08)
MOUTH = (0.09, 0.06, 0.05)
TOOTH = (0.92, 0.88, 0.76)
FIN = (0.36, 0.34, 0.20)
FIN_EDGE = (0.60, 0.56, 0.38)
RAY = (0.18, 0.17, 0.10)

# wide flat head (width >> height), flattened front trunk, long tapering tail
PROF = ef.Profile([
    (-0.80, 0.030, 0.012, 0.010, 0.000),
    (-0.77, 0.075, 0.030, 0.026, 0.000),
    (-0.70, 0.120, 0.048, 0.040, 0.002),
    (-0.58, 0.155, 0.064, 0.052, 0.004),
    (-0.46, 0.165, 0.074, 0.062, 0.006),
    (-0.30, 0.150, 0.086, 0.076, 0.006),
    (-0.10, 0.120, 0.090, 0.080, 0.006),
    (0.10, 0.086, 0.080, 0.070, 0.006),
    (0.30, 0.056, 0.058, 0.052, 0.006),
    (0.50, 0.032, 0.036, 0.032, 0.006),
    (0.70, 0.014, 0.016, 0.014, 0.006),
    (0.80, 0.002, 0.003, 0.003, 0.006),
], power=lambda y: 2.8 if y < -0.3 else 2.2)

Y_HEAD = -0.47


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.15


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(HEAD, HEAD_TOP, nh.smoothstep(0.0, 0.9, v))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.2, -0.8, v) * 0.6)
    c = nh.lerp(c, BLOTCH, 0.35 * nh.smoothstep(0.15, 0.45, ef.mottle(co, 14.0, 3.0)) * nh.smoothstep(0.0, 0.5, v))
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.2), (-0.64, 0.25), (-0.54, 0.2), (-0.50, 0.9), (-0.60, 1.0), (-0.52, 1.7)]
    c = nh.lerp(c, SUTURE, 0.5 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    c = nh.lerp(c, SUTURE, 0.8 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.015 - 0.02 * abs(v))))))
    return c


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.55)


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.3 + 0.3 * t)


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=28, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 44, 22, scale_color, lift=0.004, fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # low tail fin fold, longer below than above
    df.web(mb, PROF, 0.46, 0.80, lambda u: (0.06 * u, 0.05 * df.bump(u, 0.7, 0.05) + 0.004), rays(7),
           side=1, n=ef.ray_cols(7), rows=2)
    df.web(mb, PROF, 0.40, 0.80, lambda u: (0.06 * u, -(0.065 * df.bump(u, 0.7, 0.05) + 0.004)), rays(8),
           side=-1, n=ef.ray_cols(8), rows=2)
    for s in (1, -1):
        df.lobed_fin(mb, PROF, s, -0.42, -0.35, (0.8, 0.45, -0.35), 0.27, 0.036, lobe_paint, rays(5),
                     web_w=0.055, cols=ef.ray_cols(5), lobe_frac=0.7)
        df.lobed_fin(mb, PROF, s, 0.08, -0.6, (0.6, 0.7, -0.3), 0.13, 0.022, lobe_paint, rays(3),
                     web_w=0.035, cols=ef.ray_cols(3))
    ef.mouth_line(mb, PROF, -0.795, -0.58, mouth_z, MOUTH, grow=0.005)
    df.teeth(mb, PROF, -0.78, -0.60, mouth_z, 6, 0.012, TOOTH)
    # eyes on top of the flat head, close together
    ef.surface_eye(mb, PROF, -0.62, 1.15, 0.024, (0.35, -0.2, 0.9), iris=(0.72, 0.58, 0.25))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
