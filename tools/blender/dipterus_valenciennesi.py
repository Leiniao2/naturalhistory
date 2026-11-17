"""
Procedural Dipterus valenciennesi for the map: one of the earliest well-known lungfishes
(Dipnoi), from the Middle Devonian (Givetian, about 385 million years ago) lake beds of
the Orcadian Basin, Scotland; about 35 cm long.

A stout, blunt-snouted fish with the mouth underneath, crushing tooth plates instead of
marginal teeth, a head covered in shiny cosmine, two dorsal fins on the back half of the
body (hence "Dipterus", two-winged), an anal fin and a heterocercal tail. Its pectoral
and pelvic fins are the lungfish "archipterygium": long, pointed leaf shapes with a
scaled central lobe fringed by fin rays on both sides. Like modern lungfish it could
gulp air.

Built from nh_dev_fish / nh_early_fish pieces. Colours are unknown: mottled olive-brown,
paler below.

Usage:
  blender --background --python tools/blender/dipterus_valenciennesi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dipterus.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Dipterus"

BACK = (0.26, 0.24, 0.14)
FLANK = (0.52, 0.48, 0.30)
BELLY = (0.86, 0.80, 0.62)
BLOTCH = (0.16, 0.14, 0.08)
COSMINE = (0.66, 0.58, 0.40)
COSMINE_TOP = (0.40, 0.36, 0.22)
PORE = (0.20, 0.17, 0.10)
MOUTH = (0.10, 0.07, 0.05)
FIN = (0.36, 0.32, 0.20)
FIN_EDGE = (0.62, 0.56, 0.38)
RAY = (0.18, 0.16, 0.10)

PROF = ef.Profile([
    (-0.80, 0.030, 0.040, 0.030, -0.010),
    (-0.78, 0.080, 0.090, 0.070, -0.008),
    (-0.72, 0.120, 0.135, 0.110, -0.004),
    (-0.60, 0.150, 0.175, 0.150, 0.000),
    (-0.42, 0.160, 0.195, 0.175, 0.004),
    (-0.20, 0.145, 0.185, 0.165, 0.008),
    (0.02, 0.112, 0.145, 0.130, 0.014),
    (0.20, 0.076, 0.098, 0.088, 0.026),
    (0.36, 0.046, 0.058, 0.052, 0.050),
    (0.54, 0.024, 0.028, 0.025, 0.095),
    (0.70, 0.010, 0.012, 0.010, 0.140),
    (0.80, 0.002, 0.003, 0.003, 0.170),
], power=lambda y: 2.3 if y < -0.5 else 2.1)

Y_HEAD = -0.54


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.75


def head_color(co, n):
    u, v = PROF.rel(co)
    c = nh.lerp(COSMINE, COSMINE_TOP, nh.smoothstep(0.0, 0.9, v) * 0.7)
    c = nh.lerp(c, BELLY, nh.smoothstep(-0.4, -0.9, v) * 0.5)
    c = nh.lerp(c, PORE, 0.45 * nh.smoothstep(0.15, 0.40, ef.mottle(co, 30.0, 2.0)))
    c = nh.lerp(c, PORE, 0.8 * (1.0 - nh.smoothstep(0.005, 0.013, abs(co.y - (Y_HEAD - 0.015 - 0.025 * abs(v))))))
    return c


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.65)


def lobe_paint(t, co):
    return nh.lerp(FLANK, BACK, 0.25 + 0.3 * t)


def leaf(mb, s, y, angle, direction, length, r0, cols):
    """Archipterygium: scaled central lobe with rays fringing both edges about equally."""
    rays = ef.ray_color(FIN, RAY, FIN_EDGE, cols)
    df.lobed_fin(mb, PROF, s, y, angle, direction, length, r0, lobe_paint, rays,
                 web_w=0.035, lead_w=0.030, lobe_frac=0.85, cols=ef.ray_cols(cols))


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=16, na=28, grow=0.005)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 34, 18, scale_color, lift=0.005, fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # two dorsal fins on the back half, the second close to the tail
    df.web(mb, PROF, 0.02, 0.15, lambda u: (0.05 * u + 0.04, 0.10 * df.bump(u, 0.6, 0.2) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.26, 0.40, lambda u: (0.05 * u + 0.04, 0.09 * df.bump(u, 0.6, 0.2) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.24, 0.38, lambda u: (0.05 * u + 0.04, -0.09 * df.bump(u, 0.6, 0.2) - 0.006), rays(4),
           side=-1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.42, 0.80, lambda u: (0.08 * u, -(0.15 * df.bump(u, 0.8, 0.05) * (1 - 0.3 * u) + 0.005)),
           rays(8), side=-1, n=ef.ray_cols(8), rows=3)
    df.web(mb, PROF, 0.44, 0.80, lambda u: (0.02, 0.03 * df.bump(u, 0.6) + 0.003), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    for s in (1, -1):
        leaf(mb, s, -0.48, -0.95, (0.5, 0.7, -0.5), 0.28, 0.030, 5)
        leaf(mb, s, 0.00, -1.25, (0.4, 0.85, -0.4), 0.22, 0.024, 4)
    ef.mouth_line(mb, PROF, -0.78, -0.70, mouth_z, MOUTH, grow=0.005)
    ef.surface_eye(mb, PROF, -0.68, 0.40, 0.022, (0.9, -0.3, 0.3), iris=(0.70, 0.56, 0.24))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
