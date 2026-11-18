"""
Procedural Goniophyllum pyramidale (mid-Silurian solitary rugose coral of Gotland and the
Wenlock Limestone of England, a few centimetres tall) for map colonies (Fixed style).

A four-sided "box coral": a solitary corallite shaped like an upside-down square pyramid,
tip in the sediment, with growth wrinkles across its flat faces and a deep square calice
that could be shut with four triangular lid plates (an operculum of one large and three
smaller plates) - an armoured door for the polyp. The group shows one coral with its lids
lifted and the polyp's ring of tentacles out, and two with their lids shut. Grey-buff
skeleton, darker lids, pink-orange polyp. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/goniophyllum_pyramidale.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GoniophyllumPyramidale.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

NAME = "GoniophyllumPyramidale"
WALL = (0.86, 0.80, 0.66)
WALL_DARK = (0.60, 0.53, 0.42)
EDGE = (0.84, 0.80, 0.70)
LID = (0.50, 0.40, 0.30)
LID_EDGE = (0.62, 0.55, 0.42)
POLYP = (0.92, 0.56, 0.42)
POLYP_TIP = (0.98, 0.84, 0.62)
CALICE = (0.20, 0.16, 0.12)

H = 0.80     # corallite height
R = 0.30     # half-width of the square top


def wall_col(co, n):
    k = 0.5 + 0.5 * math.sin(co.z * 70.0 + 0.4 * math.sin(co.x * 9.0))
    c = nh.lerp(WALL, WALL_DARK, 0.45 * nh.smoothstep(0.6, 0.95, k))
    return c


def corallite(mb, m, open_lids):
    # inverted square pyramid: a 4-sided tube from the tip up to the square rim
    zs = [0.0, 0.08, 0.25, 0.45, 0.65, H]
    rs = [0.0, 0.07, 0.15, 0.22, 0.27, R]
    rim = nh.tube([(0, 0, z) for z in zs], rs, sides=4, cap_end=False)
    # slight growth wrinkles: ripple the faces outward
    for v in rim.verts:
        f = 1.0 + 0.03 * math.sin(v.co.z * 45.0)
        v.co.x *= f
        v.co.y *= f
    nh.transform(rim, m @ Matrix.Rotation(math.radians(45), 4, "Z"))
    mb.add(rim, wall_col, smooth=False)
    # calice floor, sunk a little below the rim
    floor = nh.tube([(0, 0, H - 0.10), (0, 0, H - 0.09)], [R * 0.86, R * 0.86], sides=4)
    nh.transform(floor, m @ Matrix.Rotation(math.radians(45), 4, "Z"))
    mb.add(floor, CALICE)
    # four triangular lid plates hinged on the rim edges (one larger, "cardinal" plate)
    corners = [Vector((R, R, H)), Vector((-R, R, H)), Vector((-R, -R, H)), Vector((R, -R, H))]
    centre = Vector((0, 0, H + 0.02))
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        mid = (a + b) / 2
        apex = centre + (mid - centre) * (0.0 if i == 0 else 0.12)
        if open_lids:
            # swing the plate up about its hinge edge
            hinge = (b - a).normalized()
            rot = Matrix.Rotation(math.radians(80 if i == 0 else 65), 4, hinge)
            apex = mid + (rot @ (apex - mid).to_4d()).to_3d()
        lift = Vector((0, 0, 0.012))
        pts = [a + lift, b + lift, apex + lift]
        bm = bmesh.new()
        top = [bm.verts.new(p + Vector((0, 0, 0.012))) for p in pts]
        bot = [bm.verts.new(p - Vector((0, 0, 0.004))) for p in pts]
        bm.faces.new(top)
        bm.faces.new(list(reversed(bot)))
        for k in range(3):
            j = (k + 1) % 3
            bm.faces.new([top[k], bot[k], bot[j], top[j]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        nh.transform(bm, m)
        mb.add(bm, lambda co, n: LID if n.z > 0.2 else LID_EDGE, smooth=False)
    if open_lids:
        # polyp: a short column with a ring of tentacles
        col = nh.tube([(0, 0, H - 0.10), (0, 0, H + 0.06)], [0.17, 0.15], sides=12)
        nh.transform(col, m)
        mb.add(col, POLYP)
        for k in range(14):
            a = k / 14 * math.tau
            d = Vector((math.cos(a), math.sin(a), 0))
            p0 = Vector((0, 0, H + 0.06)) + d * 0.12
            t = nh.tube([p0, p0 + d * 0.08 + Vector((0, 0, 0.10)), p0 + d * 0.16 + Vector((0, 0, 0.13))],
                        [0.022, 0.014, 0.0], sides=5)
            nh.transform(t, m)
            mb.add(t, lambda co, n: nh.lerp(POLYP, POLYP_TIP, 0.6))


CORALS = ((0.0, -0.05, 0.0, 10, 0, True, 1.0), (-0.40, 0.30, 0.0, -14, 25, False, 0.85),
          (0.40, 0.32, 0.0, 12, -20, False, 0.75))


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 1.0, ((0.42, 0.40, 0.34), (0.56, 0.53, 0.46)))
    for x, y, z, tilt, yaw, open_lids, k in CORALS:
        m = Matrix.Translation(Vector((x, y, -0.10 * k))) @ Matrix.Rotation(math.radians(yaw), 4, "Z") \
            @ Matrix.Rotation(math.radians(tilt), 4, "X") @ Matrix.Scale(k, 4)
        corallite(mb, m, open_lids)
    obj = mb.to_object(NAME, roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **ec.VIEWS)
