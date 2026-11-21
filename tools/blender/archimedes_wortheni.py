"""
Procedural Archimedes wortheni (Early Carboniferous fenestrate bryozoan colony, about 20 cm
tall) for map colonies (Fixed style).

The colony stands upright on a small holdfast on the sea floor: a thick, pale corkscrew
axis (a central column wound by a heavy screw thread, the part that fossilises as the famous
"Archimedes screw") from whose thread a thin, lacy frond spirals outwards and slightly
upwards like a spiral staircase, widest low down and narrowing toward the top. The frond is
painted as a fenestrate net: pale tan-pink strands round darker window holes. Faces -Y,
pivot on the ground.

Usage:
  blender --background --python tools/blender/archimedes_wortheni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Archimedes.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

NAME = "Archimedes"
AXIS = (0.86, 0.83, 0.74)
AXIS_DARK = (0.66, 0.62, 0.54)
STRAND = (0.88, 0.70, 0.62)
HOLE = (0.42, 0.26, 0.24)
SEABED = (0.52, 0.50, 0.42)
SEABED_DARK = (0.38, 0.37, 0.32)

H = 1.25          # axis height
Z0 = 0.06
PITCH = 0.17      # rise per turn
TURNS = (H - 0.12) / PITCH
R_AXIS = 0.045
R_THREAD = 0.095


def sheet(fn, nu, nv, th, colour):
    """Thin solid sheet from fn(u, v) -> (point, up) on a nu x nv grid."""
    bm = bmesh.new()
    top, bot = [], []
    for i in range(nu + 1):
        rt, rb = [], []
        for j in range(nv + 1):
            p, up = fn(i / nu, j / nv)
            rt.append(bm.verts.new(p + up * th * 0.5))
            rb.append(bm.verts.new(p - up * th * 0.5))
        top.append(rt)
        bot.append(rb)
    for i in range(nu):
        for j in range(nv):
            bm.faces.new([top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]])
            bm.faces.new([bot[i][j], bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j]])
    for i in range(nu):
        for j in (0, nv):
            bm.faces.new([top[i][j], bot[i][j], bot[i + 1][j], top[i + 1][j]])
    for j in range(nv):
        for i in (0, nu):
            bm.faces.new([top[i][j], top[i][j + 1], bot[i][j + 1], bot[i][j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def helix_point(a, r, rise=0.0):
    return Vector((math.cos(a) * r, math.sin(a) * r, Z0 + 0.06 + a / math.tau * PITCH + rise))


def build():
    mb = nh.MeshBuilder()

    def bed(n):
        return 1.0 + 0.12 * noise.noise(n * 2.5)
    mb.add(nh.ellipsoid((0, 0, 0.01), (0.55, 0.50, 0.05), subdivisions=3, deform=bed),
           lambda co, n: nh.lerp(SEABED_DARK, SEABED, 0.5 + 0.5 * noise.noise(co * 8.0)))

    # holdfast roots and the central column
    for k in range(5):
        a = k * math.tau / 5
        mb.add(nh.tube([(0, 0, Z0 + 0.06), (math.cos(a) * 0.08, math.sin(a) * 0.08, Z0 + 0.01),
                        (math.cos(a) * 0.14, math.sin(a) * 0.14, Z0 - 0.01)], [0.025, 0.018, 0.008], sides=5), AXIS_DARK)
    mb.add(nh.tube([(0, 0, Z0 - 0.01), (0, 0, Z0 + H * 0.5), (0, 0, Z0 + H), (0, 0, Z0 + H + 0.03)],
                   [R_AXIS, R_AXIS, R_AXIS * 0.8, 0.0], sides=12), AXIS)

    amax = TURNS * math.tau

    # heavy screw thread
    def thread(u, v):
        a = u * amax
        r = R_AXIS * 0.8 + (R_THREAD - R_AXIS * 0.8) * v
        up = Vector((0, 0, 1))
        return helix_point(a, r, -0.01 * v), up
    nu = int(TURNS * 20)
    mb.add(sheet(thread, nu, 2, 0.05, AXIS),
           lambda co, n: nh.lerp(AXIS_DARK, AXIS, 0.5 + 0.5 * max(0.0, n.z)))

    # lacy frond spiralling out from the thread, tilted up like a funnel
    def frond_r(a):
        t = a / amax
        return 0.42 * (1 - 0.62 * t) + 0.05

    def frond(u, v):
        a = u * amax
        r = R_THREAD * 0.9 + (frond_r(a) - R_THREAD * 0.9) * v
        rise = 0.10 * v * v
        tilt = Vector((-math.cos(a) * 0.25, -math.sin(a) * 0.25, 1.0)).normalized()
        return helix_point(a, r, rise - 0.015), tilt

    def net_col(co, n):
        r = math.hypot(co.x, co.y)
        a = math.atan2(co.y, co.x)
        cu = (a * r / 0.028) % 1.0
        cv = (r / 0.030) % 1.0
        if r < R_THREAD * 1.05:
            return AXIS
        hole = 0.18 < cu < 0.82 and 0.22 < cv < 0.78
        k = 0.9 + 0.1 * noise.noise(co * 30.0)
        c = HOLE if hole else STRAND
        return (c[0] * k, c[1] * k, c[2] * k)
    mb.add(sheet(frond, int(TURNS * 48), 10, 0.012, STRAND), net_col)

    obj = mb.to_object(NAME, roughness=0.65)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.25, 0.32, 0.30), views=((35, 20), (-90, 5), (10, 70)))
