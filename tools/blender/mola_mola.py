"""
Procedural ocean sunfish (Mola mola) for the map.

A tall, flat, oval disc that ends abruptly in the clavus (a rudder of scalloped
ossicle lobes) instead of a tail, with long, stiff, swept dorsal and anal fins
rising from muscular bases, a small beak of fused teeth, a big rimmed eye, a
small gill opening and paddle pectorals. Rough, leathery skin; silver-grey,
darker above, with high-contrast pale blotches.

The body, fins, clavus, lips and eye socket are built as overlapping shells and
fused (nh_model.MeshBuilder.fuse) into one seamless surface, displaced with fine
noise for the leathery skin, decimated and then repainted procedurally. Small
crisp parts (eye, beak, gill slit, thin pectorals) are added on top.

Usage:
  blender --background --python tools/blender/mola_mola.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OceanSunfish.fbx (map style Swim:
pivot at the body centre, facing -Y, dorsal fin up).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402

BACK_Y = 0.42      # where the body ends in the clavus
FUSE_VOXEL = 0.009
MAX_TRIS = 11000   # for the fused surface; crisp details come on top

DORSAL = (0.30, 0.35, 0.41)
SILVER = (0.62, 0.66, 0.70)
BELLY = (0.86, 0.87, 0.87)
BLOTCH = (0.93, 0.94, 0.94)
FRECKLE = (0.26, 0.30, 0.35)
FIN = (0.32, 0.35, 0.40)
FIN_TIP = (0.20, 0.22, 0.26)
CLAVUS = (0.40, 0.44, 0.49)
LOBE_EDGE = (0.74, 0.77, 0.79)

EYE = (-0.335, 0.095)
EYE_R = 0.044
MOUTH = (-0.505, -0.02)
LOBES = 9


def half_height(y):
    return 0.41 * math.sqrt(max(0.0, 1.0 - ((y - 0.06) / 0.56) ** 2))


def top(y):
    return half_height(y) + 0.01


def bot(y):
    return -half_height(y)


def width(y):
    return 0.088 * (half_height(y) / 0.41) ** 0.8 * (1.0 - 0.5 * nh.smoothstep(0.0, BACK_Y, y))


def swept_fin(sign):
    """Dorsal (sign=1) or anal (sign=-1) fin outline: long, swept back, pointed."""
    edge_z = top if sign > 0 else bot
    y_a, y_b = 0.07, 0.35
    tip = (0.0, 0.44 if sign > 0 else 0.42, sign * 1.02)
    base, edge = [], []
    n, split = 17, 0.6
    for i in range(n):
        u = i / (n - 1)
        y = y_a + (y_b - y_a) * u
        base.append((0.0, y, edge_z(y) - sign * 0.05))  # root well inside the body so it fuses
        if u <= split:
            p = fish.bezier((0, y_a, edge_z(y_a)), (0, 0.16, sign * 0.78), tip, u / split)
        else:
            p = fish.bezier(tip, (0, 0.37, sign * 0.6), (0, y_b + 0.02, edge_z(y_b) + sign * 0.02),
                            (u - split) / (1 - split))
        edge.append(tuple(p))
    return base, edge


def lobe_z(k):
    return -0.33 + 0.66 * k / (LOBES - 1)


# ---------------------------------------------------------------- painting

def paint(co, n):
    y, z = co.y, co.z
    grain = noise.noise(Vector((co.x * 60.0, y * 60.0, z * 60.0))) * 0.035  # leathery speckle

    if y > BACK_Y - 0.015:  # clavus: grooved band of ossicle lobes with pale rims
        t = nh.smoothstep(BACK_Y + 0.02, BACK_Y + 0.12, y)
        col = nh.lerp(CLAVUS, LOBE_EDGE, t)
        k = (z + 0.33) / 0.66 * (LOBES - 1)
        groove = 1.0 - nh.smoothstep(0.05, 0.22, abs(k - round(k) - 0.5) * -1 + 0.5)  # dark between lobes
        col = nh.lerp(col, FIN_TIP, groove * 0.45 * (1.0 - t * 0.4))
        return tuple(c + grain for c in col)

    over = z - top(y) if z > 0 else bot(y) - z  # how far beyond the body outline (fins)
    col = body_color(y, z)
    if over > -0.07:
        v = min(1.0, max(0.0, over) / 0.6)
        fin = nh.lerp(FIN, FIN_TIP, v ** 0.7)
        fin = tuple(c + noise.noise(Vector((y * 40.0, 0.0, 1.7))) * 0.04 for c in fin)  # faint fin-ray streaks
        col = nh.lerp(col, fin, nh.smoothstep(-0.07, 0.06, over))
    return tuple(c + grain for c in col)


def body_color(y, z):
    shade = nh.smoothstep(-0.3, 0.32, z)
    col = nh.lerp(BELLY, SILVER, nh.smoothstep(-0.32, 0.05, z))
    col = nh.lerp(col, DORSAL, nh.smoothstep(0.05, 0.38, z))
    p = Vector((y * 5.5, z * 5.5, 2.1))
    blotch = nh.smoothstep(0.1, 0.3, noise.noise(p) + 0.18 * noise.noise(p * 2.3))
    col = nh.lerp(col, BLOTCH, blotch * (0.95 - 0.35 * shade))
    freckle = nh.smoothstep(0.3, 0.5, noise.noise(Vector((y * 13.0, z * 13.0, 7.7))))
    col = nh.lerp(col, FRECKLE, freckle * (0.25 + 0.35 * shade))
    col = nh.lerp(col, CLAVUS, nh.smoothstep(BACK_Y - 0.12, BACK_Y, y) * 0.5)  # darker toward the clavus
    lip = 1.0 - nh.smoothstep(0.0, 0.07, (Vector((y, z)) - Vector(MOUTH)).length)
    return nh.lerp(col, (0.70, 0.72, 0.74), lip * 0.7)


# ---------------------------------------------------------------- build helpers

def leathery(bm):
    """Fine bumpy displacement along the normals: the sunfish's rough, thick skin."""
    bm.normal_update()
    for v in bm.verts:
        p = v.co
        d = (noise.noise(p * 22.0) * 0.0018 + noise.noise(p * 47.0 + Vector((5, 1, 3))) * 0.0016
             + (noise.ridged_multi_fractal(p * 9.0, 0.9, 2.0, 2, 1.0, 2.0) - 1.0) * 0.0015)
        v.co = p + v.normal * d


