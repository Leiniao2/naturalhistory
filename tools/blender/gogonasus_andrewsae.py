"""
Procedural Gogonasus andrewsae for the map: a small tetrapodomorph lobe-finned fish from
the Late Devonian (Frasnian, about 380 million years ago) Gogo reef of Western
Australia; about 30-40 cm long. Its beautifully preserved 3-D skull showed a very large
spiracle opening on top of the head, as in early tetrapods.

A stocky Eusthenopteron-like fish: deep body, short tail, very large eyes, a big dark
spiracle slit behind each eye on the skull roof, two dorsal fins set well back, lobed
pectoral and pelvic fins and a three-lobed (diphycercal) tail. Colours unknown: a reef
fish in warm red-brown with pale spots.

Usage:
  blender --background --python tools/blender/gogonasus_andrewsae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gogonasus.fbx (Swim: pivot at the body centre,
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

NAME = "Gogonasus"

BACK = (0.40, 0.18, 0.10)
FLANK = (0.72, 0.42, 0.24)
BELLY = (0.94, 0.84, 0.70)
BLOTCH = (0.96, 0.86, 0.62)
HEAD = (0.70, 0.44, 0.28)
HEAD_TOP = (0.42, 0.20, 0.12)
SUTURE = (0.16, 0.14, 0.09)
MOUTH = (0.10, 0.07, 0.05)
TOOTH = (0.92, 0.88, 0.76)
FIN = (0.52, 0.26, 0.14)
FIN_EDGE = (0.86, 0.62, 0.40)
RAY = (0.20, 0.18, 0.10)

PROF = ef.Profile([
    (-0.80, 0.012, 0.024, 0.016, -0.010),
    (-0.76, 0.060, 0.080, 0.064, -0.008),
    (-0.68, 0.108, 0.132, 0.110, -0.004),
    (-0.56, 0.140, 0.172, 0.150, 0.000),
    (-0.40, 0.148, 0.188, 0.170, 0.004),
    (-0.20, 0.134, 0.178, 0.162, 0.004),
    (0.00, 0.108, 0.150, 0.136, 0.004),
    (0.20, 0.072, 0.104, 0.094, 0.004),
    (0.36, 0.044, 0.062, 0.058, 0.004),
    (0.52, 0.026, 0.034, 0.032, 0.004),
    (0.70, 0.012, 0.015, 0.014, 0.004),
    (0.80, 0.002, 0.003, 0.003, 0.004),
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
    sp = math.hypot((co.y + 0.53) / 0.040, (abs(co.x) - 0.045) / 0.012)
    c = nh.lerp(c, (0.05, 0.03, 0.02), (1.0 - nh.smoothstep(0.8, 1.0, sp)) * nh.smoothstep(0.3, 0.6, v))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY)
    c = nh.lerp(c, BLOTCH, 0.75 * nh.smoothstep(0.38, 0.5, ef.mottle(co, 30.0, 6.0)) * nh.smoothstep(-0.5, 0.2, v))
    # silvery band along the lateral line
    return nh.lerp(c, (0.70, 0.68, 0.56), 0.3 * (1.0 - nh.smoothstep(0.03, 0.10, abs(v - 0.05))))


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.25 + 0.3 * t)


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # dorsal fins far back; anal fin opposite the second dorsal
    df.web(mb, PROF, -0.04, 0.08, lambda u: (0.05 * u + 0.03, 0.10 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.20, 0.31, lambda u: (0.05 * u + 0.03, 0.12 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.20, 0.31, lambda u: (0.05 * u + 0.03, -0.09 * df.bump(u, 0.6, 0.15) - 0.006), rays(4),
           side=-1, n=ef.ray_cols(4), rows=2)
    # three-lobed tail: equal upper and lower lobes, then a small central lobe
    for side in (1, -1):
        df.web(mb, PROF, 0.40, 0.66,
               lambda u, s=side: (0.10 * u, s * (0.15 * df.bump(u, 0.9, 0.05) * (1 - 0.25 * u) + 0.005)), rays(8),
               side=side, n=ef.ray_cols(8), rows=3)
        df.web(mb, PROF, 0.645, 0.80, lambda u, s=side: (0.03, s * (0.05 * df.bump(u, 0.6) + 0.003)), rays(3),
               side=side, n=ef.ray_cols(3), rows=2)
    for s in (1, -1):
        df.lobed_fin(mb, PROF, s, -0.42, -0.9, (0.55, 0.65, -0.45), 0.24, 0.032, lobe_paint, rays(5),
                     web_w=0.06, cols=ef.ray_cols(5))
        df.lobed_fin(mb, PROF, s, 0.00, -1.25, (0.45, 0.8, -0.4), 0.17, 0.024, lobe_paint, rays(4),
                     web_w=0.045, cols=ef.ray_cols(4))


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=26, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 44, 20, scale_color, lift=0.004, fade_y=(0.45, 0.75))
    fins(mb)
    ef.mouth_line(mb, PROF, -0.79, -0.58, mouth_z, MOUTH, grow=0.005)
    df.teeth(mb, PROF, -0.78, -0.62, mouth_z, 5, 0.014, TOOTH)
    ef.surface_eye(mb, PROF, -0.64, 0.50, 0.046, (0.9, -0.3, 0.3), iris=(0.70, 0.55, 0.22))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
