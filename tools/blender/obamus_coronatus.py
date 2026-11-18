"""
Procedural Obamus coronatus (Ediacaran, South Australia): a small, ring-shaped (torus) animal
0.5-2 cm across with raised ridges winding spirally round the ring like a crown, sunk partly
into the microbial mat. Buff-ochre ring with darker grooves on a dark green-brown mat
patch. Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/obamus_coronatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Obamus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
import nh_edi_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

RING = (0.84, 0.66, 0.40)
GROOVE = (0.46, 0.32, 0.18)
MAT = (0.30, 0.34, 0.20)
RIDGES = 18
RM, RN = 0.4, 0.14


def build():
    mb = nh.MeshBuilder()
    bm = bmesh.new()
    nu, nv = 96, 20
    grid = []
    for i in range(nu):
        u = i / nu * math.tau
        row = []
        for j in range(nv):
            v = j / nv * math.tau
            ridge = math.cos(RIDGES * u + 2 * v)
            r = RN * (1 + 0.16 * ridge)
            x = (RM + r * math.cos(v)) * math.cos(u)
            y = (RM + r * math.cos(v)) * math.sin(u)
            z = r * math.sin(v) * 0.85
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for i in range(nu):
        for j in range(nv):
            a, b = grid[i][j], grid[(i + 1) % nu][j]
            c, d = grid[(i + 1) % nu][(j + 1) % nv], grid[i][(j + 1) % nv]
            bm.faces.new([a, b, c, d])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col(co, n):
        u = math.atan2(co.y, co.x)
        rr = math.hypot(co.x, co.y) - RM
        v = math.atan2(co.z / 0.85, rr)
        ridge = math.cos(RIDGES * u + 2 * v)
        return nh.lerp(GROOVE, RING, nh.smoothstep(-0.6, 0.5, ridge))
    mb.add(bm, col)
    mat = nh.uv_ellipsoid((0, 0, -0.02), (0.75, 0.75, 0.06), segments=32, rings=8)
    mb.add(mat, kit.mottled(MAT, 0.25, 6))
    return ec.ground(mb.to_object("Obamus", roughness=0.6))


if __name__ == "__main__":
    ec.export(build, "Obamus", fixed=True)
