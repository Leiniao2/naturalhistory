"""
Procedural Fuxianhuia protensa (Chengjiang fuxianhuiid arthropod, ~11 cm).

A small, rounded head shield with a pair of stalked eyes and short antennae in front;
a long trunk: a broad thorax of overlapping tergites with drooping pleurae, narrowing
into a slim, limbless abdomen of ring segments that ends in a flat, paddle-like tail
fluke with two lobes. Many slender leg tips under the thorax. Dark olive-brown with
paler edges. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Fuxianhuia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_b2_cambrian_kit as ck  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.40, 0.36, 0.24)
EDGE = (0.68, 0.60, 0.42)
ABD = (0.50, 0.42, 0.28)
LEG = (0.64, 0.52, 0.34)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.plate(-0.62, 0.2, 0.12, 0.07, edge_droop=0.6), SHELL)
    tw = lambda t: 0.27 * (1 - 0.35 * t)
    ck.tergites(mb, -0.5, 0.25, 14, tw, 0.06,
                lambda i, t: (lambda co, n: nh.lerp(SHELL, EDGE, nh.smoothstep(0.12, 0.25, abs(co.x)))))
    mb.add(ec.segmented_trunk(0.22, 0.8, 9, lambda t: 0.08 * (1 - 0.35 * t), flat=0.8, sides=10, tip=0.04),
           ec.banded(ABD, SHELL, ABD, 0.22, 0.58 / 9, amount=0.5))
    for s in (-1, 1):
        f = ec.paddle(0.16, 0.06, n=10, taper=0.5, thickness=0.012)
        nh.transform(f, Matrix.Rotation(math.radians(70), 4, "Z"))
        ec.mirror(f, s)
        nh.transform(f, Matrix.Translation((s * 0.01, 0.8, 0)))
        mb.add(f, SHELL, smooth=False)
        ck.stalked_eye(mb, (s * 0.04, -0.72, 0.02), (s * 0.12, -0.8, 0.03), 0.03, SHELL, (0.04, 0.03, 0.02))
        ck.antenna(mb, (s * 0.03, -0.73, -0.02), s, 0.2, 0.013, LEG, spread=0.6)
    ck.legs_under(mb, -0.48, 0.2, 14, tw, LEG, z=-0.03, reach=0.11, drop=0.07, r=0.01)
    return ec.centre(mb.to_object("Fuxianhuia", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Fuxianhuia")
