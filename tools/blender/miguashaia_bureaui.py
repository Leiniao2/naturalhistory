"""
Procedural Miguashaia bureaui for the map: one of the earliest coelacanths, from the Late
Devonian (Frasnian, about 380 million years ago) of Miguasha, Quebec; about 45 cm long.

A deep-bodied coelacanth: a rayed first dorsal fin, a fleshy lobed second dorsal and anal
fin, lobed pectoral and pelvic fins, and - unlike later coelacanths - an asymmetric tail
with a larger upper lobe and no small central tassel. Colours unknown: painted dark
steel-blue with pale spots like the living coelacanth.

Usage:
  blender --background --python tools/blender/miguashaia_bureaui.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Miguashaia.fbx (Swim: pivot at the body centre,
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

NAME = "Miguashaia"

BACK = (0.10, 0.14, 0.22)
FLANK = (0.20, 0.28, 0.40)
BELLY = (0.50, 0.58, 0.66)
BLOTCH = (0.86, 0.88, 0.84)
HEAD = (0.22, 0.30, 0.42)
HEAD_TOP = (0.12, 0.16, 0.24)
SUTURE = (0.16, 0.14, 0.09)
MOUTH = (0.10, 0.07, 0.05)
TOOTH = (0.92, 0.88, 0.76)
FIN = (0.16, 0.22, 0.32)
FIN_EDGE = (0.44, 0.54, 0.64)
RAY = (0.06, 0.08, 0.12)

PROF = ef.Profile([
    (-0.80, 0.012, 0.030, 0.020, -0.012),
    (-0.76, 0.052, 0.090, 0.070, -0.010),
    (-0.68, 0.090, 0.140, 0.120, -0.006),
    (-0.56, 0.114, 0.180, 0.165, 0.000),
    (-0.40, 0.120, 0.200, 0.190, 0.004),
    (-0.20, 0.112, 0.190, 0.180, 0.006),
    (0.00, 0.094, 0.160, 0.150, 0.010),
    (0.20, 0.064, 0.110, 0.100, 0.016),
    (0.36, 0.040, 0.066, 0.060, 0.024),
    (0.52, 0.022, 0.034, 0.030, 0.034),
    (0.70, 0.010, 0.014, 0.012, 0.046),
    (0.80, 0.002, 0.003, 0.003, 0.052),
], power=lambda y: 2.4 if y < -0.45 else 2.1)

Y_HEAD = -0.46


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.25


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(HEAD, HEAD_TOP, nh.smoothstep(0.0, 0.9, v))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.3, -0.85, v) * 0.6)
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.3), (-0.64, 0.25), (-0.56, 0.3), (-0.50, 0.9), (-0.58, 1.4), (-0.50, 1.8), (-0.66, 1.9)]
    c = nh.lerp(c, SUTURE, 0.6 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    # gill cover edge
    c = nh.lerp(c, SUTURE, 0.8 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.015 - 0.02 * abs(v))))))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY)
    c = nh.lerp(c, BLOTCH, 0.85 * nh.smoothstep(0.36, 0.46, ef.mottle(co, 26.0, 9.0)))
    # silvery band along the lateral line
    return nh.lerp(c, (0.70, 0.68, 0.56), 0.3 * (1.0 - nh.smoothstep(0.03, 0.10, abs(v - 0.05))))


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.25 + 0.3 * t)


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # first dorsal: a tall rayed fan
    df.web(mb, PROF, -0.24, -0.10, lambda u: (0.08 * u + 0.04, 0.15 * df.bump(u, 0.5, 0.2) + 0.006), rays(6),
           side=1, n=ef.ray_cols(6), rows=2)
    # lobed second dorsal and anal fins
    for side, ang in ((1, math.pi / 2), (-1, -math.pi / 2)):
        df.lobed_fin(mb, PROF, 1, 0.22, ang, (0.0, 0.75, side * 0.65), 0.15, 0.026, lobe_paint, rays(4),
                     web_w=0.04, cols=ef.ray_cols(4), toward=(0, 1.0, -side * 0.6))
    # asymmetric tail: a bigger upper lobe, no central tassel
    df.web(mb, PROF, 0.42, 0.80, lambda u: (0.14 * u, 0.20 * df.bump(u, 0.8, 0.05) * (1 - 0.1 * u) + 0.005), rays(9),
           side=1, n=ef.ray_cols(9), rows=3)
    df.web(mb, PROF, 0.44, 0.76, lambda u: (0.10 * u, -(0.14 * df.bump(u, 0.8, 0.05) + 0.005)), rays(7),
           side=-1, n=ef.ray_cols(7), rows=3)
    for s in (1, -1):
        df.lobed_fin(mb, PROF, s, -0.40, -0.5, (0.6, 0.6, -0.35), 0.24, 0.032, lobe_paint, rays(5),
                     web_w=0.06, cols=ef.ray_cols(5))
        df.lobed_fin(mb, PROF, s, 0.02, -1.25, (0.45, 0.8, -0.4), 0.17, 0.024, lobe_paint, rays(4),
                     web_w=0.045, cols=ef.ray_cols(4))


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=26, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 44, 20, scale_color, lift=0.004, fade_y=(0.45, 0.75))
    fins(mb)
    ef.mouth_line(mb, PROF, -0.79, -0.58, mouth_z, MOUTH, grow=0.005)
    df.teeth(mb, PROF, -0.78, -0.62, mouth_z, 5, 0.014, TOOTH)
    ef.surface_eye(mb, PROF, -0.66, 0.50, 0.036, (0.9, -0.3, 0.3), iris=(0.62, 0.70, 0.40))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
