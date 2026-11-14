"""
Procedural Ankylosaurus magniventris for map colonies.

A low, very broad tank of a body slung between short, stout, slightly sprawled
legs on blunt hoofed toes. The back is a shield of keeled oval osteoderms in
transverse rows, with two bony half-rings over the neck and a fringe of
triangular spikes along the flanks; the stiffened tail carries paired flat
side spikes and ends in a heavy, two-lobed bony club. The head is short, wide
and triangular, with pyramidal squamosal horns jutting back from its corners,
quadratojugal horns pointing down behind the cheeks, a knobbly armoured roof
and a narrow beak.
Earthy brown hide with a paler belly; osteoderms darker with pale, worn keels.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ankylosaurus_magniventris.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ankylosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

HIDE = (0.46, 0.36, 0.24)       # earthy brown
HIDE_DARK = (0.30, 0.22, 0.14)
BELLY = (0.68, 0.58, 0.42)
PLATE = (0.34, 0.26, 0.17)
KEEL = (0.74, 0.66, 0.50)
SPIKE_TIP = (0.86, 0.80, 0.66)
HOOF = (0.16, 0.13, 0.10)
BEAK = (0.18, 0.15, 0.11)
EYE = (0.60, 0.40, 0.12)
PUPIL = (0.03, 0.02, 0.02)

BODY_C = Vector((0.0, 0.04, 0.40))
BODY_R = Vector((0.46, 0.60, 0.21))


# ---------------------------------------------------------------- helpers

def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14, deform=None):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings, deform=deform)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def frame(normal, forward=Vector((0, 1, 0))):
    """Rotation whose local Z is `normal` and local Y follows `forward` as closely as possible."""
    n = normal.normalized()
    f = (forward - n * forward.dot(n)).normalized()
    s = f.cross(n)
    return Matrix((s, f, n)).transposed().to_4x4()


def paint_local(bm, fn):
    """Bake colours from the primitive's local (unposed) coordinates into its "Col" layer."""
    col = bm.loops.layers.color.new("Col")
    for f in bm.faces:
        for l in f.loops:
            c = fn(l.vert.co)
            l[col] = (c[0], c[1], c[2], 1.0)


def scute(pos, normal, r, length=1.25, keel=0.9, forward=Vector((0, 1, 0))):
    """Low oval osteoderm with a sharp keel along its length, lying on the surface at pos.
    Dark bone with a pale, worn keel crest."""
    def kd(n):
        return 1.0 + keel * max(0.0, n.z) ** 2 * (1.0 - abs(n.x)) ** 5
    h = r * 0.24
    bm = nh.uv_ellipsoid((0, 0, 0), (r, r * length, h), segments=8, rings=5, deform=kd)
    paint_local(bm, lambda co: nh.lerp(PLATE, KEEL, nh.smoothstep(h * 1.0, h * (1.0 + keel * 0.8), co.z)))
    nh.transform(bm, frame(normal, forward))
    nh.transform(bm, Matrix.Translation(pos - normal * h * 0.3))
    return bm


def spike(base, direction, r, length, flat=0.45):
    """Flattened triangular spike (flat in the plane of direction and the body forward axis)."""
    d = direction.normalized()
    bm = nh.tube([Vector((0, 0, 0)), Vector((0, 0, length * 0.55)), Vector((0, 0, length))],
                 [r, r * 0.55, 0.0], sides=8, scale_xy=(1.0, flat))
    paint_local(bm, lambda co: nh.lerp(PLATE, SPIKE_TIP, nh.smoothstep(length * 0.15, length * 0.9, co.z)))
    nh.transform(bm, frame(d, Vector((0, 1, 0))))
    nh.transform(bm, Matrix.Translation(base))
    return bm


