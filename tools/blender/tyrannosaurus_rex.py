"""
Procedural low-poly Tyrannosaurus rex for map colonies.

Modern posture: body horizontal and balanced over the hips, heavy tail held
straight out behind, deep boxy skull with a slightly open jaw full of teeth,
S-curved muscular neck, tiny two-fingered arms, huge thighs tapering into
bird-like lower legs and three-toed clawed feet, mid-stride. Dark olive-brown
back with darker stripes, cream belly and throat, a reddish flush on the face.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/tyrannosaurus_rex.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TyrannosaurusRex.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

BACK = (0.33, 0.30, 0.16)     # dark olive-brown
FLANK = (0.46, 0.39, 0.22)
BELLY = (0.88, 0.80, 0.60)    # cream
STRIPE = (0.16, 0.14, 0.08)
FACE = (0.60, 0.24, 0.14)     # reddish flush
LEG = (0.36, 0.31, 0.20)
MOUTH = (0.50, 0.13, 0.13)
TOOTH = (0.95, 0.92, 0.80)
CLAW = (0.14, 0.12, 0.10)
EYE = (0.90, 0.60, 0.12)
PUPIL = (0.03, 0.02, 0.02)

LIFT = 0.12  # raises body/neck/head above the original layout so the legs get longer


# ---------------------------------------------------------------- geometry helpers

def loft(sections, sides=18, power=2.0, ref=Vector((0, 0, 1)), cap_start=True, cap_end=True):
    """Skin superelliptic rings along a path.
    sections: (center, ra, rb) with ra along `side` (fwd x ref) and rb along `up` (side x fwd).
    For a mostly-horizontal path with ref=Z: ra = half width, rb = half height.
    power > 2 squares the cross-section off (boxy skull)."""
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


def cone(base, tip, r, sides=4):
    return nh.tube([base, tip], [r, 0.0], sides=sides)


# ---------------------------------------------------------------- colouring

def skin(co, n):
    """Dark striped back, lighter flanks, cream belly/throat, red face."""
    top = nh.smoothstep(-0.45, 0.55, n.z)
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.55, -0.05, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.1, 0.8, n.z))
    # transverse stripes over the back and tail
    if co.y > -0.38:
        s = 0.5 + 0.5 * math.sin(co.y * 24.0 + abs(co.x) * 5.0)
        c = nh.lerp(c, STRIPE, 0.7 * nh.smoothstep(0.6, 0.9, s) * top * nh.smoothstep(-0.38, -0.25, co.y))
    # reddish flush on the face, strongest around the eyes and cheeks
    if co.y < -0.66:
        f = nh.smoothstep(-0.66, -0.84, co.y) * nh.smoothstep(-0.6, 0.0, n.z) * (1.0 - nh.smoothstep(0.3, 0.9, n.z))
        c = nh.lerp(c, FACE, 0.3 * f)
    # mottled scales
    m = noise.noise(co * 14.0)
    return tuple(max(0.0, v * (1.0 + 0.12 * m)) for v in c)


def leg_skin(co, n):
    c = nh.lerp(LEG, skin(co, n), nh.smoothstep(0.2, 0.7, co.z))
    m = noise.noise(co * 18.0)
    return tuple(max(0.0, v * (1.0 + 0.1 * m)) for v in c)


# ---------------------------------------------------------------- parts

def lifted(sections):
    return [((c[0], c[1], c[2] + LIFT), a, b) for c, a, b in sections]


def densify(sections, steps):
    """Catmull-Rom resample of a loft so vertex-colour stripes have enough rings to land on."""
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
            # keep tips (zero radius) only at the ends
            ra = max(0.0, cr(p0[1], p1[1], p2[1], p3[1])) if (i > 0 or k > 0) else p1[1]
            rb = max(0.0, cr(p0[2], p1[2], p2[2], p3[2])) if (i > 0 or k > 0) else p1[2]
            out.append((tuple(cr(p0[0], p1[0], p2[0], p3[0])), ra, rb))
    out.append((tuple(vals[-1][0]), vals[-1][1], vals[-1][2]))
    return out


TORSO = lifted([
    ((0.0, 1.66, 0.82), 0.0, 0.0),
    ((0.0, 1.52, 0.82), 0.026, 0.03),
    ((0.0, 1.30, 0.84), 0.055, 0.065),
    ((0.0, 1.05, 0.87), 0.09, 0.105),
    ((0.0, 0.80, 0.90), 0.13, 0.15),
    ((0.0, 0.55, 0.92), 0.17, 0.195),
    ((0.0, 0.32, 0.93), 0.205, 0.235),
    ((0.0, 0.10, 0.91), 0.23, 0.27),
    ((0.0, -0.10, 0.87), 0.24, 0.295),
    ((0.0, -0.28, 0.88), 0.23, 0.285),
    ((0.0, -0.42, 0.95), 0.215, 0.25),
    ((0.0, -0.51, 1.04), 0.19, 0.21),
    ((0.0, -0.56, 1.12), 0.18, 0.19),
    ((0.0, -0.60, 1.16), 0.17, 0.17),
])


def profile(rows):
    """Loft sections from (y, top z, bottom z, half width) rows, lifted."""
    return [((0.0, y, (top + bot) * 0.5 + LIFT), w, (top - bot) * 0.5) for y, top, bot, w in rows]


# Skull: tall boxy snout with a convex top, broad back flaring over the jaw muscles
SKULL_ROWS = [
    (-0.48, 1.26, 1.02, 0.15),   # tucked into the neck so there's no seam
    (-0.56, 1.34, 1.025, 0.195),
    (-0.65, 1.37, 1.03, 0.215),
    (-0.75, 1.365, 1.03, 0.19),
    (-0.86, 1.34, 1.028, 0.155),
    (-0.96, 1.30, 1.026, 0.13),
    (-1.04, 1.26, 1.028, 0.115),
    (-1.10, 1.215, 1.034, 0.10),
    (-1.135, 1.165, 1.045, 0.075),
]
# Lower jaw: deep at the back (angular), slimmer toward the chin
JAW_ROWS = [
    (-0.54, 1.015, 0.84, 0.17),
    (-0.66, 1.015, 0.865, 0.18),
    (-0.78, 1.01, 0.90, 0.15),
    (-0.90, 1.005, 0.925, 0.125),
    (-1.00, 1.005, 0.94, 0.108),
    (-1.07, 1.005, 0.952, 0.092),
    (-1.11, 1.0, 0.962, 0.068),
]
SKULL = profile(SKULL_ROWS)
JAW = profile(JAW_ROWS)

HINGE = Vector((0.0, -0.58, 1.01 + LIFT))
JAW_OPEN = math.radians(14)
JAW_ROT = Matrix.Translation(HINGE) @ Matrix.Rotation(JAW_OPEN, 4, "X") @ Matrix.Translation(-HINGE)


def row_at(rows, y):
    """(top, bottom, half width) interpolated at y (rows ordered by decreasing y)."""
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k + LIFT, b0 + (b1 - b0) * k + LIFT, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1]
    return t + LIFT, b + LIFT, w


def torso():
    """Tail tip -> hips -> barrel chest -> S-curved neck, one continuous loft."""
    return loft(densify(TORSO, 4), sides=24, power=2.1)


def skull():
    return loft(densify(SKULL, 3), sides=22, power=2.9)


def jaw_closed():
    return loft(densify(JAW, 3), sides=18, power=2.7)


def lip(rows, y0, y1, z_of, x_scale, r0, r1, steps=10):
    """A soft lip ridge along each side of a jaw margin (covers the tooth bases)."""
    out = []
    for sx in (1, -1):
        pts, radii = [], []
        for i in range(steps + 1):
            t = i / steps
            y = y0 + (y1 - y0) * t
            top, bot, w = row_at(rows, y)
            pts.append((sx * w * x_scale, y, z_of(top, bot)))
            radii.append(r0 + (r1 - r0) * t)
        out.append(nh.tube(pts, radii, sides=8))
    return out


def head_parts():
    """Sculpted bosses and flares on the skull, fused with it."""
    parts = []
    top, bot, w = row_at(SKULL_ROWS, -0.73)
    for sx in (1, -1):
        e = Vector((sx * w * 0.84, -0.73, top - 0.075))
        parts.append(nh.ellipsoid(e + Vector((-sx * 0.006, -0.012, 0.036)), (0.045, 0.065, 0.026), subdivisions=3))  # brow boss
        parts.append(nh.ellipsoid(e + Vector((-sx * 0.04, -0.085, 0.036)), (0.024, 0.036, 0.026), subdivisions=2))   # lacrimal horn
        parts.append(nh.ellipsoid(e + Vector((-sx * 0.02, 0.05, 0.012)), (0.022, 0.03, 0.02), subdivisions=2))   # postorbital boss
        # jugal flare: the cheek bone sweeping out below and behind the eye
        t2, b2, w2 = row_at(SKULL_ROWS, -0.66)
        parts.append(nh.ellipsoid((sx * (w2 - 0.012), -0.69, b2 + 0.06), (0.03, 0.14, 0.038), subdivisions=3))
        # jaw-closing muscle mass bulging out of the back of the skull
        parts.append(nh.ellipsoid((sx * (w2 - 0.035), -0.58, b2 + 0.12), (0.04, 0.08, 0.075), subdivisions=3))
        # nasal ridge bumps along the snout top
        for k, y in enumerate((-0.92, -0.99, -1.05)):
            t3, b3, w3 = row_at(SKULL_ROWS, y)
            parts.append(nh.ellipsoid((sx * w3 * 0.35, y, t3 - 0.006), (0.022, 0.03, 0.012), subdivisions=2))
    # upper lips covering the tooth bases
    parts += lip(SKULL_ROWS, -0.66, -1.10, lambda t, b: b + 0.006, 0.86, 0.026, 0.018)
    return parts


def leg_parts(side, hip, knee, ankle, ball, toe_spread=0.42):
    """One continuous limb (sunk into the hip) plus toes; claws are added later as details."""
    sx = side
    hip, knee, ankle, ball = (Vector((sx * p[0], p[1], p[2])) for p in (hip, knee, ankle, ball))
    d, d2, d3 = knee - hip, ankle - knee, ball - ankle
    path = [
        (hip + Vector((-sx * 0.06, 0, 0.16)), 0.0, 0.0),
        (hip + Vector((-sx * 0.04, 0, 0.12)), 0.20, 0.10),
        (hip + d * 0.05, 0.26, 0.15),
        (hip + d * 0.30, 0.255, 0.16),
        (hip + d * 0.58, 0.20, 0.135),
        (hip + d * 0.85, 0.135, 0.105),
        (knee, 0.10, 0.088),
        (knee + d2 * 0.22, 0.118, 0.088),   # calf
        (knee + d2 * 0.55, 0.09, 0.072),
        (knee + d2 * 0.85, 0.068, 0.06),
        (ankle, 0.064, 0.06),
        (ankle + d3 * 0.4, 0.058, 0.054),
        (ankle + d3 * 0.8, 0.056, 0.054),
        (ball, 0.062, 0.058),
        (ball + Vector((0, -0.03, -0.01)), 0.0, 0.0),
    ]
    parts = [loft(densify(path, 3), sides=18, ref=Vector((1, 0, 0)))]
    claws = []
    fwd = Vector((0, -1, 0))
    for k, ang in enumerate((-toe_spread, 0.0, toe_spread)):
        dirv = Matrix.Rotation(ang * -sx, 3, "Z") @ fwd
        length = 0.22 if k == 1 else 0.17
        p0 = ball + Vector((0, 0, -0.005))
        p1 = Vector((ball.x, ball.y, 0.034)) + dirv * length * 0.5
        p2 = Vector((ball.x, ball.y, 0.026)) + dirv * length
        parts.append(nh.tube([p0, p1, p2], [0.042, 0.032, 0.022], sides=10))
        # toe pads
        parts.append(nh.ellipsoid(p1 + Vector((0, 0, -0.012)), (0.03, 0.04, 0.02), subdivisions=2))
        claws.append((p2 - dirv * 0.012 + Vector((0, 0, 0.006)), p2 + dirv * 0.065 + Vector((0, 0, -0.018)), 0.022))
    claws.append((ball + Vector((0, 0.02, 0.03)), ball + Vector((sx * 0.02, 0.075, 0.005)), 0.017))  # dewclaw
    return parts, claws, (knee, d2)


def arm_parts(side):
    sx = side
    sh = Vector((sx * 0.16, -0.36, 0.80 + LIFT))
    el = Vector((sx * 0.21, -0.42, 0.69 + LIFT))
    wr = Vector((sx * 0.20, -0.50, 0.67 + LIFT))
    parts = [nh.tube([sh + Vector((-sx * 0.05, 0.02, 0.03)), sh, el, wr], [0.06, 0.048, 0.032, 0.024], sides=10)]
    claws, fingers = [], []
    for k in (-1, 1):
        base = wr + Vector((sx * 0.01 * k, -0.005, 0))
        tip = base + Vector((sx * 0.012 * k, -0.045, -0.03))
        fingers.append(nh.tube([base, tip], [0.013, 0.008], sides=6))
        claws.append((tip, tip + Vector((0, -0.02, -0.02)), 0.008))
    return parts, fingers, claws


# ---------------------------------------------------------------- skin sculpt

KNEES = []  # (knee point, shin direction) filled by build(); used for the knee folds


def displacement(co, n):
    """Sculpted surface detail (model units, along the normal)."""
    d = 0.0
    # pebbly scales everywhere
    d += 0.0016 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 40.0)))
    # osteoderm-like bumps in rows along the back and neck
    ax = abs(co.x)
    if -0.62 < co.y < 1.25 and n.z > 0.35:
        row = max(1.0 - nh.smoothstep(0.0, 0.045, ax), 0.7 * (1.0 - nh.smoothstep(0.0, 0.035, abs(ax - 0.075))))
        bump = 1.0 - nh.smoothstep(0.0, 0.45, noise.cell(Vector((co.x * 26.0, co.y * 20.0, co.z * 26.0))))
        taper = 1.0 - nh.smoothstep(0.7, 1.25, co.y)
        d += 0.012 * row * bump * nh.smoothstep(0.35, 0.8, n.z) * taper
    # skin folds on the throat and neck sides
    if -0.64 < co.y < -0.28:
        m = nh.smoothstep(-0.64, -0.56, co.y) * (1.0 - nh.smoothstep(-0.36, -0.28, co.y))
        throat = nh.smoothstep(-0.1, -0.6, n.z)
        sides = nh.smoothstep(0.4, 0.9, abs(n.x)) * 0.6
        d += 0.006 * math.sin(co.y * 80.0 + co.z * 12.0) * m * max(throat, sides)
    # folds behind the knees
    for k, d2 in KNEES:
        r = (co - k).length
        if r < 0.15:
            back = nh.smoothstep(0.1, 0.6, n.dot(Vector((0, 1, 0))))
            d += 0.005 * math.sin(r * 90.0) * (1.0 - r / 0.15) * back
    # foot scutes: transverse bands on the toes and the front of the metatarsus
    if co.z < 0.07 + 0.0 and n.z > 0.2:
        d += 0.004 * max(0.0, math.sin(co.y * 95.0))
    elif 0.06 < co.z < 0.32 and n.y < -0.3:
        d += 0.004 * max(0.0, math.sin(co.z * 85.0))
    # antorbital fenestra: a shallow depression on the side of the snout
    if -1.0 < co.y < -0.76 and co.z > 1.0 + LIFT:
        top, bot, w = row_at(SKULL_ROWS, co.y)
        cz = (top + bot) * 0.5 + 0.03
        r = math.hypot((co.y + 0.875) / 0.085, (co.z - cz) / 0.05)
        d -= 0.02 * (1.0 - nh.smoothstep(0.55, 1.0, r)) * nh.smoothstep(0.4, 0.8, abs(n.x))
    return d


def sculpt(bm):
    bm.normal_update()
    offs = [(v, v.normal.copy() * displacement(v.co, v.normal)) for v in bm.verts]
    for v, o in offs:
        v.co += o
    bm.normal_update()
    return bm


def decimate(bm, max_tris):
    """Collapse-decimate a bmesh to roughly max_tris triangles."""
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    n = sum(len(p.vertices) - 2 for p in mesh.polygons)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = min(1.0, max_tris / max(n, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    print(f"  decimated {n} -> {len(out.faces)} faces")
    return out


def body_paint(co, n):
    c = skin(co, n) if co.z > 0.62 else leg_skin(co, n)
    # darker crevices between scales, lighter osteoderm tops
    cell = noise.cell(co * 48.0)
    c = tuple(v * (0.9 + 0.14 * (1.0 - nh.smoothstep(0.2, 0.7, cell))) for v in c)
    # darken the antorbital depression and the lip line a touch
    if -1.0 < co.y < -0.76 and co.z > 1.0 + LIFT and abs(n.x) > 0.4:
        top, bot, w = row_at(SKULL_ROWS, co.y)
        cz = (top + bot) * 0.5 + 0.03
        r = math.hypot((co.y + 0.875) / 0.085, (co.z - cz) / 0.05)
        c = nh.lerp(c, STRIPE, 0.45 * (1.0 - nh.smoothstep(0.5, 1.0, r)))
    return c


def teeth(mb):
    # upper row: mostly hidden behind the lips, only the tips show
    for i in range(9):
        t = i / 8
        y = -0.70 - t * 0.40
        top, bot, w = row_at(SKULL_ROWS, y)
        length = 0.05 + 0.02 * math.sin(t * math.pi)
        for sx in (1, -1):
            base = Vector((sx * w * 0.80, y, bot + 0.02))
            mb.add(cone(base, base + Vector((0, -0.008, -0.02 - length)), 0.014, sides=5), TOOTH, smooth=False)
    # lower row points up from the open jaw
    for i in range(8):
        t = i / 7
        y = -0.74 - t * 0.33
        top, bot, w = row_at(JAW_ROWS, y)
        length = 0.035 + 0.012 * math.sin(t * math.pi)
        for sx in (1, -1):
            base = JAW_ROT @ Vector((sx * w * 0.76, y, top - 0.015))
            tip = JAW_ROT @ Vector((sx * w * 0.76, y - 0.006, top + length))
            mb.add(cone(base, tip, 0.012, sides=5), TOOTH, smooth=False)


def mouth_lining(mb):
    """Dark red tongue and palate so the open mouth reads from the side."""
    top, bot, w = row_at(JAW_ROWS, -0.82)
    tongue = nh.uv_ellipsoid((0, -0.82, top - 0.012), (w * 0.72, 0.24, 0.022), segments=14, rings=8)
    mb.add(nh.transform(tongue, JAW_ROT), MOUTH)
    top, bot, w = row_at(SKULL_ROWS, -0.84)
    mb.add(nh.uv_ellipsoid((0, -0.84, bot + 0.012), (w * 0.8, 0.26, 0.02), segments=14, rings=8), MOUTH)


def eyes(mb):
    top, bot, w = row_at(SKULL_ROWS, -0.73)
    for sx in (1, -1):
        e = Vector((sx * w * 0.86, -0.73, top - 0.075))
        mb.add(nh.ellipsoid(e, (0.026, 0.028, 0.024), subdivisions=3), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.017, -0.012, 0.0)), (0.009, 0.012, 0.016), subdivisions=2), PUPIL)
        # nostril at the snout tip
        t2, b2, w2 = row_at(SKULL_ROWS, -1.105)
        mb.add(nh.ellipsoid((sx * w2 * 0.52, -1.105, t2 - 0.028), (0.014, 0.024, 0.011), subdivisions=2), PUPIL)


def build():
    KNEES.clear()
    hip_z = 0.86 + LIFT
    legs = [
        leg_parts(1, hip=(0.19, 0.12, hip_z), knee=(0.21, -0.15, 0.62), ankle=(0.20, 0.04, 0.26), ball=(0.18, -0.12, 0.04)),
        leg_parts(-1, hip=(0.19, 0.14, hip_z), knee=(0.21, 0.13, 0.60), ankle=(0.20, 0.44, 0.29), ball=(0.18, 0.40, 0.04)),
    ]
    arms = [arm_parts(1), arm_parts(-1)]

    # --- one seamless body: torso, neck, skull and its bosses, legs, arms
    body = nh.MeshBuilder()
    body.add(torso(), BACK)
    body.add(skull(), BACK)
    for part in head_parts():
        body.add(part, BACK)
    # throat filling between jaw and neck
    body.add(nh.ellipsoid((0, -0.50, 0.96 + LIFT), (0.15, 0.14, 0.12), subdivisions=3), BACK)
    for sx in (1, -1):
        # caudofemoralis: the huge tail-base muscle that powers the stride
        body.add(nh.ellipsoid((sx * 0.13, 0.52, 0.92 + LIFT), (0.09, 0.32, 0.13), subdivisions=3), BACK)
        # pectoral / chest muscle mass
        body.add(nh.ellipsoid((sx * 0.10, -0.33, 0.86 + LIFT), (0.13, 0.16, 0.17), subdivisions=3), BACK)
    for parts, claws, knee in legs:
        KNEES.append(knee)
        for part in parts:
            body.add(part, BACK)
    for parts, fingers, claws in arms:
        for part in parts:
            body.add(part, BACK)
    fused = sculpt(body.fuse(voxel=0.008, smooth=6, smooth_factor=0.5))
    fused = decimate(fused, 23000)

    # --- lower jaw as its own fused piece so the mouth stays open
    jb = nh.MeshBuilder()
    jb.add(jaw_closed(), BACK)
    for part in lip(JAW_ROWS, -0.70, -1.08, lambda t, b: t - 0.006, 0.84, 0.02, 0.014):
        jb.add(part, BACK)
    jfused = sculpt(jb.fuse(voxel=0.007, smooth=4, smooth_factor=0.5))
    jfused = nh.transform(decimate(jfused, 3500), JAW_ROT)

    mb = nh.MeshBuilder()
    mb.add(fused, body_paint)
    mb.add(jfused, body_paint)
    mouth_lining(mb)
    teeth(mb)
    eyes(mb)
    for parts, claws, knee in legs:
        for base, tip, r in claws:
            mb.add(cone(base, tip, r, sides=6), CLAW)
    for parts, fingers, claws in arms:
        for f in fingers:
            mb.add(f, skin)
        for base, tip, r in claws:
            mb.add(cone(base, tip, r, sides=5), CLAW)

    obj = mb.to_object("TyrannosaurusRex", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


def render_head(path):
    """Extra close-up of the head (after nh.run has set up the scene)."""
    scene = bpy.context.scene
    obj = bpy.data.objects["TyrannosaurusRex"]
    vs = [obj.matrix_world @ v.co for v in obj.data.vertices]
    snout = min(vs, key=lambda v: v.y)
    head = Vector((0.0, snout.y + 0.32, snout.z + 0.05))
    cam = scene.camera
    cam.location = head + Vector((0.62, -0.75, 0.32))
    cam.rotation_euler = (head - cam.location).to_track_quat("-Z", "Y").to_euler()
    out = Path(path)
    scene.render.filepath = str(out.with_name(f"{out.stem}_head.png"))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, "TyrannosaurusRex", ground=(0.33, 0.42, 0.24),
           views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
