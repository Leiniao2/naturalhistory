"""
Procedural African bush elephant (Loxodonta africana) for map colonies.

A big bull mid-stride: deep barrel body with the saddle-shaped back that dips
behind the high shoulders, heavy pillar legs ending in round feet with pale
toenails, a high forehead with the two bulges over the trunk base, a long
ringed trunk that hangs down and curls forward at the tip, upward-curving ivory
tusks, and the huge Africa-shaped ears spread a little away from the shoulders.
A thin tail ends in a tuft of black hair.

The body, legs, head and trunk are built from overlapping parts and fused into
one seamless surface; the skin is then sculpted with a network of wrinkles
(deep rings across the trunk, folds at the knees and on the flanks) and painted
dusty grey with darker creases. Ears, tusks, eyes, toenails and the tail tuft
are crisp details on top.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/loxodonta_africana.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AfricanElephant.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

SKIN = (0.42, 0.40, 0.38)        # dusty grey
SKIN_DARK = (0.27, 0.25, 0.24)   # creases, wet-looking underside
SKIN_DUST = (0.55, 0.49, 0.42)   # reddish dust on the back
EAR_INNER = (0.48, 0.40, 0.39)   # pinkish-grey inside with veins
VEIN = (0.36, 0.28, 0.28)
IVORY = (0.92, 0.88, 0.76)
IVORY_BASE = (0.70, 0.62, 0.48)
NAIL = (0.70, 0.66, 0.58)
EYE = (0.10, 0.06, 0.04)
HAIR = (0.06, 0.05, 0.05)

VOXEL = 0.012
BODY_TRIS = 19000


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
    """Smooth resample of a polyline (and per-point radii packed as the 4th value)."""
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


# ---------------------------------------------------------------- anatomy

TRUNK = [(0, -0.93, 1.20), (0, -1.03, 1.05), (0, -1.07, 0.85), (0, -1.07, 0.62),
         (0, -1.06, 0.42), (0, -1.09, 0.27), (0, -1.15, 0.20), (0, -1.20, 0.22)]
TRUNK_R = [0.13, 0.11, 0.09, 0.075, 0.064, 0.056, 0.05, 0.046]

LEGS = {  # name: (x, y, stride) — walking: left-front and right-hind forward
    "lf": (-0.22, -0.36, -0.10), "rf": (0.22, -0.36, 0.06),
    "lh": (-0.22, 0.48, 0.05), "rh": (0.22, 0.48, -0.10),
}


def torso(b):
    def barrel(n):
        k = 1.0 + 0.06 * max(0.0, -n.z)              # sagging belly
        k *= 1.0 - 0.05 * max(0.0, n.z) * (1.0 - abs(n.y))  # saddle dip on the back
        return k
    b.add(oriented((0, 0.06, 1.03), (0.37, 0.66, 0.42), pitch=2, segments=28, rings=20, deform=barrel))
    b.add(oriented((0, -0.32, 1.12), (0.36, 0.34, 0.42)))           # deep chest, high shoulders
    b.add(oriented((0, -0.30, 1.44), (0.16, 0.20, 0.10)))           # withers peak
    b.add(oriented((0, 0.44, 1.10), (0.32, 0.30, 0.36)))            # rump
    b.add(oriented((0, 0.50, 1.36), (0.14, 0.16, 0.09)))            # hip bones
    b.add(oriented((0, 0.05, 0.70), (0.30, 0.48, 0.16)))            # belly
    for s in (-1, 1):
        b.add(oriented((s * 0.22, -0.38, 1.08), (0.15, 0.24, 0.32), pitch=-10))  # shoulder
        b.add(oriented((s * 0.21, 0.46, 1.05), (0.15, 0.26, 0.32), pitch=10))    # haunch


def leg(b, name):
    x, y, stride = LEGS[name]
    front = y < 0
    top = 1.0 if front else 0.98
    knee_z = 0.50 if front else 0.52
    r_top, r_knee, r_foot = (0.155, 0.12, 0.125) if front else (0.165, 0.115, 0.115)
    knee_y = y + stride * 0.5 + (0.0 if front else -0.03)
    pts = [(x * 0.95, y, top), (x, y + stride * 0.15, 0.75), (x, knee_y, knee_z),
           (x, y + stride * 0.85, 0.25), (x, y + stride, 0.07), (x, y + stride, 0.0)]
    radii = [r_top, r_top * 0.88, r_knee, r_knee * 0.93, r_foot, r_foot * 1.05]
    b.add(smooth_tube(pts, radii, steps=3, sides=18))
    b.add(oriented((x, knee_y - (0.02 if front else -0.02), knee_z), (r_knee * 1.05, r_knee * 1.0, 0.09)))
    # round foot pad
    b.add(oriented((x, y + stride - 0.01, 0.05), (r_foot * 1.12, r_foot * 1.18, 0.055)))


def head(b):
    b.add(oriented((0, -0.74, 1.34), (0.27, 0.28, 0.33), pitch=-15, segments=24, rings=16))  # cranium
    for s in (-1, 1):
        b.add(oriented((s * 0.09, -0.86, 1.38), (0.11, 0.10, 0.13), pitch=-25))  # forehead bulges
        b.add(oriented((s * 0.15, -0.80, 1.10), (0.10, 0.12, 0.10)))            # cheeks / tusk sheaths
        b.add(smooth_tube([(s * 0.13, -0.84, 1.08), (s * 0.135, -0.92, 0.97)], [0.065, 0.055], steps=1))
    b.add(oriented((0, -0.78, 1.00), (0.10, 0.10, 0.07)))                       # lower lip / chin
    b.add(smooth_tube([(0, -0.55, 1.18), (0, -0.68, 1.25)], [0.27, 0.25], steps=1, sides=18))  # neck
    b.add(smooth_tube(TRUNK, TRUNK_R, steps=4, sides=16))


def tail(b):
    pts = [(0, 0.70, 1.20), (0, 0.78, 1.05), (0, 0.80, 0.85), (0.02, 0.79, 0.68)]
    b.add(smooth_tube(pts, [0.04, 0.025, 0.018, 0.014], steps=3, sides=8))


# ---------------------------------------------------------------- skin

def trunk_param(p):
    """(distance to trunk axis, arc position 0..1) — for the trunk rings."""
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


def cracks(p, scale, width):
    """1 on the thin lines between voronoi cells (the cracked-mud pattern of elephant skin)."""
    d = noise.voronoi(p * scale)[0]
    return 1.0 - nh.smoothstep(0.0, width, d[1] - d[0])


def wrinkles(p, n):
    """0..1 crease depth at p."""
    w = 0.0
    d, s = trunk_param(p)
    if d < 0.16 and p.y < -0.88:
        ring = 0.5 + 0.5 * math.sin(s * 140.0 + noise.noise(p * 8.0) * 1.5)
        w = max(w, nh.smoothstep(0.75, 0.98, ring) * nh.smoothstep(0.02, 0.15, s))
    # cracked-mud network everywhere, coarse and fine
    w = max(w, 0.55 * cracks(p, 9.0, 0.06), 0.4 * cracks(p, 24.0, 0.06))
    # horizontal folds around the knees and ankles
    if p.z < 0.75:
        for x, y, stride in LEGS.values():
            if math.hypot(p.x - x, p.y - (y + stride * 0.5)) < 0.22:
                band = 0.5 + 0.5 * math.sin(p.z * 90.0 + noise.noise(p * 6.0) * 2.0)
                w = max(w, 0.9 * nh.smoothstep(0.75, 0.97, band) * nh.smoothstep(0.08, 0.2, p.z))
    # vertical folds on the neck behind the head
    if -0.66 < p.y < -0.48 and p.z > 0.9:
        w = max(w, 0.8 * nh.smoothstep(0.8, 0.97, 0.5 + 0.5 * math.sin(p.y * 150.0 + p.z * 8.0)))
    return w


def sculpt(bm):
    bm.normal_update()
    offs = []
    for v in bm.verts:
        p, n = v.co, v.normal
        d = -0.007 * wrinkles(p, n) + 0.002 * noise.noise(p * 7.0)
        offs.append((v, n * d))
    for v, o in offs:
        v.co += o
    bm.normal_update()


def skin_color(p, n):
    c = nh.lerp(SKIN, SKIN_DUST, 0.45 * nh.smoothstep(0.5, 0.95, n.z) * nh.smoothstep(1.1, 1.4, p.z))
    c = nh.lerp(c, SKIN_DARK, 0.45 * nh.smoothstep(-0.3, -0.85, n.z))
    c = nh.lerp(c, SKIN_DARK, 0.8 * wrinkles(p, n))
    # mud splash on the lower legs
    c = nh.lerp(c, SKIN_DUST, 0.35 * nh.smoothstep(0.35, 0.05, p.z))
    m = noise.noise(p * 5.0)
    return tuple(max(0.0, v * (1.0 + 0.08 * m)) for v in c)


# ---------------------------------------------------------------- details

EAR_SHAPE = [  # (back, up) control points, clockwise from the root: broad top, lobe hanging at the front
    (0.0, 0.12), (0.10, 0.22), (0.30, 0.25), (0.48, 0.20), (0.60, 0.06), (0.62, -0.12), (0.55, -0.30),
    (0.42, -0.42), (0.30, -0.50), (0.20, -0.64), (0.10, -0.70), (0.03, -0.62), (0.02, -0.40), (-0.02, -0.15),
]


def ear_outline():
    """Africa-shaped ear in local (u = back, v = up) coordinates, attached near u = 0."""
    closed = EAR_SHAPE + EAR_SHAPE[:3]
    pts = catmull([(u, v, 0.0) for u, v in closed], 4)
    pts = pts[4:4 + 4 * len(EAR_SHAPE)]  # one full loop, the end segments only steer the tangents
    return [tuple(p) for p in pts]


def ear(mb, s):
    bm = nh.flat_panel(ear_outline(), thickness=0.022)
    # cupped: the rim curls toward the body, the middle bulges out
    for v in bm.verts:
        u, w = v.co.x, v.co.y
        v.co.z += 0.03 * math.sin(math.pi * min(1.0, u / 0.58)) - 0.025 * (u / 0.58) ** 3 + 0.012 * math.sin(w * 6.0)
    # local x=back, y=up, z=out -> world
    rot = Matrix(((0, 0, s), (1, 0, 0), (0, 1, 0))).to_4x4()
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Rotation(math.radians(-s * 32), 4, "Z"))  # spread away from the shoulder
    nh.transform(bm, Matrix.Translation(Vector((s * 0.25, -0.70, 1.38))))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)  # the left ear's basis is a reflection

    def color(co, n):
        outward = n.x * s
        inner = nh.smoothstep(-0.1, -0.5, outward)  # faces the body
        c = nh.lerp(skin_color(co, n), EAR_INNER, inner)
        vein = 1.0 - nh.smoothstep(0.0, 0.12, noise.cell(co * 12.0))
        c = nh.lerp(c, VEIN if inner > 0.5 else SKIN_DARK, 0.6 * vein)
        return c
    mb.add(bm, color)
    # thick ear root blending into the head
    mb.add(oriented((s * 0.22, -0.69, 1.30), (0.05, 0.06, 0.15), yaw=-s * 25, segments=12, rings=8), skin_color)


def tusks(mb):
    for s in (-1, 1):
        pts = [(s * 0.13, -0.86, 1.06), (s * 0.15, -0.96, 0.92), (s * 0.17, -1.08, 0.82),
               (s * 0.19, -1.22, 0.80), (s * 0.19, -1.33, 0.86), (s * 0.18, -1.38, 0.93)]
        rad = [0.05, 0.047, 0.042, 0.035, 0.024, 0.0]

        def color(co, n):
            return nh.lerp(IVORY_BASE, IVORY, nh.smoothstep(-0.95, -1.15, co.y))
        mb.add(smooth_tube(pts, rad, steps=4, sides=12), color)


class Parts(nh.MeshBuilder):
    """Body builder: parts are plain skin until the fused surface is repainted."""

    def add(self, src, color=SKIN, smooth=True):
        super().add(src, color, smooth)


def build():
    b = Parts()
    torso(b)
    for name in LEGS:
        leg(b, name)
    head(b)
    tail(b)
    fused = b.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, BODY_TRIS)

    mb = nh.MeshBuilder()
    mb.add(fused, skin_color)
    for s in (-1, 1):
        ear(mb, s)
        # small eyes behind the trunk base, with a wrinkled lid ring
        mb.add(oriented((s * 0.195, -0.86, 1.25), (0.022, 0.03, 0.022), yaw=s * 30), SKIN_DARK)
        mb.add(oriented((s * 0.204, -0.868, 1.25), (0.014, 0.02, 0.016), yaw=s * 30), EYE)
    tusks(mb)
    # toenails: 4 on the front feet, 3 on the hind feet
    for name, (x, y, stride) in LEGS.items():
        front = y < 0
        r = 0.125 if front else 0.115
        for k in range(4 if front else 3):
            a = math.radians((-45 + k * 30) if front else (-35 + k * 35))
            cx, cy = x + math.sin(a) * r * 1.08, y + stride - 0.01 - math.cos(a) * r * 1.12
            mb.add(oriented((cx, cy, 0.035), (0.034, 0.02, 0.026), yaw=math.degrees(a), segments=10, rings=6), NAIL)
    # tail tuft
    for k in range(7):
        a = k / 7 * math.tau
        base = Vector((0.02, 0.79, 0.70))
        mb.add(nh.tube([base, base + Vector((math.cos(a) * 0.025, math.sin(a) * 0.02, -0.12))],
                       [0.008, 0.0], sides=4), HAIR)

    obj = mb.to_object("AfricanElephant", roughness=0.85)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "AfricanElephant", ground=(0.55, 0.48, 0.32), views=((35, 22), (-90, 6), (20, 60), (0, 8)))
