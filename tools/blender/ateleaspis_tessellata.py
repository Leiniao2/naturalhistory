"""
Procedural Ateleaspis tessellata for the map: one of the most primitive osteostracans
(jawless armoured fish), about 20 cm long, from the Silurian (Wenlock-Ludlow) of
Scotland and Norway.

Unlike Tremataspis it has a low, broad, horseshoe-shaped head shield covering only the
head, with rounded back corners and no horns; its surface is a mosaic of small
polygonal bony tiles (tesserae), which gives the species its name. Eyes close
together on top, a median opening in front of them, sensory fields along the margins
and between the eyes. Behind the shield: a pair of flap-like pectoral fins (the oldest
true paired fins), a long trunk of rhombic scales, two dorsal fins and an upturned
(epicercal) tail.

Adapted from tremataspis_mammillata.py (nh_dev_fish.domed_slab + nh_early_fish).
Colours are unknown: brown-olive shield with pale tile edges.

Usage:
  blender --background --python tools/blender/ateleaspis_tessellata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AteleaspisTessellata.fbx (Swim: pivot at the body
centre, facing -Y, shield up).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "AteleaspisTessellata"

SHIELD = (0.36, 0.38, 0.30)
SHIELD_DARK = (0.20, 0.22, 0.17)
SHIELD_UNDER = (0.82, 0.80, 0.68)
FIELD = (0.14, 0.15, 0.11)
TILE = (0.46, 0.48, 0.38)
OPENING = (0.05, 0.04, 0.03)
BACK = (0.20, 0.21, 0.16)
FLANK = (0.40, 0.41, 0.32)
BELLY = (0.80, 0.72, 0.56)
BLOTCH = (0.18, 0.13, 0.08)
FIN = (0.40, 0.32, 0.22)
FIN_EDGE = (0.64, 0.54, 0.38)
RAY = (0.22, 0.16, 0.10)

HALF = [
    (0.00, -0.80), (0.08, -0.79), (0.16, -0.76), (0.23, -0.71), (0.28, -0.64), (0.31, -0.56),
    (0.325, -0.48), (0.325, -0.40), (0.315, -0.33), (0.29, -0.28), (0.25, -0.255), (0.20, -0.26),
    (0.15, -0.28), (0.11, -0.29), (0.05, -0.29), (0.00, -0.29),
]
DOME = 0.08
RIM = 0.12
EYE_Y, EYE_X = -0.58, 0.040


def posterior(p):
    return p.y > -0.30 and abs(p.x) <= 0.12


def top_z(p, d):
    mid = 1.0 - nh.smoothstep(0.0, 0.26, abs(p.x))
    return DOME * df.rise(d, RIM) * (0.55 + 0.45 * mid)


def bot_z(p, d):
    deep = 0.40 + 0.6 * nh.smoothstep(-0.65, -0.40, p.y) * (1.0 - nh.smoothstep(0.08, 0.20, abs(p.x)))
    return -deep * DOME * nh.smoothstep(0.0, RIM * 1.2, d) ** 0.8


def field(p, d):
    """1 on the sensory fields: strips inside both side margins and one behind the eyes."""
    lat = (1.0 - nh.smoothstep(0.016, 0.026, abs(d - 0.04))) * nh.smoothstep(-0.70, -0.62, p.y) \
        * (1.0 - nh.smoothstep(-0.36, -0.30, p.y))
    med = (1.0 - nh.smoothstep(0.02, 0.03, abs(p.x))) * nh.smoothstep(-0.54, -0.50, p.y) \
        * (1.0 - nh.smoothstep(-0.40, -0.36, p.y))
    return max(lat, med)


def shield_color(p, d, top):
    if not top:
        return SHIELD_UNDER
    c = nh.lerp(SHIELD, SHIELD_DARK, 0.4 * nh.smoothstep(0.02, 0.15, d))
    c = nh.lerp(c, TILE, 0.9 * df.tesserae(p, 0.04, 0.22))
    f = field(p, d)
    if f > 0:
        c = nh.lerp(c, nh.lerp(FIELD, TILE, df.tesserae(p, 0.018, 0.25)), f)
    return c


TRUNK = ef.Profile([
    (-0.36, 0.115, 0.070, 0.055, -0.004),
    (-0.26, 0.110, 0.072, 0.055, -0.002),
    (-0.05, 0.085, 0.066, 0.048, 0.004),
    (0.20, 0.058, 0.050, 0.038, 0.014),
    (0.42, 0.036, 0.034, 0.026, 0.030),
    (0.62, 0.018, 0.018, 0.013, 0.060),
    (0.84, 0.002, 0.003, 0.002, 0.110),
], power=2.4)


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.35)


def build():
    mb = nh.MeshBuilder()
    df.domed_slab(mb, HALF, top_z, bot_z, shield_color, spacing=0.03, posterior=posterior)
    # long low median ridge along the back of the box
    # eyes close together on top, pineal and nasohypophysial openings in front
    for s in (1, -1):
        z = top_z(Vector((s * EYE_X, EYE_Y)), 0.3)
        mb.add(nh.uv_ellipsoid((s * EYE_X, EYE_Y, z - 0.002), (0.026, 0.032, 0.012), 10, 5), SHIELD_DARK)
        ef.eye(mb, (s * EYE_X, EYE_Y, z + 0.002), (s * 0.4, -0.1, 0.9), 0.018, iris=(0.62, 0.52, 0.28))
    mb.add(nh.uv_ellipsoid((0, -0.66, top_z(Vector((0, -0.66)), 0.3)), (0.010, 0.022, 0.005), 8, 4), OPENING)
    ef.scale_shell(mb, TRUNK, -0.32, 0.84, 34, 14, scale_color, lift=0.003, fade_y=(0.52, 0.80))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # two dorsal fins
    df.web(mb, TRUNK, -0.12, 0.02, lambda u: (0.04 * u + 0.02, 0.06 * df.bump(u, 0.6, 0.2) + 0.005), rays(3),
           side=1, n=ef.ray_cols(3), rows=2)
    df.web(mb, TRUNK, 0.26, 0.38, lambda u: (0.03 * u + 0.02, 0.05 * df.bump(u, 0.6, 0.2) + 0.005), rays(3),
           side=1, n=ef.ray_cols(3), rows=2)
    # epicercal tail: web below the up-turned axis
    df.web(mb, TRUNK, 0.46, 0.84, lambda u: (0.07 * u, -(0.12 * df.bump(u, 0.8, 0.05) * (1 - 0.3 * u) + 0.004)),
           rays(7), side=-1, n=ef.ray_cols(7), rows=3)
    # flap-like pectoral fins just behind the shield corners
    for s in (1, -1):
        ef.paired_fin(mb, TRUNK, s, -0.30, -0.14, -0.25, lambda u: 0.13 * (1 - u) ** 0.5 + 0.01,
                      1.0, 0.15, 0.7, rays(4), cols=ef.ray_cols(4), rows=2)
    return df.finish(mb, NAME, roughness=0.5)


if __name__ == "__main__":
    nh.run(build, NAME, views=((35, 35), (-90, 8), (0, 80), (-150, 20)), background=df.PREVIEW["background"])
