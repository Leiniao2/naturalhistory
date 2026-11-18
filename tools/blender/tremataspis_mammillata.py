"""
Procedural Tremataspis mammillata for the map: an osteostracan, a jawless armoured fish
from the Late Silurian (Ludlow, about 425 million years ago) of Saaremaa, Estonia; about
8 cm long.

A tank among early fish: one solid, spindle-shaped bony box enclosing the head and the
front half of the body, rounded at the snout and tapering behind, with no horns (cornua)
and no paired fins at all. On top: the two small eyes close together, the pineal and
nasohypophysial openings in front of them, a long median ridge, and the osteostracan
lateral "sensory fields" as long, tile-covered strips inside both margins. The mamillate
(nipple-like) tubercles that give it its name cover the shield. Behind the box, a short
scaly trunk with a small dorsal fin and an upturned (epicercal) tail.

Adapted from cephalaspis_lyelli.py (nh_dev_fish.domed_slab + nh_early_fish scale lattice).
Colours are unknown: dark olive-grey shield with pale tubercles.

Usage:
  blender --background --python tools/blender/tremataspis_mammillata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TremataspisMammillata.fbx (Swim: pivot at the body
centre, facing -Y, shield up). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "TremataspisMammillata"

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
    (0.00, -0.80), (0.08, -0.79), (0.15, -0.76), (0.20, -0.71), (0.235, -0.63), (0.255, -0.53),
    (0.262, -0.42), (0.258, -0.30), (0.245, -0.18), (0.222, -0.06), (0.19, 0.04), (0.155, 0.11),
    (0.12, 0.15), (0.08, 0.16), (0.04, 0.16), (0.00, 0.16),
]
DOME = 0.11
RIM = 0.10
EYE_Y, EYE_X = -0.56, 0.036


def posterior(p):
    return p.y > 0.13 and abs(p.x) <= 0.125


def top_z(p, d):
    mid = 1.0 - nh.smoothstep(0.0, 0.26, abs(p.x))
    return DOME * df.rise(d, RIM) * (0.55 + 0.45 * mid)


def bot_z(p, d):
    deep = 0.45 + 0.5 * nh.smoothstep(-0.7, -0.4, p.y) * (1.0 - nh.smoothstep(0.10, 0.24, abs(p.x)))
    return -deep * DOME * nh.smoothstep(0.0, RIM * 1.2, d) ** 0.8


def field(p, d):
    """1 on the sensory fields: strips inside both side margins and one behind the eyes."""
    lat = (1.0 - nh.smoothstep(0.020, 0.032, abs(d - 0.05))) * nh.smoothstep(-0.72, -0.64, p.y) \
        * (1.0 - nh.smoothstep(-0.02, 0.06, p.y))
    return lat


def shield_color(p, d, top):
    if not top:
        return SHIELD_UNDER
    c = nh.lerp(SHIELD, SHIELD_DARK, 0.4 * nh.smoothstep(0.02, 0.15, d))
    c = nh.lerp(c, SHIELD_UNDER, 0.55 * df.tubercles(p, 120.0))
    f = field(p, d)
    if f > 0:
        c = nh.lerp(c, nh.lerp(FIELD, TILE, df.tesserae(p, 0.018, 0.25)), f)
    return c


TRUNK = ef.Profile([
    (0.08, 0.120, 0.075, 0.060, -0.004),
    (0.16, 0.105, 0.075, 0.055, -0.002),
    (0.30, 0.070, 0.060, 0.042, 0.006),
    (0.44, 0.044, 0.040, 0.030, 0.022),
    (0.58, 0.026, 0.024, 0.018, 0.050),
    (0.72, 0.012, 0.012, 0.009, 0.090),
    (0.84, 0.002, 0.003, 0.002, 0.130),
], power=2.4)


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.35)


def build():
    mb = nh.MeshBuilder()
    df.domed_slab(mb, HALF, top_z, bot_z, shield_color, spacing=0.03, posterior=posterior)
    # long low median ridge along the back of the box
    mb.add(nh.tube([(0, -0.44, DOME * 0.95), (0, -0.20, DOME + 0.012), (0, 0.04, DOME * 0.85 + 0.01),
                    (0, 0.15, DOME * 0.5)], [0.010, 0.014, 0.012, 0.0], sides=5), SHIELD_DARK)
    # eyes close together on top, pineal and nasohypophysial openings in front
    for s in (1, -1):
        z = top_z(Vector((s * EYE_X, EYE_Y)), 0.3)
        mb.add(nh.uv_ellipsoid((s * EYE_X, EYE_Y, z - 0.002), (0.026, 0.032, 0.012), 10, 5), SHIELD_DARK)
        ef.eye(mb, (s * EYE_X, EYE_Y, z + 0.002), (s * 0.4, -0.1, 0.9), 0.018, iris=(0.62, 0.52, 0.28))
    mb.add(nh.uv_ellipsoid((0, -0.57, top_z(Vector((0, -0.57)), 0.3)), (0.010, 0.022, 0.005), 8, 4), OPENING)
    ef.scale_shell(mb, TRUNK, 0.10, 0.84, 26, 14, scale_color, lift=0.003, fade_y=(0.50, 0.78))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, TRUNK, 0.24, 0.36, lambda u: (0.04 * u + 0.02, 0.05 * df.bump(u, 0.6, 0.2) + 0.005), rays(3),
           side=1, n=ef.ray_cols(3), rows=2)
    df.web(mb, TRUNK, 0.44, 0.84, lambda u: (0.07 * u, -(0.12 * df.bump(u, 0.8, 0.05) * (1 - 0.3 * u) + 0.004)),
           rays(7), side=-1, n=ef.ray_cols(7), rows=3)
    df.web(mb, TRUNK, 0.50, 0.84, lambda u: (0.02, 0.02 * df.bump(u, 0.6) + 0.003), rays(3),
           side=1, n=ef.ray_cols(3), rows=2)
    return df.finish(mb, NAME, roughness=0.5)


if __name__ == "__main__":
    nh.run(build, NAME, views=((35, 35), (-90, 8), (0, 80), (-150, 20)), background=df.PREVIEW["background"])
