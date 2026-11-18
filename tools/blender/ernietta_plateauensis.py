"""
Procedural Ernietta plateauensis (latest Ediacaran, Namibia, ~548 Ma): a sack-shaped animal
half buried in sand. The wall is a quilt of vertical tube-like units side by side, sewn
together along a zigzag seam that runs round the lower body; the rounded base sits in a low
sand mound and only the open, slightly flaring rim stands above the seabed. Ochre tubes with
darker seams and a dark interior. Fixed style: pivot on the seabed (z = 0).

Usage:
  blender --background --python tools/blender/ernietta_plateauensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ernietta.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

TUBE = (0.80, 0.62, 0.38)
SEAM = (0.42, 0.28, 0.16)
INSIDE = (0.22, 0.14, 0.08)
SAND = (0.80, 0.72, 0.54)
TUBES = 24
# (radius, z) profile of the sack: rounded base -> widest -> slightly narrower rim, flaring
PROF = [(0.02, 0.0), (0.2, 0.03), (0.32, 0.12), (0.37, 0.26), (0.36, 0.42), (0.33, 0.58), (0.34, 0.68), (0.37, 0.72)]


def build():
    mb = nh.MeshBuilder()
    bm = bmesh.new()
    seg = 96
    rows = []
    for r, z in PROF:
        ring = []
        for k in range(seg):
            a = k / seg * math.tau
            bump = 1.0 + 0.07 * abs(math.cos(a * TUBES / 2))
            ring.append(bm.verts.new((math.cos(a) * r * bump, math.sin(a) * r * bump, z)))
        rows.append(ring)
    # inner wall (slightly smaller, reversed) to give the open cup some thickness
    inner = []
    for r, z in reversed(PROF[3:]):
        inner.append([bm.verts.new((math.cos(k / seg * math.tau) * (r - 0.04), math.sin(k / seg * math.tau) * (r - 0.04), z - 0.02))
                      for k in range(seg)])
    allrows = rows + inner
    for a, b in zip(allrows, allrows[1:]):
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rows[0])))
    bm.faces.new(inner[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col(co, n):
        rr = math.hypot(co.x, co.y)
        a = math.atan2(co.y, co.x)
        edge = nh.smoothstep(0.85, 1.0, abs(math.cos(a * TUBES / 2)))
        # zigzag seam round the lower body
        zz = 0.2 + 0.05 * (abs(((a * TUBES / math.pi) % 2) - 1) * 2 - 1)
        seam = 1 - nh.smoothstep(0.0, 0.02, abs(co.z - zz - 0.18))
        c = nh.lerp(TUBE, SEAM, max(edge * 0.35, seam))
        if co.z > 0.22 and rr < 0.318:
            c = nh.lerp(INSIDE, SEAM, nh.smoothstep(0.55, 0.72, co.z) * 0.5)
        return c
    mb.add(bm, col)
    sand = nh.uv_ellipsoid((0, 0, 0.0), (0.7, 0.7, 0.3), segments=36, rings=12)
    for v in sand.verts:
        v.co.z = max(v.co.z, 0.0) * 1.0
    mb.add(sand, kit_sand)
    return ec.ground(mb.to_object("Ernietta", roughness=0.7))


def kit_sand(co, n):
    rr = math.hypot(co.x, co.y)
    return nh.lerp(SAND, (0.66, 0.58, 0.42), nh.smoothstep(0.3, 0.7, rr))


if __name__ == "__main__":
    ec.export(build, "Ernietta", fixed=True)