def body_surface(y, a):
    """Point and normal on the body ellipsoid at length y, angle a from the top (+ = toward +X)."""
    t = (y - BODY_C.y) / BODY_R.y
    k = math.sqrt(max(0.0, 1.0 - t * t))
    p = Vector((BODY_R.x * k * math.sin(a), y, BODY_C.z + BODY_R.z * k * math.cos(a)))
    g = Vector(((p.x - BODY_C.x) / BODY_R.x ** 2, (p.y - BODY_C.y) / BODY_R.y ** 2, (p.z - BODY_C.z) / BODY_R.z ** 2))
    return p, g.normalized()


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


# ---------------------------------------------------------------- anatomy

SKULL_ROWS = [  # (y, top z, bottom z, half width): broad behind, tapering to a narrow beak
    (-0.50, 0.47, 0.29, 0.16),
    (-0.57, 0.50, 0.27, 0.225),
    (-0.64, 0.50, 0.27, 0.22),
    (-0.72, 0.48, 0.28, 0.185),
    (-0.80, 0.45, 0.29, 0.135),
    (-0.87, 0.415, 0.30, 0.095),
    (-0.92, 0.38, 0.31, 0.062),
    (-0.945, 0.35, 0.32, 0.03),
]
TAIL = [(0, 0.48, 0.42), (0, 0.70, 0.40), (0, 0.92, 0.37), (0, 1.12, 0.34), (0, 1.30, 0.32)]
TAIL_R = [0.19, 0.12, 0.085, 0.06, 0.05]
CLUB_Y = 1.38


def row_at(rows, y):
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k, b0 + (b1 - b0) * k, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1]
    return t, b, w


