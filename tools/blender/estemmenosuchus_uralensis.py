"""
Procedural Estemmenosuchus uralensis (Middle Permian dinocephalian, ~3 m) for map colonies.

A heavy, big-headed dinocephalian from the Ural foreland: a deep barrel body with the
shoulders carried higher than the hips, a short, thick neck and a short tapering tail.
The limbs are semi-sprawling - the forelimbs bow out at the elbows, the hind limbs stand
more upright beneath the hips - on broad, short-toed, blunt-clawed feet. The huge, deep
skull carries the bizarre bony ornaments that give the genus its name ("crowned
crocodile"): a pair of tall, flattened "antlers" rising up and outward from the skull
roof above and behind the eyes, ending in knobbed, lobed tips; a pair of flattened cheek
flanges jutting out sideways and down below the eyes; and low paired bosses over the
snout and brows. The mouth is closed; big pointed incisors and the canine tusks show
over the lower jaw.
Body, legs, head and all the skin-covered bony ornaments are fused into one seamless
surface and sculpted by displacement: smooth, hairless, glandular skin dotted with gland
pores, a few folds at the neck and limb joints and a groove along the lips. Painted dull
slate-brown, mottled over the back and paler on the belly, with the horns and cheek
flanges flushed rusty red toward their tips.
Crisp details on top: teeth, eyes, nostrils and claws.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/estemmenosuchus_uralensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Estemmenosuchus.fbx
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

NAME = "Estemmenosuchus"

HIDE = (0.46, 0.41, 0.36)        # slate-brown
HIDE_DARK = (0.27, 0.24, 0.21)
BELLY = (0.70, 0.64, 0.56)
MOTTLE = (0.20, 0.18, 0.16)
HORN = (0.56, 0.42, 0.34)        # rusty flush on the ornaments
HORN_TIP = (0.74, 0.62, 0.50)
LIP = (0.12, 0.10, 0.09)
TOOTH = (0.93, 0.89, 0.76)
CLAW = (0.14, 0.12, 0.10)
EYE = (0.55, 0.32, 0.10)
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

# Huge deep skull, mouth closed (y, top z, bottom z, half width); the lips meet at lip_z(y)
SKULL_ROWS = [
    (-0.54, 0.935, 0.610, 0.165),
    (-0.62, 0.965, 0.585, 0.185),
    (-0.70, 0.960, 0.572, 0.176),
    (-0.78, 0.925, 0.568, 0.148),
    (-0.86, 0.880, 0.572, 0.124),
    (-0.92, 0.845, 0.580, 0.108),
    (-0.97, 0.805, 0.592, 0.092),
    (-1.005, 0.760, 0.610, 0.072),
    (-1.030, 0.712, 0.632, 0.045),
    (-1.042, 0.672, 0.650, 0.014),
]
EYE_Y, EYE_Z = -0.775, 0.855

# the head (skull and ornaments) is built at 1:1, then enlarged about the back of the skull
HEAD_PIVOT = Vector((0.0, -0.56, 0.78))
HEAD = Matrix.Translation(HEAD_PIVOT) @ Matrix.Scale(1.15, 4) @ Matrix.Translation(-HEAD_PIVOT)
HEAD_INV = HEAD.inverted()


def H(bm):
    return nh.transform(bm, HEAD)


def local(co):
    """Point in the unscaled head frame (identity behind the head)."""
    return HEAD_INV @ Vector(co) if co.y < -0.50 else Vector(co)


def row_at(rows, y):
    for (y0, t0, b0, w0), (y1, t1, b1, w1) in zip(rows, rows[1:]):
        if y1 <= y <= y0:
            k = (y0 - y) / (y0 - y1)
            return t0 + (t1 - t0) * k, b0 + (b1 - b0) * k, w0 + (w1 - w0) * k
    _, t, b, w = rows[-1] if y < rows[-1][0] else rows[0]
    return t, b, w


def lip_z(y):
    """The closed mouth line: low and nearly straight, rising a little at the front."""
    return 0.655 + 0.025 * nh.smoothstep(-0.9, -1.04, y) - 0.02 * nh.smoothstep(-0.75, -0.6, y)


def profile(rows):
    return [((0.0, y, (top + bot) * 0.5), w, (top - bot) * 0.5) for y, top, bot, w in rows]


# the skull ornaments: (path, radii, scale_xy) - flattened, skin-covered bone
ANTLER = [  # (out, up) outline of the frontal horn blade, facing forward; palmate, lobed top
    (0.050, 0.890), (0.135, 0.895), (0.150, 0.975), (0.195, 1.035), (0.250, 1.075), (0.272, 1.125),
    (0.250, 1.160), (0.212, 1.145), (0.192, 1.185), (0.150, 1.198), (0.124, 1.160), (0.100, 1.125),
    (0.085, 1.030), (0.060, 0.960),
]
CHEEK = [  # (out, along y) outline of the cheek flange, a plate tilted down and outward
    (0.100, -0.790), (0.200, -0.805), (0.268, -0.795), (0.300, -0.765), (0.292, -0.725),
    (0.252, -0.700), (0.180, -0.700), (0.100, -0.712),
]


def antler(sx):
    """Broad flattened horn blade rising up and outward from the skull roof to a lobed tip."""
    bm = nh.flat_panel([(sx * u, v, 0.0) for u, v in ANTLER], thickness=0.056)
    nh.transform(bm, Matrix.Rotation(math.radians(90), 4, "X"))        # into the XZ plane
    nh.transform(bm, Matrix.Translation((0.0, 0.0, -0.90)))
    nh.transform(bm, Matrix.Rotation(math.radians(-12), 4, "X"))       # lean back a little
    nh.transform(bm, Matrix.Translation((0.0, -0.705, 0.90)))
    # turn the blade so it sweeps out and a little back: broad from the front and the side
    pivot = Vector((sx * 0.09, -0.705, 0.0))
    nh.transform(bm, Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(sx * 32), 4, "Z")
                 @ Matrix.Translation(-pivot))
    # a thicker rib up the middle of the blade
    p = [(sx * 0.090, -0.700, 0.900), (sx * 0.140, -0.690, 1.030), (sx * 0.185, -0.682, 1.120)]
    return [bm, nh.tube(p, [0.044, 0.036, 0.028], sides=12, scale_xy=(0.6, 1.0))]


def cheek_flange(sx):
    """Flattened jugal flange jutting out sideways and down below the eye."""
    bm = nh.flat_panel([(sx * u, w, 0.0) for u, w in CHEEK], thickness=0.050)
    nh.transform(bm, Matrix.Translation((-sx * 0.10, 0.0, 0.0)))
    nh.transform(bm, Matrix.Rotation(math.radians(sx * 16), 4, "Y"))
    nh.transform(bm, Matrix.Translation((sx * 0.10, 0.0, 0.745)))
    return [bm, oriented((sx * 0.13, -0.75, 0.73), (0.06, 0.06, 0.05))]


def bosses(sx):
    """Low paired bumps over the snout and a small knob behind each horn."""
    return [oriented((sx * 0.040, -0.935, 0.835), (0.030, 0.050, 0.022)),
            oriented((sx * 0.120, -0.640, 0.930), (0.040, 0.046, 0.036))]


LEG_DATA = []   # (side, foot centre, toe angles, toe lengths, toe radius)


def leg(b, pts, radii, foot, foot_r, s, angs, lens, toe_r):
    b.add(nh.tube(pts, radii, sides=16), HIDE)
    for p, r in zip(pts[1:-1], radii[1:-1]):
        b.add(oriented(p, (r * 1.08, r * 1.1, r * 1.1)), HIDE)          # joints
    b.add(nh.tube([pts[-1], Vector(foot) + Vector((0, 0.01, 0.01))], [radii[-1], radii[-1] * 0.95], sides=12), HIDE)
    b.add(oriented(foot, foot_r), HIDE)
    LEG_DATA.append((s, Vector(foot), angs, lens, toe_r))


def body(b):
    b.add(oriented((0, -0.02, 0.640), (0.300, 0.500, 0.285), pitch=4, segments=32, rings=22), HIDE)   # barrel
    b.add(oriented((0, -0.34, 0.690), (0.275, 0.260, 0.270)), HIDE)          # shoulders, chest
    b.add(oriented((0, -0.30, 0.520), (0.200, 0.200, 0.160)), HIDE)          # deep brisket
    b.add(oriented((0, 0.34, 0.640), (0.240, 0.220, 0.225), pitch=-6), HIDE)  # hips
    b.add(nh.tube([(0, 0.46, 0.64), (0, 0.62, 0.56), (0, 0.76, 0.46), (0, 0.86, 0.38)],
                  [0.13, 0.085, 0.045, 0.0], sides=16), HIDE)                # short tail
    b.add(nh.tube([(0, -0.40, 0.76), (0, -0.52, 0.78), (0, -0.60, 0.78)], [0.22, 0.21, 0.19], sides=18), HIDE)  # neck
    b.add(oriented((0, -0.58, 0.64), (0.15, 0.12, 0.10)), HIDE)              # throat
    for sx in (1, -1):
        b.add(oriented((sx * 0.12, -0.62, 0.86), (0.08, 0.10, 0.09)), HIDE)  # jaw muscles behind the eyes


def head(b):
    b.add(H(loft(densify(profile(SKULL_ROWS), 3), sides=24, power=2.4)), HIDE)
    for sx in (1, -1):
        for part in antler(sx) + cheek_flange(sx) + bosses(sx):
            b.add(H(part), HIDE)
        b.add(H(oriented((sx * 0.105, EYE_Y, EYE_Z + 0.02), (0.045, 0.055, 0.040))), HIDE)   # orbit rim
        b.add(H(oriented((sx * 0.080, -0.955, 0.660), (0.034, 0.040, 0.050))), HIDE)          # canine root bulge


def limbs(b):
    for s in (-1, 1):
        # forelimb: bowed out at the elbow
        leg(b, [Vector((s * 0.20, -0.36, 0.62)), Vector((s * 0.37, -0.33, 0.40)), Vector((s * 0.37, -0.40, 0.11))],
            [0.120, 0.085, 0.064], (s * 0.375, -0.445, 0.034), (0.070, 0.080, 0.034), s,
            (-36, -16, 2, 20, 40), (0.050, 0.060, 0.064, 0.058, 0.046), 0.020)
        b.add(oriented((s * 0.25, -0.36, 0.58), (0.11, 0.13, 0.16), roll=s * -25), HIDE)   # upper arm muscle
        b.add(oriented((s * 0.37, -0.36, 0.27), (0.075, 0.07, 0.11)), HIDE)              # forearm
        # hind limb: more upright beneath the hip, knee forward
        leg(b, [Vector((s * 0.18, 0.34, 0.60)), Vector((s * 0.29, 0.24, 0.35)), Vector((s * 0.28, 0.38, 0.11))],
            [0.130, 0.090, 0.066], (s * 0.285, 0.330, 0.034), (0.070, 0.085, 0.034), s,
            (-30, -12, 4, 20, 36), (0.052, 0.064, 0.068, 0.062, 0.048), 0.021)
        b.add(oriented((s * 0.20, 0.32, 0.53), (0.12, 0.18, 0.18), pitch=25), HIDE)       # thigh
        b.add(oriented((s * 0.285, 0.30, 0.24), (0.07, 0.085, 0.11), pitch=-25), HIDE)    # calf


def toes(b):
    out = []
    for s, palm, angs, lens, r in LEG_DATA:
        for ang, ln in zip(angs, lens):
            a = math.radians(ang)
            d = Vector((s * math.sin(a), -math.cos(a), 0.0))
            base = palm + d * 0.04
            tip = base + d * ln + Vector((0, 0, -0.012))
            b.add(nh.tube([base, base + d * ln * 0.5 + Vector((0, 0, 0.004)), tip], [r, r * 0.9, r * 0.75],
                          sides=8), HIDE)
            out.append((tip, d, r))
    return out


# ---------------------------------------------------------------- skin

def ornament(co):
    """0..1: how far out along a horn / cheek flange this point is (for the rusty flush)."""
    co = local(co)
    ax = abs(co.x)
    # antlers: above the skull roof
    t_ant = 0.0
    if -0.80 < co.y < -0.56 and co.z > 0.95:
        t_ant = nh.smoothstep(0.97, 1.16, co.z)
    t_chk = 0.0
    if -0.82 < co.y < -0.68 and 0.6 < co.z < 0.80 and ax > 0.16:
        t_chk = nh.smoothstep(0.20, 0.30, ax)
    return max(t_ant, t_chk)


def lip_dist(co):
    co = local(co)
    if co.y > -0.58:
        return 1.0
    _t, _b, w = row_at(SKULL_ROWS, co.y)
    if abs(co.x) < w * 0.4:
        return 1.0
    return min(1.0, abs(co.z - lip_z(co.y)) / 0.010)


def sculpt(bm):
    bm.normal_update()
    moves = []
    for v in bm.verts:
        co, n = v.co, v.normal
        # smooth glandular skin: low swellings and scattered gland pores
        d = 0.0012 * noise.noise(co * 14.0)
        pore = noise.cell(co * 55.0)
        d -= 0.0016 * (1.0 - nh.smoothstep(0.0, 0.10, pore))
        # neck folds
        if -0.62 < co.y < -0.42 and co.z < 0.85:
            d -= 0.003 * nh.smoothstep(0.65, 0.95, 0.5 + 0.5 * math.sin(co.y * 80.0 + co.z * 12.0))
        # rugose, knobbly bone texture on the ornaments
        t = ornament(co)
        if t > 0.0:
            d += 0.003 * t * (1.0 - nh.smoothstep(0.0, 0.45, noise.cell(co * 40.0)))
        d -= 0.005 * (1.0 - lip_dist(co))
        moves.append((v, n * d))
    for v, m in moves:
        v.co += m
    bm.normal_update()


def paint(co, n):
    c = nh.lerp(BELLY, HIDE, nh.smoothstep(-0.65, -0.1, n.z))
    c = nh.lerp(c, HIDE_DARK, 0.5 * nh.smoothstep(0.35, 0.95, n.z))
    blot = noise.noise(Vector((co.x * 6.0, co.y * 6.0, co.z * 6.0)))
    c = nh.lerp(c, MOTTLE, 0.45 * nh.smoothstep(0.2, 0.55, blot) * nh.smoothstep(-0.2, 0.4, n.z))
    if co.z < 0.25:
        c = nh.lerp(HIDE_DARK, c, nh.smoothstep(0.05, 0.25, co.z))
    lc = local(co)
    if lc.y < -0.55:
        # paler lower jaw, dark lip line
        if lc.z < lip_z(lc.y) - 0.004:
            c = nh.lerp(c, BELLY, 0.35)
        c = nh.lerp(c, LIP, 0.8 * (1.0 - lip_dist(co)))
    t = ornament(co)
    if t > 0.0:
        c = nh.lerp(c, HORN, nh.smoothstep(0.0, 0.5, t))
        c = nh.lerp(c, HORN_TIP, nh.smoothstep(0.65, 1.0, t))
    # pale gland pores
    pore = noise.cell(co * 55.0)
    c = nh.lerp(c, BELLY, 0.25 * (1.0 - nh.smoothstep(0.0, 0.10, pore)))
    k = 1.0 + 0.07 * noise.noise(co * 20.0)
    return tuple(max(0.0, x * k) for x in c)


# ---------------------------------------------------------------- crisp details

class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal


def teeth(mb, surf):
    """Big interlocking incisors at the front and a canine tusk each side, over the lower lip."""
    spots = []
    for a in (-0.55, -0.30, -0.08, 0.08, 0.30, 0.55):          # incisors around the snout tip
        d = Vector((math.sin(a), -math.cos(a), 0.0))
        spots.append((Vector((0.0, -0.98, 0.0)) + d * 0.3, -d, 0.034 if abs(a) < 0.4 else 0.030, 0.0085))
    for sx in (1, -1):
        spots.append((Vector((sx * 0.4, -0.950, 0.0)), Vector((-sx, 0, 0)), 0.060, 0.014))     # canines
        for y in (-0.90, -0.87, -0.84, -0.81):                                                # post-canines
            spots.append((Vector((sx * 0.4, y, 0.0)), Vector((-sx, 0, 0)), 0.016, 0.006))
    for origin, direction, ln, r in spots:
        z = lip_z(origin.y if abs(direction.y) < 0.5 else -1.02) + 0.012
        loc, nrm = surf.hit(HEAD @ Vector((origin.x, origin.y, z)), direction)
        if loc is None:
            continue
        ln *= 1.15
        out = Vector((nrm.x, nrm.y, 0.0))
        out = out.normalized() if out.length > 1e-4 else Vector()
        base = loc - out * 0.006
        tip = loc + Vector((0, 0, -ln)) + out * 0.006
        mb.add(nh.tube([base, base.lerp(tip, 0.5) + out * 0.002, tip], [r, r * 0.8, 0.0], sides=8), TOOTH)


def head_details(mb, surf):
    for sx in (1, -1):
        loc, nrm = surf.hit(HEAD @ Vector((sx * 0.4, EYE_Y, EYE_Z)), (-sx, 0, 0))
        if loc is None:
            continue
        look = Vector((sx, -0.25, 0.1)).normalized()
        c = loc - look * 0.008
        mb.add(nh.ellipsoid(c, (0.021, 0.024, 0.020), subdivisions=2), EYE)
        mb.add(nh.ellipsoid(c + look * 0.014, (0.009, 0.010, 0.011), subdivisions=2), PUPIL)
        loc, _n = surf.hit(HEAD @ Vector((sx * 0.030, -1.02, 1.2)), (0, -0.25, -1))
        if loc is not None:
            mb.add(nh.ellipsoid(loc, (0.010, 0.008, 0.008), subdivisions=1), PUPIL)


def claws(mb, tips):
    for tip, d, r in tips:
        base = tip - d * 0.008 + Vector((0, 0, 0.006))
        end = tip + d * 0.026 + Vector((0, 0, -0.012))
        mb.add(nh.tube([base, base + d * 0.012, end], [r * 0.7, r * 0.5, 0.0], sides=6), CLAW)


# ---------------------------------------------------------------- build / preview

def build():
    LEG_DATA.clear()
    b = nh.MeshBuilder()
    body(b)
    head(b)
    limbs(b)
    claw_tips = toes(b)
    fused = b.fuse(voxel=0.0095, smooth=5, smooth_factor=0.5)
    sculpt(fused)
    fused = decimate(fused, 21000)

    surf = Surface(fused)
    mb = nh.MeshBuilder()
    teeth(mb, surf)
    head_details(mb, surf)
    claws(mb, claw_tips)
    mb.add(fused, paint)
    obj = mb.to_object(NAME, roughness=0.55)
    nh.ground_to_zero(obj)
    return obj


def render_head(path):
    scene = bpy.context.scene
    cam = scene.camera
    head_c = Vector((0.0, -0.84, 0.88))
    out = Path(path)
    for i, off in enumerate((Vector((0.75, -0.75, 0.20)), Vector((0.0, -1.1, 0.08)))):
        cam.location = head_c + off
        cam.rotation_euler = (head_c - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.40, 0.38, 0.27), views=((35, 22), (-90, 6), (25, 65)))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        render_head(argv[argv.index("--render") + 1])
