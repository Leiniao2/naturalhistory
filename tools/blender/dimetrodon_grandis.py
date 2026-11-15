"""
Procedural Dimetrodon grandis (Early Permian sphenacodont synapsid, ~3 m) for map colonies.

A long, low sprawling synapsid standing on a sun-warmed bank: the forelimbs and hind limbs
splay out to the sides with the upper arm and thigh held nearly horizontal, the elbows and
knees bent at right angles and broad five-toed feet planted forward-outward. The trunk is
fairly narrow and deep, the neck short, and the long tail tapers away and droops toward
the ground with a slight sideways sweep. The skull is deep, narrow and tall-sided with
the orbits set high and far back; the mouth hangs slightly open to show the differentiated
teeth that give the genus its name ("two measures of teeth"): small incisors at the front
of the snout, a notch in the upper jaw line, two pairs of large canine-like fangs, then a
row of smaller blade-like cheek teeth, with a matching lower canine.
The body, legs, head and neck are fused into one seamless surface and lightly scaled by
displacement; the tall back sail is a crisp, separate membrane stretched between some
twenty-four elongated neural spines rising from the neck to the hips, tallest over the
middle of the back, the skin dipping slightly between the spine tips.
Painted brick-brown with dark transverse bands across the back and tail and a pale cream
belly; the sail is ochre with dark spines, a dusky lower band and a pale crown.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/dimetrodon_grandis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dimetrodon.fbx
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

NAME = "Dimetrodon"

BACK = (0.36, 0.20, 0.12)       # brick-brown
FLANK = (0.52, 0.32, 0.19)
BELLY = (0.80, 0.70, 0.52)
BAND = (0.17, 0.10, 0.07)
LEG = (0.40, 0.25, 0.16)
SAIL = (0.74, 0.50, 0.24)       # ochre membrane
SAIL_LOW = (0.36, 0.20, 0.12)
SAIL_TOP = (0.92, 0.82, 0.60)
SPINE = (0.22, 0.13, 0.08)
LIP = (0.12, 0.07, 0.05)
MOUTH = (0.50, 0.20, 0.18)
TOOTH = (0.94, 0.90, 0.78)
CLAW = (0.10, 0.08, 0.06)
EYE = (0.80, 0.56, 0.12)
PUPIL = (0.02, 0.02, 0.02)


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


def frac(x):
    return x - math.floor(x)


# ---------------------------------------------------------------- anatomy

def tail_x(y):
    """The tail sweeps gently off to one side."""
    s = max(0.0, (y - 0.30) / 1.1)
    return 0.16 * s * s


# neck -> shoulders -> deep narrow trunk -> hips -> long drooping tail
TORSO = [
    ((0.0, -0.64, 0.415), 0.080, 0.095),
    ((0.0, -0.56, 0.390), 0.105, 0.115),
    ((0.0, -0.46, 0.350), 0.140, 0.145),
    ((0.0, -0.32, 0.325), 0.160, 0.165),
    ((0.0, -0.14, 0.315), 0.168, 0.170),
    ((0.0, 0.04, 0.315), 0.152, 0.158),
    ((0.0, 0.20, 0.315), 0.125, 0.130),
    ((0.0, 0.34, 0.300), 0.094, 0.100),
    ((tail_x(0.52), 0.52, 0.265), 0.068, 0.076),
    ((tail_x(0.72), 0.72, 0.215), 0.050, 0.056),
    ((tail_x(0.92), 0.92, 0.165), 0.036, 0.040),
    ((tail_x(1.10), 1.10, 0.120), 0.024, 0.027),
    ((tail_x(1.26), 1.26, 0.082), 0.013, 0.015),
    ((tail_x(1.36), 1.36, 0.060), 0.005, 0.006),
    ((tail_x(1.40), 1.40, 0.055), 0.0, 0.0),
]


def torso_at(y):
    """(center x, center z, half width, half height) of the torso loft at y."""
    secs = TORSO
    for (c0, a0, b0), (c1, a1, b1) in zip(secs, secs[1:]):
        if c0[1] <= y <= c1[1]:
            k = (y - c0[1]) / (c1[1] - c0[1])
            return (c0[0] + (c1[0] - c0[0]) * k, c0[2] + (c1[2] - c0[2]) * k,
                    a0 + (a1 - a0) * k, b0 + (b1 - b0) * k)
    c, a, b = secs[0] if y < secs[0][0][1] else secs[-1]
    return c[0], c[2], a, b


# Upper skull: deep, narrow, with a notch in the tooth line in front of the fangs.
# (y, top z, tooth-margin z, half width)
SKULL_ROWS = [
    (-0.56, 0.500, 0.345, 0.080),
    (-0.61, 0.520, 0.322, 0.085),
    (-0.66, 0.518, 0.310, 0.080),
    (-0.71, 0.505, 0.304, 0.070),
    (-0.76, 0.486, 0.299, 0.060),
    (-0.81, 0.464, 0.294, 0.052),   # canine bulge of the maxilla
    (-0.845, 0.450, 0.297, 0.047),
    (-0.868, 0.440, 0.312, 0.043),  # the notch (diastema) in front of the fangs
    (-0.890, 0.426, 0.305, 0.038),  # premaxilla dips again
    (-0.910, 0.412, 0.307, 0.033),
    (-0.925, 0.392, 0.311, 0.025),
    (-0.936, 0.362, 0.317, 0.010),
]
JAW_ROWS = [  # lower jaw (y, top z, bottom z, half width), closed position
    (-0.56, 0.345, 0.250, 0.076),
    (-0.63, 0.318, 0.250, 0.072),
    (-0.70, 0.304, 0.254, 0.062),
    (-0.77, 0.298, 0.258, 0.052),
    (-0.84, 0.296, 0.262, 0.044),
    (-0.89, 0.298, 0.266, 0.036),
    (-0.915, 0.301, 0.272, 0.026),
    (-0.928, 0.303, 0.282, 0.010),
]
HINGE = Vector((0.0, -0.61, 0.315))
JAW_ROT = Matrix.Translation(HINGE) @ Matrix.Rotation(math.radians(5), 4, "X") @ Matrix.Translation(-HINGE)
EYE_Y = -0.645


def row_at(rows, y):
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k, b0 + (b1 - b0) * k, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1] if y < rows[-1][0] else rows[0]
    return t, b, w


def profile(rows, wk=1.0):
    return [((0.0, y, (top + bot) * 0.5), w * wk, (top - bot) * 0.5) for y, top, bot, w in rows]


# Sail: neural spines from the neck to the hips, a rounded crest highest mid-back.
SAIL_Y0, SAIL_Y1 = -0.56, 0.28
N_SPINES = 24


def sail_height(y):
    """Height of the sail crest above the back at y (0 outside the sail)."""
    t = (y - SAIL_Y0) / (SAIL_Y1 - SAIL_Y0)
    if t <= 0.0 or t >= 1.0:
        return 0.0
    # rounded, slightly front-heavy crest: steep at the neck, longer slope to the hips
    s = math.sin(math.pi * t ** 0.85)
    return 0.66 * s ** 0.8


def back_z(y):
    _x, zc, _w, h = torso_at(y)
    return zc + h


def spine_y(i):
    return SAIL_Y0 + 0.012 + (SAIL_Y1 - SAIL_Y0 - 0.024) * i / (N_SPINES - 1)


def spine_tip(i):
    """Spines lean back a little; tips stand slightly proud of the membrane."""
    y = spine_y(i)
    h = sail_height(y) + 0.02
    return Vector((0.0, y + 0.06 * h, back_z(y) + h))


def sail_membrane(cols=80, rows=8, th=0.006):
    """Double-sided membrane stretched between the spines; its top edge sags between tips."""
    bm = bmesh.new()
    grid = {}
    for side in (-1, 1):
        for i in range(cols + 1):
            t = i / cols
            y = SAIL_Y0 + 0.01 + (SAIL_Y1 - SAIL_Y0 - 0.02) * t
            # scallop: the membrane edge dips between neighbouring spine tips
            pos = (y - spine_y(0)) / (spine_y(1) - spine_y(0))
            sag = 0.035 * math.sin(math.pi * frac(pos)) ** 1.5 * nh.smoothstep(0.0, 0.08, sail_height(y))
            h = max(0.004, sail_height(y) - sag)
            base = back_z(y) - 0.05
            for j in range(rows + 1):
                f = j / rows
                z = base + (h + 0.05) * f
                yy = y + 0.06 * (z - back_z(y)) * nh.smoothstep(0.0, 0.1, z - back_z(y))
                thick = th * (1.0 - 0.5 * f)
                grid[(side, i, j)] = bm.verts.new(Vector((side * thick, yy, z)))
    for i in range(cols):
        for j in range(rows):
            for side in (-1, 1):
                q = [grid[(side, i, j)], grid[(side, i + 1, j)], grid[(side, i + 1, j + 1)], grid[(side, i, j + 1)]]
                bm.faces.new(q if side > 0 else list(reversed(q)))
    for i in range(cols):  # top edge
        bm.faces.new([grid[(1, i, rows)], grid[(1, i + 1, rows)], grid[(-1, i + 1, rows)], grid[(-1, i, rows)]])
    for j in range(rows):  # front and back edges
        bm.faces.new([grid[(1, 0, j)], grid[(1, 0, j + 1)], grid[(-1, 0, j + 1)], grid[(-1, 0, j)]])
        bm.faces.new([grid[(-1, cols, j)], grid[(-1, cols, j + 1)], grid[(1, cols, j + 1)], grid[(1, cols, j)]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def sail_paint(co, n):
    y = co.y
    h = max(sail_height(y), 0.02)
    t = (co.z - back_z(y)) / h
    c = nh.lerp(SAIL_LOW, SAIL, nh.smoothstep(0.02, 0.32, t))
    c = nh.lerp(c, SAIL_TOP, nh.smoothstep(0.80, 0.97, t))
    # faint dusky vertical streaks between the spines
    streak = noise.noise(Vector((y * 40.0, 0.0, co.z * 3.0)))
    c = nh.lerp(c, SAIL_LOW, 0.25 * nh.smoothstep(0.1, 0.5, streak) * (1.0 - t))
    k = 0.94 + 0.1 * noise.noise(co * 30.0)
    return tuple(x * k for x in c)


def spines(mb):
    for i in range(N_SPINES):
        y = spine_y(i)
        tip = spine_tip(i)
        base = Vector((0.0, y, back_z(y) - 0.04))
        mid = base.lerp(tip, 0.5) + Vector((0, 0.008, 0))
        r = 0.0095 if sail_height(y) > 0.1 else 0.007
        mb.add(nh.tube([base, mid, tip], [r, r * 0.8, r * 0.35], sides=6), SPINE)


LEG_DATA = []   # (side, foot centre, toe angles, toe lengths) for the crisp claws


def limbs(b):
    for s in (-1, 1):
        # forelimb: humerus straight out sideways, elbow bent, forearm down to a broad hand
        sh = Vector((s * 0.12, -0.40, 0.29))
        el = Vector((s * 0.33, -0.42, 0.24))
        wr = Vector((s * 0.35, -0.47, 0.035))
        b.add(nh.tube([sh, el], [0.070, 0.052], sides=14), LEG)
        b.add(oriented((s * 0.23, -0.41, 0.27), (0.085, 0.055, 0.055)), LEG)          # biceps / shoulder
        b.add(oriented(el, (0.050, 0.050, 0.052)), LEG)
        b.add(nh.tube([el, el.lerp(wr, 0.5) + Vector((s * 0.008, 0, 0)), wr], [0.050, 0.042, 0.032], sides=12), LEG)
        hand = Vector((s * 0.36, -0.50, 0.022))
        b.add(oriented(hand, (0.050, 0.060, 0.024)), LEG)
        LEG_DATA.append((s, hand, (-40, -18, 4, 26, 50), (0.050, 0.064, 0.070, 0.064, 0.046), 0.013))
        # hind limb: thigh out sideways, knee forward, shin down, long foot pointing forward-out
        hip = Vector((s * 0.11, 0.18, 0.29))
        kn = Vector((s * 0.35, 0.12, 0.25))
        an = Vector((s * 0.37, 0.20, 0.038))
        b.add(nh.tube([hip, kn], [0.090, 0.058], sides=14), LEG)
        b.add(oriented((s * 0.20, 0.17, 0.28), (0.10, 0.075, 0.070), yaw=-s * 8), LEG)  # thigh muscle
        b.add(oriented(kn, (0.055, 0.055, 0.058)), LEG)
        b.add(nh.tube([kn, kn.lerp(an, 0.5), an], [0.055, 0.046, 0.034], sides=12), LEG)
        foot = Vector((s * 0.38, 0.17, 0.022))
        b.add(oriented(foot, (0.055, 0.070, 0.024), yaw=-s * 20), LEG)
        LEG_DATA.append((s, foot, (-28, -8, 12, 32, 58), (0.060, 0.080, 0.092, 0.084, 0.056), 0.014))


def toes(b):
    """Toes fused into the feet; returns the claw placements."""
    out = []
    for s, palm, angs, lens, r in LEG_DATA:
        for ang, ln in zip(angs, lens):
            a = math.radians(ang)
            d = Vector((s * math.sin(a), -math.cos(a), 0.0))
            base = palm + d * 0.025
            tip = base + d * ln + Vector((0, 0, -0.006))
            b.add(nh.tube([base, base + d * ln * 0.55 + Vector((0, 0, 0.003)), tip], [r, r * 0.85, r * 0.65],
                          sides=8), LEG)
            out.append((tip, d))
    return out


# ---------------------------------------------------------------- skin

def sculpt(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        co, n = v.co, v.normal
        # small rounded scales, a little bigger on the back
        d = 0.0016 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 60.0)))
        d += 0.0012 * nh.smoothstep(0.3, 0.9, n.z) * (1.0 - nh.smoothstep(0.0, 0.4, noise.cell(co * 34.0)))
        # lip groove along the upper tooth margin
        if co.y < -0.6:
            _t, bot, w = row_at(SKULL_ROWS, co.y)
            if abs(co.x) > w * 0.5:
                d -= 0.004 * (1.0 - nh.smoothstep(0.0, 0.012, abs(co.z - bot - 0.008)))
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def body_paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.65, -0.15, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.05, 0.75, n.z))
    if co.z < 0.22 and co.y < 0.32:            # legs darker, no counter-shading
        c = nh.lerp(LEG, c, nh.smoothstep(0.10, 0.22, co.z) * nh.smoothstep(0.25, 0.10, abs(co.x)))
    # dark transverse bands over the back and tail, broken by noise
    if co.y > -0.55:
        band = 0.5 + 0.5 * math.sin(co.y * 22.0 + noise.noise(co * 5.0) * 1.6)
        c = nh.lerp(c, BAND, 0.6 * nh.smoothstep(0.6, 0.9, band) * nh.smoothstep(-0.25, 0.35, n.z))
    # head: darker crown, pale lower jaw, dark lip line
    if co.y < -0.58:
        c = nh.lerp(c, BACK, 0.35 * nh.smoothstep(0.2, 0.8, n.z))
        _t, bot, w = row_at(SKULL_ROWS, co.y)
        if co.z < bot + 0.002:
            c = nh.lerp(c, BELLY, 0.45)
        c = nh.lerp(c, LIP, 0.8 * (1.0 - nh.smoothstep(0.003, 0.012, abs(co.z - bot - 0.006))) *
                    nh.smoothstep(w * 0.4, w * 0.7, abs(co.x)))
    m = noise.noise(co * 16.0)
    k = (1.0 + 0.1 * m) * (0.94 + 0.1 * (1.0 - nh.smoothstep(0.1, 0.6, noise.cell(co * 60.0))))
    return tuple(max(0.0, x * k) for x in c)


# ---------------------------------------------------------------- crisp details

def teeth(mb, surf, jaw_surf):
    """Incisors, a notch, two big fangs, then small cheek teeth; a lower canine below."""
    up = [(-0.922, 0.018, 0.0050), (-0.910, 0.024, 0.0058), (-0.896, 0.020, 0.0055)]   # incisors
    up.append((-0.842, 0.072, 0.0115))   # main fang
    up.append((-0.824, 0.058, 0.0100))   # second fang
    y = -0.80
    while y < -0.63:                    # cheek teeth, getting smaller toward the back
        k = (y + 0.62) / -0.18
        up.append((y, 0.010 + 0.012 * k, 0.0042 + 0.002 * k))
        y += 0.0165
    for y, ln, r in up:
        top, bot, w = row_at(SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.80, y, bot - 0.1), (0, 0, 1))
            if loc is None or loc.z > bot + 0.06:
                continue
            base = loc + Vector((0, 0, 0.006))
            tip = Vector((loc.x + sx * 0.002, y + 0.1 * ln, loc.z - ln))
            mb.add(cone(base, tip, r), TOOTH, smooth=False)
    low = [(-0.915, 0.018, 0.005), (-0.898, 0.040, 0.0085)]  # lower incisor and canine
    y = -0.86
    while y < -0.66:
        low.append((y, 0.010, 0.004))
        y += 0.02
    for y, ln, r in low:
        top, bot, w = row_at(JAW_ROWS, y)
        for sx in (1, -1):
            o = JAW_ROT @ Vector((sx * w * 0.86 * 0.6, y, top + 0.1))
            loc, _n = jaw_surf.hit(o, JAW_ROT.to_3x3() @ Vector((0, 0, -1)))
            if loc is None:
                continue
            up_dir = JAW_ROT.to_3x3() @ Vector((0, 0, 1))
            mb.add(cone(loc - up_dir * 0.006, loc + up_dir * ln + Vector((-sx * 0.002, -0.003, 0)), r),
                   TOOTH, smooth=False)


class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal


def head_details(mb):
    top, bot, w = row_at(SKULL_ROWS, EYE_Y)
    for sx in (1, -1):
        e = Vector((sx * w * 0.80, EYE_Y, top - 0.040))
        mb.add(nh.ellipsoid(e, (0.018, 0.022, 0.018), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.012, -0.002, 0)), (0.006, 0.010, 0.012), subdivisions=1), PUPIL)
        t2, b2, w2 = row_at(SKULL_ROWS, -0.912)
        mb.add(nh.ellipsoid((sx * w2 * 0.66, -0.914, t2 - 0.020), (0.005, 0.008, 0.007), subdivisions=1), PUPIL)
    # dark mouth lining between the jaws
    mb.add(oriented((0, -0.75, 0.302), (0.040, 0.17, 0.010), pitch=-3, segments=14, rings=6), MOUTH)


def claws(mb, tips):
    for tip, d in tips:
        base = tip - d * 0.006 + Vector((0, 0, 0.004))
        end = tip + d * 0.022 + Vector((0, 0, -0.008))
        mb.add(nh.tube([base, base + d * 0.012, end], [0.0075, 0.0055, 0.0], sides=6), CLAW)


# ---------------------------------------------------------------- build / preview

def build():
    LEG_DATA.clear()
    b = nh.MeshBuilder()
    b.add(loft(densify(TORSO, 4), sides=24, power=2.1), FLANK)
    b.add(loft(densify(profile(SKULL_ROWS), 3), sides=20, power=2.5), FLANK)
    b.add(oriented((0, -0.60, 0.37), (0.075, 0.08, 0.075)), FLANK)                    # throat / jaw muscles
    for sx in (1, -1):
        b.add(oriented((sx * 0.060, EYE_Y, row_at(SKULL_ROWS, EYE_Y)[0] - 0.035), (0.030, 0.040, 0.028)), FLANK)
        b.add(oriented((sx * 0.06, -0.58, 0.41), (0.04, 0.06, 0.055)), FLANK)           # temporal muscle
        b.add(oriented((sx * 0.08, -0.40, 0.30), (0.08, 0.10, 0.10)), FLANK)            # chest
        b.add(oriented((sx * 0.07, 0.26, 0.30), (0.06, 0.16, 0.08)), FLANK)             # tail-base muscle
    limbs(b)
    claw_tips = toes(b)
    fused = b.fuse(voxel=0.0075, smooth=5, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, 17500)

    jb = nh.MeshBuilder()
    jb.add(loft(densify(profile(JAW_ROWS, 0.86), 3), sides=16, power=2.3), FLANK)
    jfused = nh.transform(decimate(jb.fuse(voxel=0.0055, smooth=4, smooth_factor=0.5), 1600), JAW_ROT)

    surf, jaw_surf = Surface(fused), Surface(jfused)
    mb = nh.MeshBuilder()
    teeth(mb, surf, jaw_surf)
    mb.add(fused, body_paint)
    mb.add(jfused, lambda co, n: nh.lerp(body_paint(co, n), BELLY, 0.35 * nh.smoothstep(0.0, -0.8, n.z)))
    mb.add(sail_membrane(), sail_paint)
    spines(mb)
    head_details(mb)
    claws(mb, claw_tips)
    obj = mb.to_object(NAME, roughness=0.65)
    nh.ground_to_zero(obj)
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head = Vector((0.0, -0.78, 0.36))
    out = Path(path)
    for i, off in enumerate((Vector((0.42, -0.42, 0.12)), Vector((-0.55, -0.12, 0.02)))):
        cam.location = head + off
        cam.rotation_euler = (head - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.46, 0.38, 0.26), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
