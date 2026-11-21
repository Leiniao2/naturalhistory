"""
Procedural Yunnanozoon lividum (Chengjiang possible early chordate, a few cm).

A small, laterally flattened, leaf-shaped swimmer: a deep body tapering to both ends,
a low segmented dorsal fin-fold along the back marked by a row of rectangular blocks,
zig-zag muscle blocks down the flanks, a short snout and paired dark gill arches in the
lower front. Bluish grey-green with darker banding. Swim style (undulates): pivot at
the body centre, faces -Y.

Output: Assets/Resources/Models/Species/Yunnanozoon.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BODY = (0.56, 0.66, 0.62)
BAND = (0.34, 0.44, 0.42)
BELLY = (0.82, 0.86, 0.78)
GILL = (0.52, 0.22, 0.24)
FIN = (0.66, 0.74, 0.70)


def build():
    mb = nh.MeshBuilder()
    L = 0.8
    b = nh.uv_ellipsoid((0, 0, 0), (0.07, L, 0.2), segments=20, rings=16)
    for v in b.verts:
        y = v.co.y / L
        v.co.z *= 1 - 0.35 * max(0.0, y)
    def col(co, n):
        w = (co.y * 22 + abs(co.z) * 10) % 1.0
        c = nh.lerp(BODY, BAND, nh.smoothstep(0.75, 0.95, w))
        return nh.lerp(BELLY, c, nh.smoothstep(-0.12, 0.0, co.z))
    mb.add(b, col)
    for i in range(14):
        y = -0.5 + i * 0.075
        h = 0.045 * (1 - abs(y) / 0.9)
        z = 0.2 * math.sqrt(max(0.0, 1 - (y / L) ** 2)) * (1 - 0.35 * max(0.0, y / L))
        mb.add(nh.uv_ellipsoid((0, y, z + h * 0.4), (0.015, 0.03, h), segments=8, rings=4), FIN)
    for i in range(6):
        y = -0.5 + i * 0.06
        for s in (-1, 1):
            mb.add(nh.uv_ellipsoid((s * 0.05, y, -0.06), (0.025, 0.012, 0.05), segments=8, rings=4), GILL)
    for s in (-1, 1):
        mb.add(nh.ellipsoid((s * 0.045, -0.66, 0.05), (0.014, 0.014, 0.014), subdivisions=2), (0.05, 0.05, 0.05))
    return ec.centre(mb.to_object("Yunnanozoon", roughness=0.4))


if __name__ == "__main__":
    ec.export(build, "Yunnanozoon")
