"""
Procedural Eusthenopteron foordi for the map: a tristichopterid lobe-finned fish from the
Late Devonian (Frasnian, about 380 million years ago) Escuminac Formation at Miguasha,
Quebec - one of the best-known fossil fishes, up to about 1.8 m long.

Long, torpedo-shaped body covered in rounded cosmoid scales; a fairly pointed head with
a wide gape and small fangs; fleshy, scaled lobes at the base of the pectoral and pelvic
fins (with the humerus-radius-ulna pattern of tetrapod limbs inside); two dorsal fins set
far back, the first above the pelvics, the second opposite the anal fin; and the
characteristic three-lobed (trifurcate) diphycercal tail: equal upper and lower lobes
with a small central lobe continuing the body axis between them.

Built from nh_dev_fish / nh_early_fish pieces. Colours are unknown: olive-bronze back,
silvery flanks, pale belly.

Usage:
  blender --background --python tools/blender/eusthenopteron_foordi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eusthenopteron.fbx (Swim: pivot at the body
centre, facing -Y). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Eusthenopteron"

BACK = (0.30, 0.30, 0.17)
FLANK = (0.66, 0.62, 0.44)
BELLY = (0.92, 0.88, 0.74)
BLOTCH = (0.18, 0.17, 0.10)
HEAD = (0.58, 0.53, 0.36)
HEAD_TOP = (0.30, 0.28, 0.17)
SUTURE = (0.16, 0.14, 0.09)
MOUTH = (0.10, 0.07, 0.05)
TOOTH = (0.92, 0.88, 0.76)
FIN = (0.40, 0.36, 0.22)
FIN_EDGE = (0.66, 0.58, 0.38)
RAY = (0.20, 0.18, 0.10)

PROF = ef.Profile([
    (-0.80, 0.010, 0.018, 0.012, -0.010),
    (-0.76, 0.050, 0.060, 0.048, -0.008),
    (-0.68, 0.085, 0.095, 0.080, -0.004),
    (-0.56, 0.110, 0.122, 0.108, 0.000),
    (-0.40, 0.118, 0.135, 0.125, 0.004),
    (-0.20, 0.108, 0.130, 0.120, 0.004),
    (0.00, 0.090, 0.112, 0.102, 0.004),
    (0.20, 0.064, 0.082, 0.074, 0.004),
    (0.36, 0.042, 0.052, 0.048, 0.004),
    (0.55, 0.024, 0.028, 0.026, 0.004),
    (0.72, 0.012, 0.014, 0.013, 0.004),
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
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.4)
    # silvery band along the lateral line
    return nh.lerp(c, (0.70, 0.68, 0.56), 0.3 * (1.0 - nh.smoothstep(0.03, 0.10, abs(v - 0.05))))


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.25 + 0.3 * t)


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # dorsal fins far back; anal fin opposite the second dorsal
    df.web(mb, PROF, -0.04, 0.08, lambda u: (0.05 * u + 0.03, 0.075 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.20, 0.31, lambda u: (0.05 * u + 0.03, 0.09 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
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
    ef.surface_eye(mb, PROF, -0.66, 0.45, 0.028, (0.9, -0.3, 0.3), iris=(0.70, 0.55, 0.22))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
