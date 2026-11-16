"""
Procedural Cynognathus crateronotus (Early-Middle Triassic cynodont, ~1.2 m) for map colonies.

A wolf-sized, wolf-like predatory cynodont (a close relative of the ancestors of mammals)
caught mid-stride. The head is very large for the body - long, with a broad back where
the jaw muscles bulge out over wide cheek arches behind the eyes, a deep snout and a
massive, deep lower jaw, the mouth a little open to show the incisors, the big dagger-like
upper and lower canines and the blade-like cheek teeth behind them. The body is compact
with a deep chest; the limbs are carried more upright than in earlier synapsids, the hind
legs well beneath the hips and the elbows only a little out from the chest, on five-toed
clawed feet. A short, tapering tail.
Body, legs, neck and head are fused into one seamless surface; a coat of short fur (which
cynodonts probably had) is displaced into it. Painted dusky grey-brown, darker along the
back with faint dark stripes over the shoulders and haunches, paler buff flanks and a
cream throat and belly; a darker, short-haired muzzle.
Crisp details on top: lower jaw, incisors, canines and cheek teeth, eyes, nostrils and claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/cynognathus_crateronotus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cynognathus.fbx
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

NAME = "Cynognathus"

FUR = (0.36, 0.30, 0.23)        # dusky grey-brown
FUR_DARK = (0.18, 0.15, 0.11)
FLANK = (0.56, 0.48, 0.36)      # buff
BELLY = (0.82, 0.76, 0.62)
STRIPE = (0.16, 0.13, 0.10)
MUZZLE = (0.24, 0.20, 0.16)
LEG = (0.32, 0.27, 0.21)
LIP = (0.08, 0.06, 0.05)
MOUTH = (0.48, 0.20, 0.18)
TOOTH = (0.95, 0.92, 0.82)
CLAW = (0.10, 0.08, 0.06)
EYE = (0.62, 0.40, 0.12)
PUPIL = (0.02, 0.02, 0.02)
NOSE = (0.10, 0.08, 0.07)


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
    s = max(0.0, (y - 0.2) / 0.3)
    return 0.05 * s * s


# neck -> deep chest -> waist -> hips -> short tapering tail
TORSO = [
    ((0.0, -0.40, 0.475), 0.072, 0.082),
    ((0.0, -0.33, 0.460), 0.090, 0.104),
    ((0.0, -0.23, 0.440), 0.118, 0.138),
    ((0.0, -0.10, 0.432), 0.122, 0.135),
    ((0.0, 0.03, 0.438), 0.110, 0.115),
    ((0.0, 0.14, 0.448), 0.112, 0.112),
    ((0.0, 0.23, 0.440), 0.084, 0.086),
    ((tail_x(0.31), 0.31, 0.410), 0.050, 0.052),
    ((tail_x(0.38), 0.38, 0.372), 0.032, 0.033),
    ((tail_x(0.44), 0.44, 0.333), 0.016, 0.016),
    ((tail_x(0.475), 0.475, 0.310), 0.0, 0.0),
]

# Big skull, broad over the cheek arches; (y, top z, upper lip z, half width)
SKULL_ROWS = [
    (-0.37, 0.530, 0.410, 0.082),
    (-0.42, 0.550, 0.398, 0.098),
    (-0.47, 0.548, 0.392, 0.094),
    (-0.52, 0.530, 0.390, 0.072),
    (-0.57, 0.516, 0.389, 0.058),
    (-0.62, 0.502, 0.390, 0.052),
    (-0.655, 0.490, 0.392, 0.049),   # broad over the canine roots
    (-0.685, 0.474, 0.395, 0.042),
    (-0.705, 0.452, 0.398, 0.030),
    (-0.714, 0.426, 0.401, 0.012),
]
JAW_ROWS = [  # massive lower jaw (y, lip z, bottom z, half width), deep coronoid region behind
    (-0.37, 0.415, 0.322, 0.080),
    (-0.44, 0.402, 0.330, 0.077),
    (-0.52, 0.394, 0.344, 0.060),
    (-0.60, 0.393, 0.350, 0.046),
    (-0.65, 0.396, 0.350, 0.040),
    (-0.68, 0.399, 0.354, 0.033),
    (-0.700, 0.402, 0.368, 0.017),
]
HINGE = Vector((0.0, -0.39, 0.402))
JAW_ROT = Matrix.Translation(HINGE) @ Matrix.Rotation(math.radians(11), 4, "X") @ Matrix.Translation(-HINGE)
EYE_Y = -0.535
CANINE_Y = -0.652
HIP_Z = 0.44


def row_at(rows, y):
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k, b0 + (b1 - b0) * k, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1] if y < rows[-1][0] else rows[0]
    return t, b, w


def profile(rows, wk=1.0):
    return [((0.0, y, (top + bot) * 0.5), w * wk, (top - bot) * 0.5) for y, top, bot, w in rows]


LEG_DATA = []   # (side, foot centre, toe angles, toe lengths, toe radius)


def limbs(b):
    for s, ph in ((1, 1.0), (-1, -1.0)):
        # forelimb: semi-erect, elbow a little out, forearm under the shoulder
        sh = Vector((s * 0.095, -0.24, 0.40))
        el = Vector((s * 0.140, -0.20 + 0.02 * ph, 0.235))
        wr = Vector((s * 0.128, -0.25 - 0.05 * ph, 0.055))
        b.add(oriented((s * 0.085, -0.24, 0.40), (0.06, 0.09, 0.10), pitch=-20), FUR)
        b.add(nh.tube([sh, sh.lerp(el, 0.5), el], [0.058, 0.048, 0.036], sides=14), FUR)
        b.add(nh.tube([el, el.lerp(wr, 0.45), wr], [0.036, 0.031, 0.022], sides=12), FUR)
        b.add(oriented(el.lerp(wr, 0.3), (0.032, 0.036, 0.06), pitch=15), FUR)          # forearm muscle
        hand = Vector((wr.x, wr.y - 0.03, 0.018))
        b.add(nh.tube([wr, hand + Vector((0, 0.008, 0.005))], [0.022, 0.021], sides=10), FUR)
        b.add(oriented(hand, (0.030, 0.036, 0.016)), FUR)
        LEG_DATA.append((s, hand, (-30, -14, 0, 14, 30), (0.028, 0.034, 0.038, 0.035, 0.026), 0.0085))
        # hind limb: well under the hip, knee forward, ankle back
        hip = Vector((s * 0.095, 0.15, 0.42))
        kn = Vector((s * 0.125, 0.07 - 0.05 * ph, 0.25))
        an = Vector((s * 0.122, 0.20 - 0.07 * ph, 0.065))
        b.add(oriented((s * 0.09, 0.14, 0.39), (0.07, 0.13, 0.12), pitch=30), FUR)       # thigh
        b.add(nh.tube([hip, hip.lerp(kn, 0.5), kn], [0.066, 0.054, 0.040], sides=14), FUR)
        b.add(nh.tube([kn, kn.lerp(an, 0.5), an], [0.040, 0.031, 0.021], sides=12), FUR)
        b.add(oriented(kn.lerp(an, 0.25) + Vector((0, 0.008, 0)), (0.030, 0.034, 0.05), pitch=-30), FUR)  # calf
        foot = Vector((an.x, an.y - 0.05, 0.018))
        b.add(nh.tube([an, an.lerp(foot, 0.5), foot + Vector((0, 0.012, 0.005))], [0.021, 0.02, 0.02],
                      sides=10), FUR)
        b.add(oriented(foot, (0.031, 0.042, 0.016)), FUR)
        LEG_DATA.append((s, foot, (-28, -12, 2, 16, 32), (0.032, 0.040, 0.045, 0.041, 0.030), 0.009))


def toes(b):
    out = []
    for s, palm, angs, lens, r in LEG_DATA:
        for ang, ln in zip(angs, lens):
            a = math.radians(ang)
            d = Vector((s * math.sin(a), -math.cos(a), 0.0))
            base = palm + d * 0.018
            tip = base + d * ln + Vector((0, 0, -0.006))
            b.add(nh.tube([base, base + d * ln * 0.55 + Vector((0, 0, 0.003)), tip], [r, r * 0.85, r * 0.62],
                          sides=8), FUR)
            out.append((tip, d, r))
    return out


# ---------------------------------------------------------------- fur / paint

def lip_dist(co):
    """0 on the mouth line along the side of the head, 1 away from it."""
    if co.y > -0.40 or co.y < -0.72:
        return 1.0
    _t, lip, w = row_at(SKULL_ROWS, co.y)
    if abs(co.x) < w * 0.45:
        return 1.0
    return min(1.0, abs(co.z - lip) / 0.006)


def muzzle(co):
    """1 on the short-haired snout in front of the eyes."""
    return nh.smoothstep(-0.56, -0.62, co.y)


def sculpt(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        co, n = v.co, v.normal
        d = 0.0
        if co.z > 0.03:
            fur = 1.0 - 0.7 * muzzle(co)
            streak = noise.noise(Vector((co.x * 150.0, co.y * 40.0, co.z * 150.0)))
            d += fur * (0.0016 * noise.noise(co * 70.0) + 0.0011 * streak)
        d -= 0.004 * (1.0 - lip_dist(co))
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def body_paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.7, -0.15, n.z))
    c = nh.lerp(c, FUR, nh.smoothstep(0.1, 0.75, n.z))
    c = nh.lerp(c, FUR_DARK, 0.45 * nh.smoothstep(0.75, 0.98, n.z) * nh.smoothstep(-0.45, -0.35, co.y))
    if co.z < 0.25:
        c = nh.lerp(LEG, c, nh.smoothstep(0.08, 0.25, co.z))
    c = nh.lerp(c, FUR_DARK, 0.35 * nh.smoothstep(0.1, 0.5, noise.noise(co * 60.0)))   # guard hairs
    # faint stripes over the shoulders, back and haunches
    if -0.35 < co.y < 0.35:
        wob = noise.noise(co * 8.0) * 1.5
        band = 0.5 + 0.5 * math.sin(co.y * 48.0 + wob)
        side = nh.smoothstep(-0.2, 0.35, n.z)
        c = nh.lerp(c, STRIPE, 0.5 * nh.smoothstep(0.75, 0.95, band) * side)
    if co.y < -0.36:
        _t, lip, w = row_at(SKULL_ROWS, co.y)
        if co.z < lip - 0.003:
            c = nh.lerp(c, BELLY, 0.55 * nh.smoothstep(lip - 0.003, lip - 0.03, co.z))
        c = nh.lerp(c, MUZZLE, 0.6 * muzzle(co) * nh.smoothstep(-0.5, 0.2, n.z))
        c = nh.lerp(c, LIP, 0.85 * (1.0 - lip_dist(co)))
    return c


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal


def teeth(mb, surf, jaw_surf):
    # upper incisors
    for y, ln, r in ((-0.708, 0.013, 0.0040), (-0.698, 0.015, 0.0044), (-0.686, 0.015, 0.0044),
                     (-0.673, 0.013, 0.0040)):
        _t, lip, w = row_at(SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.62, y, lip - 0.06), (0, 0, 1))
            if loc is None or loc.z > lip + 0.03:
                continue
            mb.add(cone(loc + Vector((0, 0, 0.004)), Vector((loc.x, y + 0.002, loc.z - ln)), r), TOOTH, smooth=False)
    # big upper canines, hanging outside the lower jaw past the lip line
    for sx in (1, -1):
        _t, lip, w = row_at(SKULL_ROWS, CANINE_Y)
        x0 = w * 0.84
        pts = [Vector((sx * x0 * 0.9, CANINE_Y, lip + 0.012)), Vector((sx * x0, CANINE_Y + 0.002, lip - 0.012)),
               Vector((sx * (x0 + 0.001), CANINE_Y + 0.006, lip - 0.032)),
               Vector((sx * x0, CANINE_Y + 0.012, lip - 0.050))]
        mb.add(nh.tube(pts, [0.0095, 0.0088, 0.0058, 0.0], sides=8, scale_xy=(1.0, 0.7)), TOOTH)
    # blade-like postcanines
    y = -0.625
    while y < -0.515:
        _t, lip, w = row_at(SKULL_ROWS, y)
        for sx in (1, -1):
            loc, _n = surf.hit((sx * w * 0.80, y, lip - 0.06), (0, 0, 1))
            if loc is not None and loc.z < lip + 0.03:
                mb.add(nh.tube([loc + Vector((0, 0, 0.003)), loc + Vector((0, 0, -0.006)), loc + Vector((0, 0.001, -0.010))],
                               [0.0042, 0.0032, 0.0], sides=6, scale_xy=(1.0, 0.5)), TOOTH, smooth=False)
        y += 0.017
    up = JAW_ROT.to_3x3() @ Vector((0, 0, 1))
    # lower incisors, lower canines (fitting in front of the uppers) and cheek teeth
    for y, ln, r in ((-0.692, 0.012, 0.004), (-0.682, 0.013, 0.0042), (-0.670, 0.024, 0.0068),
                     (-0.60, 0.009, 0.004), (-0.58, 0.009, 0.004), (-0.56, 0.009, 0.004), (-0.54, 0.008, 0.0038)):
        jt, _jb, jw = row_at(JAW_ROWS, y)
        for sx in (1, -1):
            loc, _n = jaw_surf.hit(JAW_ROT @ Vector((sx * jw * (0.62 if y < -0.67 else 0.78), y, jt + 0.06)), -up)
            if loc is None:
                continue
            mb.add(cone(loc - up * 0.004, loc + up * ln + Vector((0, -0.002, 0)), r), TOOTH, smooth=False)


def head_details(mb, surf):
    top, lip, w = row_at(SKULL_ROWS, EYE_Y)
    for sx in (1, -1):
        loc, n = surf.hit((sx * 0.2, EYE_Y, top - 0.032), (-sx, 0, 0))
        e = loc - n * 0.004 if loc is not None else Vector((sx * w * 0.9, EYE_Y, top - 0.032))
        mb.add(nh.ellipsoid(e, (0.012, 0.014, 0.012), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(e + Vector((sx * 0.0085, -0.002, 0)), (0.004, 0.0075, 0.0075), subdivisions=2), PUPIL)
        t2, l2, w2 = row_at(SKULL_ROWS, -0.703)
        mb.add(nh.ellipsoid((sx * w2 * 0.55, -0.707, t2 - 0.012), (0.0055, 0.006, 0.005), subdivisions=1), NOSE)


def claws(mb, tips):
    for tip, d, r in tips:
        base = tip - d * 0.004 + Vector((0, 0, 0.004))
        end = tip + d * 0.018 + Vector((0, 0, -0.007))
        mb.add(nh.tube([base, base + d * 0.009, end], [r * 0.65, r * 0.48, 0.0], sides=6), CLAW)


# ---------------------------------------------------------------- build / preview

def build():
    LEG_DATA.clear()
    b = nh.MeshBuilder()
    b.add(loft(densify(TORSO, 4), sides=24, power=2.1), FUR)
    b.add(loft(densify(profile(SKULL_ROWS), 3), sides=20, power=2.4), FUR)
    b.add(oriented((0, -0.38, 0.40), (0.075, 0.07, 0.07)), FUR)                       # throat
    for sx in (1, -1):
        b.add(oriented((sx * 0.078, -0.42, 0.47), (0.04, 0.07, 0.058)), FUR)          # jaw muscles over the cheek arch
        b.add(oriented((sx * 0.062, -0.44, 0.432), (0.03, 0.07, 0.026)), FUR)         # zygomatic arch
        b.add(oriented((sx * 0.036, CANINE_Y, 0.43), (0.018, 0.03, 0.036)), FUR)      # canine root bulge
        b.add(oriented((sx * 0.06, -0.22, 0.40), (0.07, 0.10, 0.11)), FUR)            # chest
    limbs(b)
    claw_tips = toes(b)
    fused = b.fuse(voxel=0.0052, smooth=5, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, 13000)

    jb = nh.MeshBuilder()
    jb.add(loft(densify(profile(JAW_ROWS, 0.95), 3), sides=18, power=2.3), FUR)
    jfused = nh.transform(decimate(jb.fuse(voxel=0.0045, smooth=4, smooth_factor=0.5), 1500), JAW_ROT)

    surf, jaw_surf = Surface(fused), Surface(jfused)
    mb = nh.MeshBuilder()
    teeth(mb, surf, jaw_surf)
    mb.add(fused, body_paint)
    mb.add(jfused, lambda co, n: nh.lerp(body_paint(co, n), BELLY, 0.5 * nh.smoothstep(0.1, -0.7, n.z)))
    mb.add(oriented((0, -0.55, 0.392), (0.04, 0.15, 0.008), pitch=-6, segments=14, rings=6), MOUTH)
    head_details(mb, surf)
    claws(mb, claw_tips)
    obj = mb.to_object(NAME, roughness=0.75)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"  height {max(zs):.3f}, hip {HIP_Z:.3f} -> hip fraction {HIP_Z / max(zs):.2f}")
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head = Vector((0.0, -0.56, 0.43))
    out = Path(path)
    for i, off in enumerate((Vector((0.38, -0.38, 0.10)), Vector((-0.48, -0.08, 0.0)))):
        cam.location = head + off
        cam.rotation_euler = (head - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.44, 0.40, 0.28), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
