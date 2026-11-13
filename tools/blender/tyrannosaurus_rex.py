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
        c = nh.lerp(c, FACE, 0.5 * f)
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
    return loft(densify(TORSO, 4), sides=20, power=2.1)


def skull():
    return loft(densify(SKULL, 2), sides=18, power=2.9)


def jaw():
    return nh.transform(loft(densify(JAW, 2), sides=14, power=2.7), JAW_ROT)


def teeth(mb):
    # upper row hangs from the skull margin, biggest in the middle of the snout
    for i in range(8):
        t = i / 7
        y = -0.71 - t * 0.38
        top, bot, w = row_at(SKULL_ROWS, y)
        length = 0.045 + 0.02 * math.sin(t * math.pi)
        for sx in (1, -1):
            base = Vector((sx * w * 0.80, y, bot + 0.02))
            mb.add(cone(base, base + Vector((0, -0.008, -0.02 - length)), 0.015), TOOTH, smooth=False)
    # lower row points up from the open jaw
    for i in range(7):
        t = i / 6
        y = -0.75 - t * 0.31
        top, bot, w = row_at(JAW_ROWS, y)
        length = 0.035 + 0.012 * math.sin(t * math.pi)
        for sx in (1, -1):
            base = JAW_ROT @ Vector((sx * w * 0.76, y, top - 0.015))
            tip = JAW_ROT @ Vector((sx * w * 0.76, y - 0.006, top + length))
            mb.add(cone(base, tip, 0.012), TOOTH, smooth=False)


def mouth_lining(mb):
    """Dark red tongue and palate so the open mouth reads from the side."""
    top, bot, w = row_at(JAW_ROWS, -0.82)
    tongue = nh.uv_ellipsoid((0, -0.82, top - 0.012), (w * 0.72, 0.24, 0.02), segments=10, rings=6)
    mb.add(nh.transform(tongue, JAW_ROT), MOUTH)
    top, bot, w = row_at(SKULL_ROWS, -0.84)
    mb.add(nh.uv_ellipsoid((0, -0.84, bot + 0.012), (w * 0.8, 0.26, 0.02), segments=10, rings=6), MOUTH)


def face_details(mb):
    top, bot, w = row_at(SKULL_ROWS, -0.73)
    for sx in (1, -1):
        # small amber eye set high on the skull, looking a bit forward
        e = Vector((sx * w * 0.84, -0.73, top - 0.075))
        mb.add(nh.ellipsoid(e, (0.026, 0.028, 0.024), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.016, -0.012, 0.0)), (0.012, 0.013, 0.014), subdivisions=1), PUPIL)
        # heavy brow ridge, lacrimal horn in front of the eye, postorbital boss behind
        mb.add(nh.ellipsoid(e + Vector((-sx * 0.006, -0.01, 0.034)), (0.04, 0.06, 0.022), subdivisions=2), skin)
        mb.add(nh.ellipsoid(e + Vector((-sx * 0.035, -0.08, 0.04)), (0.028, 0.036, 0.026), subdivisions=1), skin)
        mb.add(nh.ellipsoid(e + Vector((-sx * 0.01, 0.055, 0.02)), (0.026, 0.032, 0.024), subdivisions=1), skin)
        # nostril at the snout tip
        t2, b2, w2 = row_at(SKULL_ROWS, -1.105)
        mb.add(nh.ellipsoid((sx * w2 * 0.5, -1.105, t2 - 0.025), (0.014, 0.022, 0.01), subdivisions=1), PUPIL)


def leg(side, hip, knee, ankle, ball, toe_spread=0.42):
    """One continuous blended limb: thigh muscle sunk into the hip, calf, robust metatarsus, toes."""
    sx = side
    hip, knee, ankle, ball = (Vector((sx * p[0], p[1], p[2])) for p in (hip, knee, ankle, ball))
    d, d2, d3 = knee - hip, ankle - knee, ball - ankle
    # (point, fore-aft half depth, lateral half width); the first rings sit deep inside the body
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
        (ankle, 0.062, 0.058),
        (ankle + d3 * 0.4, 0.056, 0.052),
        (ankle + d3 * 0.8, 0.054, 0.052),
        (ball, 0.06, 0.056),
        (ball + Vector((0, -0.03, -0.01)), 0.0, 0.0),
    ]
    parts = [(loft(densify(path, 3), sides=14, ref=Vector((1, 0, 0))), leg_skin)]
    # three forward toes, splayed, each ending in a claw
    fwd = Vector((0, -1, 0))
    for k, ang in enumerate((-toe_spread, 0.0, toe_spread)):
        dirv = Matrix.Rotation(ang * -sx, 3, "Z") @ fwd
        length = 0.22 if k == 1 else 0.17
        p0 = ball + Vector((0, 0, -0.005))
        p1 = Vector((ball.x, ball.y, 0.032)) + dirv * length * 0.5
        p2 = Vector((ball.x, ball.y, 0.024)) + dirv * length
        parts.append((nh.tube([p0, p1, p2], [0.04, 0.03, 0.02], sides=7), leg_skin))
        tip = p2 + dirv * 0.06 + Vector((0, 0, -0.016))
        parts.append((cone(p2 - dirv * 0.01 + Vector((0, 0, 0.004)), tip, 0.02, sides=5), CLAW))
    # small dewclaw behind
    parts.append((cone(ball + Vector((0, 0.02, 0.03)), ball + Vector((sx * 0.02, 0.07, 0.005)), 0.016), CLAW))
    return parts


def arm(side):
    sx = side
    sh = Vector((sx * 0.15, -0.36, 0.79 + LIFT))
    el = Vector((sx * 0.20, -0.42, 0.68 + LIFT))
    wr = Vector((sx * 0.19, -0.50, 0.66 + LIFT))
    parts = [(nh.tube([sh, el, wr], [0.042, 0.03, 0.022], sides=8), skin)]
    for k in (-1, 1):
        base = wr + Vector((sx * 0.009 * k, -0.005, 0))
        tip = base + Vector((sx * 0.012 * k, -0.045, -0.03))
        parts.append((nh.tube([base, tip], [0.012, 0.007], sides=5), skin))
        parts.append((cone(tip, tip + Vector((0, -0.018, -0.018)), 0.007), CLAW))
    return parts


def build():
    mb = nh.MeshBuilder()
    mb.add(torso(), skin)
    mb.add(skull(), skin)
    mb.add(jaw(), skin)
    mouth_lining(mb)
    teeth(mb)
    face_details(mb)
    # throat filling between jaw and neck
    mb.add(nh.ellipsoid((0, -0.50, 0.96 + LIFT), (0.15, 0.14, 0.12), subdivisions=2), skin)

    # mid-stride: left leg planted forward, right leg pushing off behind
    hip_z = 0.86 + LIFT
    for part, col in leg(1, hip=(0.19, 0.12, hip_z), knee=(0.21, -0.15, 0.62),
                         ankle=(0.20, 0.04, 0.26), ball=(0.18, -0.12, 0.04)):
        mb.add(part, col)
    for part, col in leg(-1, hip=(0.19, 0.14, hip_z), knee=(0.21, 0.13, 0.60),
                         ankle=(0.20, 0.44, 0.29), ball=(0.18, 0.40, 0.04)):
        mb.add(part, col)
    for s in (1, -1):
        for part, col in arm(s):
            mb.add(part, col)

    obj = mb.to_object("TyrannosaurusRex", roughness=0.7)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "TyrannosaurusRex", ground=(0.33, 0.42, 0.24),
           views=((35, 22), (-90, 6), (25, 65)))
