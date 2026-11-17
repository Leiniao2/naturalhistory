"""
Procedural Lagerpeton chanarensis (Middle-Late Triassic lagerpetid, ~70 cm) for map colonies.

A lagerpetid from the Chanares Formation of Argentina: a small, lightly built avemetatarsalian,
among the closest relatives of the pterosaurs and near the ancestry of the dinosaurs. Built on
the Eoraptor's body plan (eoraptor_lunensis.py) but slimmer and on much longer, stilt-like legs
with a very long metatarsus, a small head with small pointed teeth, short arms and a long tail
held out behind. Painted a sandy grey-brown with dark spots along the back and a pale belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/lagerpeton_chanarensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lagerpeton.fbx
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

NAME = "Lagerpeton"

BACK = (0.42, 0.36, 0.27)       # grey-brown
FLANK = (0.62, 0.55, 0.42)      # sandy
BELLY = (0.88, 0.84, 0.72)      # pale
STRIPE = (0.20, 0.16, 0.11)     # dark spots
LEG = (0.50, 0.44, 0.33)
MASK = (0.30, 0.25, 0.18)
MOUTH = (0.52, 0.20, 0.18)
TOOTH = (0.95, 0.92, 0.82)
CLAW = (0.12, 0.09, 0.07)
EYE = (0.88, 0.62, 0.14)
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


def cone(base, tip, r, sides=5):
    return nh.tube([base, tip], [r, 0.0], sides=sides)


# ---------------------------------------------------------------- anatomy

def tail_x(y):
    """The tail swings a little to one side, mid-stride."""
    s = max(0.0, (y - 0.25) / 0.65)
    return 0.07 * s * s


# head base -> S-curved neck -> short chest -> hips -> long tail held straight out
TORSO = [
    ((0.0, -0.405, 0.612), 0.030, 0.034),
    ((0.0, -0.37, 0.598), 0.031, 0.036),
    ((0.0, -0.32, 0.565), 0.034, 0.040),
    ((0.0, -0.265, 0.528), 0.042, 0.050),
    ((0.0, -0.20, 0.500), 0.060, 0.072),
    ((0.0, -0.11, 0.488), 0.074, 0.088),
    ((0.0, -0.01, 0.490), 0.072, 0.082),
    ((0.0, 0.08, 0.497), 0.064, 0.068),
    ((0.0, 0.17, 0.495), 0.052, 0.054),
    ((tail_x(0.28), 0.28, 0.487), 0.038, 0.041),
    ((tail_x(0.41), 0.41, 0.474), 0.028, 0.030),
    ((tail_x(0.54), 0.54, 0.459), 0.020, 0.021),
    ((tail_x(0.67), 0.67, 0.444), 0.013, 0.013),
    ((tail_x(0.79), 0.79, 0.430), 0.007, 0.007),
    ((tail_x(0.88), 0.88, 0.420), 0.0, 0.0),
]

# Small, low skull with a pointed snout (y, top z, upper lip z, half width)
SKULL_ROWS = [
    (-0.395, 0.656, 0.582, 0.036),
    (-0.42, 0.672, 0.576, 0.042),
    (-0.445, 0.668, 0.572, 0.039),
    (-0.47, 0.652, 0.571, 0.032),
    (-0.495, 0.635, 0.571, 0.026),
    (-0.52, 0.618, 0.573, 0.020),
    (-0.54, 0.604, 0.576, 0.0155),
    (-0.555, 0.593, 0.579, 0.010),
    (-0.563, 0.586, 0.581, 0.004),
]
JAW_ROWS = [  # lower jaw (y, lip z, bottom z, half width)
    (-0.40, 0.582, 0.546, 0.033),
    (-0.44, 0.575, 0.550, 0.031),
    (-0.48, 0.573, 0.555, 0.024),
    (-0.515, 0.574, 0.560, 0.018),
    (-0.542, 0.577, 0.566, 0.011),
    (-0.556, 0.579, 0.572, 0.004),
]
HINGE = Vector((0.0, -0.405, 0.582))
JAW_ROT = Matrix.Translation(HINGE) @ Matrix.Rotation(math.radians(9), 4, "X") @ Matrix.Translation(-HINGE)
EYE_Y = -0.432


def row_at(rows, y):
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k, b0 + (b1 - b0) * k, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1] if y < rows[-1][0] else rows[0]
    return t, b, w


def profile(rows, wk=1.0):
    return [((0.0, y, (top + bot) * 0.5), w * wk, (top - bot) * 0.5) for y, top, bot, w in rows]


TOES = []      # (base, direction, length, radius, claw)
FINGERS = []   # (points, radii, claw)
HIP_Z = 0.49


def leg(b, s, hip, knee, ankle, ball):
    """Long bird-like hind leg: thick thigh, slender shin, long metatarsus, three toes + hallux."""
    hip, knee, ankle, ball = (Vector((s * p[0], p[1], p[2])) for p in (hip, knee, ankle, ball))
    b.add(oriented(hip.lerp(knee, 0.35) + Vector((-s * 0.008, 0.01, 0.01)), (0.034, 0.072, 0.085),
                   pitch=math.degrees(math.atan2(knee.y - hip.y, hip.z - knee.z))), LEG)     # thigh muscle
    b.add(nh.tube([hip + Vector((0, 0, 0.03)), hip, hip.lerp(knee, 0.5), knee], [0.04, 0.046, 0.036, 0.022],
                  sides=14), LEG)
    b.add(nh.tube([knee, knee.lerp(ankle, 0.3), knee.lerp(ankle, 0.7), ankle], [0.024, 0.027, 0.017, 0.012],
                  sides=12), LEG)                                                            # shin with calf
    b.add(nh.tube([ankle, ankle.lerp(ball, 0.5), ball], [0.011, 0.0095, 0.010], sides=10), LEG)
    fwd = Vector((0, -1, 0))
    for k, ang in enumerate((-24, 0, 24)):
        d = Matrix.Rotation(math.radians(ang) * -s, 3, "Z") @ fwd
        ln = 0.062 if k == 1 else 0.048
        TOES.append((ball + Vector((0, 0, -0.002)), d, ln, 0.0085, True))
    # small inner toe (hallux) held off the ground behind the ball
    d = Vector((-s * 0.5, -0.4, -0.3)).normalized()
    TOES.append((ball + Vector((-s * 0.004, 0.02, 0.012)), d, 0.022, 0.005, True))


def arm(b, s):
    """Arm about half the leg length, ending in a grasping five-fingered hand."""
    sh = Vector((s * 0.050, -0.205, 0.462))
    el = Vector((s * 0.068, -0.175, 0.385))
    wr = Vector((s * 0.062, -0.235, 0.355))
    b.add(oriented((s * 0.045, -0.20, 0.455), (0.03, 0.04, 0.045)), FLANK)
    b.add(nh.tube([sh, sh.lerp(el, 0.5), el], [0.020, 0.017, 0.012], sides=10), FLANK)
    b.add(nh.tube([el, el.lerp(wr, 0.5), wr], [0.012, 0.010, 0.0085], sides=10), FLANK)
    b.add(oriented(wr + Vector((0, -0.010, -0.004)), (0.011, 0.014, 0.007), pitch=-30), FLANK)  # palm
    # digits I-III long and clawed, curling down and in; IV and V small stubs
    for k, (dx, ln, r, clawed) in enumerate(((-0.008, 0.026, 0.0042, True), (-0.002, 0.034, 0.0042, True),
                                             (0.005, 0.032, 0.0038, True), (0.010, 0.016, 0.003, False),
                                             (0.013, 0.008, 0.0026, False))):
        base = wr + Vector((s * dx, -0.018, -0.008))
        spread = Vector((s * dx * 2.5, -1.0, -0.55)).normalized()
        mid = base + spread * ln * 0.55
        tip = mid + (spread + Vector((0, 0.2, -0.7))).normalized() * ln * 0.45
        FINGERS.append(([base, mid, tip], [r, r * 0.85, r * 0.65], clawed))


# ---------------------------------------------------------------- skin

def sculpt(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        co, n = v.co, v.normal
        d = 0.0007 * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * 160.0)))
        d += 0.0005 * noise.noise(co * 70.0)
        # low bumps in a row along the spine
        if -0.36 < co.y < 0.6 and n.z > 0.5:
            row = 1.0 - nh.smoothstep(0.0, 0.012, abs(co.x - tail_x(co.y)))
            bump = 0.5 + 0.5 * math.sin(co.y * 140.0)
            d += 0.0022 * row * bump
        # antorbital depression on the side of the snout
        if -0.53 < co.y < -0.45 and abs(n.x) > 0.4:
            top, lip, w = row_at(SKULL_ROWS, co.y)
            r = math.hypot((co.y + 0.49) / 0.032, (co.z - (top + lip) * 0.5 - 0.002) / 0.016)
            d -= 0.004 * (1.0 - nh.smoothstep(0.5, 1.0, r))
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def body_paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.7, -0.1, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.2, 0.85, n.z))
    if co.z < 0.30:
        c = nh.lerp(LEG, c, nh.smoothstep(0.15, 0.30, co.z))
    # dark bands across the back and tail
    if co.y > -0.25:
        wob = noise.noise(co * 18.0) * 1.2
        spot = noise.noise(co * 34.0 + Vector((5.1, 2.3, 0.7))) + 0.15 * wob
        side = nh.smoothstep(-0.2, 0.4, n.z) * nh.smoothstep(0.36, 0.45, co.z)
        c = nh.lerp(c, STRIPE, 0.6 * nh.smoothstep(0.28, 0.42, spot) * side)
    # head: darker crown, eye stripe, pale throat
    if co.y < -0.30:
        c = nh.lerp(c, MASK, 0.5 * nh.smoothstep(0.2, 0.85, n.z) * nh.smoothstep(-0.30, -0.42, co.y))
        top, lip, w = row_at(SKULL_ROWS, co.y)
        e = math.hypot((co.y - EYE_Y) / 0.07, (co.z - (top - 0.022)) / 0.011)
        c = nh.lerp(c, MASK, 0.55 * (1.0 - nh.smoothstep(0.6, 1.0, e)))
        if co.z < lip and co.y < -0.38:
            c = nh.lerp(c, BELLY, 0.6)
    m = noise.noise(co * 40.0)
    k = (1.0 + 0.08 * m) * (0.95 + 0.08 * (1.0 - nh.smoothstep(0.1, 0.6, noise.cell(co * 160.0))))
    return tuple(max(0.0, x * k) for x in c)


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal


def leaf_tooth(base, length, width, fwd=0.0):
    """Leaf-shaped (lanceolate) tooth: broad flattened blade with a point."""
    tip = base + Vector((0, fwd, -length))
    pts = [base, base.lerp(tip, 0.45), tip]
    return nh.tube(pts, [width * 0.7, width, 0.0], sides=6, scale_xy=(1.0, 0.45))


def teeth(mb, surf, jaw_surf):
    # upper jaw: leaf-shaped teeth at the front, small recurved blades behind
    y = -0.556
    while y < -0.43:
        _t, lip, w = row_at(SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.72, y, lip - 0.03), (0, 0, 1))
            if loc is None or loc.z > lip + 0.02:
                continue
            if False:
                mb.add(leaf_tooth(loc + Vector((0, 0, 0.002)), 0.0085, 0.0034), TOOTH, smooth=False)
            else:
                base = loc + Vector((0, 0, 0.002))
                mb.add(nh.tube([base, base + Vector((0, -0.0015, -0.0045)), base + Vector((0, 0.0012, -0.008))],
                               [0.0022, 0.0014, 0.0], sides=5), TOOTH, smooth=False)
        y += 0.0105
    up = JAW_ROT.to_3x3() @ Vector((0, 0, 1))
    y = -0.548
    while y < -0.45:
        jt, _jb, jw = row_at(JAW_ROWS, y)
        for sx in (1, -1):
            loc, _n = jaw_surf.hit(JAW_ROT @ Vector((sx * jw * 0.66, y, jt + 0.03)), -up)
            if loc is None:
                continue
            ln = 0.0065 if y < -0.515 else 0.0055
            mb.add(cone(loc - up * 0.002, loc + up * ln + Vector((0, -0.001, 0)), 0.0019), TOOTH, smooth=False)
        y += 0.011


def head_details(mb):
    top, lip, w = row_at(SKULL_ROWS, EYE_Y)
    for sx in (1, -1):
        e = Vector((sx * w * 0.80, EYE_Y, top - 0.021))
        mb.add(nh.ellipsoid(e, (0.0105, 0.0135, 0.012), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.007, -0.002, 0)), (0.004, 0.006, 0.0075), subdivisions=2), PUPIL)
        t2, l2, w2 = row_at(SKULL_ROWS, -0.55)
        mb.add(nh.ellipsoid((sx * w2 * 0.7, -0.55, t2 - 0.003), (0.0026, 0.0042, 0.0022), subdivisions=1), PUPIL)


def digits(mb):
    for base, d, ln, r, clawed in TOES:
        tip = base + d * ln + Vector((0, 0, 0.0 if d.z < -0.1 else -0.001))
        mid = base.lerp(tip, 0.5) + Vector((0, 0, 0.003 if d.z > -0.1 else 0.0))
        mb.add(nh.tube([base - d * 0.006, mid, tip], [r, r * 0.8, r * 0.62], sides=7), LEG)
        cb = tip - d * 0.002
        mb.add(nh.tube([cb, cb + d * 0.006 + Vector((0, 0, 0.002)), cb + d * 0.014 + Vector((0, 0, -0.005))],
                       [r * 0.6, r * 0.45, 0.0], sides=6), CLAW)
    for pts, radii, clawed in FINGERS:
        mb.add(nh.tube(pts, radii, sides=6), FLANK)
        if clawed:
            d = (pts[-1] - pts[-2]).normalized()
            c0 = pts[-1] - d * 0.002
            mb.add(nh.tube([c0, c0 + d * 0.006 + Vector((0, 0.001, 0)), c0 + d * 0.012 + Vector((0, 0.004, -0.002))],
                           [radii[-1] * 0.95, radii[-1] * 0.65, 0.0], sides=6), CLAW)


# ---------------------------------------------------------------- build / preview

def build():
    TOES.clear()
    FINGERS.clear()
    b = nh.MeshBuilder()
    b.add(loft(densify(TORSO, 4), sides=22, power=2.1), FLANK)
    b.add(loft(densify(profile(SKULL_ROWS), 3), sides=18, power=2.3), FLANK)
    b.add(oriented((0, -0.40, 0.578), (0.030, 0.030, 0.028)), FLANK)                  # throat
    for sx in (1, -1):
        b.add(oriented((sx * 0.024, -0.405, 0.632), (0.016, 0.022, 0.02)), FLANK)      # jaw muscles
        b.add(oriented((sx * 0.026, EYE_Y, row_at(SKULL_ROWS, EYE_Y)[0] - 0.016), (0.012, 0.018, 0.010)), FLANK)  # brow
        b.add(oriented((sx * 0.048, 0.22, 0.485), (0.026, 0.10, 0.034)), FLANK)        # tail-base muscle
    leg(b, 1, hip=(0.062, 0.07, HIP_Z - 0.01), knee=(0.072, -0.05, 0.31), ankle=(0.068, 0.06, 0.115),
        ball=(0.064, -0.035, 0.010))
    leg(b, -1, hip=(0.062, 0.09, HIP_Z - 0.01), knee=(0.072, 0.03, 0.30), ankle=(0.066, 0.20, 0.135),
        ball=(0.062, 0.19, 0.012))
    for s in (1, -1):
        arm(b, s)
    fused = b.fuse(voxel=0.0035, smooth=5, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, 10000)

    jb = nh.MeshBuilder()
    jb.add(loft(densify(profile(JAW_ROWS, 0.95), 3), sides=16, power=2.2), FLANK)
    jfused = nh.transform(decimate(jb.fuse(voxel=0.0028, smooth=4, smooth_factor=0.5), 1200), JAW_ROT)

    surf, jaw_surf = Surface(fused), Surface(jfused)
    mb = nh.MeshBuilder()
    teeth(mb, surf, jaw_surf)
    mb.add(fused, body_paint)
    mb.add(jfused, lambda co, n: nh.lerp(body_paint(co, n), BELLY, 0.5 * nh.smoothstep(0.1, -0.7, n.z)))
    mb.add(oriented((0, -0.48, 0.574), (0.018, 0.075, 0.004), pitch=-5, segments=12, rings=6), MOUTH)
    head_details(mb)
    digits(mb)
    obj = mb.to_object(NAME, roughness=0.65)
    # Lagerpetids stood on long, stilt-like hind legs and were slimmer than Eoraptor: stretch
    # everything below the belly upward (the legs, mostly the long metatarsus) and narrow the body
    for v in obj.data.vertices:
        co = v.co
        if co.z < LEG_TOP:
            co.z *= LEG_STRETCH
        else:
            co.z += LEG_TOP * (LEG_STRETCH - 1.0)
            co.x *= 0.86
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    hip = HIP_Z + LEG_TOP * (LEG_STRETCH - 1.0)
    print(f"  height {max(zs):.3f}, hip {hip:.3f} -> hip fraction {hip / max(zs):.2f}")
    return obj


LEG_TOP, LEG_STRETCH = 0.44, 1.35


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head = Vector((0.0, -0.46, 0.60))
    out = Path(path)
    for i, off in enumerate((Vector((0.20, -0.20, 0.06)), Vector((-0.17, -0.12, -0.02)))):
        cam.location = head + off
        cam.rotation_euler = (head - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.46, 0.40, 0.28), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
