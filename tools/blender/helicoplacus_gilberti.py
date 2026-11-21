"""
Procedural Helicoplacus gilberti (early Cambrian helicoplacoid echinoderm, a few cm).

An upright, spindle-shaped body like a twisted pine cone, its pointed lower end sunk in
the mud; the skin of small plates is arranged in ridges that spiral round the body, and a
single feeding groove (ambulacrum) of paler plates winds round it in a spiral to the
mouth near the top. Tan-orange plates, darker furrows. Fixed: pivot on the seabed.

Output: Assets/Resources/Models/Species/Helicoplacus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

PLATE = (0.84, 0.56, 0.30)
FURROW = (0.50, 0.30, 0.16)
GROOVE = (0.98, 0.88, 0.66)
MUD = (0.48, 0.42, 0.32)


def build():
    mb = nh.MeshBuilder()
    H = 1.0
    def deform(n):
        a = math.atan2(n.y, n.x)
        return 1.0 + 0.05 * math.cos(10 * a + n.z * 14)
    b = nh.uv_ellipsoid((0, 0, 0), (0.2, 0.2, H * 0.5), segments=36, rings=24, deform=deform)
    for v in b.verts:
        z = v.co.z / (H * 0.5)
        if z < 0:
            k = 1 - 0.55 * (-z)
            v.co.x *= k
            v.co.y *= k
    nh.transform(b, Matrix.Translation((0, 0, H * 0.5 - 0.08)))
    def col(co, n):
        a = math.atan2(co.y, co.x)
        z = co.z
        rid = 0.5 + 0.5 * math.cos(10 * a + (z - 0.42) / 0.5 * 14)
        c = nh.lerp(FURROW, PLATE, nh.smoothstep(0.2, 0.7, rid))
        g = math.cos(a - z * 9.0)
        return nh.lerp(c, GROOVE, nh.smoothstep(0.88, 0.97, g))
    mb.add(b, col)
    mb.add(nh.uv_ellipsoid((0, 0, H - 0.08), (0.03, 0.03, 0.02), segments=8, rings=4), FURROW)
    mud = nh.uv_ellipsoid((0, 0, 0), (0.24, 0.24, 0.04), segments=16, rings=6)
    mb.add(mud, MUD)
    return ec.ground(mb.to_object("Helicoplacus", roughness=0.6))


if __name__ == "__main__":
    ec.export(build, "Helicoplacus", fixed=True)
