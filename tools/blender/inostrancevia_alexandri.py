"""
Procedural Inostrancevia alexandri (Late Permian gorgonopsid, ~3.5 m) for map colonies.

The largest gorgonopsian, the apex predator of the end-Permian Russian platform, caught
mid-stride. Compared with the older sprawling synapsids its limbs are carried much more
upright: the hind legs swing beneath the hips with the knee forward and the ankle back,
and the forelimbs are semi-erect with the elbows only a little out from the chest, on
compact five-toed clawed feet. A deep, dog-like chest, a slim waist, strong haunches and a
moderately long tail held clear of the ground. The skull is long and low with a broad,
heavy temporal region behind the eyes, a rounded, slightly convex snout and a deep chin;
huge, laterally flattened sabre-like upper canines hang down outside the closed lower jaw
well past the chin, behind a row of big pointed incisors.
Body, legs, neck and head are fused into one seamless surface and sculpted by
displacement: fine pebbly skin, a lip groove and wrinkles over the snout. Painted
ochre-tawny with dark brown transverse stripes over the back, haunches and tail, a darker
face mask and crown, and a pale cream throat and belly.
Crisp details on top: sabres, incisors and small post-canines, eyes, nostrils and claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/inostrancevia_alexandri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Inostrancevia.fbx
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

NAME = "Inostrancevia"

BACK = (0.42, 0.29, 0.16)       # dark ochre
FLANK = (0.62, 0.46, 0.27)      # tawny
BELLY = (0.84, 0.76, 0.60)
STRIPE = (0.19, 0.12, 0.07)
LEG = (0.50, 0.36, 0.22)
MASK = (0.26, 0.17, 0.10)
LIP = (0.10, 0.06, 0.04)
MOUTH = (0.48, 0.18, 0.16)
TOOTH = (0.95, 0.91, 0.80)
SABRE_ROOT = (0.80, 0.74, 0.60)
CLAW = (0.10, 0.08, 0.06)
EYE = (0.86, 0.60, 0.12)
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
    """The tail swings a little to one side, mid-stride."""
    s = max(0.0, (y - 0.45) / 0.85)
    return 0.10 * s * s


# neck -> deep chest -> slim waist -> haunches -> tail held clear of the ground
TORSO = [
    ((0.0, -0.62, 0.590), 0.085, 0.095),
    ((0.0, -0.52, 0.575), 0.115, 0.125),
    ((0.0, -0.40, 0.540), 0.150, 0.172),
    ((0.0, -0.24, 0.515), 0.168, 0.185),
    ((0.0, -0.06, 0.520), 0.150, 0.160),
    ((0.0, 0.12, 0.530), 0.135, 0.138),
    ((0.0, 0.30, 0.545), 0.138, 0.140),
    ((0.0, 0.44, 0.540), 0.112, 0.115),
    ((tail_x(0.58), 0.58, 0.515), 0.078, 0.082),
    ((tail_x(0.76), 0.76, 0.460), 0.054, 0.058),
    ((tail_x(0.94), 0.94, 0.390), 0.037, 0.040),
    ((tail_x(1.10), 1.10, 0.320), 0.022, 0.024),
    ((tail_x(1.22), 1.22, 0.265), 0.010, 0.011),
    ((tail_x(1.28), 1.28, 0.240), 0.0, 0.0),
]

# Long, low skull, broad behind the eyes; closed jaw (y, top z, upper lip z, half width)
SKULL_ROWS = [
    (-0.56, 0.665, 0.505, 0.100),
    (-0.62, 0.680, 0.490, 0.112),
    (-0.68, 0.668, 0.482, 0.104),
    (-0.74, 0.645, 0.478, 0.086),
    (-0.80, 0.622, 0.476, 0.072),
    (-0.86, 0.614, 0.476, 0.066),
    (-0.91, 0.608, 0.478, 0.064),   # broad over the sabre roots
    (-0.955, 0.598, 0.482, 0.057),
    (-0.99, 0.580, 0.486, 0.047),
    (-1.012, 0.556, 0.490, 0.032),
    (-1.024, 0.525, 0.494, 0.012),
]
JAW_ROWS = [  # lower jaw (y, lip z, bottom z, half width), deepening into the chin
    (-0.56, 0.510, 0.420, 0.094),
    (-0.64, 0.490, 0.425, 0.090),
    (-0.72, 0.480, 0.432, 0.076),
    (-0.80, 0.477, 0.436, 0.060),
    (-0.88, 0.477, 0.432, 0.050),
    (-0.94, 0.480, 0.418, 0.046),
    (-0.985, 0.485, 0.418, 0.038),
    (-1.008, 0.490, 0.436, 0.024),
    (-1.016, 0.492, 0.458, 0.008),
]
HINGE = Vector((0.0, -0.58, 0.485))
JAW_ROT = Matrix.Translation(HINGE) @ Matrix.Rotation(math.radians(11), 4, "X") @ Matrix.Translation(-HINGE)
EYE_Y = -0.715
SABRE_Y = -0.915


def row_at(rows, y):
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k, b0 + (b1 - b0) * k, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1] if y < rows[-1][0] else rows[0]
    return t, b, w


def profile(rows, wk=1.0):
    return [((0.0, y, (top + bot) * 0.5), w * wk, (top - bot) * 0.5) for y, top, bot, w in rows]


LEG_DATA = []   # (side, foot centre, toe angles, toe lengths, toe radius) for toes and claws


def limbs(b):
    for s in (-1, 1):
        # semi-erect forelimb: elbow a little out and back, forearm under the shoulder
        sh = Vector((s * 0.135, -0.36, 0.48))
        el = Vector((s * 0.200, -0.30, 0.285))
        wr = Vector((s * 0.195, -0.37, 0.065))
        b.add(oriented((s * 0.12, -0.36, 0.47), (0.08, 0.12, 0.13), pitch=-20), LEG)        # shoulder / triceps
        b.add(nh.tube([sh, sh.lerp(el, 0.5), el], [0.080, 0.065, 0.052], sides=14), LEG)
        b.add(oriented(el, (0.050, 0.055, 0.052)), LEG)
        b.add(nh.tube([el, el.lerp(wr, 0.45), wr], [0.050, 0.045, 0.032], sides=12), LEG)
        b.add(oriented((s * 0.20, -0.33, 0.20), (0.045, 0.05, 0.075), pitch=15), LEG)        # forearm muscle
        hand = Vector((s * 0.198, -0.405, 0.024))
        b.add(nh.tube([wr, hand + Vector((0, 0.01, 0.006))], [0.032, 0.03], sides=10), LEG)
        b.add(oriented(hand, (0.040, 0.050, 0.022)), LEG)
        LEG_DATA.append((s, hand, (-30, -14, 0, 14, 30), (0.040, 0.050, 0.056, 0.052, 0.040), 0.012))
        # hind limb under the hip: knee forward, ankle back, digitigrade-ish foot
        hip = Vector((s * 0.125, 0.33, 0.50))
        kn = Vector((s * 0.175, 0.22, 0.30))
        an = Vector((s * 0.170, 0.38, 0.085))
        b.add(oriented((s * 0.12, 0.30, 0.46), (0.085, 0.17, 0.15), pitch=30), LEG)           # thigh
        b.add(nh.tube([hip, hip.lerp(kn, 0.5), kn], [0.085, 0.070, 0.052], sides=14), LEG)
        b.add(oriented(kn, (0.052, 0.055, 0.055)), LEG)
        b.add(nh.tube([kn, kn.lerp(an, 0.5), an], [0.052, 0.042, 0.030], sides=12), LEG)
        b.add(oriented((s * 0.175, 0.28, 0.24), (0.045, 0.07, 0.08), pitch=-35), LEG)         # calf
        foot = Vector((s * 0.172, 0.34, 0.024))
        b.add(nh.tube([an, foot + Vector((0, 0.012, 0.006))], [0.030, 0.028], sides=10), LEG)
        b.add(oriented(foot, (0.042, 0.058, 0.022)), LEG)
        LEG_DATA.append((s, foot, (-28, -12, 2, 16, 32), (0.045, 0.058, 0.066, 0.060, 0.044), 0.0125))


def toes(b):
    out = []
    for s, palm, angs, lens, r in LEG_DATA:
        for ang, ln in zip(angs, lens):
            a = math.radians(ang)
            d = Vector((s * math.sin(a), -math.cos(a), 0.0))
            base = palm + d * 0.025
            tip = base + d * ln + Vector((0, 0, -0.008))
            b.add(nh.tube([base, base + d * ln * 0.55 + Vector((0, 0, 0.004)), tip], [r, r * 0.85, r * 0.62],
                          sides=8), LEG)
            out.append((tip, d))
    return out


# ---------------------------------------------------------------- skin

def lip_dist(co):
    """0 on the closed mouth line along the side of the head, 1 away from it."""
    if co.y > -0.58 or co.y < -1.02:
        return 1.0
    _t, lip, w = row_at(SKULL_ROWS, co.y)
    if abs(co.x) < w * 0.45:
        return 1.0
    return min(1.0, abs(co.z - lip) / 0.008)


def sculpt(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        co, n = v.co, v.normal
        d = 0.0014 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 65.0)))
        d += 0.0010 * noise.noise(co * 30.0)
        d -= 0.004 * (1.0 - lip_dist(co))
        if co.y < -0.80 and co.z > 0.5:                 # wrinkled skin over the snout
            d += 0.0015 * noise.noise(Vector((co.x * 80.0, co.y * 30.0, co.z * 80.0)))
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def body_paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.7, -0.15, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.15, 0.85, n.z))
    if co.z < 0.30:
        c = nh.lerp(LEG, c, nh.smoothstep(0.12, 0.30, co.z))
    # tiger-like dark stripes over the back, haunches and tail
    if co.y > -0.45:
        wob = noise.noise(co * 5.0) * 1.4
        band = 0.5 + 0.5 * math.sin(co.y * 30.0 + co.z * 4.0 + wob)
        side = nh.smoothstep(-0.35, 0.2, n.z)
        c = nh.lerp(c, STRIPE, 0.75 * nh.smoothstep(0.72, 0.92, band) * side)
    # head: dark mask over the crown and snout, pale throat and jaw
    if co.y < -0.55:
        c = nh.lerp(c, MASK, 0.55 * nh.smoothstep(0.1, 0.8, n.z))
        _t, lip, w = row_at(SKULL_ROWS, co.y)
        if co.z < lip - 0.004:
            c = nh.lerp(c, BELLY, 0.55 * nh.smoothstep(lip - 0.004, lip - 0.03, co.z))
        c = nh.lerp(c, LIP, 0.85 * (1.0 - lip_dist(co)))
        # dark eye stripe
        e = math.hypot((co.y - EYE_Y) / 0.06, (co.z - (row_at(SKULL_ROWS, co.y)[0] - 0.04)) / 0.025)
        c = nh.lerp(c, MASK, 0.5 * (1.0 - nh.smoothstep(0.6, 1.0, e)))
    m = noise.noise(co * 16.0)
    k = (1.0 + 0.08 * m) * (0.95 + 0.08 * (1.0 - nh.smoothstep(0.1, 0.6, noise.cell(co * 65.0))))
    return tuple(max(0.0, x * k) for x in c)


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal


def sabres(mb):
    """Huge, laterally flattened, gently recurved upper canines hanging outside the jaw."""
    def col(co, n):
        return nh.lerp(TOOTH, SABRE_ROOT, nh.smoothstep(0.43, 0.47, co.z))
    for sx in (1, -1):
        _t, lip, w = row_at(SKULL_ROWS, SABRE_Y)
        _jt, _jb, jw = row_at(JAW_ROWS, SABRE_Y - 0.02)
        x0 = max(w * 0.80, jw + 0.004)
        pts = [Vector((sx * w * 0.70, SABRE_Y, lip + 0.03)),
               Vector((sx * x0, SABRE_Y + 0.002, lip - 0.01)),
               Vector((sx * (x0 + 0.004), SABRE_Y + 0.010, lip - 0.055)),
               Vector((sx * (x0 + 0.002), SABRE_Y + 0.024, lip - 0.100)),
               Vector((sx * x0, SABRE_Y + 0.040, lip - 0.135))]
        # blade: wide fore-aft, thin side to side
        bm = nh.tube(pts, [0.020, 0.019, 0.0155, 0.010, 0.0], sides=10, scale_xy=(1.0, 0.45))
        mb.add(bm, col, smooth=True)


def teeth(mb, surf, jaw_surf):
    for y, ln, r in ((-1.014, 0.026, 0.0065), (-1.000, 0.032, 0.0075), (-0.984, 0.034, 0.008),
                     (-0.966, 0.030, 0.0075)):                       # big incisors
        _t, lip, w = row_at(SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.70, y, lip - 0.1), (0, 0, 1))
            if loc is None or loc.z > lip + 0.05:
                continue
            mb.add(cone(loc + Vector((0, 0, 0.006)), Vector((loc.x, y + 0.004, loc.z - ln)), r),
                   TOOTH, smooth=False)
    y = -0.88
    while y < -0.74:                                                 # few small post-canines
        _t, lip, w = row_at(SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.80, y, lip - 0.1), (0, 0, 1))
            if loc is not None and loc.z < lip + 0.05:
                mb.add(cone(loc + Vector((0, 0, 0.004)), Vector((loc.x, y, loc.z - 0.011)), 0.0042),
                       TOOTH, smooth=False)
        y += 0.024
    up = JAW_ROT.to_3x3() @ Vector((0, 0, 1))
    for y, ln, r in ((-1.000, 0.022, 0.006), (-0.985, 0.026, 0.0065), (-0.968, 0.028, 0.007),
                     (-0.945, 0.036, 0.0085)):                        # lower incisors and canine
        jt, _jb, jw = row_at(JAW_ROWS, y)
        for sx in (1, -1):
            loc, _n = jaw_surf.hit(JAW_ROT @ Vector((sx * jw * 0.62, y, jt + 0.1)), -up)
            if loc is None:
                continue
            mb.add(cone(loc - up * 0.006, loc + up * ln + Vector((0, -0.003, 0)), r), TOOTH, smooth=False)


def head_details(mb):
    top, lip, w = row_at(SKULL_ROWS, EYE_Y)
    for sx in (1, -1):
        e = Vector((sx * w * 0.86, EYE_Y, top - 0.045))
        mb.add(nh.ellipsoid(e, (0.017, 0.021, 0.017), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.011, -0.003, 0)), (0.006, 0.010, 0.011), subdivisions=2), PUPIL)
        t2, l2, w2 = row_at(SKULL_ROWS, -1.006)
        mb.add(nh.ellipsoid((sx * w2 * 0.6, -1.010, t2 - 0.012), (0.006, 0.007, 0.006), subdivisions=1), PUPIL)


def claws(mb, tips):
    for tip, d in tips:
        base = tip - d * 0.006 + Vector((0, 0, 0.005))
        end = tip + d * 0.024 + Vector((0, 0, -0.010))
        mb.add(nh.tube([base, base + d * 0.012, end], [0.0078, 0.0058, 0.0], sides=6), CLAW)


# ---------------------------------------------------------------- build / preview

def build():
    LEG_DATA.clear()
    b = nh.MeshBuilder()
    b.add(loft(densify(TORSO, 4), sides=24, power=2.1), FLANK)
    b.add(loft(densify(profile(SKULL_ROWS), 3), sides=20, power=2.4), FLANK)
    b.add(oriented((0, -0.60, 0.53), (0.095, 0.08, 0.09)), FLANK)                    # throat
    for sx in (1, -1):
        b.add(oriented((sx * 0.070, -0.62, 0.60), (0.045, 0.07, 0.06)), FLANK)        # jaw-closing muscles
        b.add(oriented((sx * 0.060, EYE_Y, row_at(SKULL_ROWS, EYE_Y)[0] - 0.040), (0.026, 0.036, 0.024)), FLANK)
        b.add(oriented((sx * 0.052, SABRE_Y, 0.53), (0.022, 0.035, 0.045)), FLANK)    # sabre root bulge
        b.add(oriented((sx * 0.07, -0.34, 0.50), (0.09, 0.13, 0.14)), FLANK)          # chest
    limbs(b)
    claw_tips = toes(b)
    fused = b.fuse(voxel=0.0075, smooth=5, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, 20000)

    jb = nh.MeshBuilder()
    jb.add(loft(densify(profile(JAW_ROWS, 0.95), 3), sides=18, power=2.3), FLANK)
    jfused = nh.transform(decimate(jb.fuse(voxel=0.006, smooth=4, smooth_factor=0.5), 2000), JAW_ROT)

    surf, jaw_surf = Surface(fused), Surface(jfused)
    mb = nh.MeshBuilder()
    teeth(mb, surf, jaw_surf)
    mb.add(fused, body_paint)
    mb.add(jfused, lambda co, n: nh.lerp(body_paint(co, n), BELLY, 0.5 * nh.smoothstep(0.1, -0.7, n.z)))
    mb.add(oriented((0, -0.79, 0.468), (0.050, 0.20, 0.012), pitch=-6, segments=14, rings=6), MOUTH)
    sabres(mb)
    head_details(mb)
    claws(mb, claw_tips)
    obj = mb.to_object(NAME, roughness=0.65)
    nh.ground_to_zero(obj)
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head = Vector((0.0, -0.84, 0.52))
    out = Path(path)
    for i, off in enumerate((Vector((0.50, -0.50, 0.14)), Vector((-0.65, -0.12, 0.02)))):
        cam.location = head + off
        cam.rotation_euler = (head - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.44, 0.38, 0.27), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
