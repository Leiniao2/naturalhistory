"""
Procedural seven-spot ladybird (Coccinella septempunctata) on a leaf, for map colonies.

A broad, gently curled green leaf with raised veins lies on the ground; the beetle
(about a third of the leaf's length) sits in the middle: glossy domed red elytra
with seven crisp black spots (three per wing case plus one shared behind the
pronotum) built as thin caps that follow the dome, a black pronotum with white
front corners, small black head, short legs and antennae. The gloss is baked into
the vertex colours as a soft highlight, since the map shader is diffuse only.
Faces -Y, pivot on the ground (lowest point of the leaf at z = 0).

Usage:
  blender --background --python tools/blender/seven_spot_ladybird.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SevenSpotLadybird.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

RED = (0.86, 0.07, 0.035)
RED_DARK = (0.45, 0.02, 0.02)
GLOSS = (1.0, 0.62, 0.55)
BLACK = (0.025, 0.022, 0.022)
WHITE = (0.93, 0.92, 0.88)
LEAF = (0.22, 0.48, 0.10)
LEAF_LIGHT = (0.42, 0.66, 0.18)
LEAF_EDGE = (0.16, 0.36, 0.07)
VEIN = (0.55, 0.74, 0.30)
LIGHT_DIR = Vector((-0.45, -0.55, 0.70)).normalized()  # baked highlight direction

LEAF_LEN, LEAF_W = 1.25, 0.32  # length along Y, half-width


# ---------------------------------------------------------------- leaf

def leaf_point(u, v):
    """u in [-1, 1] across, v in [0, 1] from stalk to tip."""
    w = LEAF_W * math.sin(math.pi * min(v * 1.05, 1.0)) ** 0.75 * (1.0 - 0.25 * v) + 0.01
    x = u * w
    y = -LEAF_LEN * 0.5 + v * LEAF_LEN
    z = 0.10 * (abs(u) ** 2) * (w / LEAF_W)     # edges curl up
    z += 0.10 * max(0.0, v - 0.75) ** 2 * 6     # tip lifts a little
    z -= 0.012 * (1.0 - abs(u)) ** 3            # shallow groove along the midrib
    z += 0.008 * noise.noise(Vector((x * 6, y * 6, 0.3)))
    return Vector((x, y, z))


def leaf_height(x, y):
    v = min(1.0, max(0.0, (y + LEAF_LEN * 0.5) / LEAF_LEN))
    w = LEAF_W * math.sin(math.pi * min(v * 1.05, 1.0)) ** 0.75 * (1.0 - 0.25 * v) + 0.01
    return leaf_point(max(-1.0, min(1.0, x / w)), v).z


def build_leaf(mb):
    nu, nv = 14, 30
    bm = bmesh.new()
    top = [[bm.verts.new(leaf_point(-1 + 2 * i / nu, j / nv)) for i in range(nu + 1)] for j in range(nv + 1)]
    bot = [[bm.verts.new(leaf_point(-1 + 2 * i / nu, j / nv) - Vector((0, 0, 0.012))) for i in range(nu + 1)]
           for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            bm.faces.new([top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]])
            bm.faces.new([bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]])
    for j in range(nv):  # side walls
        bm.faces.new([top[j][0], bot[j][0], bot[j + 1][0], top[j + 1][0]])
        bm.faces.new([top[j][nu], top[j + 1][nu], bot[j + 1][nu], bot[j][nu]])

    def color(co, n):
        v = (co.y + LEAF_LEN * 0.5) / LEAF_LEN
        w = LEAF_W * math.sin(math.pi * min(v * 1.05, 1.0)) ** 0.75 * (1.0 - 0.25 * v) + 0.01
        u = min(1.0, abs(co.x) / w)
        c = nh.lerp(LEAF_LIGHT, LEAF, nh.smoothstep(0.0, 0.5, u))
        c = nh.lerp(c, LEAF_EDGE, nh.smoothstep(0.75, 1.0, u))
        return nh.lerp(c, LEAF_EDGE, 0.5) if n.z < -0.3 else c
    mb.add(bm, color)

    # raised veins: midrib plus curving side veins
    lift = Vector((0, 0, 0.006))
    mid = [leaf_point(0, v) + lift for v in (0.0, 0.2, 0.4, 0.6, 0.8, 0.97)]
    mb.add(nh.tube(mid, [0.012, 0.011, 0.009, 0.007, 0.005, 0.0], sides=5), VEIN)
    for k in range(6):
        v0 = 0.12 + k * 0.13
        for s in (-1, 1):
            pts = [leaf_point(s * u, v0 + u * 0.12) + lift for u in (0.0, 0.3, 0.6, 0.85)]
            mb.add(nh.tube(pts, [0.006, 0.005, 0.0035, 0.0], sides=4), VEIN)
    # short stalk
    base = leaf_point(0, 0)
    mb.add(nh.tube([base, base + Vector((0.01, -0.08, -0.01)), base + Vector((0.03, -0.15, -0.006))],
                   [0.014, 0.012, 0.010], sides=6), LEAF)


# ---------------------------------------------------------------- beetle

def dome_z(center, radii, x, y):
    dx, dy = (x - center.x) / radii[0], (y - center.y) / radii[1]
    return center.z + radii[2] * math.sqrt(max(0.0, 1.0 - dx * dx - dy * dy))


def cap(center, radii, cx, cy, r, lift=0.004, rings=3, sides=16):
    """Thin disc following the top of an ellipsoid dome, seen from above as a circle."""
    bm = bmesh.new()

    def pt(x, y):
        z = dome_z(center, radii, x, y)
        p = Vector((x, y, z))
        n = Vector(((x - center.x) / radii[0] ** 2, (y - center.y) / radii[1] ** 2,
                    (z - center.z) / radii[2] ** 2)).normalized()
        return p + n * lift
    c = bm.verts.new(pt(cx, cy))
    prev = None
    for k in range(1, rings + 1):
        rr = r * k / rings
        ring = [bm.verts.new(pt(cx + math.cos(a) * rr, cy + math.sin(a) * rr))
                for a in (i / sides * math.tau for i in range(sides))]
        for i in range(sides):
            j = (i + 1) % sides
            if prev is None:
                bm.faces.new([c, ring[i], ring[j]])
            else:
                bm.faces.new([prev[i], ring[i], ring[j], prev[j]])
        prev = ring
    return bm


def glossy(base, dark):
    def color(co, n):
        c = nh.lerp(dark, base, nh.smoothstep(-0.4, 0.5, n.z))
        h = max(0.0, n.dot(LIGHT_DIR)) ** 18
        return nh.lerp(c, GLOSS if base == RED else (0.5, 0.5, 0.5), h * 0.85)
    return color


def build_beetle(mb, z0):
    L = 0.40
    elytra_c = Vector((0.0, 0.03, z0))
    er = (0.165, 0.20, 0.15)

    def flatten(n):  # flatter belly
        return 1.0 if n.z >= 0 else 1.0 - 0.6 * min(1.0, -n.z)
    mb.add(nh.uv_ellipsoid(elytra_c, er, 32, 18, deform=flatten), glossy(RED, RED_DARK))
    # suture line between the wing cases
    pts = [Vector((0, y, dome_z(elytra_c, er, 0, y) + 0.002)) for y in (-0.16, -0.08, 0.0, 0.08, 0.16, 0.21)]
    mb.add(nh.tube(pts, [0.006, 0.006, 0.006, 0.006, 0.005, 0.003], sides=4), BLACK)
    # the seven spots
    spots = [(0.0, -0.135, 0.040)]
    for s in (-1, 1):
        spots += [(s * 0.098, -0.075, 0.034), (s * 0.072, 0.045, 0.046), (s * 0.090, 0.150, 0.034)]
    for x, y, r in spots:
        mb.add(cap(elytra_c, er, x, y, r), BLACK)

    # pronotum with white front corners
    pc = Vector((0.0, -0.175, z0 - 0.015))
    pr = (0.115, 0.070, 0.085)
    mb.add(nh.uv_ellipsoid(pc, pr, 20, 12), glossy(BLACK, BLACK))
    for s in (-1, 1):
        mb.add(cap(pc, pr, s * 0.080, -0.212, 0.024, lift=0.003), WHITE)
    # head
    hc = Vector((0.0, -0.235, z0 - 0.035))
    mb.add(nh.uv_ellipsoid(hc, (0.060, 0.040, 0.045), 14, 10), BLACK)
    for s in (-1, 1):
        mb.add(nh.uv_ellipsoid(hc + Vector((s * 0.040, -0.012, 0.010)), (0.014, 0.012, 0.014), 8, 6),
               (0.10, 0.09, 0.08))
        mb.add(nh.uv_ellipsoid(hc + Vector((s * 0.022, -0.030, 0.018)), (0.010, 0.008, 0.006), 6, 4), WHITE)
        # short clubbed antennae
        a0 = hc + Vector((s * 0.030, -0.035, 0.008))
        mb.add(nh.tube([a0, a0 + Vector((s * 0.03, -0.04, 0.01)), a0 + Vector((s * 0.06, -0.06, 0.0))],
                       [0.004, 0.0035, 0.006], sides=4), BLACK)
        # legs reaching down to the leaf
        for y, reach in ((-0.16, -0.05), (-0.06, 0.0), (0.05, 0.05)):
            hip = Vector((s * 0.08, y, z0 - 0.03))
            knee = Vector((s * 0.17, y + reach * 0.4, z0 - 0.02))
            foot = Vector((s * 0.20, y + reach, 0.0))
            foot.z = leaf_height(foot.x, foot.y) + 0.004
            mb.add(nh.tube([hip, knee, foot], [0.010, 0.008, 0.005], sides=5), BLACK)
    return L


def build():
    mb = nh.MeshBuilder()
    build_leaf(mb)
    surface = leaf_point(0, 0.48).z
    build_beetle(mb, surface + 0.075)
    obj = mb.to_object("SevenSpotLadybird", roughness=0.35)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "SevenSpotLadybird", ground=(0.33, 0.28, 0.20), views=((35, 35), (10, 70), (-90, 12)))