def decimate(bm, max_tris):
    mesh = bpy.data.meshes.new("_decimate")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_decimate", mesh)
    bpy.context.scene.collection.objects.link(obj)
    tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
    mod = obj.modifiers.new("decimate", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = min(1.0, max_tris / max(tris, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    return out


def surface(bvh, y, z, side=1):
    """Flank point and normal of the fused body at side-view (y, z)."""
    hit, normal, _i, _d = bvh.ray_cast(Vector((side * 2.0, y, z)), Vector((-side, 0, 0)))
    if hit is None:
        return Vector((side * fish.surface_x(top, bot, width, y, z), y, z)), Vector((side, 0, 0))
    return hit, normal


def build_fused():
    mb = nh.MeshBuilder()
    grey = lambda *a: SILVER  # noqa: E731 - colours are repainted after fusing
    fish.body(mb, top, bot, width, -0.52, BACK_Y, lambda co: SILVER, stations=40, ring=32, close_end=False)

    for sign in (1, -1):
        base, edge = swept_fin(sign)
        fish.fin(mb, base, edge, grey, rows=6, th0=0.075, th1=0.024)
        # muscular base: an elongated bulge carrying the fin out of the body
        for y, r in ((0.17, 0.055), (0.25, 0.065), (0.32, 0.05)):
            z = (top(y) + 0.04) if sign > 0 else (bot(y) - 0.04)
            mb.add(nh.ellipsoid((0, y, z), (r, 0.1, 0.12), subdivisions=2), SILVER)

    # Clavus: a thick band with a row of rounded ossicle lobes along its edge
    base, edge = [], []
    for i in range(LOBES * 4 + 1):
        u = i / (LOBES * 4)
        z = -0.35 + 0.70 * u
        base.append((0.0, BACK_Y - 0.06, z))
        edge.append((0.0, BACK_Y + 0.07 + 0.02 * math.sin(math.pi * u), z * 1.03))
    fish.fin(mb, base, edge, grey, rows=4, th0=0.07, th1=0.04)
    for k in range(LOBES):
        z = lobe_z(k)
        mb.add(nh.ellipsoid((0, BACK_Y + 0.085 + 0.02 * math.sin(math.pi * (k / (LOBES - 1))), z * 1.03),
                            (0.024, 0.045, 0.042), subdivisions=2), SILVER)

    # Lips around the small round mouth and a raised socket around the eye
    mb.add(nh.ellipsoid((0, MOUTH[0] + 0.005, MOUTH[1]), (0.05, 0.05, 0.05), subdivisions=3), SILVER)
    for sx in (1, -1):
        x = fish.surface_x(top, bot, width, *EYE)
        mb.add(nh.ellipsoid((sx * (x - 0.01), EYE[0], EYE[1]), (0.036, EYE_R * 1.6, EYE_R * 1.5), subdivisions=3), SILVER)

    fused = mb.fuse(voxel=FUSE_VOXEL, smooth=4, smooth_factor=0.5)
    leathery(fused)
    return decimate(fused, MAX_TRIS)


def build():
    fused = build_fused()
    bvh = BVHTree.FromBMesh(fused)
    mb = nh.MeshBuilder()

    # crisp details, placed on the fused surface
    for side in (1, -1):
        # eye: silver iris ring, dark pupil, catchlights
        p, n = surface(bvh, *EYE, side)
        x = abs(p.x)
        mb.add(nh.ellipsoid((side * (x - 0.004), EYE[0], EYE[1]), (0.012, EYE_R * 1.05, EYE_R), subdivisions=3), (0.80, 0.82, 0.84))
        mb.add(nh.ellipsoid((side * (x + 0.004), EYE[0] - 0.002, EYE[1]), (0.012, EYE_R * 0.7, EYE_R * 0.66), subdivisions=3), (0.03, 0.03, 0.04))
        mb.add(nh.ellipsoid((side * (x + 0.013), EYE[0] - 0.012, EYE[1] + 0.012), (0.003, 0.009, 0.009), subdivisions=1), (0.97, 0.97, 0.97))
        mb.add(nh.ellipsoid((side * (x + 0.011), EYE[0] + 0.012, EYE[1] - 0.012), (0.002, 0.004, 0.004), subdivisions=1), (0.9, 0.9, 0.9))

        # small gill opening in front of the pectoral fin
        p, n = surface(bvh, -0.175, -0.03, side)
        mb.add(nh.ellipsoid((p.x, p.y, p.z), (0.008, 0.011, 0.038), subdivisions=2), (0.12, 0.13, 0.15))

        # pectoral fin: a thin rounded paddle sticking back and out
        root = [surface(bvh, -0.14, 0.02 - 0.075 * u, side)[0] for u in (i / 8 for i in range(9))]
        base, edge = [], []
        for i, q in enumerate(root):
            u = i / 8
            reach = 0.06 + 0.09 * math.sin(math.pi * u) ** 0.7
            base.append((q.x - side * 0.004, q.y, q.z))
            edge.append((q.x + side * reach * 0.35, q.y + reach, -0.03 + (q.z + 0.03) * 1.6))
        fish.fin(mb, base, edge, lambda u, v, co: nh.lerp((0.60, 0.64, 0.68), FIN, v ** 0.8), rows=4, th0=0.014, th1=0.004)

    # beak of fused teeth: ivory upper and lower plates around a dark gap
    my, mz = MOUTH
    mb.add(nh.ellipsoid((0, my - 0.047, mz + 0.016), (0.032, 0.02, 0.016), subdivisions=2), (0.86, 0.83, 0.74))
    mb.add(nh.ellipsoid((0, my - 0.045, mz - 0.02), (0.029, 0.019, 0.015), subdivisions=2), (0.82, 0.79, 0.70))
    mb.add(nh.ellipsoid((0, my - 0.055, mz - 0.002), (0.025, 0.01, 0.007), subdivisions=1), (0.05, 0.04, 0.05))

    mb.add(fused, color=paint)
    return mb.to_object("OceanSunfish", roughness=0.5)


if __name__ == "__main__":
    nh.run(build, "OceanSunfish", **fish.PREVIEW)
