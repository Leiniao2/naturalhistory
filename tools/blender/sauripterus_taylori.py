"""
Procedural Sauripterus taylori for the map: a rhizodont lobe-finned fish from the Late
Devonian (Famennian, about 365 million years ago) rivers of Pennsylvania; about 1.5-2 m
long. Famous for its huge pectoral fins, whose bones include eight finger-like rays.

A long, powerful ambush predator: a big, broad head with long fangs, a long body with
small dorsal and anal fins far back near the tail, a diphycercal tail and above all very
large, broad, fleshy-lobed pectoral fins. Colours unknown: dark olive-grey with pale belly.

Usage:
  blender --background --python tools/blender/sauripterus_taylori.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sauripterus.fbx (Swim: pivot at the body centre,
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

NAME = "Sauripterus"

BACK = (0.30, 0.34, 0.27)
FLANK = (0.60, 0.63, 0.50)
BELLY = (0.88, 0.86, 0.76)
BLOTCH = (0.14, 0.16, 0.12)
HEAD = (0.58, 0.60, 0.48)
HEAD_TOP = (0.32, 0.36, 0.29)
SUTURE = (0.16, 0.14, 0.09)
MOUTH = (0.10, 0.07, 0.05)
TOOTH = (0.92, 0.88, 0.76)
FIN = (0.28, 0.32, 0.27)
FIN_EDGE = (0.58, 0.60, 0.50)
RAY = (0.20, 0.18, 0.10)

PROF = ef.Profile([
    (-0.80, 0.020, 0.016, 0.012, -0.004),
    (-0.76, 0.060, 0.044, 0.038, -0.004),
    (-0.68, 0.090, 0.068, 0.060, -0.002),
    (-0.56, 0.108, 0.088, 0.080, 0.000),
    (-0.42, 0.112, 0.098, 0.090, 0.002),
    (-0.20, 0.100, 0.096, 0.088, 0.002),
    (0.00, 0.084, 0.086, 0.080, 0.002),
    (0.20, 0.064, 0.068, 0.062, 0.002),
    (0.40, 0.042, 0.046, 0.042, 0.002),
    (0.58, 0.024, 0.026, 0.024, 0.002),
    (0.72, 0.012, 0.013, 0.012, 0.002),
    (0.80, 0.002, 0.003, 0.003, 0.002),
], power=lambda y: 2.4 if y < -0.45 else 2.1)

Y_HEAD = -0.50


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
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.4)
    # silvery band along the lateral line
    return nh.lerp(c, (0.70, 0.68, 0.56), 0.3 * (1.0 - nh.smoothstep(0.03, 0.10, abs(v - 0.05))))


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.25 + 0.3 * t)


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # small dorsal and anal fins far back
    df.web(mb, PROF, 0.30, 0.40, lambda u: (0.05 * u + 0.03, 0.07 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.30, 0.40, lambda u: (0.05 * u + 0.03, -0.07 * df.bump(u, 0.6, 0.15) - 0.006), rays(4),
           side=-1, n=ef.ray_cols(4), rows=2)
    # long symmetric (diphycercal) tail fin
    for side in (1, -1):
        df.web(mb, PROF, 0.48, 0.80, lambda u, s=side: (0.08 * u, s * (0.10 * df.bump(u, 0.8, 0.05) + 0.005)), rays(9),
               side=side, n=ef.ray_cols(9), rows=3)
    for s in (1, -1):
        # very large, broad pectoral fins
        df.lobed_fin(mb, PROF, s, -0.44, -0.6, (0.75, 0.45, -0.4), 0.46, 0.060, lobe_paint, rays(8),
                     web_w=0.15, lead_w=0.035, cols=ef.ray_cols(8), lobe_frac=0.55)
        df.lobed_fin(mb, PROF, s, 0.08, -1.25, (0.45, 0.8, -0.4), 0.16, 0.024, lobe_paint, rays(4),
                     web_w=0.045, cols=ef.ray_cols(4))


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=26, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 44, 20, scale_color, lift=0.004, fade_y=(0.45, 0.75))
    fins(mb)
    ef.mouth_line(mb, PROF, -0.79, -0.56, mouth_z, MOUTH, grow=0.005)
    df.teeth(mb, PROF, -0.78, -0.58, mouth_z, 7, 0.014, TOOTH)
    # big fangs at the front of the jaws
    df.teeth(mb, PROF, -0.775, -0.73, mouth_z, 1, 0.065, TOOTH, r=0.011)
    df.teeth(mb, PROF, -0.765, -0.72, mouth_z, 1, 0.050, TOOTH, r=0.010, up=1)
    ef.surface_eye(mb, PROF, -0.66, 0.65, 0.024, (0.9, -0.3, 0.3), iris=(0.70, 0.55, 0.22))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
