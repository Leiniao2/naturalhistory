"""
Procedural low-poly Vetulicola cuneata (Chengjiang vetulicolian).

A two-part animal: a large, boxy, wedge-shaped front section built of stiff
cuticular plates (a dorsal and ventral pair meeting along the sides), with a
wide mouth opening at the front and a row of five round gill pouches (openings)
along each side; behind it a narrower, flattened tail of seven segments,
tapering to a pointed tip and bent slightly up. Olive grey plates with darker
seams and gill rims; paler tail bands. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Vetulicola.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

PLATE = (0.58, 0.58, 0.46)
SEAM = (0.30, 0.30, 0.24)
GILL = (0.22, 0.16, 0.14)
GILL_RIM = (0.80, 0.68, 0.50)
TAIL = (0.66, 0.62, 0.48)
TAIL_DARK = (0.44, 0.40, 0.30)
MOUTH = (0.18, 0.12, 0.10)


def build():
    mb = nh.MeshBuilder()
    # boxy front: a cube rounded and tapered into a wedge
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=7, use_grid_fill=True)
    for v in bm.verts:
        x, y, z = v.co
        t = y + 0.5                    # 0 front .. 1 back
        w = 0.17 * (1 - 0.25 * t)
        h = 0.15 * (1 - 0.3 * t)
        v.co = Vector((x * 2 * w, -0.4 + 0.5 * t, z * 2 * h))
        # round the long edges
        v.co.x *= 1 - 0.22 * (2 * z) ** 4
        v.co.z *= 1 - 0.22 * (2 * x) ** 4
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def plate_col(co, n):
        c = PLATE
        if abs(co.z) < 0.006:
            c = SEAM                       # lateral groove where the plates meet
        if abs(co.x) < 0.006 and co.z > 0:
            c = SEAM                       # dorsal midline
        if co.y < -0.395 and abs(co.z) < 0.06 and abs(co.x) < 0.09:
            c = MOUTH
        return c

    mb.add(bm, plate_col, smooth=False)
    # five gill openings along each side, just above the groove
    for k in range(5):
        y = -0.3 + k * 0.075
        t = (y + 0.4) / 0.5
        w = 0.17 * (1 - 0.25 * t)
        for s in (-1, 1):
            rim = nh.tube([(s * (w - 0.005), y, 0.035), (s * (w + 0.012), y, 0.035)], [0.024, 0.02], sides=10)
            mb.add(rim, GILL_RIM)
            mb.add(nh.tube([(s * (w + 0.004), y, 0.035), (s * (w + 0.016), y, 0.035)], [0.016, 0.014], sides=10), GILL)
    # tail: seven segments, flattened side-to-side, tip raised
    pts, radii = [], []
    for i in range(15):
        t = i / 14.0
        y = 0.08 + 0.7 * t
        pts.append((0, y, 0.06 * t * t))
        radii.append(0.1 * (1 - 0.8 * t) * (0.85 if i % 2 == 0 else 1.0))
    radii[-1] = 0.0
    mb.add(nh.tube(pts, radii, sides=10, scale_xy=(0.55, 1.0)),
           ec.banded(TAIL, TAIL_DARK, TAIL, 0.08, 0.7 / 7, amount=0.8))
    return ec.centre(mb.to_object("Vetulicola", roughness=0.5))


if __name__ == "__main__":
    ec.export(build, "Vetulicola")
