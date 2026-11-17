"""
Shared Megatherium builder for the giant ground sloth scripts
(megatherium_americanum.py, megatherium_tarijense.py). Builds on nh_model.

Megatherium walked on all fours most of the time, and the body follows the skeleton
rather than a bear's: a pear-shaped trunk that is narrowest at the chest and swells
into an enormously broad pelvis and massive, short hind legs, so the hips are the
highest point and the back slopes down to the shoulders. In front of them a short
neck carries a small, narrow, long-snouted head with a deep lower jaw (the jaw of
Megatherium has a deep ventral flange under the tooth row), a mobile upper lip and
small ears. Long, strong forelimbs end in hands that bore the weight on the outer
edge: the big curved claws of digits II-IV are folded inward under the hand and held
clear of the ground, like a fist turned on its side. The hind feet are also turned so
the animal stood on their outer edges, with the great claw of digit III curled in
along the inner side. A thick, muscular, conical tail runs back and down from the
pelvis (it may have braced the animal as a tripod when it reared to browse).

All of that is fused from overlapping parts into one seamless surface
(nh_model.MeshBuilder.fuse); the coat is then displaced into shaggy, downward-hanging
locks (longest on the flanks, belly fringe and upper limbs, short on the face and
feet) and repainted: brown hair with paler tips and dark gaps between the locks, a
darker face, bare grey-brown skin on the lip, nose and soles. Hair colour and length
are not known from fossils for Megatherium (they are inferred from other sloths
and preserved hide of its relatives), so they are a conservative guess. Crisp eyes,
nostrils and the horn-coloured claws are added on top.

A MegatheriumSpec holds the proportions and colours; build(spec) returns the object.
Faces -Y, pivot on the ground (z = 0 under the feet), about 2 units long with the
snout tip near y = -1. The tail stays above the stride hip line (species.json
"mapHip" about 0.36) so only the legs swing when it walks.
"""

import math
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

TAG_COAT = (0.0, 0.0, 0.0)  # region tags painted before fusing (red = bare skin)
TAG_SKIN = (1.0, 0.0, 0.0)


@dataclass
class MegatheriumSpec:
    name: str
    voxel: float = 0.012
    max_tris: int = 20000
    # trunk
    bulk: float = 1.0        # width/depth multiplier of the barrel and pelvis
    hip_w: float = 1.0       # extra breadth of the pelvis
    # limbs (length multipliers; hind legs are short and massive in every species)
    fore_len: float = 1.0
    hind_thick: float = 1.0
    # head
    head_k: float = 1.0      # head size
    snout_len: float = 1.0
    tail_k: float = 1.0      # tail thickness
    hair_len: float = 1.0    # shaggy coat length
    claw_k: float = 1.0
    # colours
    coat: tuple = (0.33, 0.23, 0.14)
    coat_tip: tuple = (0.50, 0.38, 0.24)
    underfur: tuple = (0.17, 0.11, 0.07)
    face: tuple = (0.24, 0.18, 0.12)
    skin: tuple = (0.27, 0.23, 0.21)
    claw: tuple = (0.62, 0.56, 0.45)
    claw_tip: tuple = (0.30, 0.26, 0.21)
    eye: tuple = (0.05, 0.035, 0.025)


# ---------------------------------------------------------------- helpers

def oriented(center, radii, pitch=0.0, yaw=0.0, roll=0.0, segments=20, rings=14, deform=None):
    """UV ellipsoid rotated about X (pitch), Y (roll) then Z (yaw), degrees, moved to center."""
    bm = nh.uv_ellipsoid((0, 0, 0), radii, segments=segments, rings=rings, deform=deform)
    rot = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(roll), 4, "Y")
           @ Matrix.Rotation(math.radians(pitch), 4, "X"))
    nh.transform(bm, rot)
    nh.transform(bm, Matrix.Translation(Vector(center)))
    return bm


def catmull(points, steps):
    """Smooth Catmull-Rom resample of a polyline (any vector size)."""
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(pts[-1])
    return out


def smooth_tube(points, radii, steps=4, sides=14, **kw):
    pts = catmull([(*p, r) for p, r in zip(points, radii)], steps)
    return nh.tube([p.xyz for p in pts], [max(0.0, p.w) for p in pts], sides=sides, **kw)


def claw(base, direction, length, radius, curl, curl_axis, sides=7):
    """Curved, tapering claw: starts along `direction` and bends about `curl_axis` by `curl` degrees."""
    pts, radii = [], []
    p = Vector(base)
    d = Vector(direction).normalized()
    n = 7
    for i in range(n + 1):
        t = i / n
        pts.append(p.copy())
        radii.append(radius * (1.0 - t) ** 0.8 if i < n else 0.0)
        d = Matrix.Rotation(math.radians(curl / n), 3, Vector(curl_axis)) @ d
        p = p + d * (length / n)
    return nh.tube(pts, radii, sides=sides, cap_start=True)


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

