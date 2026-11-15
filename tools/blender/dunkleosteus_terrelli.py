"""
Procedural high-detail Dunkleosteus terrelli (Late Devonian arthrodire placoderm) for the
map (Swim style).

Follows the recent, more compact reconstructions (about 4 m rather than 6-10 m): a
deep, blunt, massively armoured head and thorax taking up over a third of the body,
then a short, muscular, shark-like rear body with a single dorsal fin, pectoral fins
emerging from behind the armour, small pelvic and anal fins and a heterocercal tail
(long upturned upper lobe, smaller lower lobe).

The body, fins and lower jaw are lofted sections and fin slabs fused into seamless
surfaces (nh_model.MeshBuilder.fuse). The head and thoracic shields are then sculpted
procedurally: a mirrored Voronoi layout of the main dermal plates (rostral, pineal,
preorbital, postorbital, central, nuchal, paranuchal, suborbital, marginal; median
dorsal, anterior/posterior dorsolateral, anterior lateral and ventral plates) gives
wiggly suture grooves, the armour stands slightly proud of the scaleless skin behind
it, the gap of the cranio-thoracic joint is cut in, and the bone gets a pitted,
tuberculate texture. Crisp details on top: the self-sharpening bony jaw blades (upper
anterior supragnathal fangs, posterior supragnathal blades and the lower inferognathal
blades rising to a pointed front cusp, mouth slightly open), and the big eyes in their
orbital notches, each ringed by bony sclerotic plates.

Usage:
  blender --background --python tools/blender/dunkleosteus_terrelli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dunkleosteus.fbx
Pivot at the body centre, faces -Y, dorsal fin up (+Z). About 2.1 units long.
"""

import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

NAME = "Dunkleosteus"
VOXEL = 0.024
JAW_VOXEL = 0.018
JAW_OPEN = math.radians(19)

ARMOUR = (0.58, 0.52, 0.42)        # weathered bone-brown
ARMOUR_DARK = (0.36, 0.32, 0.27)   # back of the shields
ARMOUR_LIGHT = (0.76, 0.70, 0.58)
SUTURE = (0.11, 0.09, 0.08)
SKIN_BACK = (0.17, 0.20, 0.22)
SKIN_FLANK = (0.34, 0.37, 0.38)
BELLY = (0.80, 0.78, 0.70)
FIN_TIP = (0.10, 0.12, 0.13)
MOUTH = (0.28, 0.10, 0.10)
BLADE = (0.95, 0.92, 0.82)
BLADE_ROOT = (0.62, 0.56, 0.45)
EYE = (0.03, 0.03, 0.04)
IRIS = (0.62, 0.50, 0.20)
RING = (0.70, 0.64, 0.52)
RING_DARK = (0.40, 0.35, 0.28)

Y_TIP, Y_PED = -0.98, 0.70        # snout tip, end of the caudal peduncle
Y_HINGE = -0.66                   # jaw joint (below and behind the eye)
Y_JOINT = -0.50                   # cranio-thoracic joint (head shield / thoracic shield)
Y_ARMOUR_END = -0.16              # back edge of the thoracic shield
EYE_Y = -0.80


# ---------------------------------------------------------------- body profile

