"""
Procedural Eoporpita medusa (Ediacaran, South Australia), shown as the floating, Porpita-like
colony it was first described as: a round, flat disc with concentric rings and fine radial
ridges, a raised central boss, and a dense fringe of short radiating tentacles round the rim
with a second ring of shorter ones beneath. Blue-violet like the living blue button.
Float style: the disc sits on the water line (z = 0), tentacles spread just below.

Usage:
  blender --background --python tools/blender/eoporpita_medusa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eoporpita.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

DISC = (0.36, 0.46, 0.78)
RIDGE = (0.22, 0.28, 0.58)
BOSS = (0.70, 0.76, 0.92)
TENT = (0.30, 0.52, 0.92)
TENT2 = (0.55, 0.40, 0.80)
R = 0.42


def disc_color(co, n):
    rr = math.hypot(co.x, co.y) / R
    ring = math.sin(rr * 7 * math.pi) * 0.5 + 0.5
    rad = math.sin(math.atan2(co.y, co.x) * 36) * 0.5 + 0.5
    c = nh.lerp(DISC, RIDGE, 0.5 * nh.smoothstep(0.7, 1.0, ring) + 0.35 * nh.smoothstep(0.7, 1.0, rad) * rr)
    return nh.lerp(BOSS, c, nh.smoothstep(0.12, 0.3, rr))


def build():
    mb = nh.MeshBuilder()

    def deform(n):
        rr = math.hypot(n.x, n.y)
        return 1.0 + 0.03 * math.cos(rr * 7 * math.pi)
    disc = nh.uv_ellipsoid((0, 0, 0), (R, R, 0.05), segments=36, rings=12, deform=deform)
    mb.add(disc, disc_color)
    mb.add(nh.ellipsoid((0, 0, 0.04), (0.09, 0.09, 0.04), subdivisions=3), BOSS)
    kit.crown(mb, (0, 0, -0.01), R * 0.96, 48, 0.22, 0.014, TENT, up=(0, 0, 1), spread=95,
              droop=-0.25, seed=3, jitter=0.25)
    kit.crown(mb, (0, 0, -0.04), R * 0.7, 30, 0.16, 0.011, TENT2, up=(0, 0, -1), spread=60,
              droop=0.0, seed=5)
    obj = mb.to_object("Eoporpita", roughness=0.35)
    return obj


if __name__ == "__main__":
    ec.export(build, "Eoporpita", views=((35, 30), (-90, 6), (0, 80)))