# walking: left-front and right-hind forward (y offsets of the feet)
STRIDE = {"lf": -0.07, "rf": 0.05, "lh": 0.05, "rh": -0.06}


def head_c(s):
    return Vector((0, -0.80, 0.64))


def torso(b, s):
    k, w = s.bulk, s.hip_w
    # pear-shaped trunk: narrow chest, deep barrel, enormous pelvis, hips the highest point
    b.add(oriented((0, -0.40, 0.64), (0.19 * k, 0.24, 0.21 * k), pitch=-10), TAG_COAT)   # narrow chest
    b.add(oriented((0, -0.08, 0.64), (0.26 * k, 0.36, 0.26 * k), segments=26, rings=18), TAG_COAT)  # barrel
    b.add(oriented((0, 0.28, 0.69), (0.31 * k * w, 0.28, 0.28 * k), segments=26, rings=18), TAG_COAT)  # pelvis
    b.add(oriented((0, 0.48, 0.66), (0.24 * k * w, 0.18, 0.23 * k)), TAG_COAT)             # rump
    b.add(oriented((0, 0.0, 0.47), (0.21 * k, 0.36, 0.10)), TAG_COAT)                      # belly
    b.add(oriented((0, 0.02, 0.44), (0.22 * k, 0.34, 0.06)), TAG_COAT)                     # hanging belly fringe
    for sx in (-1, 1):
        b.add(oriented((sx * 0.22 * k, 0.0, 0.52), (0.06, 0.32, 0.12)), TAG_COAT)          # shaggy flank skirt
    for sx in (-1, 1):
        b.add(oriented((sx * 0.15 * k, -0.42, 0.66), (0.10, 0.14, 0.13)), TAG_COAT)        # shoulders
    # short, thick neck carrying the head a little below the shoulder line
    h = head_c(s)
    b.add(smooth_tube([(0, -0.48, 0.68), (0, -0.62, 0.68), (0, h.y + 0.04, h.z + 0.01)],
                      [0.15 * k, 0.11, 0.075 * s.head_k], sides=16), TAG_COAT)


def head(b, s):
    """Small, narrow head with a long snout, deep lower jaw and small ears."""
    h, hk, sl = head_c(s), s.head_k, s.snout_len

    def p(x, y, z):
        return h + Vector((x, y * (sl if y < -0.06 else 1.0), z)) * hk

    b.add(oriented(p(0, 0, 0.01), (0.072 * hk, 0.105 * hk, 0.075 * hk)), TAG_COAT)        # cranium
    b.add(smooth_tube([p(0, -0.05, 0.02), p(0, -0.13, 0.0), p(0, -0.19, -0.025)],
                      [0.058 * hk, 0.047 * hk, 0.036 * hk], sides=14, scale_xy=(0.85, 1.0)), TAG_COAT)  # snout
    b.add(oriented(p(0, -0.205, -0.04), (0.034 * hk, 0.030 * hk, 0.030 * hk)), TAG_SKIN)  # mobile upper lip
    # deep mandible with its downward flange under the tooth row
    b.add(oriented(p(0, -0.08, -0.06), (0.048 * hk, 0.10 * hk, 0.055 * hk), pitch=8), TAG_COAT)
    b.add(oriented(p(0, -0.17, -0.06), (0.026 * hk, 0.04 * hk, 0.02 * hk)), TAG_SKIN)     # lower lip
    for sx in (-1, 1):
        b.add(oriented(p(sx * 0.05, -0.02, -0.03), (0.035 * hk, 0.06 * hk, 0.04 * hk)), TAG_COAT)  # cheeks
        b.add(oriented(p(sx * 0.055, 0.05, 0.07), (0.018 * hk, 0.012 * hk, 0.022 * hk), roll=sx * 30),
              TAG_COAT)                                                                    # small ears