def _interp(table, y):
    """Monotone cubic (PCHIP) interpolation through (y, value) control points."""
    if y <= table[0][0]:
        return table[0][1]
    if y >= table[-1][0]:
        return table[-1][1]
    xs = [p[0] for p in table]
    vs = [p[1] for p in table]
    n = len(xs)
    d = [(vs[i + 1] - vs[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m.append(0.0)
            continue
        h0, h1 = xs[i] - xs[i - 1], xs[i + 1] - xs[i]
        w1, w2 = 2 * h1 + h0, h1 + 2 * h0
        m.append((w1 + w2) / (w1 / d[i - 1] + w2 / d[i]))
    m.append(d[-1])
    for i in range(n - 1):
        if y <= xs[i + 1]:
            h = xs[i + 1] - xs[i]
            t = (y - xs[i]) / h
            h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
            h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
            return h00 * vs[i] + h10 * h * m[i] + h01 * vs[i + 1] + h11 * h * m[i + 1]
    return vs[-1]


# blunt, deep head; the thorax is the widest and deepest part; short muscular rear body
HALF_W = [(-0.99, 0.03), (-0.96, 0.10), (-0.88, 0.16), (-0.74, 0.21), (-0.52, 0.25), (-0.30, 0.26),
          (-0.12, 0.235), (0.10, 0.175), (0.32, 0.115), (0.52, 0.068), (0.70, 0.045)]
HALF_H_TOP = [(-0.99, 0.06), (-0.965, 0.17), (-0.90, 0.24), (-0.76, 0.29), (-0.52, 0.33), (-0.30, 0.34),
              (-0.12, 0.31), (0.10, 0.235), (0.32, 0.15), (0.52, 0.085), (0.70, 0.055)]
HALF_H_BOT = [(-0.99, 0.06), (-0.965, 0.15), (-0.90, 0.21), (-0.76, 0.26), (-0.52, 0.30), (-0.30, 0.31),
              (-0.12, 0.28), (0.10, 0.21), (0.32, 0.13), (0.52, 0.07), (0.70, 0.045)]
CENTER_Z = [(-0.99, -0.05), (-0.88, -0.01), (-0.5, 0.0), (0.2, 0.0), (0.70, 0.04)]


def w(y): return _interp(HALF_W, y)
def ht(y): return _interp(HALF_H_TOP, y)
def hb(y): return _interp(HALF_H_BOT, y)
def zc(y): return _interp(CENTER_Z, y)


def palate(y):
    """0 outside the mouth, 1 where the head's underside is cut away for the lower jaw."""
    return 1.0 - nh.smoothstep(Y_HINGE - 0.05, Y_HINGE + 0.07, y)


PALATE_HB = 0.40  # fraction of the belly depth left under the head where the lower jaw sits


def hb_head(y):
    return hb(y) * (1.0 - palate(y) * (1.0 - PALATE_HB))


def section(y, a, n=None):
    """Superellipse cross-section point at angle a (0 = +x, pi/2 = up)."""
    if n is None:  # boxier head and thorax, rounder rear body
        n = 2.4 + 0.5 * (1.0 - nh.smoothstep(-0.4, 0.0, y))
    c, s = math.cos(a), math.sin(a)
    x = w(y) * math.copysign(abs(c) ** (2.0 / n), c)
    hz = ht(y) if s >= 0 else hb_head(y)
    # flatter belly under the thoracic shield
    if s < 0 and y < Y_ARMOUR_END:
        hz *= 1.0 - 0.10 * abs(s) ** 4
    z = zc(y) + hz * math.copysign(abs(s) ** (2.0 / n), s)
    return Vector((x, y, z))


def loft(y0, y1, ny, na, point, ease=True):
    """Closed lofted shell between y0 and y1 (pointed caps) from point(y, angle)."""
    bm = bmesh.new()
    if ease:
        ys = [y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(i / (ny - 1) * math.pi)) for i in range(ny)]
    else:
        ys = [y0 + (y1 - y0) * i / (ny - 1) for i in range(ny)]
    rings = []
    for i, y in enumerate(ys):
        if i == 0 or i == ny - 1:
            p = sum((point(y, k / na * math.tau) for k in range(na)), Vector()) / na
            rings.append([bm.verts.new(p)])
            continue
        rings.append([bm.verts.new(point(y, k / na * math.tau)) for k in range(na)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(na):
                bm.faces.new([a[0], b[(k + 1) % na], b[k]])
        elif len(b) == 1:
            for k in range(na):
                bm.faces.new([a[k], a[(k + 1) % na], b[0]])
        else:
            for k in range(na):
                j = (k + 1) % na
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def fin_slab(outline, thick, frame):
    """Fin from a 2D outline [(u, v)] with a thickness per point; frame(u, v) -> (pos, normal)."""
    bm = bmesh.new()
    top, bot = [], []
    for (u, v), t in zip(outline, thick):
        p, n = frame(u, v)
        top.append(bm.verts.new(p + n * t * 0.5))
        bot.append(bm.verts.new(p - n * t * 0.5))
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    m = len(outline)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.triangulate(bm, faces=bm.faces, ngon_method="EAR_CLIP")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def curve(p0, p1, bulge, steps):
    """Points from p0 to p1 (exclusive of p1) bowed sideways by `bulge` (fraction of length)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    side = Vector((-d.y, d.x))
    return [tuple(p0 + d * (i / steps) + side * bulge * math.sin(i / steps * math.pi)) for i in range(steps)]


def taper(outline, root_v, tip_v, t_root, t_tip, axis=1):
    out = []
    for p in outline:
        t = (abs(p[axis]) - root_v) / (tip_v - root_v)
        t = max(0.0, min(1.0, t))
        out.append(t_root + (t_tip - t_root) * t)
    return out


# ---------------------------------------------------------------- fins

def midline_frame(u, v):  # u = y, v = z, fin in the x = 0 plane
    return Vector((0.0, u, v)), Vector((1.0, 0.0, 0.0))


def dorsal_fin():
    base_z = lambda y: zc(y) + ht(y) - 0.05  # noqa: E731
    a, b = (-0.10, base_z(-0.10)), (0.22, base_z(0.22))
    apex = (0.10, zc(0.0) + ht(0.0) + 0.24)
    trail = (0.25, base_z(0.25) + 0.05)
    pts = [a] + curve(a, apex, -0.10, 7) + curve(apex, trail, 0.12, 6) + [trail, b]
    pts += curve(b, a, 0.0, 4)[1:]
    th = taper(pts, base_z(0.05) + 0.04, apex[1], 0.08, 0.035)
    return fin_slab(pts, th, midline_frame)


def anal_fin():
    z_root = zc(0.40) - hb(0.40) + 0.03
    a, b = (0.34, z_root), (0.46, z_root + 0.01)
    apex = (0.44, z_root - 0.10)
    trail = (0.49, z_root - 0.03)
    pts = [a] + curve(a, apex, 0.12, 4) + curve(apex, trail, -0.1, 3) + [trail, b]
    return fin_slab(pts, taper(pts, z_root, z_root - 0.1, 0.06, 0.03), midline_frame)


def caudal():
    """Heterocercal tail: the body axis turns up into the long upper lobe."""
    y_root = 0.58
    top_root, bot_root = (y_root, zc(y_root) + 0.06), (y_root + 0.03, zc(y_root) - 0.05)
    up_tip, lo_tip = (1.13, 0.52), (0.96, -0.30)
    fork = (0.90, 0.07)
    pts = ([top_root] + curve(top_root, up_tip, -0.06, 9) + curve(up_tip, fork, 0.14, 8)
           + curve(fork, lo_tip, 0.10, 6) + curve(lo_tip, bot_root, -0.10, 7))
    th = []
    for (u, v) in pts:
        k = (Vector((u, v)) - Vector((y_root, 0.02))).length / 0.6
        th.append(0.085 + (0.032 - 0.085) * min(1.0, k))
    return fin_slab(pts, th, midline_frame)


def tail_stock():
    """Fleshy upturned axis carried into the upper caudal lobe."""
    pts = [(0.0, 0.50, zc(0.5)), (0.0, 0.70, zc(0.7) + 0.02), (0.0, 0.86, 0.17), (0.0, 1.00, 0.34),
           (0.0, 1.10, 0.48)]
    return nh.tube(pts, [0.07, 0.05, 0.035, 0.02, 0.0], sides=12, scale_xy=(0.75, 1.0))


def pectoral(sign):
    """Broad, fleshy-based pectoral fin from the notch behind the anterior lateral plate."""
    droop, sweep = math.radians(30), 0.30
    y_front, y_back = -0.26, -0.10

    def frame(u, v):
        y = u + v * sweep
        z_root = zc(u) - hb(u) * 0.35
        x = sign * (w(u) * 0.88 + v * math.cos(droop))
        z = z_root - v * math.sin(droop) - 0.05 * v * v
        return Vector((x, y, z)), Vector((sign * math.sin(droop), 0.0, math.cos(droop)))
    a, b = (y_front, 0.0), (y_back, 0.0)
    tip = (y_front + 0.10, 0.38)
    pts = [a] + curve(a, tip, 0.12, 7) + curve(tip, b, 0.16, 6) + [b]
    return fin_slab(pts, taper(pts, 0.0, 0.38, 0.07, 0.03), frame)


def pelvic(sign):
    droop = math.radians(40)

    def frame(u, v):
        x = sign * (w(u) * 0.45 + v * math.cos(droop))
        z = zc(u) - hb(u) * 0.85 - v * math.sin(droop)
        return Vector((x, u + v * 0.4, z)), Vector((sign * math.sin(droop), 0.0, math.cos(droop)))
    pts = [(0.14, 0.0), (0.16, 0.08), (0.22, 0.13), (0.27, 0.05), (0.26, 0.0)]
    return fin_slab(pts, [0.05, 0.04, 0.03, 0.04, 0.05], frame)


# ---------------------------------------------------------------- lower jaw

def jaw_top(y):
    """z of the palate / upper jaw line (bottom of the head shell over the mouth)."""
    return zc(y) - hb_head(y)


def lower_jaw_point(y, a):
    """Inferognathal and its soft tissue: a deep, narrow U in plan with a sunken mouth floor."""
    c, s = math.cos(a), math.sin(a)
    n = 2.3
    t = max(0.0, min(1.0, (y - Y_TIP) / (Y_HINGE + 0.08 - Y_TIP)))
    half_w = w(y) * 0.86 * math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 3)) ** 0.7 + 0.01
    x = half_w * math.copysign(abs(c) ** (2.0 / n), c)
    top = jaw_top(y) + 0.01
    depth = zc(y) - hb(y) * 0.98
    mid, half = (top + depth) * 0.5, (top - depth) * 0.5
    z = mid + half * math.copysign(abs(s) ** (2.0 / n), s)
    if s > 0:
        z -= 0.05 * max(0.0, 1.0 - (abs(x) / max(half_w * 0.72, 1e-4)) ** 2)
    return Vector((x, y, z))


HINGE = None


def jaw_open_matrix():
    hy, hz = HINGE
    return (Matrix.Translation(Vector((0, hy, hz))) @ Matrix.Rotation(JAW_OPEN, 4, "X")
            @ Matrix.Translation(Vector((0, -hy, -hz))))


# ---------------------------------------------------------------- armour plates

def shell_coords(p):
    """(y, phi) of a point: phi = angle from the dorsal midline (0) round to the belly (pi),
    mirrored so both flanks share one plate layout."""
    y = max(min(p.y, Y_PED), Y_TIP)
    ww, zz = max(w(y), 1e-3), zc(y)
    hz = max(ht(y) if p.z >= zz else hb(y), 1e-3)
    phi = math.atan2(abs(p.x) / ww, (p.z - zz) / hz)
    return p.y, phi


# (y, phi) seeds of the dermal plates; the head shield and thoracic shield are separate sets
HEAD_PLATES = [
    (-0.95, 0.00), (-0.91, 0.55),                          # rostral, preorbital front
    (-0.86, 0.25), (-0.80, 0.0),                           # preorbital, pineal
    (-0.70, 0.12), (-0.70, 0.55),                          # central, postorbital
    (-0.56, 0.00), (-0.56, 0.45),                          # nuchal, paranuchal
    (-0.60, 0.95), (-0.80, 1.20), (-0.71, 1.38),           # marginal, suborbital, postsuborbital
    (-0.90, 1.05),
]
THORAX_PLATES = [
    (-0.30, 0.00), (-0.42, 0.42), (-0.24, 0.58),           # median dorsal, ADL, PDL
    (-0.40, 1.00), (-0.26, 1.25),                          # anterior lateral, spinal region
    (-0.40, 1.75), (-0.22, 1.95), (-0.36, 2.60), (-0.20, 2.75),   # ventral plates (AVL, PVL)
]
PLATE_SCALE_Y = 1.0
PLATE_SCALE_PHI = 0.16


def joint_y(phi):
    """Cranio-thoracic joint line: slants forward lower down the flank."""
    return Y_JOINT - 0.07 * min(phi, 1.6) + (0.10 * max(0.0, phi - 1.6))


def armour_end_y(phi):
    """Back edge of the thoracic shield (higher on the back, notched over the pectoral fin)."""
    notch = 0.07 * math.exp(-((phi - 1.38) / 0.18) ** 2)
    return Y_ARMOUR_END - 0.05 * abs(math.cos(phi)) - notch


def armour_field(p):
    """Returns (armour 0..1, suture groove 0..1, joint gap 0..1) for a point on the body."""
    y, phi = shell_coords(p)
    if y > -0.05 or abs(p.x) > w(max(y, Y_TIP)) * 1.12:
        return 0.0, 0.0, 0.0
    # gentle warp so the sutures wander like real ones
    wy = y + 0.012 * noise.noise(Vector((y * 5.0, phi * 2.0, 0.7)))
    wp = phi + 0.04 * noise.noise(Vector((y * 4.0, phi * 2.5, 3.3)))
    end = armour_end_y(phi)
    armour = 1.0 - nh.smoothstep(end - 0.008, end + 0.008, wy)
    if armour <= 0.0:
        return 0.0, 0.0, 0.0
    jy = joint_y(phi)
    gap = 1.0 - nh.smoothstep(0.008, 0.02, abs(wy - jy))
    if phi > 2.3:
        gap = 0.0  # the joint is open only on the back and flanks
    seeds = HEAD_PLATES if wy < jy else THORAX_PLATES
    d = sorted(math.hypot((wy - sy) / PLATE_SCALE_Y, (wp - sp) * PLATE_SCALE_PHI) for sy, sp in seeds)
    # also distance across the midline (seeds mirrored onto the other flank)
    d2 = sorted(d + [math.hypot((wy - sy) / PLATE_SCALE_Y, (wp + sp) * PLATE_SCALE_PHI) for sy, sp in seeds if sp > 0.05])
    edge = d2[1] - d2[0]
    groove = 1.0 - nh.smoothstep(0.008, 0.022, edge)
    return armour, groove * armour, gap * armour


def orbit_field(p):
    """0..1 in the orbital notch around the eye (bone is cut away there)."""
    ey, ez = EYE_Y, eye_z()
    d = math.hypot((p.y - ey) / 0.075, (p.z - ez) / 0.07)
    if abs(p.x) < w(p.y) * 0.5:
        return 0.0
    return 1.0 - nh.smoothstep(0.75, 1.05, d)


def eye_z():
    return zc(EYE_Y) + ht(EYE_Y) * 0.35


def fin_distance(p):
    y = max(min(p.y, Y_PED), Y_TIP)
    ww, hz = max(w(y), 1e-3), max(ht(y) if p.z >= zc(y) else hb(y), 1e-3)
    r = math.sqrt((p.x / ww) ** 2 + ((p.z - zc(y)) / hz) ** 2)
    extra = max(0.0, p.y - Y_PED) * 1.1
    return max(0.0, r - 1.0) * min(ww, hz) + extra


def sculpt(bm):
    """Raise and texture the armour, cut sutures and the joint, paint everything."""
    bm.normal_update()
    disp, paint = {}, {}
    for v in bm.verts:
        p = v.co.copy()
        n = v.normal.copy()
        arm, groove, gap = armour_field(p)
        orb = orbit_field(p)
        arm *= 1.0 - orb
        tub = noise.noise(p * 60.0)
        pits = noise.noise(p * 26.0 + Vector((2, 5, 1)))
        d = 0.0
        d += 0.010 * arm                                   # shields stand proud of the skin
        d += arm * (0.0016 * tub + 0.0008 * pits)          # tuberculate bone
        d -= 0.009 * groove + 0.018 * gap
        d -= 0.018 * orb
        d += (1.0 - arm) * 0.0008 * noise.noise(p * 80.0)  # fine skin
        disp[v] = n * d

        # colour
        y = p.y
        up = nh.smoothstep(-0.4, 0.9, (p.z - zc(min(max(y, Y_TIP), Y_PED))) / max(ht(min(max(y, Y_TIP), Y_PED)), 1e-3))
        mott = 0.5 + 0.5 * noise.noise(p * 7.0)
        bone = nh.lerp(nh.lerp(ARMOUR, ARMOUR_LIGHT, 0.3 * (1.0 - up)), ARMOUR_DARK, up * 0.75)
        bone = nh.lerp(bone, ARMOUR_LIGHT, 0.25 * nh.smoothstep(0.35, 0.7, tub))
        bone = nh.lerp(bone, ARMOUR_DARK, 0.12 * mott)
        skin = nh.lerp(SKIN_FLANK, SKIN_BACK, up)
        skin = nh.lerp(skin, (skin[0] * 0.8, skin[1] * 0.85, skin[2] * 0.85), mott * 0.6)
        belly = nh.smoothstep(0.25, -0.45, n.z) * nh.smoothstep(Y_TIP, -0.6, y)
        if abs(p.x) > w(min(max(y, Y_TIP), Y_PED)) * 1.05 and fin_distance(p) > 0.02:
            belly = nh.smoothstep(0.1, -0.3, n.z) * 0.6
        skin = nh.lerp(skin, BELLY, belly * (1.0 - nh.smoothstep(Y_PED - 0.15, Y_PED, y)))
        skin = nh.lerp(skin, FIN_TIP, nh.smoothstep(0.08, 0.28, fin_distance(p)) * 0.8)
        c = nh.lerp(skin, bone, arm)
        c = nh.lerp(c, BELLY, 0.4 * arm * nh.smoothstep(0.0, -0.7, n.z))
        c = nh.lerp(c, SUTURE, 0.85 * min(1.0, groove + gap))
        c = nh.lerp(c, (0.08, 0.07, 0.07), orb * 0.9)
        # mouth roof: dark between the upper blades
        if palate(y) > 0.3 and n.z < -0.3 and p.z < jaw_top(y) + 0.03 and abs(p.x) < w(y) * 0.8:
            c = nh.lerp(c, MOUTH, nh.smoothstep(-0.3, -0.7, n.z) * palate(y))
        paint[v] = c
    for v, dv in disp.items():
        v.co += dv
    bm.normal_update()
    col = bm.loops.layers.color.get("Col")
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            c = paint[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


def jaw_sculpt(bm):
    """Lower jaw (already opened): bony inferognathal sides, dark mouth floor."""
    bm.normal_update()
    inv = jaw_open_matrix().inverted()
    col = bm.loops.layers.color.get("Col")
    paint = {}
    for v in bm.verts:
        q = inv @ v.co
        n = v.normal
        mott = 0.5 + 0.5 * noise.noise(q * 7.0)
        c = nh.lerp(ARMOUR, ARMOUR_DARK, 0.35)
        c = nh.lerp(c, BELLY, nh.smoothstep(-0.2, -0.9, n.z) * 0.5)
        c = nh.lerp(c, ARMOUR_DARK, 0.25 * mott)
        if n.z > 0.35:
            half_w = max(w(q.y) * 0.8, 1e-3)
            inner = 1.0 - nh.smoothstep(0.55, 0.8, abs(q.x) / half_w)
            c = nh.lerp(c, MOUTH, inner)
        v.co += n * 0.0018 * noise.noise(q * 55.0)
        paint[v] = c
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            c = paint[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


# ---------------------------------------------------------------- jaw blades

def blade(points, up, height, thick, cusp=None):
    """Bony cutting plate along `points` (its root line), its sharp edge `height` along `up`.
    cusp: optional (index, extra) to raise one point into a fang."""
    bm = bmesh.new()
    n = len(points)
    root_o, root_i, edge = [], [], []
    for i, p in enumerate(points):
        d = (points[min(i + 1, n - 1)] - points[max(i - 1, 0)]).normalized()
        side = d.cross(up).normalized()
        h = height[i] if isinstance(height, (list, tuple)) else height
        if cusp is not None:
            ci, extra = cusp
            h += extra * math.exp(-((i - ci) / 1.1) ** 2)
        root_o.append(bm.verts.new(p + side * thick * 0.5))
        root_i.append(bm.verts.new(p - side * thick * 0.5))
        edge.append(bm.verts.new(p + up * h))
    for i in range(n - 1):
        bm.faces.new([root_o[i], root_o[i + 1], edge[i + 1], edge[i]])
        bm.faces.new([root_i[i + 1], root_i[i], edge[i], edge[i + 1]])
        bm.faces.new([root_o[i + 1], root_o[i], root_i[i], root_i[i + 1]])
    bm.faces.new([root_o[0], edge[0], root_i[0]])
    bm.faces.new([root_i[-1], edge[-1], root_o[-1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def blade_color(up, z0, h):
    def fn(co, nrm):
        t = max(0.0, min(1.0, (co.dot(up) - z0) / h))
        return nh.lerp(BLADE_ROOT, BLADE, nh.smoothstep(0.0, 0.5, t))
    return fn


def rim(y, inset, z_of):
    t = max(0.0, min(1.0, (y - Y_TIP) / (Y_HINGE + 0.08 - Y_TIP)))
    hw = w(y) * inset * math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 3)) ** 0.7
    return hw, z_of(y)


def add_blades(mb):
    down, upv = Vector((0, 0, -1)), Vector((0, 0, 1))
    # upper: anterior supragnathals (paired fangs at the snout tip) + posterior blades
    for s in (-1, 1):
        pts = []
        for k in range(7):
            y = Y_TIP + 0.035 + 0.06 * k / 6
            hw, z = rim(y, 0.66, jaw_top)
            pts.append(Vector((s * max(hw, 0.014), y, z + 0.012)))
        mb.add(blade(pts, down, [0.04, 0.055, 0.06, 0.05, 0.04, 0.035, 0.03], 0.022, cusp=(1, 0.045)),
               blade_color(down, -(jaw_top(Y_TIP + 0.05) + 0.01), 0.08), smooth=False)
        pts = []
        for k in range(9):
            y = Y_TIP + 0.13 + 0.17 * k / 8
            hw, z = rim(y, 0.86, jaw_top)
            pts.append(Vector((s * hw, y, z + 0.012)))
        mb.add(blade(pts, down, [0.025, 0.04, 0.046, 0.048, 0.046, 0.04, 0.032, 0.024, 0.014], 0.02),
               blade_color(down, -(jaw_top(-0.8) + 0.01), 0.05), smooth=False)
    # lower: inferognathal blades rising to a pointed front cusp, opened with the jaw
    m = jaw_open_matrix()
    for s in (-1, 1):
        pts = []
        for k in range(12):
            y = Y_TIP + 0.03 + 0.30 * k / 11
            hw, z = rim(y, 0.86, jaw_top)
            pts.append(m @ Vector((s * max(hw, 0.012), y, z - 0.004)))
        up = (m.to_3x3() @ upv).normalized()
        hs = [0.04, 0.055, 0.058, 0.046, 0.038, 0.04, 0.044, 0.045, 0.042, 0.034, 0.024, 0.012]
        mb.add(blade(pts, up, hs, 0.024, cusp=(1, 0.055)),
               blade_color(up, pts[0].dot(up) - 0.005, 0.07), smooth=False)


# ---------------------------------------------------------------- eyes

def add_eyes(mb, surf):
    ez = eye_z()
    for s in (-1, 1):
        # find the orbit surface
        o = Vector((s * 1.0, EYE_Y, ez))
        loc, nrm, _i, _d = surf.ray_cast(o, Vector((-s, 0.0, 0.0)))
        if loc is None:
            continue
        look = Vector((s * 0.85, -0.35, 0.25)).normalized()
        centre = loc - look * 0.012
        r = 0.048
        mb.add(nh.ellipsoid(centre, (r, r, r), subdivisions=3),
               lambda co, n, c=centre, lk=look, rr=r: (
                   EYE if (co - c).normalized().dot(lk) > 0.86 else
                   IRIS if (co - c).normalized().dot(lk) > 0.70 else (0.12, 0.10, 0.08)))
        # sclerotic ring: a ring of small bony plates round the eye
        side = look.cross(Vector((0, 0, 1))).normalized()
        upv = side.cross(look).normalized()
        count = 12
        for k in range(count):
            a0 = k / count * math.tau
            a1 = (k + 0.85) / count * math.tau
            pts = []
            for j in range(4):
                a = a0 + (a1 - a0) * j / 3
                pts.append(centre + look * (r * 0.55) + (side * math.cos(a) + upv * math.sin(a)) * r * 0.98)
            mb.add(nh.tube(pts, [0.011, 0.012, 0.012, 0.011], sides=6, scale_xy=(1.0, 0.55)),
                   RING if k % 2 == 0 else RING_DARK)


# ---------------------------------------------------------------- build

def build_body():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    parts.add(loft(Y_TIP, Y_PED + 0.02, 100, 60, lambda y, a: section(y, a)), grey)
    parts.add(dorsal_fin(), grey)
    parts.add(anal_fin(), grey)
    parts.add(caudal(), grey)
    parts.add(tail_stock(), grey)
    for sg in (-1, 1):
        parts.add(pectoral(sg), grey)
        parts.add(pelvic(sg), grey)
    fused = parts.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5)
    return sculpt(fused)


def build_lower_jaw():
    parts = nh.MeshBuilder()
    parts.add(loft(Y_TIP + 0.005, Y_HINGE + 0.09, 40, 44, lower_jaw_point), (0.5, 0.5, 0.5))
    fused = parts.fuse(voxel=JAW_VOXEL, smooth=4, smooth_factor=0.5)
    nh.transform(fused, jaw_open_matrix())
    return jaw_sculpt(fused)


def build():
    global HINGE
    HINGE = (Y_HINGE + 0.03, jaw_top(Y_HINGE) - 0.01)
    body = build_body()
    surf = BVHTree.FromBMesh(body)
    mb = nh.MeshBuilder()
    mb.add(body)
    mb.add(build_lower_jaw())
    add_blades(mb)
    add_eyes(mb, surf)
    obj = mb.to_object(NAME, roughness=0.6)
    # pivot at the body centre
    vs = obj.data.vertices
    zs = [v.co.z for v in vs]
    ys = [v.co.y for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


def closeup(path, cam_loc, target, lens=55):
    scene = bpy.context.scene
    cam = scene.camera
    cam.data.lens = lens
    cam.location = Vector(cam_loc)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, NAME)
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        nh.render_preview(obj, out, views=((35, 25), (90, 4), (30, 62)), background=(0.05, 0.18, 0.24))
        closeup(out.with_name(f"{out.stem}_head.png"), (1.25, -2.0, 0.25), (0.0, -0.85, -0.05), lens=50)
        closeup(out.with_name(f"{out.stem}_mouth.png"), (0.55, -2.2, -0.25), (0.0, -0.95, -0.15), lens=60)


if __name__ == "__main__":
    main()
