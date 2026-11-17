"""
Procedural Pteraspis rostrata for the map: a pteraspid heterostracan, a jawless armoured
fish from the Early Devonian (Lochkovian-Pragian, about 415-410 million years ago) of
Britain and western Europe; about 20 cm long.

Built for active swimming rather than bottom grubbing: the front half of the body is
enclosed in a streamlined, spindle-shaped box of a few large plates, drawn out in front
into a long pointed rostrum overhanging the jawless mouth, with a stout dorsal spine at
the back of the shield and a pair of wing-like cornual plates sticking out sideways and
back from the flanks (perhaps acting as stabilisers, like the wings of a missile). The
small eyes are set in notches on the sides of the shield. Behind it a scale-covered
trunk ends in a hypocercal tail, whose body axis bends down into the lower lobe.

Lofted shield and trunk (nh_dev_fish / nh_early_fish). Colours are unknown: glossy
blue-grey dentine armour with fine growth ridges, a darker trunk.

Usage:
  blender --background --python tools/blender/pteraspis_rostrata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pteraspis.fbx (Swim: pivot at the body centre,
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
import nh_fish as fish  # noqa: E402

NAME = "Pteraspis"

PLATE = (0.48, 0.52, 0.56)
PLATE_DARK = (0.26, 0.29, 0.33)
RIDGE = (0.66, 0.70, 0.72)
SUTURE = (0.12, 0.13, 0.15)
BELLY = (0.78, 0.78, 0.74)
BACK = (0.20, 0.22, 0.25)
FLANK = (0.38, 0.40, 0.42)
BLOTCH = (0.14, 0.15, 0.17)
FIN = (0.30, 0.32, 0.35)
FIN_EDGE = (0.56, 0.58, 0.60)
RAY = (0.16, 0.17, 0.19)
MOUTH = (0.06, 0.05, 0.05)

PROF = ef.Profile([
    (-0.80, 0.004, 0.004, 0.004, 0.010),
    (-0.70, 0.022, 0.020, 0.018, 0.006),
    (-0.60, 0.060, 0.050, 0.046, 0.000),
    (-0.48, 0.095, 0.085, 0.075, 0.000),
    (-0.32, 0.115, 0.110, 0.095, 0.004),
    (-0.16, 0.112, 0.112, 0.092, 0.006),
    (-0.02, 0.090, 0.090, 0.072, 0.000),
    (0.14, 0.060, 0.062, 0.050, -0.010),
    (0.30, 0.040, 0.040, 0.034, -0.024),
    (0.46, 0.024, 0.024, 0.020, -0.045),
    (0.64, 0.010, 0.011, 0.009, -0.085),
    (0.80, 0.002, 0.002, 0.002, -0.120),
], power=lambda y: 2.4 if y < 0.0 else 2.1)

Y_SHIELD = -0.04


def shield_color(co, u, v):
    c = nh.lerp(PLATE, PLATE_DARK, 0.5 * nh.smoothstep(0.1, 0.9, v))
    c = nh.lerp(c, BELLY, 0.6 * nh.smoothstep(-0.2, -0.8, v))
    # fine growth ridges running along the plates
    r = 0.5 + 0.5 * math.sin((v * 1.0 + u * 0.2) * 70.0)
    c = nh.lerp(c, RIDGE, 0.25 * nh.smoothstep(0.7, 1.0, r))
    # plate boundaries: rostral, orbital/dorsal disc, branchial plates
    phi = ef.phi_of(PROF, co)
    seeds = [(-0.66, 0.5), (-0.30, 0.0), (-0.30, 1.4), (-0.30, 2.6)]
    return nh.lerp(c, SUTURE, 0.7 * ef.plates(seeds, co.y, phi, sy=1.0, sphi=0.08, width=0.012))


def scale_color(co, u, v):
    return ef.countershade(v, BACK, FLANK, BELLY, co, BLOTCH, 0.3)


def build():
    mb = nh.MeshBuilder()
    df.skin(mb, PROF, PROF.y0, Y_SHIELD, shield_color, ny=36, na=28, grow=0.003, cap1=False)
    ef.scale_shell(mb, PROF, Y_SHIELD - 0.01, 0.78, 32, 16, scale_color, lift=0.003, fade_y=(0.45, 0.75))
    # dorsal spine at the back of the shield
    base = Vector((0.0, -0.12, PROF.top(-0.12) - 0.004))
    ef.spine(mb, base, base + Vector((0.0, 0.17, 0.10)), 0.022, PLATE, PLATE_DARK, sides=6)
    # cornual plates: flat wings sticking out sideways and back
    for s in (1, -1):
        b = [(s * PROF.W(y) * 0.95, y, PROF.CZ(y) - 0.01) for y in [-0.28 + 0.16 * k / 5 for k in range(6)]]
        e = [(s * (PROF.W(-0.28) + 0.03 + 0.10 * (k / 5) ** 1.3), -0.24 + 0.22 * k / 5, PROF.CZ(-0.2) - 0.02)
             for k in range(6)]
        fish.fin(mb, b, e, lambda u, v, co: nh.lerp(PLATE, PLATE_DARK, 0.4 * v), rows=2, th0=0.016, th1=0.006)
    rays = lambda n: ef.ray_color(FIN, RAY, FIN_EDGE, n)  # noqa: E731
    # hypocercal tail: axis bends down, broad web above, lobe below
    df.web(mb, PROF, 0.34, 0.80, lambda u: (0.10 * u, 0.16 * df.bump(u, 0.8, 0.05) * (1 - 0.3 * u) + 0.004),
           rays(8), side=1, n=ef.ray_cols(8), rows=3)
    df.web(mb, PROF, 0.40, 0.80, lambda u: (0.02, -(0.03 * df.bump(u, 0.6) + 0.003)), rays(3),
           side=-1, n=ef.ray_cols(3), rows=2)
    # mouth under the rostrum
    pts = [(x, -0.57 + 2.0 * x * x, PROF.bot(-0.57) + 0.004) for x in [-0.04 + 0.08 * k / 6 for k in range(7)]]
    mb.add(nh.tube(pts, [0.003] + [0.006] * 5 + [0.003], sides=5), MOUTH)
    ef.surface_eye(mb, PROF, -0.50, 0.15, 0.018, (0.95, -0.2, 0.15), iris=(0.60, 0.55, 0.35))
    return df.finish(mb, NAME, roughness=0.35)


if __name__ == "__main__":
    nh.run(build, NAME, **df.PREVIEW)
