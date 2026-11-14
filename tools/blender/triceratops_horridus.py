"""
Procedural Triceratops horridus for map colonies.

A heavy, barrel-bodied quadruped: hips carried higher than the shoulders, a
short thick tail, pillar-like hind legs and slightly bowed forelegs on broad,
hoofed toes. The huge head (about a third of the body length) has a deep
parrot-like beak, a short nose horn, two long brow horns curving forward and a
broad, solid bony frill tilted back over the neck, rimmed with epoccipital
knobs; pointed jugal flares stick out under the cheeks.
Grey-brown hide of large tubercle scales with darker bands across the back and
a paler belly; the frill is painted rust-orange with dark radial bars and a pale
rim, the horns and beak are dark keratin with ivory tips.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/triceratops_horridus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Triceratops.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

HIDE = (0.44, 0.39, 0.29)       # grey-brown
HIDE_DARK = (0.26, 0.23, 0.17)
BELLY = (0.70, 0.64, 0.50)
FRILL = (0.70, 0.36, 0.14)      # rust-orange display frill
FRILL_BAR = (0.30, 0.14, 0.08)
FRILL_RIM = (0.88, 0.80, 0.62)
KERATIN = (0.16, 0.14, 0.11)
IVORY = (0.86, 0.80, 0.64)
HOOF = (0.18, 0.15, 0.12)
EYE = (0.55, 0.36, 0.10)
PUPIL = (0.03, 0.02, 0.02)

# frill frame: origin where the frill meets the back of the skull, leaning back over the neck
FRILL_ORIGIN = Vector((0.0, -0.57, 0.79))
FRILL_LEAN = math.radians(54)
FRILL_UP = Vector((0.0, math.sin(FRILL_LEAN), math.cos(FRILL_LEAN)))
FRILL_N = Vector((0.0, -math.cos(FRILL_LEAN), math.sin(FRILL_LEAN)))  # front face normal
FRILL_C, FRILL_A, FRILL_B = 0.25, 0.37, 0.31   # centre along FRILL_UP, half width, half height

# the whole head (skull, frill, horns, beak) is built at 1:1 then enlarged and tipped down about the occiput
HEAD_PIVOT = Vector((0.0, -0.52, 0.72))
HEAD = (Matrix.Translation(HEAD_PIVOT + Vector((0, -0.04, 0))) @ Matrix.Rotation(math.radians(6), 4, "X")
        @ Matrix.Scale(1.22, 4) @ Matrix.Translation(-HEAD_PIVOT))
HEAD_INV = HEAD.inverted()


# ---------------------------------------------------------------- helpers

def loft(sections, sides=18, power=2.0, ref=Vector((0, 0, 1))):
    """Skin superelliptic rings along a path. sections: (center, half width, half height)."""
    bm = bmesh.new()
    pts = [Vector(s[0]) for s in sections]
    rings = []
    for i, (c, ra, rb) in enumerate(sections):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = fwd.cross(ref).normalized()
        up = side.cross(fwd).normalized()
        if ra <= 1e-6:
            rings.append([bm.verts.new(Vector(c))])
            continue
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            ca, sa = math.cos(a), math.sin(a)
            x = math.copysign(abs(ca) ** (2.0 / power), ca) * ra
            y = math.copysign(abs(sa) ** (2.0 / power), sa) * rb
            ring.append(bm.verts.new(Vector(c) + side * x + up * y))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[k], b[(k + 1) % sides]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14, deform=None):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings, deform=deform)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def horn(points, radii, sides=12):
    return nh.tube(points, radii, sides=sides)


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


def frill_local(co):
    """(u across, v up the frill, w out of its front face) of a point."""
    d = HEAD_INV @ Vector(co) - FRILL_ORIGIN
    return d.x, d.dot(FRILL_UP), d.dot(FRILL_N)


def frill_cup(u):
    return 0.06 * (u / FRILL_A) ** 2


def frill_point(u, v, w=0.0):
    # the shield is gently cupped: its sides curl forward
    w += frill_cup(u)
    return FRILL_ORIGIN + Vector((u, 0, 0)) + FRILL_UP * v + FRILL_N * w


# ---------------------------------------------------------------- parts

SKULL_ROWS = [  # (y, top z, bottom z, half width)
    (-0.50, 0.84, 0.56, 0.17),
    (-0.60, 0.88, 0.50, 0.19),
    (-0.70, 0.88, 0.46, 0.185),
    (-0.80, 0.83, 0.44, 0.16),
    (-0.90, 0.76, 0.42, 0.125),
    (-0.98, 0.70, 0.41, 0.10),
    (-1.06, 0.63, 0.40, 0.078),
    (-1.12, 0.56, 0.40, 0.058),
    (-1.16, 0.49, 0.41, 0.036),
    (-1.175, 0.44, 0.43, 0.012),
]


def row_at(rows, y):
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k, b0 + (b1 - b0) * k, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1]
    return t, b, w


def skull():
    secs = [((0.0, y, (t + b) * 0.5), w, (t - b) * 0.5) for y, t, b, w in SKULL_ROWS]
    return loft(secs, sides=22, power=2.3)


def frill_plate():
    """Solid elliptical shield with a thickened rim, its bottom buried in the neck."""
    bm = bmesh.new()
    n_ring, n_rad = 40, 7
    th = 0.035
    top, bot = [], []
    centre_t = bm.verts.new(frill_point(0, FRILL_C, th))
    centre_b = bm.verts.new(frill_point(0, FRILL_C, -th))
    rings_t, rings_b = [], []
    for r in range(1, n_rad + 1):
        rt, rb = [], []
        f = r / n_rad
        for k in range(n_ring):
            a = k / n_ring * math.tau
            u = math.cos(a) * FRILL_A * f
            v = FRILL_C + math.sin(a) * FRILL_B * f
            t = th * (1.0 + 0.6 * nh.smoothstep(0.75, 1.0, f))
            rt.append(bm.verts.new(frill_point(u, v, t)))
            rb.append(bm.verts.new(frill_point(u, v, -t)))
        rings_t.append(rt)
        rings_b.append(rb)
    for rings, c, flip in ((rings_t, centre_t, False), (rings_b, centre_b, True)):
        for k in range(n_ring):
            j = (k + 1) % n_ring
            f = [c, rings[0][k], rings[0][j]]
            bm.faces.new(list(reversed(f)) if flip else f)
        for a, b in zip(rings, rings[1:]):
            for k in range(n_ring):
                j = (k + 1) % n_ring
                f = [a[k], b[k], b[j], a[j]]
                bm.faces.new(list(reversed(f)) if flip else f)
    for k in range(n_ring):
        j = (k + 1) % n_ring
        bm.faces.new([rings_t[-1][k], rings_b[-1][k], rings_b[-1][j], rings_t[-1][j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def epoccipitals():
    """Knobs around the frill margin (only on the part that stands free of the neck)."""
    out = []
    n = 26
    for k in range(n):
        a = k / n * math.tau
        u = math.cos(a) * FRILL_A * 1.0
        v = FRILL_C + math.sin(a) * FRILL_B * 1.0
        if v < 0.06:
            continue
        p = frill_point(u, v)
        out.append(oriented(tuple(p), (0.032, 0.03, 0.03), segments=10, rings=6))
    return out


def leg(b, x, y, hip_z, knee, foot, r_top, r_knee, r_foot, toes):
    """Pillar limb: upper muscle mass, joint, shank and a broad round foot with blunt hooved toes."""
    sx = math.copysign(1, x)
    top = Vector((x * 0.8, y, hip_z))
    k = Vector(knee)
    f = Vector(foot)
    b.add(nh.tube([top + Vector((0, 0, 0.08)), top, k], [r_top * 0.8, r_top, r_knee], sides=16), HIDE)
    b.add(nh.tube([k, k.lerp(f, 0.5), f + Vector((0, 0, 0.04))], [r_knee, r_knee * 0.85, r_foot], sides=16), HIDE)
    b.add(oriented(tuple(k), (r_knee * 1.1, r_knee * 1.15, r_knee * 1.3)), HIDE)   # joint, no crease
    b.add(oriented((f.x, f.y - 0.01, 0.045), (r_foot * 1.15, r_foot * 1.1, 0.05)), HIDE)
    hooves = []
    for i in range(toes):
        a = math.radians(-60 + 120 * i / (toes - 1))
        p = Vector((f.x + math.sin(a) * r_foot * 0.95 * sx, f.y - math.cos(a) * r_foot * 1.0, 0.025))
        hooves.append(p)
    return hooves


def H(bm):
    return nh.transform(bm, HEAD)


def build():
    b = nh.MeshBuilder()

    # barrel body, higher over the hips; belly hangs low
    def barrel(n):
        k = 1.0 + 0.10 * max(0.0, -n.z)                       # deep belly
        k *= 1.0 + 0.08 * max(0.0, n.y) * max(0.0, n.z)       # hips
        return k
    b.add(oriented((0, 0.08, 0.70), (0.34, 0.53, 0.33), pitch=-4, segments=32, rings=22, deform=barrel), HIDE)
    b.add(oriented((0, 0.32, 0.82), (0.27, 0.30, 0.22), pitch=8), HIDE)      # hips / sacrum
    b.add(oriented((0, -0.30, 0.70), (0.30, 0.30, 0.28)), HIDE)              # shoulders and chest
    # tail: short, thick, held off the ground
    b.add(nh.tube([(0, 0.50, 0.82), (0, 0.75, 0.74), (0, 0.98, 0.60), (0, 1.16, 0.46)],
                  [0.17, 0.12, 0.07, 0.0], sides=16), HIDE)
    # neck under the frill
    b.add(nh.tube([(0, -0.30, 0.78), (0, -0.48, 0.74), (0, -0.60, 0.70)], [0.24, 0.22, 0.2], sides=16), HIDE)

    # head
    b.add(H(skull()), HIDE)
    for sx in (-1, 1):
        b.add(H(oriented((sx * 0.135, -0.75, 0.80), (0.05, 0.06, 0.045))), HIDE)            # brow horn bosses
        b.add(H(nh.tube([(sx * 0.12, -0.64, 0.56), (sx * 0.22, -0.72, 0.47), (sx * 0.27, -0.75, 0.43)],
                      [0.06, 0.04, 0.0], sides=10)), HIDE)                                 # jugal flares
        b.add(H(oriented((sx * 0.13, -0.62, 0.60), (0.07, 0.10, 0.10))), HIDE)              # jaw muscles
    b.add(H(oriented((0, -0.86, 0.43), (0.10, 0.22, 0.06), pitch=-8)), HIDE)                 # lower jaw
    b.add(H(oriented((0, -1.00, 0.73), (0.05, 0.05, 0.05))), HIDE)                            # nose horn boss

    # beak: hooked rostral over the predentary (painted as keratin in paint())
    b.add(H(nh.tube([(0, -1.06, 0.62), (0, -1.15, 0.54), (0, -1.20, 0.45), (0, -1.195, 0.38)],
                    [0.06, 0.048, 0.03, 0.0], sides=14, scale_xy=(0.75, 1.0))), HIDE)
    b.add(H(nh.tube([(0, -0.98, 0.42), (0, -1.09, 0.415), (0, -1.17, 0.425)], [0.06, 0.042, 0.0], sides=12,
                    scale_xy=(1.0, 0.7))), HIDE)
    b.add(H(frill_plate()), HIDE)
    for e in epoccipitals():
        b.add(H(e), HIDE)

    # legs: forelimbs a little bowed, hind limbs columnar
    hooves = []
    for sx in (-1, 1):
        b.add(oriented((sx * 0.27, -0.30, 0.60), (0.11, 0.15, 0.17)), HIDE)              # upper arm
        hooves += leg(b, sx * 0.28, -0.30, 0.66, (sx * 0.33, -0.33, 0.34), (sx * 0.30, -0.36, 0.0),
                      0.13, 0.10, 0.085, 5)
        b.add(oriented((sx * 0.25, 0.34, 0.68), (0.14, 0.22, 0.24), pitch=10), HIDE)    # thigh
        hooves += leg(b, sx * 0.29, 0.36, 0.74, (sx * 0.30, 0.26, 0.40), (sx * 0.28, 0.42, 0.0),
                      0.17, 0.12, 0.095, 4)

    fused = b.fuse(voxel=0.0095, smooth=5, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, 21000)

    mb = nh.MeshBuilder()
    mb.add(fused, paint)

    # horns: two long brow horns curving forward, a short nose horn
    def horn_color(co, n, base_z=0.8, tip_z=1.15):
        return nh.lerp(KERATIN, IVORY, nh.smoothstep(base_z, tip_z, co.z))
    for sx in (-1, 1):
        pts = [(sx * 0.13, -0.74, 0.80), (sx * 0.15, -0.82, 0.92), (sx * 0.165, -0.94, 1.03),
               (sx * 0.17, -1.08, 1.09), (sx * 0.165, -1.20, 1.10)]
        mb.add(H(horn(pts, [0.058, 0.048, 0.036, 0.02, 0.0])), horn_color)
    mb.add(H(horn([(0, -1.00, 0.72), (0, -1.05, 0.79), (0, -1.09, 0.85)], [0.04, 0.025, 0.0])),
           lambda co, n: horn_color(co, n, 0.72, 0.86))
    for sx in (-1, 1):
        t, bt, w = row_at(SKULL_ROWS, -0.80)
        e = Vector((sx * (w - 0.005), -0.80, 0.72))
        mb.add(H(nh.ellipsoid(e, (0.022, 0.026, 0.018), subdivisions=2)), EYE)
        mb.add(H(nh.ellipsoid(e + Vector((sx * 0.012, -0.005, 0)), (0.008, 0.01, 0.012), subdivisions=1)), PUPIL)
        t, bt, w = row_at(SKULL_ROWS, -1.08)
        mb.add(H(nh.ellipsoid((sx * (w - 0.01), -1.08, 0.60), (0.01, 0.03, 0.018), subdivisions=2)), PUPIL)  # nostril
    for p in hooves:
        mb.add(oriented(tuple(p), (0.04, 0.04, 0.03), segments=10, rings=6,
                        deform=lambda n: 1.0 - 0.3 * max(0.0, -n.z)), HOOF)

    obj = mb.to_object("Triceratops", roughness=0.75)
    nh.ground_to_zero(obj)
    return obj


# ---------------------------------------------------------------- skin

def on_frill(co):
    """1 on the free-standing shield (either face), 0 on the neck and skull."""
    if co.z < 0.7:
        return 0.0
    u, v, w = frill_local(co)
    r = math.hypot(u / FRILL_A, (v - FRILL_C) / FRILL_B)
    near = 1.0 - nh.smoothstep(0.06, 0.1, abs(w - frill_cup(u)))
    return near * (1.0 - nh.smoothstep(1.02, 1.15, r)) * nh.smoothstep(0.02, 0.1, v)


def sculpt(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        co, n = v.co, v.normal
        # large tubercle scales, with bigger rosettes scattered across the flanks
        d = 0.003 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 34.0)))
        d += 0.0025 * (1.0 - nh.smoothstep(0.0, 0.3, noise.cell(co * 11.0 + Vector((3, 1, 7))))) * (co.y > -0.45)
        # radial grooves (blood-vessel channels) on the frill
        if co.z > 0.8:
            u, vv, w = frill_local(co)
            if vv > 0.1:
                ang = math.atan2(vv - FRILL_C * 0.3, u)
                d -= 0.003 * (0.5 + 0.5 * math.sin(ang * 22.0)) * nh.smoothstep(0.1, 0.3, vv)
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def paint(co, n):
    c = nh.lerp(BELLY, HIDE, nh.smoothstep(-0.65, -0.1, n.z))
    c = nh.lerp(c, HIDE_DARK, 0.55 * nh.smoothstep(0.4, 0.95, n.z))
    # dark bands across the back and tail
    if co.y > -0.4:
        band = 0.5 + 0.5 * math.sin(co.y * 17.0 + noise.noise(co * 4.0) * 1.5)
        c = nh.lerp(c, HIDE_DARK, 0.6 * nh.smoothstep(0.55, 0.85, band) * nh.smoothstep(0.0, 0.5, n.z))
    # legs darker toward the feet
    if co.z < 0.35:
        c = nh.lerp(HIDE_DARK, c, nh.smoothstep(0.05, 0.35, co.z))
    # frill display: orange with dark radial bars, a dark eye-spot band and a pale rim
    f = on_frill(co)
    if f > 0.0:
        u, v, w = frill_local(co)
        r = math.hypot(u / FRILL_A, (v - FRILL_C) / FRILL_B)
        fc = FRILL
        ang = math.atan2(v - FRILL_C * 0.3, u)
        bar = 0.5 + 0.5 * math.sin(ang * 11.0)
        fc = nh.lerp(fc, FRILL_BAR, 0.6 * nh.smoothstep(0.6, 0.9, bar) * nh.smoothstep(0.35, 0.6, r))
        fc = nh.lerp(fc, FRILL_BAR, 0.7 * (1.0 - nh.smoothstep(0.04, 0.1, abs(r - 0.72))))
        fc = nh.lerp(fc, FRILL_RIM, nh.smoothstep(0.86, 0.96, r))
        back = nh.smoothstep(0.2, -0.4, n.dot(FRILL_N))   # back of the frill stays hide coloured
        c = nh.lerp(c, nh.lerp(fc, HIDE_DARK, back * 0.8), f)
    # beak keratin
    loc = HEAD_INV @ Vector(co)
    beak = max(nh.smoothstep(-1.09, -1.12, loc.y), nh.smoothstep(-1.04, -1.08, loc.y) * nh.smoothstep(0.47, 0.44, loc.z))
    if beak > 0.0:
        return nh.lerp(HIDE_DARK, KERATIN, beak)
    # face: darker top of the snout
    if co.y < -0.7 and co.z > 0.5:
        c = nh.lerp(c, HIDE_DARK, 0.3 * nh.smoothstep(0.2, 0.8, n.z))
    m = noise.noise(co * 18.0)
    cell = noise.cell(co * 30.0)
    k = (1.0 + 0.08 * m) * (0.9 + 0.15 * (1.0 - nh.smoothstep(0.2, 0.7, cell)))
    return tuple(max(0.0, x * k) for x in c)


if __name__ == "__main__":
    nh.run(build, "Triceratops", ground=(0.36, 0.42, 0.26), views=((35, 22), (-90, 6), (25, 65), (-20, 10)))
