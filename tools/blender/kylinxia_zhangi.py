"""
Procedural Kylinxia zhangi (Chengjiang stem euarthropod, ~5 cm).

Shrimp-like body: a head shield bearing FIVE stalked eyes (a median one in front and two
pairs either side, as in Opabinia), a pair of large raptorial frontal appendages with
spiny claws curling down in front (as in Anomalocaris), then a trunk of many overlapping
tergites with pleural tips and leg tips below, tapering to a tail fan of three blades.
Reddish orange, paler underside. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Kylinxia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_b2_cambrian_kit as ck  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.74, 0.40, 0.20)
EDGE = (0.92, 0.70, 0.46)
DARK = (0.46, 0.20, 0.10)
LEG = (0.84, 0.58, 0.38)
SPINE = (0.96, 0.90, 0.76)
EYE = (0.03, 0.03, 0.03)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.plate(-0.5, 0.17, 0.14, 0.08, edge_droop=0.6), SHELL)
    tw = lambda t: 0.16 * (1 - 0.6 * t ** 1.4)
    ck.tergites(mb, -0.38, 0.62, 20, tw, 0.06,
                lambda i, t: (lambda co, n: nh.lerp(SHELL, EDGE, nh.smoothstep(0.06, 0.15, abs(co.x)))))
    for k, a in enumerate((-60, 0, 60)):
        b = ec.paddle(0.14, 0.035, n=8, taper=0.5, thickness=0.01)
        nh.transform(b, Matrix.Rotation(math.radians(90 + a * 0.5), 4, "Z"))
        nh.transform(b, Matrix.Translation((0, 0.6, 0)))
        mb.add(b, DARK, smooth=False)
    ck.stalked_eye(mb, (0, -0.58, 0.05), (0, -0.66, 0.1), 0.028, DARK, EYE)
    for s in (-1, 1):
        for j, (dx, dy) in enumerate(((0.08, -0.52), (0.12, -0.46))):
            ck.stalked_eye(mb, (s * 0.05, dy, 0.05), (s * (dx + 0.06), dy - 0.04, 0.09), 0.026, DARK, EYE)
        ck.frontal_limb(mb, s, (s * 0.05, -0.6, -0.02), 0.2, 0.16, 0.026, SHELL, SPINE, n=5,
                        spine_len=0.07, hook=0.6)
    ck.legs_under(mb, -0.35, 0.45, 14, tw, LEG, z=-0.03, reach=0.09, drop=0.06, r=0.009)
    return ec.centre(mb.to_object("Kylinxia", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Kylinxia")
