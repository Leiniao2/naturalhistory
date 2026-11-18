"""
Procedural Siphusauctum gregarium (Burgess Shale "tulip animal", up to 20 cm).

A long, slender, slightly bending stalk rising from a small rounded holdfast, crowned by a
tulip-shaped calyx with six faint longitudinal lobes (marking the six comb-like filter
plates inside) and a small raised opening at the top. Pale greenish cream calyx with
darker lobe lines and a ringed stalk. Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/siphusauctum_gregarium.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Siphusauctum.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

CALYX = (0.80, 0.80, 0.62)
LOBE = (0.52, 0.54, 0.38)
STALK = (0.66, 0.64, 0.48)
STALK_DARK = (0.48, 0.46, 0.34)
HOLD = (0.50, 0.44, 0.34)
APEX = (0.36, 0.28, 0.20)


def build():
    mb = nh.MeshBuilder()
    stalk = kit.curve((0, 0, 0.02), (0.06, 0.02, 0.45), (0.0, 0.0, 0.9), 10)
    mb.add(nh.tube(stalk, [0.03] * 3 + [0.026] * 6 + [0.03, 0.04], sides=8), kit.ringed(STALK, STALK_DARK, period=0.05, sharp=0.2))
    mb.add(nh.ellipsoid((0, 0, 0.02), (0.06, 0.06, 0.035), subdivisions=2), HOLD)
    c = Vector(stalk[-1])

    def deform(n):
        a = math.atan2(n.y, n.x)
        return 1.0 + 0.06 * math.cos(6 * a) * (1 - abs(n.z))
    cal = nh.uv_ellipsoid((0, 0, 0), (0.12, 0.12, 0.2), segments=30, rings=14, deform=deform)
    for v in cal.verts:
        z = v.co.z / 0.2
        v.co.x *= 0.75 + 0.35 * (z + 1) / 2
        v.co.y *= 0.75 + 0.35 * (z + 1) / 2
    for v in cal.verts:
        v.co += c + Vector((0, 0, 0.18))

    def col(co, n):
        a = math.atan2(co.y - c.y, co.x - c.x)
        return nh.lerp(CALYX, LOBE, nh.smoothstep(0.8, 1.0, -math.cos(6 * a)) * 0.8)
    mb.add(cal, col)
    mb.add(nh.tube([c + Vector((0, 0, 0.36)), c + Vector((0, 0, 0.41))], [0.03, 0.02], sides=8), APEX)
    return ec.ground(mb.to_object("Siphusauctum", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Siphusauctum", fixed=True)
