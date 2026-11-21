"""
Procedural Microdictyon sinicum (Chengjiang lobopodian, ~8 cm).

A slender, ringed worm-like body on ten pairs of stubby, clawed lobopod legs; above
each leg pair the body carries a pair of round, net-patterned plates (the sclerites the
genus is named for) standing out from the flanks. A small rounded head with a pair of
short front feelers. Pinkish-ochre body, darker orange-brown plates with a pale mesh.
Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Microdictyon.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.86, 0.62, 0.50)
BODY_DARK = (0.66, 0.42, 0.34)
PLATE = (0.62, 0.34, 0.14)
MESH = (0.95, 0.80, 0.52)
CLAW = (0.30, 0.20, 0.14)


def net(cx, cy):
    def c(co, n):
        u, v = (co.x - cx) * 60, (co.y - cy) * 60
        a = math.cos(u) * math.cos(v * 0.866 + u * 0.5) * math.cos(v * 0.866 - u * 0.5)
        return nh.lerp(PLATE, MESH, nh.smoothstep(0.25, 0.5, abs(a)))
    return c


def build():
    mb = nh.MeshBuilder()
    pts = [(0, y, 0.02 * math.sin(y * 6)) for y in [-0.7 + 0.07 * i for i in range(21)]]
    radii = [0.05 + 0.025 * math.sin(math.pi * min(1, i / 20 * 1.1)) for i in range(21)]
    radii[0], radii[-1] = 0.04, 0.0
    mb.add(nh.tube(pts, radii, sides=10), kit.ringed(BODY, BODY_DARK, period=0.035, axis=1))
    mb.add(nh.uv_ellipsoid((0, -0.72, 0.01), (0.045, 0.05, 0.04), segments=10, rings=6), BODY)
    for s in (-1, 1):
        mb.add(kit.tentacle((s * 0.02, -0.75, 0.01), (s * 0.4, -1, 0.1), 0.12, 0.012, curl=(0, 0, -0.2)), BODY_DARK)
    for i in range(10):
        y = -0.55 + i * 0.12
        for s in (-1, 1):
            kit.lobopod(mb, (s * 0.04, y, -0.02), (s * 0.5, 0, -1), 0.13, 0.024, BODY, claw=CLAW, rings=3)
            d = nh.uv_ellipsoid((0, 0, 0), (0.045, 0.045, 0.008), segments=14, rings=6)
            nh.transform(d, Matrix.Rotation(math.radians(s * 70), 4, "Y"))
            c = (s * 0.075, y, 0.03)
            nh.transform(d, Matrix.Translation(c))
            mb.add(d, net(c[0], c[1]))
    return ec.centre(mb.to_object("Microdictyon", roughness=0.55))


if __name__ == "__main__":
    ec.export(build, "Microdictyon")
