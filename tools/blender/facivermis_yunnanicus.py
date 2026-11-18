"""
Procedural Facivermis yunnanicus (early Cambrian luolishaniid lobopodian, Chengjiang, ~7 cm).

A slender, annulated, worm-like body standing up out of a short tube set in a low mud
mound: its swollen, legless rear end is lodged in the tube, while the front carries five
pairs of long, slender, spiny arms raised up and out like a feeding basket round a small
head. Pinkish flesh with paler spines, a grey-brown tube. Fixed style: pivot on the
seabed (z = 0).

Usage:
  blender --background --python tools/blender/facivermis_yunnanicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Facivermis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.84, 0.56, 0.50)
DARK = (0.60, 0.34, 0.30)
SPINE = (0.96, 0.88, 0.76)
TUBE = (0.48, 0.42, 0.34)
MUD = (0.56, 0.50, 0.40)


def axis(t):
    return Vector((0.06 * math.sin(t * 2.5), 0.03 * t, t * 0.95))


def build():
    mb = nh.MeshBuilder()
    pts, radii = [], []
    for i in range(31):
        t = i / 30
        pts.append(axis(t))
        radii.append((0.04 + 0.03 * (1 - t) ** 3) * (0.9 if i % 2 else 1.0))
    radii[-1] = 0.02
    mb.add(nh.tube(pts, radii, sides=10), kit.ringed(BODY, DARK, period=0.064, sharp=0.2))
    top = axis(1.0)
    mb.add(nh.ellipsoid(top + Vector((0, -0.01, 0.02)), (0.035, 0.035, 0.03), subdivisions=2), BODY)
    for k in range(5):
        t = 0.95 - k * 0.06
        b = axis(t)
        for s in (-1, 1):
            a = math.radians(s * (30 + k * 6))
            out = Vector((math.sin(a), -math.cos(a) * 0.6, 0)).normalized()
            arm_tip = b + out * 0.26 + Vector((0, 0, 0.18 - 0.02 * k))
            arm = kit.curve(b, b + out * 0.12 + Vector((0, 0, 0.02)), arm_tip, 5)
            mb.add(nh.tube(arm, [0.014, 0.012, 0.011, 0.009, 0.007, 0.0], sides=5), BODY)
            for q in range(1, 5):
                p = arm[q]
                for side in (-1, 1):
                    mb.add(ec.spike(p, p + Vector((0, 0, 0.03)) + out.cross(Vector((0, 0, 1))) * side * 0.025,
                                    r=0.003, sides=3), SPINE, smooth=False)
    tube = nh.tube([(0, 0, -0.02), (0, 0, 0.12), (0, 0, 0.2)], [0.085, 0.09, 0.095], sides=14)
    mb.add(tube, kit.mottled(TUBE, 0.2, 18))
    mound = nh.uv_ellipsoid((0, 0, 0), (0.3, 0.3, 0.08), segments=24, rings=8)
    for v in mound.verts:
        v.co.z = max(v.co.z, 0.0)
    mb.add(mound, kit.mottled(MUD, 0.15, 8))
    return ec.ground(mb.to_object("Facivermis", roughness=0.55))


if __name__ == "__main__":
    ec.export(build, "Facivermis", fixed=True)
