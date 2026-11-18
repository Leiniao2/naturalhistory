"""
Procedural Griphognathus whitei for the map: a lungfish from the Late Devonian (Frasnian,
about 380 million years ago) Gogo reef of Western Australia; roughly half a metre long.

An odd, long-snouted lungfish: the front of the skull was drawn out into a long, flat,
duck-bill-like snout, and instead of the tooth plates of other lungfishes the palate and
lower jaw were paved with small denticles for crushing and grinding prey picked off the
reef. The body was clad in thick, shiny cosmine-covered scales, with two dorsal fins set
far back, leaf-shaped lobed paired fins and a tail with a long lower lobe.

Bony head + rhombic scale lattice (nh_early_fish) with fin webs and lobes (nh_dev_fish),
built like dipterus_valenciennesi.py with the long bill in the profile. Colours are
unknown: warm brown with darker mottling, glossy bronze cosmine on the head.

Usage:
  blender --background --python tools/blender/griphognathus_whitei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Griphognathus.fbx (Swim: pivot at the body centre,
facing -Y). About 1.6 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Griphognathus"

BACK = (0.30, 0.20, 0.11)
FLANK = (0.60, 0.44, 0.26)
BELLY = (0.90, 0.80, 0.62)
BLOTCH = (0.18, 0.11, 0.06)
COSMINE = (0.78, 0.60, 0.36)
COSMINE_TOP = (0.46, 0.33, 0.18)
PORE = (0.22, 0.14, 0.07)
MOUTH = (0.10, 0.06, 0.04)
FIN = (0.40, 0.28, 0.16)
FIN_EDGE = (0.68, 0.52, 0.32)
RAY = (0.20, 0.13, 0.07)

PROF = ef.Profile([
    (-0.80, 0.030, 0.012, 0.010, -0.040),
    (-0.78, 0.048, 0.018, 0.016, -0.040),
    (-0.72, 0.058, 0.024, 0.020, -0.038),
    (-0.64, 0.064, 0.034, 0.028, -0.032),
    (-0.56, 0.082, 0.062, 0.050, -0.020),
    (-0.48, 0.120, 0.120, 0.105, -0.004),
    (-0.38, 0.140, 0.165, 0.150, 0.004),
    (-0.20, 0.138, 0.170, 0.155, 0.008),
    (0.02, 0.110, 0.140, 0.126, 0.014),
    (0.20, 0.076, 0.096, 0.086, 0.026),
    (0.36, 0.046, 0.058, 0.052, 0.050),
    (0.54, 0.024, 0.028, 0.025, 0.095),
    (0.70, 0.010, 0.012, 0.010, 0.140),
    (0.80, 0.002, 0.003, 0.003, 0.170),
], power=lambda y: 2.8 if y < -0.55 else (2.3 if y < -0.4 else 2.1))

Y_HEAD = -0.36


def mouth_z(y):
    return PROF.CZ(y) - PROF.HB(y) * 0.5


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
    rays = ef.ray_color(FIN, RAY, FIN_EDGE, cols)
    df.lobed_fin(mb, PROF, s, y, angle, direction, length, r0, lobe_paint, rays,
                 web_w=0.035, lead_w=0.030, lobe_frac=0.85, cols=ef.ray_cols(cols))


def build():
    mb = nh.MeshBuilder()
    ef.head_shell(mb, PROF, Y_HEAD, head_color, ny=24, na=28, grow=0.005)
    ef.scale_shell(mb, PROF, Y_HEAD - 0.02, 0.78, 34, 18, scale_color, lift=0.006, shine=0.35,
                   fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, PROF, 0.06, 0.18, lambda u: (0.05 * u + 0.04, 0.10 * df.bump(u, 0.6, 0.2) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.28, 0.42, lambda u: (0.05 * u + 0.04, 0.09 * df.bump(u, 0.6, 0.2) + 0.006), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.26, 0.40, lambda u: (0.05 * u + 0.04, -0.09 * df.bump(u, 0.6, 0.2) - 0.006), rays(4),
           side=-1, n=ef.ray_cols(4), rows=2)
    df.web(mb, PROF, 0.44, 0.80, lambda u: (0.08 * u, -(0.14 * df.bump(u, 0.8, 0.05) * (1 - 0.3 * u) + 0.005)),
           rays(8), side=-1, n=ef.ray_cols(8), rows=3)
    df.web(mb, PROF, 0.46, 0.80, lambda u: (0.02, 0.03 * df.bump(u, 0.6) + 0.003), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    for s in (1, -1):
        leaf(mb, s, -0.30, -0.95, (0.5, 0.7, -0.5), 0.26, 0.030, 5)
        leaf(mb, s, 0.06, -1.25, (0.4, 0.85, -0.4), 0.20, 0.024, 4)
    ef.mouth_line(mb, PROF, -0.795, -0.52, mouth_z, MOUTH, grow=0.004)
    ef.surface_eye(mb, PROF, -0.47, 0.55, 0.028, (0.85, -0.3, 0.4), iris=(0.72, 0.56, 0.22))
    return df.finish(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
