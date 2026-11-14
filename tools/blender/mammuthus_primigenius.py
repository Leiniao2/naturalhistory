"""
Procedural woolly mammoth (Mammuthus primigenius) for map colonies.

A bull mid-stride with the mammoth silhouette: a high domed skull, a dip behind
it, a tall fatty shoulder hump and a back that slopes steeply down to low
hindquarters; shorter hind legs than front legs, a compact barrel and a short
tail. Small furry ears sit close to the head, the trunk hangs straight with a
two-fingered tip, and the long tusks sweep out, up and inward in a spiral
until the tips nearly cross.

The body is fused from overlapping parts into one seamless surface, then the
coat is displaced into clumped, downward-flowing locks: short on the face and
trunk, long and shaggy on the flanks, the belly skirt and the upper legs,
which is extended by an extra hanging skirt volume. The coat is painted dark
reddish brown with lighter golden tips and a darker underfur, the trunk tip
and foot soles are bare grey skin. Tusks, eyes and toenails are crisp details.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/mammuthus_primigenius.py -- [--render out.png]

Output: Assets/Resources/Models/Species/WoollyMammoth.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

COAT = (0.36, 0.21, 0.11)        # dark reddish brown
COAT_TIP = (0.58, 0.40, 0.22)    # sun-bleached golden tips of the guard hairs
UNDERFUR = (0.18, 0.10, 0.06)    # dark gaps between the locks
SKIN = (0.30, 0.27, 0.25)        # bare grey skin at the trunk tip and soles
IVORY = (0.90, 0.85, 0.70)
IVORY_BASE = (0.62, 0.52, 0.38)
NAIL = (0.55, 0.50, 0.42)
EYE = (0.06, 0.04, 0.03)

VOXEL = 0.011
BODY_TRIS = 19500


# ---------------------------------------------------------------- helpers

def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14, deform=None):
    """UV ellipsoid rotated about X (pitch), Y (roll) then Z (yaw), degrees, moved to center."""
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings, deform=deform)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def decimate(bm, max_tris):
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    n = sum(len(p.vertices) - 2 for p in mesh.polygons)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = min(1.0, max_tris / max(n, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    return out


def catmull(points, steps):
    """Smooth Catmull-Rom resample of a polyline (any vector size)."""
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(pts[-1])
    return out


def smooth_tube(points, radii, steps=4, sides=14, **kw):
    pts = catmull([(*p, r) for p, r in zip(points, radii)], steps)
    return nh.tube([p.xyz for p in pts], [max(0.0, p.w) for p in pts], sides=sides, **kw)


class Parts(nh.MeshBuilder):
    """Body builder: colours are repainted after fusing, so parts default to the coat."""

    def add(self, src, color=COAT, smooth=True):
        super().add(src, color, smooth)


# ---------------------------------------------------------------- anatomy

TRUNK = [(0, -0.90, 1.22), (0, -1.00, 1.06), (0, -1.04, 0.85), (0, -1.04, 0.62),
         (0, -1.03, 0.42), (0, -1.05, 0.28), (0, -1.09, 0.20)]
TRUNK_R = [0.13, 0.11, 0.09, 0.075, 0.064, 0.056, 0.05]

LEGS = {  # name: (x, y, stride, top z) — walking: left-front and right-hind forward
    "lf": (-0.21, -0.34, -0.09, 1.05), "rf": (0.21, -0.34, 0.06, 1.05),
    "lh": (-0.20, 0.44, 0.05, 0.86), "rh": (0.20, 0.44, -0.09, 0.86),
}


def torso(b):
    b.add(oriented((0, 0.02, 1.00), (0.35, 0.58, 0.40), pitch=-8, segments=28, rings=20))  # barrel, sloping
    b.add(oriented((0, -0.30, 1.16), (0.34, 0.32, 0.42)))           # deep chest
    b.add(oriented((0, -0.34, 1.34), (0.26, 0.34, 0.24), pitch=18))  # fatty shoulder hump, sloping back
    b.add(oriented((0, 0.38, 0.92), (0.30, 0.26, 0.32)))            # low rump
    b.add(oriented((0, 0.02, 0.70), (0.29, 0.45, 0.16)))            # belly
    for s in (-1, 1):
        b.add(oriented((s * 0.21, -0.36, 1.08), (0.15, 0.23, 0.32), pitch=-10))  # shoulder
        b.add(oriented((s * 0.20, 0.42, 0.90), (0.14, 0.22, 0.27), pitch=10))    # haunch


def skirt(b):
    """Long hair hanging below the flanks and belly: extra volume that the coat fills."""
    b.add(oriented((0, -0.02, 0.62), (0.36, 0.52, 0.14)))
    for s in (-1, 1):
        b.add(oriented((s * 0.30, -0.06, 0.78), (0.08, 0.50, 0.22), pitch=-6))
        b.add(oriented((s * 0.26, -0.40, 0.70), (0.09, 0.14, 0.24)))  # hair over the forearms
        b.add(oriented((s * 0.24, 0.42, 0.64), (0.08, 0.14, 0.20)))   # breeches over the thighs


def leg(b, name):
    x, y, stride, top = LEGS[name]
    front = y < 0
    knee_z = 0.48 if front else 0.44
    r_top, r_knee, r_foot = (0.15, 0.12, 0.12) if front else (0.155, 0.115, 0.11)
    knee_y = y + stride * 0.5 + (0.0 if front else -0.03)
    pts = [(x * 0.95, y, top), (x, y + stride * 0.15, (top + knee_z) * 0.5), (x, knee_y, knee_z),
           (x, y + stride * 0.85, 0.25), (x, y + stride, 0.07), (x, y + stride, 0.0)]
    radii = [r_top, r_top * 0.9, r_knee, r_knee * 0.93, r_foot, r_foot * 1.05]
    b.add(smooth_tube(pts, radii, steps=3, sides=18))
    b.add(oriented((x, y + stride - 0.01, 0.05), (r_foot * 1.12, r_foot * 1.18, 0.055)))  # round foot


def head(b):
    b.add(oriented((0, -0.72, 1.38), (0.24, 0.25, 0.34), pitch=-20, segments=24, rings=16))  # cranium
    b.add(oriented((0, -0.69, 1.56), (0.18, 0.21, 0.17), pitch=-25))  # high dome ("peaked" skull)
    for s in (-1, 1):
        b.add(oriented((s * 0.08, -0.84, 1.40), (0.10, 0.10, 0.13), pitch=-25))  # forehead
        b.add(oriented((s * 0.13, -0.80, 1.10), (0.10, 0.12, 0.10)))            # tusk sheaths
        b.add(smooth_tube([(s * 0.12, -0.84, 1.08), (s * 0.13, -0.91, 0.98)], [0.065, 0.055], steps=1))
    b.add(oriented((0, -0.76, 1.00), (0.10, 0.10, 0.07)))           # chin / lower lip
    b.add(smooth_tube([(0, -0.50, 1.26), (0, -0.64, 1.30)], [0.27, 0.26], steps=1, sides=18))  # neck
    b.add(smooth_tube(TRUNK, TRUNK_R, steps=4, sides=16))
    for s in (-1, 1):  # small, round, furry ears (cold adaptation)
        b.add(oriented((s * 0.22, -0.60, 1.42), (0.04, 0.08, 0.09), yaw=-s * 15))


def tail(b):
    pts = [(0, 0.60, 1.02), (0, 0.66, 0.92), (0, 0.68, 0.80)]
    b.add(smooth_tube(pts, [0.04, 0.03, 0.025], steps=3, sides=8))


# ---------------------------------------------------------------- coat

FLOW = Vector((0, 0.25, -1.0)).normalized()  # the coat hangs down and a little back


def hair_length(p):
    """How long the coat is at p (model units)."""
    d, s = trunk_param(p)
    if d < 0.16 and p.y < -0.88:
        return 0.01 * (1.0 - nh.smoothstep(0.4, 0.8, s))  # short fuzz, bare toward the tip
    if p.z < 0.12:
        return 0.0                                       # bare feet
    head = nh.smoothstep(-0.75, -0.55, p.y) if p.z > 1.0 else 1.0
    low = nh.smoothstep(1.35, 0.75, p.z)                 # longest on the flanks and skirt
    legs = nh.smoothstep(0.15, 0.55, p.z)                # short on the lower legs
    hump = nh.smoothstep(1.35, 1.6, p.z) * 0.5           # shaggy hump and dome
    return (0.012 + 0.07 * low * legs + 0.03 * hump) * (0.35 + 0.65 * head)


def lock_pattern(p, n):
    """0..1 clumped strands running along FLOW projected into the surface."""
    f = FLOW - n * FLOW.dot(n)
    if f.length < 1e-4:
        f = Vector((0, 1, 0)) - n * n.y
    f.normalize()
    across = f.cross(n)
    u = p.dot(across) * 26.0
    w = p.dot(f) * 3.0
    clump = 0.5 + 0.5 * math.sin(u * 2.4 + 3.0 * noise.noise(Vector((u * 0.3, w, 2.1))))
    fine = 0.5 + 0.5 * noise.noise(Vector((u * 2.2, w * 1.4, 7.7)))
    return clump ** 1.4 * 0.75 + fine * 0.25, f


def displace(bm):
    bm.normal_update()
    moves = {}
    for v in bm.verts:
        p, n = v.co.copy(), v.normal.copy()
        amt = hair_length(p)
        if amt <= 0.0:
            moves[v] = Vector((0, 0, 0))
            continue
        pat, f = lock_pattern(p, n)
        d = n * amt * (0.25 + 0.75 * pat) + FLOW * amt * 0.6 * pat
        d += n * amt * 0.35 * noise.noise(p * 3.0)
        moves[v] = d
    for v, d in moves.items():
        v.co += d
    hair = [v for v in bm.verts if hair_length(v.co) > 0.02]
    for _ in range(2):
        bmesh.ops.smooth_vert(bm, verts=hair, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.normal_update()


def trunk_param(p):
    """(distance to trunk axis, arc position 0..1)."""
    best = (1e9, 0.0)
    total = len(TRUNK) - 1
    for i in range(total):
        a, c = Vector(TRUNK[i]), Vector(TRUNK[i + 1])
        ab = c - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
        d = (a + ab * t - p).length
        if d < best[0]:
            best = (d, (i + t) / total)
    return best


def coat_color(p, n):
    pat, _ = lock_pattern(p, n)
    c = nh.lerp(UNDERFUR, COAT, 0.4 + 0.6 * pat)
    c = nh.lerp(c, COAT_TIP, 0.45 * pat * pat * nh.smoothstep(0.0, 0.8, n.z + 0.3))
    c = nh.lerp(c, UNDERFUR, 0.3 * nh.smoothstep(-0.2, -0.8, n.z))
    c = nh.lerp(c, COAT_TIP, 0.15 * max(0.0, noise.noise(p * 4.0)))
    d, s = trunk_param(p)
    if d < 0.16 and p.y < -0.88:
        c = nh.lerp(c, SKIN, nh.smoothstep(0.5, 0.85, s))
    c = nh.lerp(c, SKIN, nh.smoothstep(0.14, 0.06, p.z))
    return c


# ---------------------------------------------------------------- details

def tusks(mb):
    for s in (-1, 1):
        # out and down from the sockets, sweeping forward and up, then curling inward
        pts = [(s * 0.12, -0.85, 1.07), (s * 0.15, -0.95, 0.90), (s * 0.24, -1.08, 0.74),
               (s * 0.36, -1.24, 0.70), (s * 0.44, -1.40, 0.80), (s * 0.43, -1.53, 1.00),
               (s * 0.32, -1.58, 1.18), (s * 0.18, -1.52, 1.28)]
        rad = [0.058, 0.055, 0.051, 0.046, 0.040, 0.032, 0.020, 0.0]

        def color(co, n):
            return nh.lerp(IVORY_BASE, IVORY, nh.smoothstep(-0.95, -1.2, co.y))
        mb.add(smooth_tube(pts, rad, steps=5, sides=12), color)


def build():
    b = Parts()
    torso(b)
    skirt(b)
    for name in LEGS:
        leg(b, name)
    head(b)
    tail(b)
    fused = b.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5)
    displace(fused)
    fused = decimate(fused, BODY_TRIS)

    mb = nh.MeshBuilder()
    mb.add(fused, coat_color)
    for s in (-1, 1):
        mb.add(oriented((s * 0.19, -0.86, 1.30), (0.02, 0.026, 0.018), yaw=s * 30, segments=10, rings=6), EYE)
    tusks(mb)
    for name, (x, y, stride, top) in LEGS.items():
        front = y < 0
        r = 0.12 if front else 0.11
        for k in range(4 if front else 3):
            a = math.radians((-45 + k * 30) if front else (-35 + k * 35))
            cx, cy = x + math.sin(a) * r * 1.08, y + stride - 0.01 - math.cos(a) * r * 1.12
            mb.add(oriented((cx, cy, 0.035), (0.032, 0.02, 0.025), yaw=math.degrees(a), segments=10, rings=6), NAIL)
    # tail tuft of long dark hair
    for k in range(7):
        a = k / 7 * math.tau
        base = Vector((0, 0.69, 0.82))
        mb.add(nh.tube([base, base + Vector((math.cos(a) * 0.03, 0.02 + math.sin(a) * 0.02, -0.14))],
                       [0.012, 0.0], sides=4), UNDERFUR)

    obj = mb.to_object("WoollyMammoth", roughness=0.9)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "WoollyMammoth", ground=(0.80, 0.82, 0.84), views=((35, 22), (-90, 6), (20, 60), (0, 8)))
