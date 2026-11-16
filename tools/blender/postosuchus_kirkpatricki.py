"""
Procedural Postosuchus kirkpatricki (Late Triassic rauisuchian, ~4.5 m) for map colonies.

A heavy-bodied pseudosuchian (on the crocodile-line of archosaurs) and the apex predator
of the Late Triassic of the American south-west, caught mid-stride on all fours. Unlike
sprawling crocodiles its limbs are columnar, held straight beneath the body; the hind
legs are long and strong, the forelimbs clearly shorter, so the back slopes up from the
shoulders to the high hips. A deep, barrel chest, a thick neck and a long, heavy tail
held clear of the ground. The skull is large, deep and narrow, with a convex snout, a
slightly down-turned tip and a deep lower jaw, the mouth a little open to show big,
laterally flattened, recurved (serrated) teeth. Two rows of bony osteoderm plates
(scutes) run side by side down the midline from the neck to the end of the tail.
Body, legs, neck and head are fused into one seamless surface and sculpted by
displacement: pebbly scales, a large antorbital depression and a lip groove. Painted
dark grey-brown above, sandy olive flanks with faint darker bands and a pale belly, a
reddish flush on the face.
Crisp details on top: lower jaw, teeth, osteoderms, eyes, nostrils and claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/postosuchus_kirkpatricki.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Postosuchus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

NAME = "Postosuchus"

BACK = (0.27, 0.24, 0.18)       # dark grey-brown
FLANK = (0.52, 0.46, 0.32)      # sandy olive
BELLY = (0.80, 0.74, 0.58)
STRIPE = (0.20, 0.17, 0.12)
LEG = (0.40, 0.35, 0.25)
FACE = (0.56, 0.28, 0.17)       # reddish flush
LIP = (0.14, 0.11, 0.08)
SCUTE = (0.22, 0.19, 0.14)
SCUTE_KEEL = (0.38, 0.33, 0.24)
MOUTH = (0.50, 0.18, 0.16)
TOOTH = (0.94, 0.90, 0.78)
CLAW = (0.10, 0.08, 0.06)
EYE = (0.84, 0.58, 0.12)
PUPIL = (0.02, 0.02, 0.02)

LIFT = 0.10   # raises body/neck/head above the original layout so the legs get longer


# ---------------------------------------------------------------- geometry helpers

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


def densify(sections, steps):
    """Catmull-Rom resample of a loft path."""
    vals = [(Vector(c), a, b) for c, a, b in sections]
    out = []
    for i in range(len(vals) - 1):
        p0, p1 = vals[max(0, i - 1)], vals[i]
        p2, p3 = vals[i + 1], vals[min(len(vals) - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            t2, t3 = t * t, t * t * t

            def cr(a, b, c, d):
                return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
            ra = max(0.0, cr(p0[1], p1[1], p2[1], p3[1]))
            rb = max(0.0, cr(p0[2], p1[2], p2[2], p3[2]))
            out.append((tuple(cr(p0[0], p1[0], p2[0], p3[0])), ra, rb))
    out.append((tuple(vals[-1][0]), vals[-1][1], vals[-1][2]))
    return out


def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=18, rings=12):
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings)
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


def cone(base, tip, r, sides=6):
    return nh.tube([base, tip], [r, 0.0], sides=sides)


# ---------------------------------------------------------------- anatomy

def tail_x(y):
    """The tail swings a little to one side, mid-stride."""
    s = max(0.0, (y - 0.35) / 0.85)
    return 0.12 * s * s


def L(sections):
    return [((c[0], c[1], c[2] + LIFT), a, b) for c, a, b in sections]


# head base -> thick neck -> deep chest -> high hips -> long heavy tail
TORSO = L([
    ((0.0, -0.60, 0.565), 0.072, 0.088),
    ((0.0, -0.54, 0.550), 0.085, 0.105),
    ((0.0, -0.47, 0.525), 0.105, 0.128),
    ((0.0, -0.38, 0.495), 0.130, 0.165),
    ((0.0, -0.25, 0.480), 0.150, 0.190),
    ((0.0, -0.08, 0.485), 0.155, 0.190),
    ((0.0, 0.08, 0.505), 0.145, 0.170),
    ((0.0, 0.22, 0.520), 0.132, 0.150),
    ((tail_x(0.36), 0.36, 0.510), 0.100, 0.115),
    ((tail_x(0.52), 0.52, 0.480), 0.076, 0.087),
    ((tail_x(0.70), 0.70, 0.430), 0.055, 0.062),
    ((tail_x(0.88), 0.88, 0.365), 0.037, 0.041),
    ((tail_x(1.04), 1.04, 0.300), 0.022, 0.024),
    ((tail_x(1.16), 1.16, 0.250), 0.010, 0.011),
    ((tail_x(1.22), 1.22, 0.230), 0.0, 0.0),
])

# Large, deep, narrow skull with a convex snout (y, top z, upper lip z, half width)
SKULL_ROWS = [
    (-0.585, 0.665, 0.462, 0.080),
    (-0.64, 0.700, 0.452, 0.084),
    (-0.69, 0.696, 0.446, 0.076),
    (-0.74, 0.674, 0.443, 0.064),
    (-0.79, 0.650, 0.442, 0.055),
    (-0.84, 0.628, 0.442, 0.049),
    (-0.88, 0.612, 0.441, 0.046),
    (-0.915, 0.594, 0.438, 0.042),
    (-0.945, 0.566, 0.437, 0.034),
    (-0.962, 0.530, 0.440, 0.020),
    (-0.968, 0.498, 0.444, 0.008),
]
JAW_ROWS = [  # lower jaw (y, lip z, bottom z, half width), deep behind
    (-0.58, 0.466, 0.366, 0.076),
    (-0.66, 0.452, 0.378, 0.074),
    (-0.74, 0.446, 0.394, 0.060),
    (-0.82, 0.444, 0.402, 0.050),
    (-0.89, 0.442, 0.404, 0.043),
    (-0.93, 0.443, 0.406, 0.036),
    (-0.952, 0.446, 0.418, 0.020),
]
HINGE = Vector((0.0, -0.60, 0.455 + LIFT))
JAW_ROT = Matrix.Translation(HINGE) @ Matrix.Rotation(math.radians(12), 4, "X") @ Matrix.Translation(-HINGE)
EYE_Y = -0.675


def row_at(rows, y):
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k + LIFT, b0 + (b1 - b0) * k + LIFT, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1] if y < rows[-1][0] else rows[0]
    return t + LIFT, b + LIFT, w


def profile(rows, wk=1.0):
    return [((0.0, y, (top + bot) * 0.5 + LIFT), w * wk, (top - bot) * 0.5) for y, top, bot, w in rows]


LEG_DATA = []   # (side, foot centre, toe angles, toe lengths, toe radius)
HIP_Z = 0.52 + LIFT


def limbs(b):
    for s, ph in ((1, 1.0), (-1, -1.0)):
        # forelimb: shorter, columnar, straight under the shoulder
        sh = Vector((s * 0.115, -0.36, 0.43 + LIFT))
        el = Vector((s * 0.150, -0.33 + 0.02 * ph, 0.28))
        wr = Vector((s * 0.148, -0.38 - 0.05 * ph, 0.065))
        b.add(oriented((s * 0.11, -0.35, 0.44 + LIFT), (0.075, 0.12, 0.13), pitch=-15), LEG)
        b.add(nh.tube([sh, sh.lerp(el, 0.5), el], [0.074, 0.062, 0.050], sides=14), LEG)
        b.add(oriented(el, (0.048, 0.052, 0.050)), LEG)
        b.add(nh.tube([el, el.lerp(wr, 0.45), wr], [0.048, 0.042, 0.032], sides=12), LEG)
        hand = Vector((wr.x, wr.y - 0.035, 0.024))
        b.add(nh.tube([wr, hand + Vector((0, 0.01, 0.006))], [0.032, 0.03], sides=10), LEG)
        b.add(oriented(hand, (0.040, 0.050, 0.022)), LEG)
        LEG_DATA.append((s, hand, (-28, -12, 2, 16, 30), (0.036, 0.046, 0.050, 0.044, 0.030), 0.012))
        # hind limb: long and strong, knee forward, ankle back
        hip = Vector((s * 0.120, 0.22, HIP_Z - 0.03))
        kn = Vector((s * 0.160, 0.13 - 0.06 * ph, 0.34))
        an = Vector((s * 0.158, 0.27 - 0.08 * ph, 0.095))
        b.add(oriented((s * 0.115, 0.22, HIP_Z - 0.06), (0.090, 0.18, 0.17), pitch=25), LEG)  # thigh
        b.add(nh.tube([hip, hip.lerp(kn, 0.5), kn], [0.090, 0.075, 0.056], sides=14), LEG)
        b.add(oriented(kn, (0.056, 0.058, 0.058)), LEG)
        b.add(nh.tube([kn, kn.lerp(an, 0.5), an], [0.056, 0.046, 0.034], sides=12), LEG)
        b.add(oriented(kn.lerp(an, 0.3) + Vector((0, 0.02, 0)), (0.048, 0.06, 0.08), pitch=-30), LEG)  # calf
        foot = Vector((an.x, an.y - 0.075, 0.024))
        b.add(nh.tube([an, an.lerp(foot, 0.5) + Vector((0, 0.008, 0)), foot + Vector((0, 0.02, 0.006))],
                      [0.034, 0.031, 0.029], sides=10), LEG)
        b.add(oriented(foot, (0.045, 0.070, 0.024)), LEG)
        LEG_DATA.append((s, foot, (-24, -8, 6, 20), (0.060, 0.074, 0.074, 0.060), 0.0135))


def toes(b):
    out = []
    for s, palm, angs, lens, r in LEG_DATA:
        for ang, ln in zip(angs, lens):
            a = math.radians(ang)
            d = Vector((s * math.sin(a), -math.cos(a), 0.0))
            base = palm + d * 0.03
            tip = base + d * ln + Vector((0, 0, -0.008))
            b.add(nh.tube([base, base + d * ln * 0.55 + Vector((0, 0, 0.004)), tip], [r, r * 0.85, r * 0.62],
                          sides=8), LEG)
            out.append((tip, d, r))
    return out


# ---------------------------------------------------------------- skin

def lip_dist(co):
    """0 on the mouth line along the side of the head, 1 away from it."""
    if co.y > -0.62 or co.y < -0.97:
        return 1.0
    _t, lip, w = row_at(SKULL_ROWS, co.y)
    if abs(co.x) < w * 0.45:
        return 1.0
    return min(1.0, abs(co.z - lip) / 0.008)


def fenestra(co):
    """1 inside the big antorbital opening on the side of the snout."""
    if not (-0.84 < co.y < -0.70):
        return 0.0
    top, lip, w = row_at(SKULL_ROWS, co.y)
    cz = lip + (top - lip) * 0.52
    r = math.hypot((co.y + 0.77) / 0.065, (co.z - cz) / 0.045)
    return 1.0 - nh.smoothstep(0.55, 1.0, r)


def sculpt(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        co, n = v.co, v.normal
        d = 0.0018 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 55.0)))
        d += 0.0012 * noise.noise(co * 25.0)
        d -= 0.005 * (1.0 - lip_dist(co))
        d -= 0.016 * fenestra(co) * nh.smoothstep(0.4, 0.8, abs(n.x))
        if co.y < -0.62 and co.z > 0.5 + LIFT:       # rugose skull roof
            d += 0.002 * noise.noise(Vector((co.x * 60.0, co.y * 30.0, co.z * 60.0)))
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def body_paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.7, -0.15, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.2, 0.85, n.z))
    if co.z < 0.30:
        c = nh.lerp(LEG, c, nh.smoothstep(0.12, 0.30, co.z))
    # faint dark bands across the flanks and tail
    if co.y > -0.5:
        wob = noise.noise(co * 5.0) * 1.2
        band = 0.5 + 0.5 * math.sin(co.y * 22.0 + wob)
        side = nh.smoothstep(-0.35, 0.2, n.z) * nh.smoothstep(0.25, 0.40, co.z)
        c = nh.lerp(c, STRIPE, 0.45 * nh.smoothstep(0.7, 0.92, band) * side)
    if co.y < -0.58:
        f = nh.smoothstep(-0.58, -0.75, co.y) * nh.smoothstep(-0.5, 0.2, n.z) * (1.0 - nh.smoothstep(0.4, 0.9, n.z))
        c = nh.lerp(c, FACE, 0.4 * f)
        _t, lip, w = row_at(SKULL_ROWS, co.y)
        if co.z < lip - 0.004:
            c = nh.lerp(c, BELLY, 0.45 * nh.smoothstep(lip - 0.004, lip - 0.04, co.z))
        c = nh.lerp(c, LIP, 0.85 * (1.0 - lip_dist(co)))
        c = nh.lerp(c, LIP, 0.55 * fenestra(co))
    m = noise.noise(co * 14.0)
    k = (1.0 + 0.08 * m) * (0.95 + 0.08 * (1.0 - nh.smoothstep(0.1, 0.6, noise.cell(co * 55.0))))
    return tuple(max(0.0, x * k) for x in c)


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal


def blade(base, down, ln, r, back=0.35):
    """Laterally flattened, recurved tooth: wide fore-aft, thin side to side."""
    tip = base + down * ln + Vector((0, back * ln * 0.5, 0))
    mid = base + down * ln * 0.5 + Vector((0, -0.12 * ln, 0))
    return nh.tube([base, mid, tip], [r, r * 0.75, 0.0], sides=8, scale_xy=(1.0, 0.45))


def teeth(mb, surf, jaw_surf):
    # upper: big blades, largest under the front of the maxilla
    y = -0.955
    while y < -0.66:
        _t, lip, w = row_at(SKULL_ROWS, y)
        t = (y + 0.955) / 0.295
        ln = 0.032 + 0.026 * math.sin(min(1.0, t * 1.8) * math.pi * 0.5) * (1.0 - 0.7 * t)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.76, y, lip - 0.1), (0, 0, 1))
            if loc is None or loc.z > lip + 0.04:
                continue
            mb.add(blade(loc + Vector((0, 0, 0.007)), Vector((0, 0, -1)), ln, 0.0105), TOOTH, smooth=False)
        y += 0.033
    up = JAW_ROT.to_3x3() @ Vector((0, 0, 1))
    y = -0.94
    while y < -0.70:
        jt, _jb, jw = row_at(JAW_ROWS, y)
        for sx in (1, -1):
            loc, _n = jaw_surf.hit(JAW_ROT @ Vector((sx * jw * 0.66, y, jt + 0.1)), -up)
            if loc is None:
                continue
            mb.add(blade(loc - up * 0.006, up, 0.030, 0.009, back=0.2), TOOTH, smooth=False)
        y += 0.034


def scutes(mb, surf):
    """Two rows of paramedian osteoderms side by side from the neck down the tail."""
    y = -0.56
    while y < 1.12:
        t = max(0.0, (y - 0.2) / 0.95)
        size = 1.0 - 0.6 * t
        if y < -0.45:
            size *= 0.8
        for sx in (1, -1):
            x = tail_x(y) + sx * 0.032 * size
            loc, n = surf.hit((x, y, 1.5), (0, 0, -1))
            if loc is None:
                continue
            rx, ry, rz = 0.031 * size, 0.031 * size, 0.0055 * size
            plate = nh.uv_ellipsoid((0, 0, 0), (1, 1, 1), segments=10, rings=6)
            for v in plate.verts:   # squared-off, flat plate with a low median keel
                ux, uy, uz = v.co
                v.co = Vector((math.copysign(abs(ux) ** 0.55, ux) * rx, math.copysign(abs(uy) ** 0.55, uy) * ry,
                               uz * rz + max(0.0, uz) * rz * 1.4 * max(0.0, 1.0 - abs(ux) * 2.2)))
            # tilt the outer edge down with the body curve
            rot = Vector((0, 0, 1)).rotation_difference(n).to_matrix().to_4x4()
            nh.transform(plate, Matrix.Rotation(-sx * 0.25, 4, "Y"))
            nh.transform(plate, rot)
            nh.transform(plate, Matrix.Translation(loc + n * 0.002 * size))

            def col(co, _nn, c=loc, up=n.copy(), k=size):
                return nh.lerp(SCUTE, SCUTE_KEEL, nh.smoothstep(0.006 * k, 0.011 * k, (co - c).dot(up)))
            mb.add(plate, col)
        y += 0.068 * (1.0 - 0.45 * t)


def head_details(mb):
    top, lip, w = row_at(SKULL_ROWS, EYE_Y)
    for sx in (1, -1):
        e = Vector((sx * w * 0.80, EYE_Y, top - 0.05))
        mb.add(nh.ellipsoid(e, (0.018, 0.022, 0.018), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.012, -0.003, 0)), (0.006, 0.009, 0.013), subdivisions=2), PUPIL)
        t2, l2, w2 = row_at(SKULL_ROWS, -0.945)
        mb.add(nh.ellipsoid((sx * w2 * 0.6, -0.945, t2 - 0.018), (0.006, 0.010, 0.007), subdivisions=1), PUPIL)


def claws(mb, tips):
    for tip, d, r in tips:
        base = tip - d * 0.006 + Vector((0, 0, 0.005))
        end = tip + d * 0.026 + Vector((0, 0, -0.010))
        mb.add(nh.tube([base, base + d * 0.012, end], [r * 0.65, r * 0.48, 0.0], sides=6), CLAW)


# ---------------------------------------------------------------- build / preview

def build():
    LEG_DATA.clear()
    b = nh.MeshBuilder()
    b.add(loft(densify(TORSO, 4), sides=24, power=2.1), FLANK)
    b.add(loft(densify(profile(SKULL_ROWS), 3), sides=20, power=2.6), FLANK)
    b.add(oriented((0, -0.585, 0.47 + LIFT), (0.08, 0.08, 0.085)), FLANK)                 # throat
    for sx in (1, -1):
        b.add(oriented((sx * 0.055, -0.605, 0.57 + LIFT), (0.04, 0.06, 0.06)), FLANK)     # jaw muscles
        b.add(oriented((sx * 0.052, EYE_Y, row_at(SKULL_ROWS, EYE_Y)[0] - 0.04), (0.026, 0.04, 0.022)), FLANK)  # brow
        b.add(oriented((sx * 0.08, -0.33, 0.44 + LIFT), (0.09, 0.14, 0.15)), FLANK)       # chest
        b.add(oriented((sx * 0.08, 0.42, 0.50 + LIFT), (0.06, 0.20, 0.09)), FLANK)        # tail-base muscle
    limbs(b)
    claw_tips = toes(b)
    fused = b.fuse(voxel=0.0075, smooth=5, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, 14500)

    jb = nh.MeshBuilder()
    jb.add(loft(densify(profile(JAW_ROWS, 0.95), 3), sides=18, power=2.4), FLANK)
    jfused = nh.transform(decimate(jb.fuse(voxel=0.006, smooth=4, smooth_factor=0.5), 1800), JAW_ROT)

    surf, jaw_surf = Surface(fused), Surface(jfused)
    mb = nh.MeshBuilder()
    teeth(mb, surf, jaw_surf)
    scutes(mb, surf)
    mb.add(fused, body_paint)
    mb.add(jfused, lambda co, n: nh.lerp(body_paint(co, n), BELLY, 0.5 * nh.smoothstep(0.1, -0.7, n.z)))
    mb.add(oriented((0, -0.77, 0.44 + LIFT), (0.045, 0.17, 0.010), pitch=-6, segments=14, rings=6), MOUTH)
    head_details(mb)
    claws(mb, claw_tips)
    obj = mb.to_object(NAME, roughness=0.65)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"  height {max(zs):.3f}, hip {HIP_Z:.3f} -> hip fraction {HIP_Z / max(zs):.2f}")
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head = Vector((0.0, -0.78, 0.54 + LIFT))
    out = Path(path)
    for i, off in enumerate((Vector((0.55, -0.55, 0.16)), Vector((-0.70, -0.12, 0.02)))):
        cam.location = head + off
        cam.rotation_euler = (head - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.48, 0.38, 0.28), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
