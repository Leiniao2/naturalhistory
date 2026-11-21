"""
Procedural Dinomischus isolatus (Burgess Shale stalked filter feeder, a few cm).

A goblet: a long, slender stalk rising from a small bulbous holdfast to a rounded,
conical cup (calyx); round the cup's rim stand about eighteen stiff, elongate, petal-like
bracts, spreading out and up like a flower. On top of the cup, the mouth and anus
openings. Pale pinkish cup, ochre bracts, darker stalk. Fixed: pivot on the seabed.

Output: Assets/Resources/Models/Species/Dinomischus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

STALK = (0.56, 0.40, 0.30)
CUP = (0.90, 0.70, 0.62)
BRACT = (0.86, 0.66, 0.32)
BRACT_TIP = (0.98, 0.88, 0.60)
HOLE = (0.30, 0.16, 0.14)


def build():
    mb = nh.MeshBuilder()
    mb.add(nh.uv_ellipsoid((0, 0, 0.03), (0.06, 0.06, 0.04), segments=12, rings=6), STALK)
    mb.add(nh.tube([(0, 0, 0.02), (0.02, 0, 0.35), (0, 0.01, 0.7)], [0.022, 0.018, 0.024], sides=8), STALK)
    cup = nh.uv_ellipsoid((0, 0, 0), (0.12, 0.12, 0.13), segments=18, rings=10)
    for v in cup.verts:
        if v.co.z < 0:
            k = 1 + v.co.z / 0.13 * 0.6
            v.co.x *= k
            v.co.y *= k
        else:
            v.co.z *= 0.4
    nh.transform(cup, Matrix.Translation((0, 0, 0.8)))
    mb.add(cup, CUP)
    for s in (-1, 1):
        mb.add(nh.ellipsoid((s * 0.04, 0, 0.855), (0.018, 0.018, 0.01), subdivisions=1), HOLE)
    N = 18
    for k in range(N):
        a = k / N * math.tau
        out = Vector((math.cos(a), math.sin(a), 0))
        f = ec.paddle(0.3, 0.035, n=10, taper=0.4, thickness=0.01)
        nh.transform(f, Matrix.Rotation(math.radians(-62), 4, "Y"))
        nh.transform(f, Matrix.Rotation(a, 4, "Z"))
        nh.transform(f, Matrix.Translation(out * 0.11 + Vector((0, 0, 0.82))))
        mb.add(f, lambda co, n: nh.lerp(BRACT, BRACT_TIP, nh.smoothstep(0.9, 1.05, co.z)), smooth=False)
    return ec.ground(mb.to_object("Dinomischus", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Dinomischus", fixed=True)
