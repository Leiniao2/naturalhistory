"""
Procedural Hyneria lindae for the map: a giant tristichopterid lobe-finned fish from the
Late Devonian (Famennian, about 365 million years ago) Catskill Formation of Pennsylvania
(Red Hill); estimated 2.5-3 m long, the top predator of its rivers.

A heavy, deep-bodied relative of Eusthenopteron: a broad, blunt, rather short head with a
wide gape and big fangs at the front of the jaws, small eyes, a large sensory-canal system
on the skull, big rounded lobed pectoral fins, dorsal and anal fins set far back and a
broad, near-symmetrical tail. The trunk carries large round overlapping scales.

Built from nh_dev_fish / nh_early_fish pieces. Colours are unknown: dark greenish-brown
with a paler belly.

Usage:
  blender --background --python tools/blender/hyneria_lindae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hyneria.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Hyneria"

BACK = (0.16, 0.18, 0.13)
FLANK = (0.34, 0.36, 0.26)
BELLY = (0.74, 0.72, 0.58)
BLOTCH = (0.10, 0.11, 0.08)
HEAD = (0.32, 0.32, 0.23)
HEAD_TOP = (0.20, 0.21, 0.15)
PIT = (0.08, 0.08, 0.06)
MOUTH = (0.09, 0.05, 0.04)
GUM = (0.45, 0.20, 0.17)
TOOTH = (0.94, 0.90, 0.80)
FIN = (0.26, 0.27, 0.19)
FIN_EDGE = (0.48, 0.48, 0.34)
RAY = (0.12, 0.13, 0.09)

PROF = ef.Profile([
    (-0.80, 0.030, 0.040, 0.030, -0.020),
    (-0.77, 0.090, 0.090, 0.075, -0.015),
    (-0.70, 0.140, 0.135, 0.120, -0.008),
    (-0.58, 0.170, 0.170, 0.155, 0.000),
    (-0.42, 0.175, 0.190, 0.175, 0.006),
    (-0.22, 0.160, 0.185, 0.170, 0.008),
    (0.00, 0.128, 0.155, 0.142, 0.008),
    (0.20, 0.088, 0.110, 0.100, 0.008),
    (0.36, 0.056, 0.070, 0.064, 0.008),
    (0.55, 0.030, 0.036, 0.033, 0.008),
    (0.72, 0.012, 0.014, 0.013, 0.008),
    (0.80, 0.002, 0.003, 0.003, 0.008),
], power=lambda y: 2.4 if y < -0.45 else 2.15)

Y_HEAD = -0.50


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.30


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(HEAD, HEAD_TOP, nh.smoothstep(0.0, 0.9, v))
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.35, -0.85, v) * 0.6)
    # big sensory pits of the canal system, in lines over the skull
    pit = nh.smoothstep(0.30, 0.50, ef.mottle(co, 26.0, 4.0))
    c = nh.lerp(c, PIT, 0.6 * pit)
    c = nh.lerp(c, PIT, 0.8 * (1.0 - nh.smoothstep(0.005, 0.014, abs(co.y - (Y_HEAD - 0.015 - 0.025 * abs(v))))))
    if co.y < -0.56 and abs(u) > 0.4:
        c = nh.lerp(c, GUM, 0.7 * (1.0 - nh.smoothstep(0.006, 0.016, abs(co.z - mouth_z(co.y)))))
    return c


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.5)


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.3 + 0.3 * t)


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=28, grow=0.005)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 36, 18, scale_color, lift=0.006, shine=0.18,
                   fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, PROF, 0.02, 0.14, lambda u: (0.05 * u + 0.03, 0.09 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.24, 0.36, lambda u: (0.05 * u + 0.03, 0.08 * df.bump(u, 0.6, 0.15) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.22, 0.36, lambda u: (0.05 * u + 0.03, -0.09 * df.bump(u, 0.6, 0.15) - 0.006), rays(4),
           side=-1, n=ef.ray_cols(4), rows=2)
    for side in (1, -1):
        df.web(mb, PROF, 0.42, 0.80,
               lambda u, s=side: (0.10 * u, s * (0.17 * df.bump(u, 0.8, 0.05) * (1 - 0.3 * u) + 0.005)), rays(9),
               side=side, n=ef.ray_cols(9), rows=3)
    for s in (1, -1):
        df.lobed_fin(mb, PROF, s, -0.44, -0.85, (0.6, 0.6, -0.5), 0.30, 0.045, lobe_paint, rays(6),
                     web_w=0.09, cols=ef.ray_cols(6))
        df.lobed_fin(mb, PROF, s, 0.04, -1.2, (0.45, 0.8, -0.4), 0.18, 0.030, lobe_paint, rays(4),
                     web_w=0.05, cols=ef.ray_cols(4))
    ef.mouth_line(mb, PROF, -0.795, -0.56, mouth_z, MOUTH, r=0.006, grow=0.006)
    # big fangs at the front of both jaws, small teeth behind
    df.teeth(mb, PROF, -0.785, -0.74, mouth_z, 2, 0.045, TOOTH, r=0.012)
    df.teeth(mb, PROF, -0.775, -0.735, lambda y: mouth_z(y) - 0.006, 1, 0.035, TOOTH, r=0.010, up=1)
    df.teeth(mb, PROF, -0.73, -0.58, mouth_z, 6, 0.016, TOOTH)
    ef.surface_eye(mb, PROF, -0.69, 0.55, 0.022, (0.85, -0.3, 0.4), iris=(0.62, 0.50, 0.20))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
