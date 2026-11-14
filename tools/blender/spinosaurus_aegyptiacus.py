"""
Procedural Spinosaurus aegyptiacus for map colonies.

Reconstructed after the 2014 / 2020 Kem Kem material: a long, low body carried
close to the ground on short hind legs with broad, flat-footed toes; robust
forelimbs with a big hooked thumb claw; a long neck and a low crocodile-like
skull with interlocking conical teeth, a notched snout ending in a rosette,
retracted nostrils and a small crest over the eyes. The tall dorsal sail rises
from the shoulders to the hips on rod-like spines, and the tail is a deep,
flexible paddle (tall neural spines above, chevrons below) for swimming.
Dark olive-grey back fading to a pale belly, a rust-red sail with dark spine
bars and a pale crown, faint banding on the tail fin.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/spinosaurus_aegyptiacus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Spinosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

BACK = (0.24, 0.25, 0.20)     # dark olive-grey
FLANK = (0.42, 0.40, 0.31)
BELLY = (0.84, 0.78, 0.62)
STRIPE = (0.13, 0.13, 0.10)
SAIL = (0.66, 0.24, 0.10)     # rust red
SAIL_TOP = (0.90, 0.74, 0.46)
SAIL_BAR = (0.20, 0.10, 0.07)
LEG = (0.30, 0.29, 0.22)
MOUTH = (0.48, 0.14, 0.13)
TOOTH = (0.95, 0.92, 0.80)
CLAW = (0.12, 0.11, 0.09)
EYE = (0.86, 0.66, 0.15)
PUPIL = (0.03, 0.02, 0.02)


# ---------------------------------------------------------------- geometry helpers

def loft(sections, sides=18, power=2.0, ref=Vector((0, 0, 1)), cap_start=True, cap_end=True):
    """Skin superelliptic rings along a path. sections: (center, half width, half height)."""
    bm = bmesh.new()
    pts = [Vector(s[0]) for s in sections]
    rings = []
    for i, (c, ra, rb) in enumerate(sections):
        if i == 0:
            fwd = pts[1] - pts[0]
        elif i == len(pts) - 1:
            fwd = pts[-1] - pts[-2]
        else:
            fwd = pts[i + 1] - pts[i - 1]
        fwd.normalize()
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
    if cap_start and len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if cap_end and len(rings[-1]) > 1:
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
            ra = max(0.0, cr(p0[1], p1[1], p2[1], p3[1])) if (i > 0 or k > 0) else p1[1]
            rb = max(0.0, cr(p0[2], p1[2], p2[2], p3[2])) if (i > 0 or k > 0) else p1[2]
            out.append((tuple(cr(p0[0], p1[0], p2[0], p3[0])), ra, rb))
    out.append((tuple(vals[-1][0]), vals[-1][1], vals[-1][2]))
    return out


def cone(base, tip, r, sides=5):
    return nh.tube([base, tip], [r, 0.0], sides=sides)


def side_panel(outline_yz, thickness):
    """Thin slab in the YZ plane (sail, tail fin) from a closed (y, z) outline."""
    bm = nh.flat_panel([(-z, y, 0.0) for y, z in outline_yz], thickness=thickness)
    return nh.transform(bm, Matrix.Rotation(math.radians(90), 4, "Y"))


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

# tail tip -> paddle tail -> hips -> long belly -> chest -> long neck
TORSO = [
    ((0.0, 1.78, 0.50), 0.0, 0.0),
    ((0.0, 1.66, 0.51), 0.010, 0.035),
    ((0.0, 1.48, 0.53), 0.020, 0.065),
    ((0.0, 1.28, 0.56), 0.033, 0.09),
    ((0.0, 1.08, 0.59), 0.05, 0.11),
    ((0.0, 0.88, 0.62), 0.075, 0.125),
    ((0.0, 0.68, 0.65), 0.11, 0.145),
    ((0.0, 0.48, 0.67), 0.15, 0.17),
    ((0.0, 0.28, 0.67), 0.175, 0.195),
    ((0.0, 0.06, 0.65), 0.19, 0.215),
    ((0.0, -0.16, 0.65), 0.185, 0.215),
    ((0.0, -0.36, 0.67), 0.16, 0.19),
    ((0.0, -0.50, 0.71), 0.12, 0.145),
    ((0.0, -0.61, 0.78), 0.085, 0.10),
    ((0.0, -0.70, 0.86), 0.068, 0.078),
    ((0.0, -0.78, 0.91), 0.062, 0.068),
    ((0.0, -0.84, 0.935), 0.058, 0.062),
]


def torso_at(y):
    """(center z, half width, half height) of the torso loft at y."""
    secs = TORSO
    for (c0, a0, b0), (c1, a1, b1) in zip(secs, secs[1:]):
        if c1[1] <= y <= c0[1]:
            k = (c0[1] - y) / (c0[1] - c1[1])
            return c0[2] + (c1[2] - c0[2]) * k, a0 + (a1 - a0) * k, b0 + (b1 - b0) * k
    c, a, b = secs[-1] if y < secs[-1][0][1] else secs[0]
    return c[2], a, b


# Skull: long and low, narrow pinched snout ending in a broad "rosette"
SKULL_ROWS = [  # (y, top z, bottom z, half width)
    (-0.80, 1.005, 0.900, 0.066),
    (-0.86, 1.020, 0.905, 0.066),
    (-0.92, 1.012, 0.910, 0.058),
    (-0.99, 0.992, 0.916, 0.046),
    (-1.07, 0.972, 0.921, 0.036),
    (-1.15, 0.960, 0.924, 0.030),
    (-1.21, 0.956, 0.925, 0.028),
    (-1.26, 0.958, 0.924, 0.036),
    (-1.31, 0.957, 0.924, 0.040),
    (-1.35, 0.950, 0.926, 0.033),
    (-1.375, 0.942, 0.929, 0.018),
]
JAW_ROWS = [
    (-0.82, 0.905, 0.845, 0.062),
    (-0.90, 0.910, 0.868, 0.055),
    (-1.00, 0.916, 0.888, 0.040),
    (-1.12, 0.920, 0.900, 0.029),
    (-1.22, 0.921, 0.903, 0.026),
    (-1.29, 0.921, 0.902, 0.034),
    (-1.34, 0.922, 0.905, 0.030),
    (-1.365, 0.922, 0.910, 0.016),
]
HINGE = Vector((0.0, -0.83, 0.905))
JAW_ROT = Matrix.Translation(HINGE) @ Matrix.Rotation(math.radians(5), 4, "X") @ Matrix.Translation(-HINGE)
EYE_Y = -0.905


def profile(rows):
    return [((0.0, y, (top + bot) * 0.5), w, (top - bot) * 0.5) for y, top, bot, w in rows]


def row_at(rows, y):
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k, b0 + (b1 - b0) * k, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1]
    return t, b, w


# Sail outline (y, z): from the shoulders to the hips, tallest over the mid-back/hips
SAIL_OUTLINE = [
    (-0.52, 0.74), (-0.50, 0.90), (-0.44, 1.06), (-0.34, 1.24), (-0.20, 1.40), (-0.04, 1.50),
    (0.10, 1.54), (0.24, 1.52), (0.38, 1.42), (0.50, 1.24), (0.60, 1.03), (0.68, 0.86),
    (0.74, 0.74), (0.40, 0.66), (0.0, 0.64), (-0.30, 0.66),
]


def sail_top(y):
    pts = SAIL_OUTLINE[:13]
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return 0.0


# Tail paddle: neural-spine fin above and a lower chevron keel, both deep and thin
TAIL_FIN_TOP = [(0.62, 0.70), (0.80, 0.84), (1.00, 0.86), (1.20, 0.83), (1.40, 0.78), (1.60, 0.69),
                (1.79, 0.55), (1.76, 0.50), (1.40, 0.55), (1.00, 0.62), (0.70, 0.66)]
TAIL_FIN_BOT = [(0.80, 0.52), (1.05, 0.44), (1.30, 0.40), (1.55, 0.40), (1.76, 0.46), (1.78, 0.50),
                (1.50, 0.50), (1.10, 0.53), (0.85, 0.57)]


def leg_parts(side, hip, knee, ankle, ball, toe_spread=0.5):
    """Short, thick hind limb with a flat-footed, wide-toed paddling foot."""
    sx = side
    hip, knee, ankle, ball = (Vector((sx * p[0], p[1], p[2])) for p in (hip, knee, ankle, ball))
    d, d2, d3 = knee - hip, ankle - knee, ball - ankle
    path = [
        (hip + Vector((-sx * 0.05, 0, 0.12)), 0.0, 0.0),
        (hip + Vector((-sx * 0.03, 0, 0.09)), 0.15, 0.08),
        (hip + d * 0.05, 0.19, 0.11),
        (hip + d * 0.35, 0.17, 0.115),
        (hip + d * 0.70, 0.12, 0.09),
        (knee, 0.075, 0.068),
        (knee + d2 * 0.25, 0.082, 0.066),
        (knee + d2 * 0.65, 0.058, 0.05),
        (ankle, 0.045, 0.042),
        (ankle + d3 * 0.5, 0.042, 0.038),
        (ball, 0.046, 0.04),
        (ball + Vector((0, -0.025, -0.008)), 0.0, 0.0),
    ]
    parts = [loft(densify(path, 3), sides=16, ref=Vector((1, 0, 0)))]
    claws = []
    fwd = Vector((0, -1, 0))
    for k, ang in enumerate((-toe_spread, 0.0, toe_spread)):
        dirv = Matrix.Rotation(ang * -sx, 3, "Z") @ fwd
        length = 0.19 if k == 1 else 0.16
        p0 = ball + Vector((0, 0, -0.004))
        p1 = Vector((ball.x, ball.y, 0.024)) + dirv * length * 0.5
        p2 = Vector((ball.x, ball.y, 0.018)) + dirv * length
        parts.append(nh.tube([p0, p1, p2], [0.032, 0.025, 0.017], sides=10, scale_xy=(1.25, 0.8)))
        claws.append((p2 - dirv * 0.008 + Vector((0, 0, 0.004)), p2 + dirv * 0.045 + Vector((0, 0, -0.014)), 0.015))
    # webbing between the toes (flat feet for soft river banks)
    parts.append(nh.ellipsoid(ball + Vector((0, -0.07, -0.02)), (0.10, 0.07, 0.016), subdivisions=3))
    return parts, claws


def arm_parts(side):
    """Robust forelimb reaching down and forward, three fingers, huge thumb claw."""
    sx = side
    sh = Vector((sx * 0.13, -0.44, 0.66))
    el = Vector((sx * 0.19, -0.48, 0.50))
    wr = Vector((sx * 0.17, -0.60, 0.40))
    parts = [nh.tube([sh + Vector((-sx * 0.05, 0.03, 0.05)), sh, el, wr], [0.07, 0.058, 0.04, 0.03], sides=12)]
    parts.append(nh.ellipsoid(sh.lerp(el, 0.4), (0.05, 0.06, 0.08), subdivisions=2))  # biceps
    fingers, claws = [], []
    for k, (dx, ln, rc) in enumerate(((0.025, 0.07, 0.016), (0.0, 0.06, 0.011), (-0.022, 0.05, 0.009))):
        base = wr + Vector((sx * dx, -0.01, -0.005))
        tip = base + Vector((sx * dx * 0.6, -ln * 0.6, -ln * 0.7))
        fingers.append(nh.tube([base, tip], [0.016, 0.01], sides=6))
        hook = 0.06 if k == 0 else 0.03
        claws.append((tip, tip + Vector((sx * 0.004, -hook * 0.7, -hook * 0.6)), rc))
    return parts, fingers, claws


# ---------------------------------------------------------------- skin

def sail_mask(co):
    """1 on the sail / tail fin above the body outline, 0 on the body."""
    zc, w, h = torso_at(co.y)
    return nh.smoothstep(zc + h * 0.85, zc + h * 0.85 + 0.06, co.z) if -0.55 < co.y < 0.8 else 0.0


def displacement(co, n):
    d = 0.0012 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 45.0)))
    # sail: ridges where the neural spines run up through the skin
    if sail_mask(co) > 0.0 and abs(n.x) > 0.5:
        s = 0.5 + 0.5 * math.cos(co.y * math.tau / 0.075)
        d += 0.004 * s ** 4 * sail_mask(co)
    # scattered low bumps along the flanks
    if co.y > -0.6 and abs(n.x) > 0.3 and co.z < 0.85:
        d += 0.0022 * (1.0 - nh.smoothstep(0.0, 0.35, noise.cell(co * 38.0)))
    return d


def sculpt(bm):
    bm.normal_update()
    offs = [(v, v.normal.copy() * displacement(v.co, v.normal)) for v in bm.verts]
    for v, o in offs:
        v.co += o
    bm.normal_update()
    return bm


def body_paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.6, -0.1, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.05, 0.75, n.z))
    if co.z < 0.45:  # legs and feet darker, no counter-shading
        c = nh.lerp(LEG, c, nh.smoothstep(0.2, 0.45, co.z))
    # irregular dark blotches along the flanks
    blot = noise.noise(Vector((co.x * 6.0, co.y * 9.0, co.z * 9.0)))
    c = nh.lerp(c, STRIPE, 0.45 * nh.smoothstep(0.25, 0.5, blot) * nh.smoothstep(-0.2, 0.3, n.z))
    # sail: rust red, dark bars on the spines, a pale crown
    m = sail_mask(co)
    if m > 0.0:
        top = sail_top(co.y)
        zc, w, h = torso_at(co.y)
        t = (co.z - zc - h) / max(top - zc - h, 0.05)
        sc = nh.lerp(SAIL, SAIL_BAR, 0.4 * nh.smoothstep(0.3, 0.0, t))
        bar = 0.5 + 0.5 * math.cos(co.y * math.tau / 0.075)
        sc = nh.lerp(sc, SAIL_BAR, 0.55 * bar ** 3)
        sc = nh.lerp(sc, SAIL_TOP, nh.smoothstep(0.78, 0.92, t))
        c = nh.lerp(c, sc, m)
    # tail paddle: banded, darker above
    if co.y > 0.75:
        band = 0.5 + 0.5 * math.sin(co.y * 26.0)
        c = nh.lerp(c, STRIPE, 0.5 * nh.smoothstep(0.55, 0.9, band) * nh.smoothstep(-0.3, 0.3, n.z + abs(n.x) * 0.5))
    # muzzle dark top, pale lips
    if co.y < -0.8 and co.z > 0.85:
        c = nh.lerp(c, BACK, 0.3 * nh.smoothstep(0.3, 0.9, n.z))
    m = noise.noise(co * 16.0)
    return tuple(max(0.0, v * (1.0 + 0.1 * m)) for v in c)


def teeth(mb):
    """Conical, interlocking teeth; the big ones in the rosette show outside the lips."""
    for i in range(13):
        t = i / 12
        y = -0.95 - t * 0.41
        top, bot, w = row_at(SKULL_ROWS, y)
        big = 1.6 if -1.34 < y < -1.27 else 1.0
        length = (0.011 + 0.005 * math.sin(t * math.pi)) * big
        for sx in (1, -1):
            base = Vector((sx * w * 0.82, y, bot + 0.008))
            mb.add(cone(base, base + Vector((sx * 0.004, -0.004, -length)), 0.0048 * big, sides=5), TOOTH, smooth=False)
    for i in range(12):
        t = i / 11
        y = -0.97 - t * 0.38
        top, bot, w = row_at(JAW_ROWS, y)
        big = 1.5 if -1.32 < y < -1.26 else 1.0
        length = (0.010 + 0.004 * math.sin(t * math.pi)) * big
        for sx in (1, -1):
            base = JAW_ROT @ Vector((sx * w * 0.84, y - 0.012, top - 0.006))
            tip = JAW_ROT @ Vector((sx * (w * 0.84 + 0.004), y - 0.014, top + length))
            mb.add(cone(base, tip, 0.0045 * big, sides=5), TOOTH, smooth=False)


def head_details(mb):
    top, bot, w = row_at(SKULL_ROWS, EYE_Y)
    for sx in (1, -1):
        e = Vector((sx * w * 0.86, EYE_Y, top - 0.03))
        mb.add(nh.ellipsoid(e, (0.014, 0.016, 0.013), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.009, -0.004, 0)), (0.005, 0.006, 0.009), subdivisions=1), PUPIL)
        # nostrils far back on the snout (retracted, as in the 2020 reconstruction)
        t2, b2, w2 = row_at(SKULL_ROWS, -1.02)
        mb.add(nh.ellipsoid((sx * w2 * 0.45, -1.02, t2 - 0.004), (0.006, 0.016, 0.004), subdivisions=1), PUPIL)
    # dark mouth lining
    top, bot, w = row_at(JAW_ROWS, -1.0)
    mb.add(nh.transform(nh.uv_ellipsoid((0, -1.0, top - 0.004), (w * 0.7, 0.18, 0.008), segments=12, rings=6),
                        JAW_ROT), MOUTH)


def build():
    body = nh.MeshBuilder()
    body.add(loft(densify(TORSO, 4), sides=24, power=2.1), BACK)
    body.add(loft(densify(profile(SKULL_ROWS), 3), sides=18, power=2.4), BACK)
    # throat filling and the brow crest
    body.add(nh.ellipsoid((0, -0.80, 0.90), (0.06, 0.08, 0.06), subdivisions=3), BACK)
    body.add(nh.ellipsoid((0, -0.885, 1.012), (0.016, 0.07, 0.022), subdivisions=3), BACK)
    for sx in (1, -1):
        t, b, w = row_at(SKULL_ROWS, EYE_Y)
        body.add(nh.ellipsoid((sx * w * 0.7, EYE_Y, t - 0.012), (0.022, 0.035, 0.014), subdivisions=2), BACK)  # brow
        body.add(nh.ellipsoid((sx * 0.11, 0.30, 0.66), (0.07, 0.24, 0.12), subdivisions=3), BACK)  # tail-base muscle
        body.add(nh.ellipsoid((sx * 0.09, -0.40, 0.62), (0.09, 0.12, 0.12), subdivisions=3), BACK)  # chest
    # sail and tail paddle, rooted inside the body
    body.add(side_panel(SAIL_OUTLINE, 0.026), BACK)
    for k in range(-6, 17):  # the spines thicken the sail into ribs
        y = k * 0.075 + 0.01
        top = sail_top(y)
        if top <= 0.8:
            continue
        zc, w, h = torso_at(y)
        body.add(nh.tube([(0, y, zc), (0, y + 0.015, top - 0.04)], [0.02, 0.013], sides=6), BACK)
    body.add(side_panel(TAIL_FIN_TOP, 0.024), BACK)
    body.add(side_panel(TAIL_FIN_BOT, 0.022), BACK)

    legs = [
        leg_parts(1, hip=(0.16, 0.30, 0.66), knee=(0.19, 0.10, 0.42), ankle=(0.18, 0.24, 0.16), ball=(0.17, 0.10, 0.03)),
        leg_parts(-1, hip=(0.16, 0.32, 0.66), knee=(0.19, 0.28, 0.40), ankle=(0.18, 0.52, 0.18), ball=(0.17, 0.46, 0.03)),
    ]
    arms = [arm_parts(1), arm_parts(-1)]
    for parts, claws in legs:
        for p in parts:
            body.add(p, BACK)
    for parts, fingers, claws in arms:
        for p in parts:
            body.add(p, BACK)
    fused = sculpt(body.fuse(voxel=0.0075, smooth=5, smooth_factor=0.5))
    fused = decimate(fused, 21000)

    jb = nh.MeshBuilder()
    jb.add(loft(densify(profile(JAW_ROWS), 3), sides=16, power=2.3), BACK)
    jfused = nh.transform(decimate(jb.fuse(voxel=0.006, smooth=4, smooth_factor=0.5), 2000), JAW_ROT)

    mb = nh.MeshBuilder()
    mb.add(fused, body_paint)
    mb.add(jfused, body_paint)
    head_details(mb)
    teeth(mb)
    for parts, claws in legs:
        for base, tip, r in claws:
            mb.add(cone(base, tip, r, sides=6), CLAW)
    for parts, fingers, claws in arms:
        for f in fingers:
            mb.add(f, LEG)
        for base, tip, r in claws:
            mb.add(cone(base, tip, r, sides=6), CLAW)

    obj = mb.to_object("Spinosaurus", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


def render_head(path):
    scene = bpy.context.scene
    obj = bpy.data.objects["Spinosaurus"]
    vs = [obj.matrix_world @ v.co for v in obj.data.vertices]
    snout = min(vs, key=lambda v: v.y)
    head = Vector((0.0, snout.y + 0.25, snout.z + 0.03))
    cam = scene.camera
    cam.location = head + Vector((0.55, -0.55, 0.25))
    cam.rotation_euler = (head - cam.location).to_track_quat("-Z", "Y").to_euler()
    out = Path(path)
    scene.render.filepath = str(out.with_name(f"{out.stem}_head.png"))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, "Spinosaurus", ground=(0.36, 0.40, 0.26), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