def fore_limb(b, out, s, sx):
    """Long, strong arm; the hand rests on its outer edge, claws folded in under it."""
    L = s.fore_len
    st = STRIDE["lf" if sx < 0 else "rf"]
    x = sx * 0.19 * s.bulk
    sh = Vector((x, -0.42, 0.66))
    el = Vector((x * 1.2, -0.38, 0.62 - 0.27 * L))
    wr = Vector((x * 1.22, -0.47 + st, 0.12))
    b.add(smooth_tube([tuple(sh), tuple(el)], [0.105, 0.085], sides=14), TAG_COAT)         # upper arm
    b.add(oriented((x * 1.05, -0.40, 0.52), (0.10, 0.12, 0.17), roll=sx * 12), TAG_COAT)   # deltoid/triceps
    b.add(smooth_tube([tuple(el), tuple((el + wr) * 0.5 + Vector((0, -0.01, 0))), tuple(wr)],
                      [0.08, 0.07, 0.055], sides=14), TAG_COAT)                             # forearm
    b.add(oriented((x * 1.22, -0.40 + st * 0.4, 0.29), (0.065, 0.075, 0.11)), TAG_COAT)    # forearm muscles
    # the hand: a heavy fist turned on its side, weight on the outer (fifth-digit) edge
    hc = Vector((wr.x + sx * 0.012, wr.y - 0.05, 0.055))
    b.add(oriented(tuple(hc), (0.05, 0.10, 0.058), roll=sx * -18), TAG_COAT)
    b.add(oriented((hc.x + sx * 0.022, hc.y, 0.022), (0.03, 0.085, 0.024)), TAG_SKIN)    # outer-edge pad
    # three big claws (digits II-IV) folded inward under the hand, clear of the ground
    ck = s.claw_k
    for i, (dy, ln, r) in enumerate(((-0.06, 0.17, 0.022), (-0.03, 0.20, 0.025), (0.0, 0.15, 0.02))):
        base = Vector((hc.x - sx * 0.035, hc.y + dy - 0.03, 0.095 - i * 0.006))
        out.append((claw(base, (-sx * 0.35, -0.85, -0.25), ln * ck, r * ck, 160, (1.0, 0.0, 0.0)), s))


def hind_limb(b, out, s, sx):
    """Massive, short hind leg; the foot stands on its outer edge with one big claw curled inward."""
    t = s.hind_thick
    st = STRIDE["lh" if sx < 0 else "rh"]
    x = sx * 0.27 * s.bulk * s.hip_w
    b.add(oriented((x, 0.28, 0.55), (0.14 * t, 0.21, 0.25 * t), pitch=-6), TAG_COAT)        # thigh
    knee = Vector((x * 1.04, 0.22, 0.30))
    ank = Vector((x * 1.02, 0.30 + st, 0.09))
    b.add(smooth_tube([tuple(knee), tuple(ank)], [0.12 * t, 0.085 * t], sides=14), TAG_COAT)  # shank
    b.add(oriented((x * 1.03, 0.30 + st * 0.4, 0.22), (0.10 * t, 0.12, 0.11)), TAG_COAT)    # calf
    fc = Vector((x * 1.04 + sx * 0.01, 0.24 + st, 0.05))
    b.add(oriented(tuple(fc), (0.07 * t, 0.15, 0.052), roll=sx * -14), TAG_COAT)          # foot
    b.add(oriented((fc.x + sx * 0.03, fc.y, 0.02), (0.035, 0.13, 0.02)), TAG_SKIN)         # outer sole
    ck = s.claw_k
    base = Vector((fc.x - sx * 0.03, fc.y - 0.11, 0.055))
    out.append((claw(base, (-sx * 0.35, -0.75, -0.3), 0.19 * ck, 0.026 * ck, 130, (0.0, 0.0, -sx * 1.0)), s))
    base = Vector((fc.x - sx * 0.005, fc.y - 0.13, 0.05))
    out.append((claw(base, (-sx * 0.1, -0.9, -0.3), 0.07 * ck, 0.012 * ck, 90, (sx * 1.0, 0.0, 0.0)), s))


def tail(b, s):
    k = s.tail_k
    pts = [(0, 0.50, 0.68), (0, 0.68, 0.60), (0, 0.84, 0.51), (0, 0.97, 0.44), (0, 1.06, 0.40)]
    b.add(smooth_tube(pts, [0.17 * k, 0.135 * k, 0.095 * k, 0.055 * k, 0.02], sides=16), TAG_COAT)


# ---------------------------------------------------------------- sculpt + paint

def skin_weight(bm):
    col = bm.loops.layers.color["Col"]
    w = {}
    for f in bm.faces:
        for l in f.loops:
            w[l.vert] = l[col][0]
    return w


def hair_amount(s, co, n):
    """How long the coat is at co: short on the face and feet, long on the flanks and belly fringe."""
    h = head_c(s)
    face = 1.0 - nh.smoothstep(0.10, 0.22, (co - h).length)
    feet = 1.0 - nh.smoothstep(0.06, 0.18, co.z)
    flank = nh.smoothstep(0.2, 0.7, abs(n.x)) * 0.5 + nh.smoothstep(0.0, -0.6, n.z) * 0.7
    base = 0.010 + 0.016 * min(1.0, flank)
    return s.hair_len * base * (1.0 - 0.8 * face) * (1.0 - 0.85 * feet)


