"""
Procedural Elpistostege watsoni for the map: an elpistostegalian lobe-finned fish from the
Late Devonian (Frasnian, about 380 million years ago) of Miguasha, Quebec; about 1.5 m
long. Its complete skeleton showed digit-like bones inside the pectoral fin, making it
the fish nearest to the first four-legged animals.

Like Panderichthys and Tiktaalik: a broad, flat, crocodile-like head with the eyes raised
on top, a flattened front body, no dorsal or anal fins, robust lobed pectoral fins and a
long tail fringed by a fin-ray web. Distinguished here by its longer snout, raised eye
bosses, heavier pectorals and banded grey-olive colouring (colours unknown).

Usage:
  blender --background --python tools/blender/elpistostege_watsoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Elpistostege.fbx (Swim: pivot at the body
centre, facing -Y). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Elpistostege"

BACK = (0.32, 0.34, 0.27)
FLANK = (0.58, 0.56, 0.42)
BELLY = (0.88, 0.84, 0.70)
BAND = (0.12, 0.13, 0.11)
HEAD = (0.54, 0.52, 0.40)
HEAD_TOP = (0.36, 0.36, 0.28)
SUTURE = (0.12, 0.12, 0.10)
MOUTH = (0.09, 0.06, 0.05)
TOOTH = (0.94, 0.90, 0.78)
FIN = (0.32, 0.33, 0.27)
FIN_EDGE = (0.62, 0.60, 0.46)
RAY = (0.16, 0.16, 0.12)

PROF = ef.Profile([
    (-0.80, 0.026, 0.010, 0.009, 0.000),
    (-0.76, 0.060, 0.022, 0.020, 0.000),
    (-0.68, 0.100, 0.036, 0.032, 0.002),
    (-0.56, 0.138, 0.050, 0.044, 0.004),
    (-0.44, 0.150, 0.062, 0.056, 0.006),
    (-0.30, 0.140, 0.074, 0.068, 0.006),
    (-0.10, 0.112, 0.080, 0.072, 0.006),
    (0.10, 0.080, 0.072, 0.064, 0.006),
    (0.30, 0.050, 0.054, 0.048, 0.006),
    (0.50, 0.028, 0.034, 0.030, 0.006),
    (0.70, 0.012, 0.015, 0.013, 0.006),
    (0.80, 0.002, 0.003, 0.003, 0.006),
], power=lambda y: 2.9 if y < -0.3 else 2.2)

Y_HEAD = -0.45


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.15


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(HEAD, HEAD_TOP, nh.smoothstep(0.0, 0.9, v))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.2, -0.8, v) * 0.6)
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.2), (-0.64, 0.25), (-0.54, 0.2), (-0.49, 0.9), (-0.60, 1.0), (-0.52, 1.7)]
    c = nh.lerp(c, SUTURE, 0.5 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    c = nh.lerp(c, SUTURE, 0.8 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.015 - 0.02 * abs(v))))))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY)
    band = 0.5 + 0.5 * math.sin(co.y * 26.0 + 0.6 * ef.mottle(co, 8.0, 2.0))
    return nh.lerp(c, BAND, 0.55 * nh.smoothstep(0.55, 0.9, band) * nh.smoothstep(-0.4, 0.2, v))


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.3 + 0.3 * t)


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=28, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 44, 22, scale_color, lift=0.004, fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # tail fringed by a fin-ray web above and below
    df.web(mb, PROF, 0.36, 0.80, lambda u: (0.06 * u, 0.065 * df.bump(u, 0.7, 0.05) + 0.004), rays(9),
           side=1, n=ef.ray_cols(9), rows=2)
    df.web(mb, PROF, 0.34, 0.80, lambda u: (0.06 * u, -(0.075 * df.bump(u, 0.7, 0.05) + 0.004)), rays(9),
           side=-1, n=ef.ray_cols(9), rows=2)
    for s in (1, -1):
        df.lobed_fin(mb, PROF, s, -0.40, -0.35, (0.85, 0.35, -0.40), 0.31, 0.044, lobe_paint, rays(5),
                     web_w=0.050, cols=ef.ray_cols(5), lobe_frac=0.75)
        df.lobed_fin(mb, PROF, s, 0.10, -0.6, (0.6, 0.7, -0.3), 0.14, 0.024, lobe_paint, rays(3),
                     web_w=0.035, cols=ef.ray_cols(3))
    ef.mouth_line(mb, PROF, -0.795, -0.56, mouth_z, MOUTH, grow=0.005)
    df.teeth(mb, PROF, -0.78, -0.58, mouth_z, 7, 0.013, TOOTH)
    # raised eye bosses on top of the head
    for s in (1, -1):
        p = PROF.point(-0.60, 1.2)
        p.x *= s
        mb.add(nh.ellipsoid((p.x, p.y, p.z - 0.004), (0.034, 0.036, 0.022), 2), HEAD_TOP)
    ef.surface_eye(mb, PROF, -0.60, 1.2, 0.024, (0.4, -0.2, 0.9), sink=0.05, iris=(0.75, 0.62, 0.25))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