def skull():
    bm = bmesh.new()
    sides = 20
    rings = []
    for y, t, b, w in SKULL_ROWS:
        zc, h = (t + b) * 0.5, (t - b) * 0.5
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            ca, sa = math.cos(a), math.sin(a)
            x = math.copysign(abs(ca) ** 0.7, ca) * w   # boxy, flat-topped skull
            z = math.copysign(abs(sa) ** 0.7, sa) * h
            ring.append(bm.verts.new((x, y, zc + z)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def leg(b, x, y, top_z, foot_y, r_top, r_foot, toes):
    sx = math.copysign(1, x)
    knee = Vector((x * 1.08, y + (foot_y - y) * 0.3, top_z * 0.5))
    foot = Vector((x * 1.05, foot_y, 0.04))
    b.add(nh.tube([(x * 0.85, y, top_z + 0.04), (x, y, top_z), tuple(knee), tuple(foot)],
                  [r_top * 0.9, r_top, r_top * 0.8, r_foot], sides=16), HIDE)
    b.add(oriented(tuple(knee), (r_top * 0.85, r_top * 0.9, r_top)), HIDE)
    b.add(oriented((foot.x, foot.y - 0.01, 0.035), (r_foot * 1.2, r_foot * 1.15, 0.04)), HIDE)
    hooves = []
    for i in range(toes):
        a = math.radians(-55 + 110 * i / (toes - 1))
        hooves.append(Vector((foot.x + math.sin(a) * r_foot * sx, foot.y - math.cos(a) * r_foot * 1.05, 0.02)))
    return hooves


# ---------------------------------------------------------------- armour

def armour():
    """[(bmesh, kind)] osteoderm details; kind picks the colouring."""
    out = []
    # cervical half-rings: two bony bands of big keeled plates over the neck
    for y, r in ((-0.50, 0.17), (-0.40, 0.21)):
        for k in range(-3, 4):
            a = k * 0.38
            p = Vector((math.sin(a) * r, y, 0.41 + math.cos(a) * r * 0.85))
            n = Vector((math.sin(a), -0.15, math.cos(a))).normalized()
            out.append((scute(p, n, 0.05, length=1.0, keel=1.8), "plate"))
    # dorsal shield: transverse rows of keeled ovals, big on top, smaller down the sides
    rows = 13
    for i in range(rows):
        y = -0.36 + i * 0.07
        cols = 9 if i % 2 == 0 else 8
        for j in range(cols):
            a = (j - (cols - 1) / 2) * 0.26
            p, n = body_surface(y, a)
            r = 0.046 * (1.0 - 0.3 * abs(a) / 1.1) * (1.0 - 0.35 * max(0.0, (i - 9) / 4))
            out.append((scute(p, n, r, length=1.3, keel=1.4), "plate"))
        # small pebbly scutes filling between rows on the flanks
        for sx in (-1, 1):
            p, n = body_surface(y + 0.035, sx * 1.42)
            out.append((scute(p, n, 0.022, length=1.0, keel=0.6), "plate"))
    # lateral spikes along the shell margin, largest at the shoulders
    for i in range(7):
        y = -0.36 + i * 0.13
        p, n = body_surface(y, 1.68)
        L = 0.21 - 0.016 * i
        for sx in (-1, 1):
            base = Vector((sx * p.x, p.y, p.z))
            d = Vector((sx * 1.0, 0.40 + 0.06 * i, -0.08))
            out.append((spike(base - d.normalized() * 0.03, d, 0.06, L, flat=0.35), "spike"))
    # tail: paired flat side spikes and small dorsal scutes
    for i in range(6):
        t = i / 5
        y = 0.62 + t * 0.62
        k = min(len(TAIL) - 2, int((y - 0.48) / 0.205))
        f = (y - TAIL[k][1]) / (TAIL[k + 1][1] - TAIL[k][1])
        z = TAIL[k][2] + (TAIL[k + 1][2] - TAIL[k][2]) * f
        r = TAIL_R[k] + (TAIL_R[k + 1] - TAIL_R[k]) * f
        for sx in (-1, 1):
            base = Vector((sx * r * 0.85, y, z))
            out.append((spike(base, Vector((sx, 0.8, 0.0)), 0.035, 0.11 - 0.05 * t, flat=0.35), "spike"))
        for sx in (-0.5, 0.5):
            out.append((scute(Vector((sx * r, y, z + r * 0.62)), Vector((sx * 1.2, 0, 1)), 0.026, keel=1.2), "plate"))
    # head horns: squamosal (back corners) and quadratojugal (below and behind the eyes)
    for sx in (-1, 1):
        out.append((spike(Vector((sx * 0.20, -0.56, 0.47)), Vector((sx * 0.9, 0.6, 0.1)), 0.06, 0.16, flat=0.8), "spike"))
        out.append((spike(Vector((sx * 0.20, -0.64, 0.31)), Vector((sx * 0.6, 0.25, -0.75)), 0.04, 0.10, flat=0.75), "spike"))
    # knobbly skull roof
    for y, x, r in ((-0.58, 0.0, 0.04), (-0.58, 0.09, 0.034), (-0.58, -0.09, 0.034), (-0.67, 0.05, 0.036),
                    (-0.67, -0.05, 0.036), (-0.75, 0.0, 0.034), (-0.75, 0.1, 0.026), (-0.75, -0.1, 0.026),
                    (-0.82, 0.0, 0.028)):
        t, bt, w = row_at(SKULL_ROWS, y)
        out.append((scute(Vector((x, y, t - 0.005)), Vector((x * 2.0, -0.2, 1.0)), r, length=1.0, keel=0.4), "plate"))
    return out


# ---------------------------------------------------------------- paint

def hide_paint(co, n):
    c = nh.lerp(BELLY, HIDE, nh.smoothstep(-0.7, -0.15, n.z))
    c = nh.lerp(c, HIDE_DARK, 0.4 * nh.smoothstep(0.4, 0.95, n.z))
    if co.z < 0.25 and abs(co.x) > 0.2:
        c = nh.lerp(HIDE_DARK, c, nh.smoothstep(0.03, 0.25, co.z))
    # the tail club is a solid mass of bone
    if co.y > CLUB_Y - 0.12:
        c = nh.lerp(c, PLATE, nh.smoothstep(CLUB_Y - 0.12, CLUB_Y - 0.06, co.y))
        c = nh.lerp(c, KEEL, 0.35 * nh.smoothstep(0.3, 0.9, n.z))
    m = noise.noise(co * 20.0)
    cell = noise.cell(co * 40.0)
    k = (1.0 + 0.08 * m) * (0.9 + 0.14 * (1.0 - nh.smoothstep(0.2, 0.7, cell)))
    return tuple(max(0.0, v * k) for v in c)


def build():
    b = nh.MeshBuilder()

    def flat_top(n):
        return 1.0 - 0.06 * max(0.0, n.z) ** 2 + 0.05 * max(0.0, -n.z) * (1.0 - abs(n.y))
    b.add(nh.uv_ellipsoid(tuple(BODY_C), tuple(BODY_R), segments=40, rings=24, deform=flat_top), HIDE)
    b.add(oriented((0, -0.36, 0.40), (0.24, 0.16, 0.16)), HIDE)                     # shoulders
    b.add(nh.tube([(0, -0.30, 0.42), (0, -0.44, 0.41), (0, -0.54, 0.39)], [0.19, 0.17, 0.15], sides=16), HIDE)  # neck
    b.add(skull(), HIDE)
    b.add(oriented((0, -0.75, 0.29), (0.11, 0.16, 0.035)), HIDE)                    # lower jaw
    b.add(nh.tube(TAIL, TAIL_R, sides=16, scale_xy=(1.0, 0.75)), HIDE)
    # tail club: two big lateral knobs and a smaller terminal one
    for sx in (-1, 1):
        b.add(oriented((sx * 0.09, CLUB_Y + 0.01, 0.32), (0.11, 0.13, 0.075), yaw=sx * 12), HIDE)
    b.add(oriented((0, CLUB_Y + 0.09, 0.32), (0.07, 0.08, 0.06)), HIDE)
    hooves = []
    for sx in (-1, 1):
        hooves += leg(b, sx * 0.25, -0.30, 0.34, -0.33, 0.10, 0.075, 5)
        b.add(oriented((sx * 0.24, 0.30, 0.38), (0.12, 0.18, 0.15)), HIDE)          # thigh
        hooves += leg(b, sx * 0.26, 0.32, 0.36, 0.35, 0.12, 0.085, 4)
    fused = b.fuse(voxel=0.009, smooth=5, smooth_factor=0.5)
    fused.normal_update()
    for v in fused.verts:
        v.co += v.normal * 0.003 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(v.co * 36.0)))
    fused = decimate(fused, 10000)

    mb = nh.MeshBuilder()
    mb.add(fused, hide_paint)

    for bm, kind in armour():
        mb.add(bm)

    for sx in (-1, 1):
        t, bt, w = row_at(SKULL_ROWS, -0.74)
        e = Vector((sx * (w - 0.01), -0.74, 0.40))
        mb.add(nh.ellipsoid(e, (0.018, 0.02, 0.014), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.01, -0.004, 0)), (0.007, 0.008, 0.009), subdivisions=1), PUPIL)
        mb.add(nh.ellipsoid((sx * 0.035, -0.935, 0.36), (0.012, 0.012, 0.014), subdivisions=1), PUPIL)  # nostril
    mb.add(nh.tube([(0, -0.90, 0.33), (0, -0.95, 0.32), (0, -0.975, 0.30)], [0.05, 0.035, 0.0], sides=10,
                   scale_xy=(1.0, 0.6)), BEAK)
    for p in hooves:
        mb.add(oriented(tuple(p), (0.034, 0.034, 0.026), segments=10, rings=6,
                        deform=lambda n: 1.0 - 0.3 * max(0.0, -n.z)), HOOF)

    obj = mb.to_object("Ankylosaurus", roughness=0.75)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Ankylosaurus", ground=(0.40, 0.42, 0.26), views=((35, 25), (-90, 6), (25, 65), (-30, 12)))