def strand(co):
    """0..1 lock pattern: thin across, long downward (hair hangs)."""
    u = noise.noise(Vector((co.x * 60.0, co.y * 60.0, co.z * 6.0)))
    f = noise.noise(Vector((co.x * 150.0, co.y * 150.0, co.z * 16.0)))
    return max(0.0, min(1.0, 0.5 + 0.7 * u + 0.3 * f))


def shaggy(bm, w, s):
    bm.normal_update()
    moves = {}
    for v in bm.verts:
        fur = 1.0 - nh.smoothstep(0.2, 0.6, w[v])
        if fur <= 0.0:
            continue
        co, n = v.co.copy(), v.normal.copy()
        amt = hair_amount(s, co, n) * fur
        pat = strand(co)
        d = n * amt * (0.35 + 0.9 * pat)
        d += Vector((0, 0, -1)) * amt * 0.6 * pat * max(0.0, 0.2 - n.z)  # locks droop a little
        moves[v] = d
    for v, d in moves.items():
        v.co += d
    hair = list(moves.keys())
    for _ in range(2):
        bmesh.ops.smooth_vert(bm, verts=hair, factor=0.4, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    for v in bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    bm.normal_update()


def paint(bm, s):
    col = bm.loops.layers.color["Col"]
    w = skin_weight(bm)
    h = head_c(s)
    vc = {}
    for v in bm.verts:
        co, n = v.co, v.normal
        pat = strand(co)
        c = nh.lerp(s.underfur, s.coat, nh.smoothstep(0.15, 0.55, pat))
        c = nh.lerp(c, s.coat_tip, 0.55 * nh.smoothstep(0.55, 0.95, pat) * (0.5 + 0.5 * max(0.0, n.z)))
        c = nh.lerp(c, s.underfur, 0.35 * nh.smoothstep(-0.2, -0.8, n.z))           # shaded belly
        c = nh.lerp(c, s.underfur, 0.4 * (1.0 - nh.smoothstep(0.05, 0.25, co.z)))   # dark lower legs
        d = (co - h).length
        c = nh.lerp(c, s.face, 0.7 * (1.0 - nh.smoothstep(0.12, 0.2, d)))
        c = nh.lerp(c, s.coat_tip, 0.12 * max(0.0, noise.noise(co * 6.0)))
        c = nh.lerp(c, s.skin, nh.smoothstep(0.35, 0.65, w[v]))
        vc[v] = c
    for f in bm.faces:
        for l in f.loops:
            c = vc[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)


def details(tree, s):
    out = []

    def snap(p):
        hit, normal, _i, _d = tree.find_nearest(Vector(p))
        return hit, normal

    h, hk, sl = head_c(s), s.head_k, s.snout_len
    for sx in (-1, 1):
        hit, n = snap(h + Vector((sx * 0.06, -0.05 * sl, 0.035)) * hk)
        out.append((nh.ellipsoid(hit - n * 0.002, (0.011 * hk, 0.013 * hk, 0.009 * hk), subdivisions=2), s.eye))
        hit, n = snap(h + Vector((sx * 0.014, -0.235 * sl, -0.025)) * hk)
        out.append((nh.ellipsoid(hit + n * 0.001, (0.007, 0.004, 0.005), subdivisions=1), s.eye))
    return out


def paint_claw(bm, s, base):
    """Horn-coloured claws darkening toward the tip."""
    def fn(co, n, b=Vector(base)):
        t = nh.smoothstep(0.02, 0.12, (co - b).length)
        return nh.lerp(s.claw, s.claw_tip, t)
    return fn


def build(spec):
    s = spec
    b = nh.MeshBuilder()
    claws = []
    torso(b, s)
    head(b, s)
    for sx in (-1, 1):
        fore_limb(b, claws, s, sx)
        hind_limb(b, claws, s, sx)
    tail(b, s)
    fused = b.fuse(voxel=s.voxel, smooth=5, smooth_factor=0.5)
    w = skin_weight(fused)
    shaggy(fused, w, s)
    fused = decimate(fused, s.max_tris)
    paint(fused, s)
    tree = BVHTree.FromBMesh(fused)
    extra = details(tree, s)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for bm, c in extra:
        mb.add(bm, c)
    for bm, _s in claws:
        bm.verts.ensure_lookup_table()
        base = bm.verts[0].co.copy()
        mb.add(bm, paint_claw(bm, s, base))
    obj = mb.to_object(s.name, roughness=0.85)
    nh.ground_to_zero(obj)
    return obj
