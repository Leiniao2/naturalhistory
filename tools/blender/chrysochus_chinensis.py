"""
Procedural Chrysochus chinensis (a metallic leaf beetle) on a dogbane stem, for map colonies.

A short upright reddish-green stem with opposite pairs of long oval leaves; the
beetle sits on top of a near-horizontal upper leaf so the map camera sees it.
Oblong, rounded beetle with a brilliant metallic sheen baked into the vertex
colours by surface direction (blue-green on top, cobalt on the flanks, violet
low down, plus a soft highlight) and finely punctured elytra; dark blue-black
beaded antennae and legs.
Faces -Y, pivot on the ground (stem base at z = 0).

Usage:
  blender --background --python tools/blender/chrysochus_chinensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChrysochusChinensis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

TOP = (0.06, 0.62, 0.50)      # blue-green on top
FLANK = (0.10, 0.30, 0.80)    # cobalt
LOW = (0.42, 0.12, 0.62)      # violet low on the sides
SHINE = (0.70, 0.98, 0.92)
DARK = (0.05, 0.05, 0.12)     # antennae, legs
PIT = 0.55                    # puncture darkening
STEM = (0.30, 0.45, 0.16)
STEM_RED = (0.45, 0.16, 0.10)
LEAF = (0.20, 0.42, 0.12)
LEAF_LIGHT = (0.36, 0.58, 0.20)
LEAF_UNDER = (0.38, 0.52, 0.30)
VEIN = (0.58, 0.70, 0.42)
LIGHT_DIR = Vector((-0.45, -0.55, 0.70)).normalized()


# ---------------------------------------------------------------- leaves and stem

def leaf_local(u, v, length, width):
    """Leaf surface in its own frame: base at the origin, tip along +Y. u in [-1, 1], v in [0, 1]."""
    w = width * math.sin(math.pi * min(v * 1.02, 1.0)) ** 0.7 * (1.0 - 0.2 * v) + 0.004
    z = 0.10 * width * u * u - 0.03 * length * v * v + 0.006 * noise.noise(Vector((u * 3, v * 5, 1.7)))
    return Vector((u * w, v * length, z))


def leaf_mesh(length, width):
    mb = nh.MeshBuilder()
    nu, nv = 8, 18
    bm = bmesh.new()
    top = [[bm.verts.new(leaf_local(-1 + 2 * i / nu, j / nv, length, width)) for i in range(nu + 1)]
           for j in range(nv + 1)]
    bot = [[bm.verts.new(leaf_local(-1 + 2 * i / nu, j / nv, length, width) - Vector((0, 0, 0.008)))
            for i in range(nu + 1)] for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            bm.faces.new([top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]])
            bm.faces.new([bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]])
        bm.faces.new([top[j][0], bot[j][0], bot[j + 1][0], top[j + 1][0]])
        bm.faces.new([top[j][nu], top[j + 1][nu], bot[j + 1][nu], bot[j][nu]])

    def color(co, n):
        if n.z < -0.3:
            return LEAF_UNDER
        return nh.lerp(LEAF_LIGHT, LEAF, nh.smoothstep(0.0, width * 0.6, abs(co.x)))
    mb.add(bm, color)
    lift = Vector((0, 0, 0.004))
    mid = [leaf_local(0, v, length, width) + lift for v in (0.0, 0.25, 0.5, 0.75, 0.97)]
    mb.add(nh.tube(mid, [0.007, 0.006, 0.005, 0.0035, 0.0], sides=4), VEIN)
    return mb


def placed(mb_local, matrix):
    bm = mb_local.bm
    nh.transform(bm, matrix)
    return bm


def leaf_matrix(attach, yaw, pitch):
    """Leaf frame -> model: base at `attach`, pointing out at `yaw`, raised by `pitch` degrees."""
    return (Matrix.Translation(attach) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
            @ Matrix.Rotation(math.radians(pitch), 4, "X"))


def stem_point(t):
    return Vector((0.025 * math.sin(t * 2.2), 0.02 * t, 0.86 * t))


# ---------------------------------------------------------------- beetle

def metallic(co, n):
    up = n.z
    c = nh.lerp(LOW, FLANK, nh.smoothstep(-0.6, 0.15, up))
    c = nh.lerp(c, TOP, nh.smoothstep(0.25, 0.85, up))
    # fine punctures: a dense, low-contrast grain
    pit = nh.smoothstep(0.15, 0.55, noise.noise(co * 220.0))
    c = tuple(x * (1.0 - (1.0 - PIT) * pit) for x in c)
    h = max(0.0, n.dot(LIGHT_DIR)) ** 14
    return nh.lerp(c, SHINE, h * 0.7)


def beetle_mesh():
    """Beetle in leaf frame: belly on z = 0, head toward +Y."""
    mb = nh.MeshBuilder()

    def flatten(n):
        return 1.0 if n.z >= 0 else 1.0 - 0.55 * min(1.0, -n.z)
    ec = Vector((0.0, 0.0, 0.050))
    mb.add(nh.uv_ellipsoid(ec, (0.072, 0.112, 0.068), 36, 20, deform=flatten), metallic)
    # suture
    pts = [Vector((0, y, ec.z + 0.068 * math.sqrt(max(0.0, 1 - (y / 0.112) ** 2)) + 0.0015))
           for y in (-0.10, -0.05, 0.0, 0.05, 0.09)]
    mb.add(nh.tube(pts, [0.0025] * 5, sides=4), DARK)
    pc = Vector((0.0, 0.118, 0.044))
    mb.add(nh.uv_ellipsoid(pc, (0.055, 0.038, 0.040), 20, 12), metallic)
    hc = Vector((0.0, 0.158, 0.030))
    mb.add(nh.uv_ellipsoid(hc, (0.038, 0.026, 0.030), 14, 10), metallic)
    for s in (-1, 1):
        mb.add(nh.uv_ellipsoid(hc + Vector((s * 0.030, 0.008, 0.008)), (0.010, 0.010, 0.011), 8, 6), DARK)
        # beaded antennae sweeping forward and out
        base = hc + Vector((s * 0.022, 0.020, 0.012))
        pts = [base + Vector((s * 0.018 * k, 0.026 * k, 0.010 * k - 0.0012 * k * k)) for k in range(6)]
        mb.add(nh.tube(pts, [0.0035, 0.0035, 0.004, 0.0045, 0.005, 0.0045], sides=5), DARK)
        for p in pts[2:]:
            mb.add(nh.uv_ellipsoid(p, (0.006, 0.006, 0.006), 6, 4), DARK)
        # legs
        for y, reach in ((0.10, 0.05), (0.03, 0.0), (-0.04, -0.05)):
            hip = Vector((s * 0.045, y, 0.022))
            knee = Vector((s * 0.105, y + reach * 0.5, 0.040))
            foot = Vector((s * 0.125, y + reach, 0.002))
            mb.add(nh.tube([hip, knee, foot], [0.008, 0.006, 0.004], sides=5), DARK)
            mb.add(nh.uv_ellipsoid(foot, (0.008, 0.012, 0.004), 6, 4), DARK)
    return mb


def build():
    mb = nh.MeshBuilder()
    # stem
    pts = [stem_point(t) for t in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
    mb.add(nh.tube(pts, [0.026, 0.022, 0.019, 0.016, 0.013, 0.0], sides=8),
           lambda co, n: nh.lerp(STEM_RED, STEM, nh.smoothstep(0.0, 0.5, co.z)))
    # opposite pairs of leaves, alternating direction up the stem
    pairs = [(0.32, 20, 0.40, 0.11, 32), (0.58, 110, 0.48, 0.13, 14), (0.82, 30, 0.26, 0.07, 45)]
    beetle_leaf = None
    for t, yaw, length, width, pitch in pairs:
        at = stem_point(t)
        for side in (0, 180):
            m = leaf_matrix(at, yaw + side, pitch if not (t == 0.58 and side == 0) else 6)
            mb.add(placed(leaf_mesh(length, width), m))
            if t == 0.58 and side == 0:
                beetle_leaf = (m, length)
    m, length = beetle_leaf
    surface = leaf_local(0, 0.45, length, 0.13).z
    slope = math.atan2(leaf_local(0, 0.55, length, 0.13).z - leaf_local(0, 0.35, length, 0.13).z, length * 0.2)
    beetle_m = (m @ Matrix.Translation(Vector((0.0, length * 0.45, surface)))
                @ Matrix.Rotation(slope, 4, "X") @ Matrix.Scale(0.85, 4))
    mb.add(placed(beetle_mesh(), beetle_m))
    obj = mb.to_object("ChrysochusChinensis", roughness=0.3)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "ChrysochusChinensis", ground=(0.33, 0.28, 0.20), views=((35, 35), (10, 70), (-90, 12)))
