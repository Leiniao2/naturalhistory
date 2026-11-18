"""
Procedural Haootia quadriformis (Ediacaran stalked cnidarian, Newfoundland, ~560 Ma).

A square, four-cornered body held up on a short stalk from a ridged holdfast disc; each corner
runs out into an arm that forks twice into bunches of short tentacles, like a living stalked
jellyfish (staurozoan). Fine dark stripes run across the body and arms for the muscle fibre
bundles that make it famous. Pinkish red. Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/haootia_quadriformis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Haootia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.82, 0.42, 0.40)
MUSCLE = (0.58, 0.22, 0.22)
TENT = (0.95, 0.66, 0.58)
STALK = (0.70, 0.40, 0.36)
HOLD = (0.55, 0.42, 0.36)


def striped(co, n):
    t = math.sin((co.x + co.y) * 60.0) * 0.5 + 0.5
    return nh.lerp(BODY, MUSCLE, nh.smoothstep(0.65, 0.95, t) * 0.8)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.frond_disc(0.18, 0.05, rings=4), HOLD)
    mb.add(nh.tube(kit.curve((0, 0, 0.02), (0, 0, 0.15), (0, 0, 0.3), 4), [0.05, 0.045, 0.045, 0.06, 0.09], sides=10),
           kit.ringed(STALK, MUSCLE, period=0.06, sharp=0.2))
    # four-cornered calyx: an inverted dome pulled out at the corners
    def deform(n):
        a = math.atan2(n.y, n.x)
        return 1.0 + 0.28 * max(0.0, math.cos(2 * (a - math.pi / 4))) ** 2 * (1 - abs(n.z))
    cup = nh.uv_ellipsoid((0, 0, 0.36), (0.22, 0.22, 0.1), segments=24, rings=10, deform=deform)
    mb.add(cup, striped)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        out = Vector((math.cos(a), math.sin(a), 0))
        root = Vector((0, 0, 0.38)) + out * 0.24
        elbow = root + out * 0.16 + Vector((0, 0, 0.12))
        mb.add(nh.tube([root, root.lerp(elbow, 0.5) + Vector((0, 0, 0.02)), elbow], [0.05, 0.04, 0.03], sides=8), striped)
        for s in (-1, 1):
            side = out.cross(Vector((0, 0, 1))) * s
            b2 = elbow + out * 0.1 + side * 0.08 + Vector((0, 0, 0.08))
            mb.add(nh.tube([elbow, b2], [0.028, 0.02], sides=6), striped)
            for t in range(7):
                d = (out * 0.5 + side * (0.3 + 0.1 * (t - 3)) + Vector((0, 0, 0.8 - 0.05 * abs(t - 3)))).normalized()
                mb.add(kit.tentacle(b2, d, 0.1 + 0.02 * (t % 3), 0.008, curl=tuple(out * 0.4 + Vector((0, 0, -0.2)))), TENT)
                mb.add(nh.ellipsoid(b2 + d * 0.1 + Vector((0, 0, 0.005)), (0.009, 0.009, 0.009), subdivisions=1), (1.0, 0.85, 0.8))
    mb.add(nh.ellipsoid((0, 0, 0.45), (0.05, 0.05, 0.03), subdivisions=2), MUSCLE)
    return ec.ground(mb.to_object("Haootia", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Haootia", fixed=True)
