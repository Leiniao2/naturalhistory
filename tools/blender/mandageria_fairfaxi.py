"""
Procedural Mandageria fairfaxi for the map: a tristichopterid lobe-finned fish from the
Late Devonian (Famennian, about 365 million years ago) river beds of Canowindra, New South
Wales; about 1.6 m long.

A big, torpedo-shaped ambush predator related to Eusthenopteron and the giant Hyneria:
a long, low, flattened head with large fangs at the front of the jaws and rows of
smaller teeth behind, a slender scaled body, lobed paired fins, the dorsal and anal fins
set far back near the tail for a fast lunging start, and a symmetrical three-lobed tail.

Bony head + rhombic scale lattice (nh_early_fish) with fin webs and lobes (nh_dev_fish).
Colours are unknown: dark grey-green back, silvery-olive flanks, pale belly.

Usage:
  blender --background --python tools/blender/mandageria_fairfaxi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mandageria.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Mandageria"

BACK = (0.24, 0.29, 0.28)
FLANK = (0.56, 0.58, 0.50)
BELLY = (0.90, 0.90, 0.84)
BLOTCH = (0.12, 0.15, 0.15)
HEAD = (0.60, 0.62, 0.54)
HEAD_TOP = (0.28, 0.33, 0.32)
SUTURE = (0.10, 0.12, 0.11)
MOUTH = (0.10, 0.06, 0.05)
TOOTH = (0.95, 0.92, 0.82)
FIN = (0.30, 0.34, 0.32)
FIN_EDGE = (0.60, 0.62, 0.54)
RAY = (0.14, 0.16, 0.15)

PROF = ef.Profile([
    (-0.80, 0.012, 0.012, 0.010, -0.008),
    (-0.76, 0.045, 0.036, 0.034, -0.008),
    (-0.68, 0.072, 0.058, 0.055, -0.004),
    (-0.56, 0.090, 0.078, 0.074, 0.000),
    (-0.42, 0.096, 0.090, 0.086, 0.002),
    (-0.22, 0.092, 0.094, 0.088, 0.002),
    (0.00, 0.078, 0.084, 0.078, 0.002),
    (0.20, 0.056, 0.062, 0.058, 0.002),
    (0.36, 0.036, 0.040, 0.037, 0.002),
    (0.55, 0.020, 0.022, 0.020, 0.002),
    (0.72, 0.010, 0.011, 0.010, 0.002),
    (0.80, 0.002, 0.003, 0.003, 0.002),
], power=lambda y: 2.6 if y < -0.45 else 2.1)

Y_HEAD = -0.44


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.20


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(HEAD, HEAD_TOP, nh.smoothstep(0.0, 0.9, v))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.3, -0.85, v) * 0.6)
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.74, 0.3), (-0.64, 0.25), (-0.54, 0.3), (-0.48, 0.9), (-0.56, 1.4), (-0.48, 1.8), (-0.66, 1.9)]
    c = nh.lerp(c, SUTURE, 0.6 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.06, width=0.010))
    c = nh.lerp(c, SUTURE, 0.8 * (1.0 - nh.smoothstep(0.004, 0.012, abs(co.y - (Y_HEAD - 0.015 - 0.02 * abs(v))))))
    return c


def scale_color(co, u, v):
    c = ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.35)
    return nh.lerp(c, (0.78, 0.78, 0.70), 0.3 * (1.0 - nh.smoothstep(0.03, 0.10, abs(v - 0.05))))


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.25 + 0.3 * t)


def fangs(mb):
    for s in (1, -1):
        for y, h, up in ((-0.770, 0.050, -1), (-0.752, 0.046, 1), (-0.71, 0.040, -1), (-0.69, 0.036, 1)):
            z = mouth_z(y)
            x = s * PROF.W(y) * 0.92
            mb.add(nh.tube([(x, y, z - up * 0.004), (x, y - 0.004, z + up * h)], [0.008, 0.0], sides=6), TOOTH)


def fins(mb):
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # single dorsal and anal fin far back, opposite each other
    df.web(mb, PROF, 0.22, 0.33, lambda u: (0.05 * u + 0.03, 0.085 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.22, 0.33, lambda u: (0.05 * u + 0.03, -0.085 * df.bump(u, 0.6, 0.15) - 0.006), rays(4),
           side=-1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.04, 0.12, lambda u: (0.04 * u + 0.02, 0.05 * df.bump(u, 0.6, 0.15) + 0.004), rays(3),
           side=1, n=ef.ray_cols(3), rows=2)
    # symmetrical three-lobed tail
    for side in (1, -1):
        df.web(mb, PROF, 0.42, 0.67,
               lambda u, s=side: (0.11 * u, s * (0.16 * df.bump(u, 0.9, 0.05) * (1 - 0.2 * u) + 0.005)), rays(8),
               side=side, n=ef.ray_cols(8), rows=3)
        df.web(mb, PROF, 0.655, 0.80, lambda u, s=side: (0.03, s * (0.045 * df.bump(u, 0.6) + 0.003)), rays(3),
               side=side, n=ef.ray_cols(3), rows=2)
    for s in (1, -1):
        df.lobed_fin(mb, PROF, s, -0.40, -0.9, (0.55, 0.65, -0.45), 0.22, 0.026, lobe_paint, rays(5),
                     web_w=0.055, cols=ef.ray_cols(5))
        df.lobed_fin(mb, PROF, s, 0.04, -1.25, (0.45, 0.8, -0.4), 0.15, 0.020, lobe_paint, rays(4),
                     web_w=0.04, cols=ef.ray_cols(4))


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=26, grow=0.004)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 48, 20, scale_color, lift=0.004, fade_y=(0.45, 0.75))
    fins(mb)
    ef.mouth_line(mb, PROF, -0.79, -0.55, mouth_z, MOUTH, grow=0.005)
    df.teeth(mb, PROF, -0.69, -0.57, mouth_z, 6, 0.012, TOOTH)
    fangs(mb)
    ef.surface_eye(mb, PROF, -0.66, 0.55, 0.022, (0.85, -0.3, 0.45), iris=(0.75, 0.62, 0.25))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
