"""
Procedural Holoptychius nobilissimus for the map: a large porolepiform lobe-finned fish
from the Late Devonian (Frasnian-Famennian, about 380-360 million years ago) Old Red
Sandstone of Scotland; Holoptychius species were found worldwide in Late Devonian rivers
and some reached well over a metre.

A deep-bodied, rather short-headed predator with fangs, long pointed lobed pectoral fins,
lobed pelvic fins, and dorsal and anal fins set very far back next to the strongly
heterocercal tail (the body axis turns up into the upper lobe). Its large, thick, rounded
scales carry wavy ridges ("Holoptychius" = wholly wrinkled).

Built from nh_dev_fish / nh_early_fish pieces. Colours are unknown: warm bronze-brown with a
pale belly.

Usage:
  blender --background --python tools/blender/holoptychius_nobilissimus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Holoptychius.fbx (Swim: pivot at the body
centre, facing -Y). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Holoptychius"

BACK = (0.30, 0.20, 0.11)
FLANK = (0.62, 0.44, 0.24)
BELLY = (0.88, 0.80, 0.62)
BLOTCH = (0.22, 0.13, 0.07)
RIDGE = (0.36, 0.23, 0.12)
HEAD = (0.56, 0.42, 0.26)
HEAD_TOP = (0.36, 0.26, 0.15)
SUTURE = (0.18, 0.11, 0.06)
MOUTH = (0.10, 0.06, 0.04)
TOOTH = (0.94, 0.90, 0.80)
FIN = (0.40, 0.28, 0.16)
FIN_EDGE = (0.66, 0.50, 0.30)
RAY = (0.22, 0.14, 0.08)

# deep trunk, the axis rising into the upper tail lobe
PROF = ef.Profile([
    (-0.80, 0.025, 0.035, 0.025, -0.030),
    (-0.77, 0.075, 0.085, 0.065, -0.025),
    (-0.68, 0.120, 0.140, 0.120, -0.015),
    (-0.54, 0.150, 0.190, 0.170, -0.005),
    (-0.36, 0.158, 0.215, 0.195, 0.000),
    (-0.14, 0.145, 0.205, 0.185, 0.004),
    (0.06, 0.115, 0.165, 0.150, 0.010),
    (0.24, 0.078, 0.110, 0.100, 0.024),
    (0.38, 0.050, 0.066, 0.060, 0.046),
    (0.54, 0.028, 0.034, 0.030, 0.090),
    (0.70, 0.012, 0.014, 0.012, 0.150),
    (0.80, 0.002, 0.003, 0.003, 0.190),
], power=lambda y: 2.4 if y < -0.5 else 2.1)

Y_HEAD = -0.53


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.30


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(HEAD, HEAD_TOP, nh.smoothstep(0.0, 0.9, v))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.35, -0.85, v) * 0.6)
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.3), (-0.64, 0.25), (-0.58, 0.9), (-0.66, 1.5), (-0.58, 1.9)]
    c = nh.lerp(c, SUTURE, 0.5 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    c = nh.lerp(c, SUTURE, 0.8 * (1.0 - nh.smoothstep(0.005, 0.013, abs(co.y - (Y_HEAD - 0.015 - 0.025 * abs(v))))))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.3)
    # wavy ridges across the big scales
    w = 0.5 + 0.5 * math.sin(co.y * 140.0 + 8.0 * math.sin(co.z * 30.0))
    return nh.lerp(c, RIDGE, 0.35 * nh.smoothstep(0.6, 0.95, w))


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.25 + 0.35 * t)


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=28, grow=0.005)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 30, 16, scale_color, lift=0.007, shine=0.20,
                   fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # dorsal and anal fins far back
    df.web(mb, PROF, 0.22, 0.36, lambda u: (0.06 * u + 0.04, 0.10 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.20, 0.36, lambda u: (0.06 * u + 0.04, -0.11 * df.bump(u, 0.6, 0.15) - 0.006), rays(4),
           side=-1, n=ef.ray_cols(4), rows=2)
    # heterocercal tail: big lower web, a thin fringe above the upturned axis
    df.web(mb, PROF, 0.40, 0.80, lambda u: (0.10 * u, -(0.21 * df.bump(u, 0.8, 0.05) * (1 - 0.35 * u) + 0.005)),
           rays(9), side=-1, n=ef.ray_cols(9), rows=3)
    df.web(mb, PROF, 0.42, 0.80, lambda u: (0.02, 0.035 * df.bump(u, 0.6) + 0.003), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    for s in (1, -1):
        df.lobed_fin(mb, PROF, s, -0.47, -0.9, (0.55, 0.65, -0.5), 0.34, 0.036, lobe_paint, rays(5),
                     web_w=0.055, cols=ef.ray_cols(5), lobe_frac=0.75)
        df.lobed_fin(mb, PROF, s, 0.02, -1.2, (0.45, 0.8, -0.4), 0.20, 0.028, lobe_paint, rays(4),
                     web_w=0.045, cols=ef.ray_cols(4))
    ef.mouth_line(mb, PROF, -0.795, -0.60, mouth_z, MOUTH, r=0.005, grow=0.006)
    df.teeth(mb, PROF, -0.78, -0.75, mouth_z, 1, 0.035, TOOTH, r=0.010)
    df.teeth(mb, PROF, -0.74, -0.62, mouth_z, 5, 0.014, TOOTH)
    ef.surface_eye(mb, PROF, -0.70, 0.50, 0.024, (0.85, -0.3, 0.4), iris=(0.70, 0.52, 0.20))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
