"""
Procedural Cephalaspis lyelli for the map: an osteostracan, a jawless armoured fish from
the Early Devonian (Lochkovian, about 415 million years ago) Old Red Sandstone of Scotland
(Forfarshire); about 20-25 cm long. Described by Louis Agassiz in 1835 and named for the
geologist Charles Lyell, it is the classic "head-shield" fish.

A flat, horseshoe-shaped bony head shield, rounded in front and drawn out at the back
corners into long backward-pointing horns (cornua), with the two small eyes close
together near the middle of the top, a tiny nostril-and-pineal opening between and in
front of them, and the osteostracan "sensory fields" - shallow, tile-covered depressions
along both side margins and one behind the eyes, perhaps electric or pressure organs. It
had no jaws (a small mouth underneath for sucking up food from the bottom), a pair of
flap-like pectoral fins behind the horns - osteostracans were the first fishes with
paired fins - and a trunk of tall, narrow scales with one dorsal fin and an upturned
(epicercal) tail.

Shield: nh_dev_fish.domed_slab; trunk: nh_early_fish scale lattice. Colours are unknown:
sandy brown shield, darker trunk.

Usage:
  blender --background --python tools/blender/cephalaspis_lyelli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cephalaspis.fbx (Swim: pivot at the body centre,
facing -Y, shield up). About 1.6 units long.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_dev_fish as df  # noqa: E402

NAME = "Cephalaspis"

SHIELD = (0.66, 0.54, 0.36)
SHIELD_DARK = (0.42, 0.33, 0.21)
SHIELD_UNDER = (0.80, 0.74, 0.60)
FIELD = (0.26, 0.20, 0.13)
TILE = (0.52, 0.42, 0.28)
OPENING = (0.05, 0.04, 0.03)
BACK = (0.26, 0.20, 0.13)
FLANK = (0.48, 0.38, 0.25)
BELLY = (0.80, 0.72, 0.56)
BLOTCH = (0.18, 0.13, 0.08)
FIN = (0.40, 0.32, 0.22)
FIN_EDGE = (0.64, 0.54, 0.38)
RAY = (0.22, 0.16, 0.10)

HALF = [
    (0.00, -0.80), (0.10, -0.795), (0.19, -0.765), (0.26, -0.715), (0.31, -0.65), (0.345, -0.56),
    (0.365, -0.46), (0.375, -0.36), (0.38, -0.26), (0.385, -0.16), (0.39, -0.06),
    (0.395, 0.04),                                   # cornual tip
    (0.37, 0.00), (0.345, -0.08), (0.32, -0.16), (0.29, -0.24), (0.25, -0.28),
    (0.20, -0.29), (0.15, -0.285), (0.10, -0.28), (0.05, -0.30), (0.00, -0.31),
]
DOME = 0.085
RIM = 0.10
EYE_Y, EYE_X = -0.50, 0.040


def posterior(p):
    return p.y > -0.32 and abs(p.x) <= 0.12


def top_z(p, d):
    mid = 1.0 - nh.smoothstep(0.0, 0.30, abs(p.x))
    return DOME * df.rise(d, RIM) * (0.45 + 0.55 * mid)


def bot_z(p, d):
    deep = 0.25 + 0.7 * nh.smoothstep(-0.6, -0.3, p.y) * (1.0 - nh.smoothstep(0.08, 0.20, abs(p.x)))
    return -deep * DOME * nh.smoothstep(0.0, RIM * 1.2, d) ** 0.8


def field(p, d):
    """1 on the sensory fields: strips inside both side margins and one behind the eyes."""
    lat = (1.0 - nh.smoothstep(0.030, 0.045, abs(d - 0.06))) * nh.smoothstep(-0.70, -0.62, p.y) \
        * (1.0 - nh.smoothstep(-0.22, -0.15, p.y))
    med = (1.0 - nh.smoothstep(0.020, 0.032, abs(p.x))) * nh.smoothstep(-0.46, -0.44, p.y) \
        * (1.0 - nh.smoothstep(-0.34, -0.32, p.y))
    return max(lat, med)


def shield_color(p, d, top):
    if not top:
        return SHIELD_UNDER
    c = nh.lerp(SHIELD, SHIELD_DARK, 0.4 * nh.smoothstep(0.02, 0.15, d))
    c = nh.lerp(c, SHIELD_UNDER, 0.35 * df.tubercles(p, 70.0))
    f = field(p, d)
    if f > 0:
        c = nh.lerp(c, nh.lerp(FIELD, TILE, df.tesserae(p, 0.018, 0.25)), f)
    return c


TRUNK = ef.Profile([
    (-0.40, 0.100, 0.060, 0.050, -0.004),
    (-0.26, 0.105, 0.080, 0.060, -0.006),
    (-0.10, 0.090, 0.090, 0.060, -0.006),
    (0.10, 0.068, 0.078, 0.052, 0.002),
    (0.30, 0.044, 0.052, 0.036, 0.020),
    (0.48, 0.026, 0.030, 0.022, 0.055),
    (0.66, 0.012, 0.014, 0.010, 0.105),
    (0.80, 0.002, 0.003, 0.002, 0.150),
], power=lambda y: 2.8 if y < 0.0 else 2.2)


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.35)


def build():
    mb = nh.MeshBuilder()
    df.domed_slab(mb, HALF, top_z, bot_z, shield_color, spacing=0.03, posterior=posterior)
    # low median crest at the back of the shield
    mb.add(nh.tube([(0, -0.40, top_z(Vector((0, -0.4)), 0.2) - 0.01), (0, -0.30, DOME + 0.02),
                    (0, -0.26, DOME + 0.02)], [0.010, 0.016, 0.0], sides=5), SHIELD_DARK)
    # eyes close together on top, pineal and nasohypophysial openings in front
    for s in (1, -1):
        z = top_z(Vector((s * EYE_X, EYE_Y)), 0.3)
        mb.add(nh.uv_ellipsoid((s * EYE_X, EYE_Y, z - 0.002), (0.026, 0.032, 0.012), 10, 5), SHIELD_DARK)
        ef.eye(mb, (s * EYE_X, EYE_Y, z + 0.002), (s * 0.4, -0.1, 0.9), 0.018, iris=(0.62, 0.52, 0.28))
    mb.add(nh.uv_ellipsoid((0, -0.57, top_z(Vector((0, -0.57)), 0.3)), (0.010, 0.022, 0.005), 8, 4), OPENING)
    ef.scale_shell(mb, TRUNK, -0.30, 0.80, 30, 14, scale_color, lift=0.003, fade_y=(0.45, 0.75))
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    df.web(mb, TRUNK, 0.08, 0.24, lambda u: (0.06 * u + 0.03, 0.08 * df.bump(u, 0.6, 0.2) + 0.005), rays(4),
           side=1, n=ef.ray_cols(4), rows=2)
    df.web(mb, TRUNK, 0.36, 0.80, lambda u: (0.08 * u, -(0.15 * df.bump(u, 0.8, 0.05) * (1 - 0.3 * u) + 0.004)),
           rays(8), side=-1, n=ef.ray_cols(8), rows=3)
    df.web(mb, TRUNK, 0.40, 0.80, lambda u: (0.02, 0.025 * df.bump(u, 0.6) + 0.003), rays(3),
           side=1, n=ef.ray_cols(3), rows=2)
    for s in (1, -1):
        # flap-like pectoral fins in the notch between horn and trunk
        base = [(s * (0.12 + 0.02 * k / 5), -0.30 + 0.06 * k / 5, -0.02) for k in range(6)]
        edge = [(s * (0.27 + 0.03 * math.sin(math.pi * k / 5)), -0.18 + 0.05 * k / 5, -0.04) for k in range(6)]
        import nh_fish as fish
        fish.fin(mb, base, edge, rays(3), rows=2, th0=0.008, th1=0.003)
    return df.finish(mb, NAME, roughness=0.5)


if __name__ == "__main__":
    nh.run(build, NAME, views=((35, 35), (-90, 8), (0, 80), (-150, 20)), background=df.PREVIEW["background"])
