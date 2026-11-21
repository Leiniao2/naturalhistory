"""
Procedural Canadaspis perfecta (Burgess Shale bivalved arthropod, ~5 cm).

The head and thorax are enclosed in a large, smooth, clam-like carapace of two oval
valves meeting along a dorsal hinge; out of the front poke short antennae and a pair of
small stalked eyes beside a short rostral spine, and walking legs show beneath the
valve edges. Behind it a tapering abdomen of seven ringed segments ends in a pair of
spiny tail rami (a fork). Olive-brown valves, paler abdomen. Faces -Y, pivot at the
body centre (Swim).

Output: Assets/Resources/Models/Species/Canadaspis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_b2_cambrian_kit as ck  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

VALVE = (0.46, 0.42, 0.26)
VALVE_RIM = (0.70, 0.64, 0.44)
HINGE = (0.32, 0.28, 0.16)
ABD = (0.66, 0.54, 0.36)
ABD_DARK = (0.46, 0.36, 0.22)
LEG = (0.70, 0.56, 0.38)


def build():
    mb = nh.MeshBuilder()
    for s in (-1, 1):
        v = nh.uv_ellipsoid((0, 0, 0), (0.16, 0.42, 0.24), segments=20, rings=12)
        for p in v.verts:
            if p.co.x * s < 0:  # inner side: flatten so the two valves read as shells
                p.co.x *= 0.15
        nh.transform(v, Matrix.Rotation(math.radians(s * 14), 4, "Y"))
        nh.transform(v, Matrix.Translation((s * 0.07, 0, 0.02)))
        mb.add(v, lambda co, n: nh.lerp(VALVE, VALVE_RIM, nh.smoothstep(-0.05, -0.2, co.z)))
    mb.add(nh.tube([(0, -0.38, 0.17), (0, 0, 0.215), (0, 0.38, 0.16)], [0.03, 0.035, 0.03], sides=6), HINGE)
    mb.add(ec.spike((0, -0.38, 0.12), (0, -0.52, 0.12), r=0.025, sides=5), HINGE)
    # abdomen
    mb.add(ec.segmented_trunk(0.3, 0.82, 7, lambda t: 0.08 * (1 - 0.45 * t), flat=0.8, sides=10, tip=0.03),
           ec.banded(ABD, ABD_DARK, ABD, 0.3, 0.52 / 7, amount=0.6))
    for s in (-1, 1):
        mb.add(nh.tube([(s * 0.02, 0.8, 0.0), (s * 0.06, 0.92, 0.0), (s * 0.08, 1.02, -0.01)],
                       [0.02, 0.014, 0.0], sides=5), ABD_DARK)
        for k in range(3):
            y = 0.86 + 0.05 * k
            mb.add(ec.spike((s * (0.04 + 0.01 * k), y, 0), (s * (0.09 + 0.01 * k), y + 0.02, 0), r=0.006, sides=3), ABD_DARK)
        ck.stalked_eye(mb, (s * 0.03, -0.36, 0.06), (s * 0.08, -0.46, 0.08), 0.025, ABD, (0.05, 0.04, 0.03))
        ck.antenna(mb, (s * 0.03, -0.38, 0.0), s, 0.18, 0.012, LEG, spread=0.6)
    ck.legs_under(mb, -0.26, 0.26, 7, lambda t: 0.16, LEG, z=-0.14, reach=0.1, drop=0.1, r=0.012)
    return ec.centre(mb.to_object("Canadaspis", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Canadaspis")
