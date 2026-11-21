"""
Procedural Haplophrentis carinatus (Burgess Shale hyolith, a few cm).

A long, slightly flattened cone-shaped shell with a keel along its top, lying on the
seabed with its open end forward; the aperture is closed by a domed lid (operculum),
from under which a pair of long, curved, flattened spines (the helens) sweep out
sideways and back to prop the shell up off the mud, and a short fringe of feeding
tentacles peeks out. Banded tan shell, darker lid. Fixed: pivot on the seabed, faces -Y.

Output: Assets/Resources/Models/Species/Haplophrentis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

SHELL = (0.80, 0.66, 0.46)
BAND = (0.58, 0.44, 0.28)
LID = (0.46, 0.34, 0.22)
HELEN = (0.36, 0.26, 0.18)
TENT = (0.92, 0.70, 0.62)


def build():
    mb = nh.MeshBuilder()
    n = 8
    pts = [(0, -0.4 + 1.0 * i / n, 0.12 - 0.06 * i / n) for i in range(n + 1)]
    radii = [0.13 * (1 - i / n) ** 0.9 for i in range(n + 1)]
    radii[-1] = 0.0
    cone = nh.tube(pts, radii, sides=12, scale_xy=(1.0, 0.75))
    for v in cone.verts:  # dorsal keel
        if v.co.z > pts[0][2] - 0.02 and abs(v.co.x) < 0.03:
            v.co.z += 0.02
    mb.add(cone, kit.ringed(SHELL, BAND, period=0.08, sharp=0.2, axis=1))
    lid = nh.uv_ellipsoid((0, 0, 0), (0.14, 0.05, 0.11), segments=16, rings=8)
    nh.transform(lid, Matrix.Rotation(math.radians(-15), 4, "X"))
    nh.transform(lid, Matrix.Translation((0, -0.42, 0.12)))
    mb.add(lid, LID)
    for s in (-1, 1):
        b = Vector((s * 0.08, -0.42, 0.06))
        pts = kit.curve(b, b + Vector((s * 0.35, -0.02, -0.02)), b + Vector((s * 0.42, 0.35, -0.06)), 6)
        mb.add(nh.tube(pts, [0.022, 0.02, 0.018, 0.015, 0.012, 0.008, 0.0], sides=5, scale_xy=(1, 0.5)), HELEN)
    kit.crown(mb, (0, -0.47, 0.16), 0.05, 7, 0.08, 0.008, TENT, up=(0, -0.4, 1), spread=45, droop=-0.1)
    return ec.ground(mb.to_object("Haplophrentis", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Haplophrentis", fixed=True)
