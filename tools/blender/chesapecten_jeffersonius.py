"""
Procedural Chesapecten jeffersonius (Pliocene of Virginia and North Carolina)
for map colonies: a large extinct scallop, Virginia's state fossil and the
first fossil from North America ever illustrated (1687).

A fan-shaped scallop up to about 17 cm across with broad radiating ribs,
two "ears" beside the straight hinge, and a flat upper valve over a more
convex lower one, lying on the sandy sea floor with the valves slightly agape
and a row of small dark eyes along the mantle edge. Warm tan-orange shell with
paler ribs. Faces -Y (the gape), pivot on the ground.

Usage:
  blender --background --python tools/blender/chesapecten_jeffersonius.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChesapectenJeffersonius.fbx
"""

import math
import sys
from pathlib import Path

import bmesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.78, 0.50, 0.28)
RIB = (0.92, 0.78, 0.58)
INNER = (0.92, 0.88, 0.80)
MANTLE = (0.70, 0.56, 0.42)
EYE = (0.05, 0.06, 0.10)

HY = 0.40          # hinge at +Y, gape toward -Y
R = 0.85           # fan radius (hinge to ventral margin)
SPAN = math.radians(52)   # half-angle of the fan
RIBS = 15
GAPE = math.radians(9)


def valve(upper):
    """A fan of ribbed shell around the hinge point; upper valve flatter."""
    bm = bmesh.new()
    nr, na = 22, 90
    dome = 0.09 if upper else 0.17
    sign = 1 if upper else -1
    grid = []
    for i in range(nr + 1):
        u = i / nr
        row = []
        for j in range(na + 1):
            v = j / na
            a = -SPAN + 2 * SPAN * v
            # rounded ventral margin: radius shrinks toward the sides of the fan
            rr = R * u * (0.82 + 0.18 * math.cos((v - 0.5) * math.pi) ** 0.5)
            x = math.sin(a) * rr
            y = HY - math.cos(a) * rr
            rib = 0.5 + 0.5 * math.cos(v * RIBS * math.tau)
            z = dome * math.sin(u * math.pi * 0.85) * math.cos((v - 0.5) * math.pi * 0.9) + 0.022 * u * rib ** 1.5
            row.append(bm.verts.new((x, y, sign * z)))
        grid.append(row)
    for i in range(nr):
        for j in range(na):
            f = [grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]]
            bm.faces.new(f if upper else list(reversed(f)))
    # thickness: a shallow inner copy so the valve is not a paper sheet
    res = bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def ears():
    bm = nh.flat_panel([(-0.26, HY + 0.02, 0), (0.26, HY + 0.02, 0), (0.18, HY - 0.16, 0), (-0.18, HY - 0.16, 0)],
                       thickness=0.03)
    return bm


def shell_col(co, n):
    a = math.atan2(co.x, HY - co.y)
    v = (a + SPAN) / (2 * SPAN)
    rib = 0.5 + 0.5 * math.cos(v * RIBS * math.tau)
    c = nh.lerp(SHELL, RIB, nh.smoothstep(0.5, 0.95, rib))
    d = (Vector((co.x, co.y - HY, 0))).length
    c = nh.lerp(c, SHELL, 0.4 * (0.5 + 0.5 * math.sin(d * 70)))          # growth lines
    c = nh.lerp(c, (0.55, 0.32, 0.16), 0.3 * max(0.0, noise.noise(co * 6)))
    return c


def tilt(bm, ang):
    from mathutils import Matrix
    nh.transform(bm, Matrix.Translation(Vector((0, HY, 0))) @ Matrix.Rotation(ang, 4, "X") @
                 Matrix.Translation(Vector((0, -HY, 0))))
    return bm


def build():
    mb = nh.MeshBuilder()
    lower = valve(False)
    mb.add(lower, shell_col)
    upper = tilt(valve(True), -GAPE)
    mb.add(upper, shell_col)
    mb.add(ears(), lambda co, n: nh.lerp(SHELL, RIB, 0.4))
    # mantle with eyes, peeking out of the gape
    for j in range(17):
        v = j / 16
        a = -SPAN * 0.85 + 2 * SPAN * 0.85 * v
        rr = R * (0.80 + 0.18 * math.cos((v - 0.5) * math.pi) ** 0.5) * 0.97
        p = Vector((math.sin(a) * rr, HY - math.cos(a) * rr, 0.03))
        mb.add(nh.ellipsoid(tuple(p), (0.026, 0.026, 0.022), subdivisions=1), MANTLE)
        mb.add(nh.ellipsoid(tuple(p + Vector((0, 0, 0.017))), (0.011,) * 3, subdivisions=1), EYE)
    obj = mb.to_object("ChesapectenJeffersonius", roughness=0.5)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "ChesapectenJeffersonius", ground=(0.74, 0.70, 0.56), views=((35, 35), (-90, 8), (0, 70)))
