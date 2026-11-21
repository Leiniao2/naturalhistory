"""
Procedural Banffia constricta (Burgess Shale vetulicolian, ~10 cm).

A two-part body: a bulbous, rounded front section with a broad mouth at the front and
a lateral groove along each side, joined by a narrow, twisted waist to a longer,
tapering rear section of about thirty narrow ring segments ending in a short point.
Ochre-brown front, banded rear. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Banffia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

FRONT = (0.72, 0.54, 0.34)
FRONT_DARK = (0.50, 0.36, 0.22)
REAR = (0.66, 0.50, 0.34)
REAR_DARK = (0.42, 0.30, 0.20)
MOUTH = (0.24, 0.14, 0.10)
GROOVE = (0.38, 0.26, 0.16)


def build():
    mb = nh.MeshBuilder()
    f = nh.uv_ellipsoid((0, -0.38, 0), (0.17, 0.3, 0.18), segments=20, rings=12)
    mb.add(f, lambda co, n: nh.lerp(FRONT, FRONT_DARK, 0.4 * nh.smoothstep(0.0, -0.15, co.z)))
    mb.add(nh.uv_ellipsoid((0, -0.67, 0.0), (0.1, 0.03, 0.07), segments=12, rings=6), MOUTH)
    for s in (-1, 1):
        mb.add(nh.tube([(s * 0.165, -0.55, 0.0), (s * 0.18, -0.38, 0.0), (s * 0.16, -0.2, 0.0)],
                       [0.012, 0.014, 0.01], sides=5), GROOVE)
    mb.add(nh.tube([(0, -0.12, 0), (0, -0.04, 0.0), (0, 0.04, 0)], [0.07, 0.045, 0.07], sides=10), FRONT_DARK)
    tr = ec.segmented_trunk(0.02, 0.85, 22, lambda t: 0.12 * (1 - 0.75 * t ** 1.3), flat=0.85, sides=10, tip=0.0)
    nh.transform(tr, Matrix.Rotation(math.radians(20), 4, "Y"))
    mb.add(tr, ec.banded(REAR, REAR_DARK, REAR, 0.02, 0.83 / 22, amount=0.6))
    return ec.centre(mb.to_object("Banffia", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Banffia")
