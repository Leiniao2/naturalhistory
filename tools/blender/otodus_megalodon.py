"""
Procedural high-detail Otodus megalodon for the map (Swim style).

A massive, deep-bodied lamniform shark following current reconstructions:
bulkier than a great white, with a big head, short blunt snout, broad
pectoral fins, a tall triangular first dorsal and a lunate tail with keels on
the caudal peduncle. The mouth hangs slightly open over rows of big serrated
triangular teeth.

The body (with all fins) and the lower jaw are built from lofted sections and
fin slabs, each fused into one seamless surface (nh_model.MeshBuilder.fuse),
given a fine dermal-denticle displacement, gill-slit grooves and a lateral
line, then repainted procedurally (counter-shading with a slightly irregular
boundary, darker fin tips, pink gums). Teeth, eyes and the mouth lining are
crisp separate shells.

Usage:
  blender --background --python tools/blender/otodus_megalodon.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Megalodon.fbx
Pivot at the body centre, faces -Y, dorsal fin up (+Z). About 2.4 units long.
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

VOXEL = 0.031           # body remesh resolution (sets the triangle budget)
JAW_VOXEL = 0.022
JAW_OPEN = math.radians(15)

BACK = (0.15, 0.19, 0.23)      # dark slate along the spine
FLANK = (0.27, 0.32, 0.37)     # blue-grey flank
BELLY = (0.90, 0.91, 0.90)
FIN_TIP = (0.10, 0.12, 0.15)
GUM = (0.72, 0.43, 0.44)
THROAT = (0.26, 0.09, 0.10)
TOOTH = (0.95, 0.93, 0.86)
TOOTH_ROOT = (0.80, 0.74, 0.62)
EYE = (0.03, 0.03, 0.04)
GILL = (0.10, 0.12, 0.14)

Y_TIP, Y_PED = -1.22, 0.80     # snout tip, end of the caudal peduncle
Y_MOUTH, Y_HINGE = -1.04, -0.52


# ---------------------------------------------------------------- body profile

def _interp(table, y):
    """Monotone cubic (PCHIP) interpolation through (y, value) control points, so the
    profile stays smooth without ringing or flat steps at each control point."""
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


HALF_W = [(-1.22, 0.02), (-1.16, 0.12), (-1.05, 0.21), (-0.85, 0.30), (-0.62, 0.35), (-0.35, 0.38),
          (-0.05, 0.36), (0.20, 0.30), (0.42, 0.20), (0.62, 0.115), (0.80, 0.09)]
HALF_H_TOP = [(-1.22, 0.02), (-1.16, 0.11), (-1.05, 0.19), (-0.85, 0.28), (-0.6, 0.37), (-0.32, 0.43),
              (-0.05, 0.41), (0.20, 0.33), (0.42, 0.21), (0.62, 0.10), (0.80, 0.075)]
HALF_H_BOT = [(-1.22, 0.02), (-1.16, 0.09), (-1.05, 0.17), (-0.85, 0.26), (-0.6, 0.34), (-0.32, 0.40),
              (-0.05, 0.38), (0.20, 0.30), (0.42, 0.19), (0.62, 0.09), (0.80, 0.07)]
CENTER_Z = [(-1.22, 0.03), (-0.9, 0.02), (-0.4, 0.0), (0.2, 0.0), (0.8, 0.02)]


def w(y): return _interp(HALF_W, y)
def ht(y): return _interp(HALF_H_TOP, y)
def hb(y): return _interp(HALF_H_BOT, y)
def zc(y): return _interp(CENTER_Z, y)


def palate(y):
    """0 outside the mouth, 1 where the head's underside is cut flat for the upper jaw."""
    return nh.smoothstep(Y_MOUTH - 0.03, Y_MOUTH + 0.05, y) * (1.0 - nh.smoothstep(Y_HINGE - 0.04, Y_HINGE + 0.08, y))


PALATE_HB = 0.34  # fraction of the full belly depth left under the head where the jaw sits


def hb_head(y):
    """Bottom half-height of the head/body shell (shallower where the lower jaw takes over)."""
    return hb(y) * (1.0 - palate(y) * (1.0 - PALATE_HB))


def section(y, a, wf=w, top=ht, bot=hb_head, n=2.6):
    """Superellipse cross-section point at angle a (0 = +x, pi/2 = up)."""
    c, s = math.cos(a), math.sin(a)
    x = wf(y) * math.copysign(abs(c) ** (2.0 / n), c)
    hz = top(y) if s >= 0 else bot(y)
    z = zc(y) + hz * math.copysign(abs(s) ** (2.0 / n), s)
    return Vector((x, y, z))


def loft(y0, y1, ny, na, point):
    """Closed lofted shell between y0 and y1 (pointed caps) from point(y, angle)."""
    bm = bmesh.new()
    ys = [y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(i / (ny - 1) * math.pi)) for i in range(ny)]
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
    # ear clipping keeps concave outlines (the lunate tail) watertight for the voxel remesh
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
    """Thickness per outline point: thick at the root, thin toward the tip (along u or v)."""
    out = []
    for p in outline:
        t = (abs(p[axis]) - root_v) / (tip_v - root_v)
        t = max(0.0, min(1.0, t))
        out.append(t_root + (t_tip - t_root) * t)
    return out


# ---------------------------------------------------------------- fins

def midline_frame(u, v):  # u = y, v = z, fin in the x = 0 plane
    return Vector((0.0, u, v)), Vector((1.0, 0.0, 0.0))


def first_dorsal():
    base_z = lambda y: zc(y) + ht(y) - 0.07  # noqa: E731
    root_front, root_back = (-0.30, base_z(-0.30)), (0.14, base_z(0.14))
    apex = (0.02, zc(-0.1) + ht(-0.1) + 0.56)
    notch = (0.17, base_z(0.17) + 0.07)
    pts = [root_front] + curve(root_front, apex, -0.10, 8) + curve(apex, notch, 0.10, 7) + [notch, root_back]
    pts += curve(root_back, root_front, 0.0, 4)[1:]
    th = taper(pts, base_z(-0.1) + 0.05, apex[1], 0.10, 0.055)
    return fin_slab(pts, th, midline_frame)


def small_fin(y0, y1, z_root, height, rake, up=True):
    """Second dorsal / anal fin: a small raked triangle on the midline."""
    s = 1 if up else -1
    a, b = (y0, z_root), (y1, z_root)
    apex = (y0 + (y1 - y0) * 0.45 + rake, z_root + s * height)
    trail = (y1 + rake * 0.6, z_root + s * height * 0.25)
    pts = [a] + curve(a, apex, -0.12 * s, 4) + curve(apex, trail, 0.1 * s, 3) + [trail, b]
    th = taper(pts, z_root, z_root + s * height, 0.07, 0.055)
    return fin_slab(pts, th, midline_frame)


def caudal():
    y_root = 0.66
    top_root, bot_root = (y_root, zc(y_root) + 0.075), (y_root + 0.02, zc(y_root) - 0.07)
    up_tip, lo_tip = (1.20, 0.70), (1.10, -0.52)
    fork = (0.95, 0.02)
    pts = ([top_root] + curve(top_root, up_tip, -0.09, 9) + curve(up_tip, fork, 0.13, 8)
           + curve(fork, lo_tip, 0.13, 7) + curve(lo_tip, bot_root, -0.08, 8))
    th = []
    for (u, v) in pts:
        k = (Vector((u, v)) - Vector((y_root, 0.0))).length / 0.75
        th.append(0.11 + (0.068 - 0.11) * min(1.0, k))
    return fin_slab(pts, th, midline_frame)


def pectoral(sign):
    droop, sweep = math.radians(22), 0.42
    y_front, y_back = -0.58, -0.30
    def frame(u, v):
        y = u + v * sweep
        z_root = zc(u) - hb(u) * 0.45
        x = sign * (w(u) * 0.80 + v * math.cos(droop))
        z = z_root - v * math.sin(droop) - 0.08 * v * v
        n = Vector((sign * math.sin(droop), 0.0, math.cos(droop)))
        return Vector((x, y, z)), n
    root_a, root_b = (y_front, 0.0), (y_back, 0.0)
    tip = (y_front + 0.10, 0.70)
    pts = [root_a] + curve(root_a, tip, 0.12, 9) + curve(tip, root_b, 0.14, 8) + [root_b]
    pts = [(u, v) for u, v in pts]
    th = taper(pts, 0.0, 0.7, 0.12, 0.065)
    return fin_slab(pts, th, frame)


def pelvic(sign):
    droop = math.radians(35)
    def frame(u, v):
        x = sign * (w(u) * 0.35 + v * math.cos(droop))
        z = zc(u) - hb(u) * 0.85 - v * math.sin(droop)
        return Vector((x, u + v * 0.35, z)), Vector((sign * math.sin(droop), 0.0, math.cos(droop)))
    pts = [(0.30, 0.0), (0.33, 0.12), (0.40, 0.18), (0.46, 0.06), (0.44, 0.0)]
    return fin_slab(pts, [0.07, 0.06, 0.055, 0.06, 0.07], frame)


def keel(sign):
    """Lateral keel on the caudal peduncle (a horizontal ridge)."""
    def frame(u, v):
        return Vector((sign * (w(u) * 0.85 + v), u, zc(u))), Vector((0.0, 0.0, 1.0))
    pts = [(0.46, 0.0), (0.56, 0.035), (0.70, 0.05), (0.80, 0.03), (0.84, 0.0)]
    return fin_slab(pts, [0.05, 0.055, 0.06, 0.055, 0.05], frame)


# ---------------------------------------------------------------- lower jaw

def jaw_top(y):
    """z of the palate / jaw line (bottom of the head shell over the mouth)."""
    return zc(y) - hb_head(y)


RIM_FRONT, RIM_BACK = Y_MOUTH + 0.035, Y_HINGE + 0.07  # tooth row from the front of the U to the corners


def _u_sin(y, front):
    """sin(phi) of the U-shaped jaw outline at y (0 at the front of the U, 1 at the sides)."""
    t = max(0.0, min(1.0, (y - front) / (RIM_BACK - front)))
    c = 1.0 - t ** (1.0 / 1.15)
    return math.sqrt(max(0.0, 1.0 - c * c))


def lower_jaw_point(y, a):
    """U-shaped chin: rounded in plan, a raised lip along the tooth row and a sunken mouth floor."""
    c, s = math.cos(a), math.sin(a)
    n = 2.2
    back = nh.smoothstep(Y_HINGE - 0.2, Y_HINGE + 0.06, y)
    half_w = w(y) * 0.95 * _u_sin(y, RIM_FRONT - 0.05) ** 0.6 * (1.0 - 0.2 * back) + 0.004
    x = half_w * math.copysign(abs(c) ** (2.0 / n), c)
    top = jaw_top(y) + 0.012
    depth = zc(y) - hb(y) * (1.0 - 0.12 * back) - 0.004
    mid = (top + depth) * 0.5
    half = (top - depth) * 0.5
    z = mid + half * math.copysign(abs(s) ** (2.0 / n), s)
    if s > 0:  # mouth floor sinks between the lips
        z -= 0.07 * max(0.0, 1.0 - (abs(x) / max(half_w * 0.72, 1e-4)) ** 2) * (1.0 - back)
    return Vector((x, y, z))


HINGE = None  # set in build(): (y, z) the lower jaw rotates about


def jaw_open_matrix():
    hy, hz = HINGE
    return (Matrix.Translation(Vector((0, hy, hz))) @ Matrix.Rotation(JAW_OPEN, 4, "X")
            @ Matrix.Translation(Vector((0, -hy, -hz))))


# ---------------------------------------------------------------- surface detail

GILL_YS = [-0.70, -0.645, -0.59, -0.535, -0.48]


def gill_amount(p):
    """0..1 groove strength for the five gill slits on the flank."""
    y, z = p.y, p.z
    if abs(p.x) < w(y) * 0.55:
        return 0.0
    rel = (z - zc(y)) / max(hb(y), 1e-3)
    if not -0.75 < rel < 0.45:
        return 0.0
    best = 0.0
    for k, gy in enumerate(GILL_YS):
        # slits curve back toward the bottom and get slightly shorter toward the rear
        lo = -0.75 + k * 0.03
        if rel < lo:
            continue
        cy = gy + 0.03 * (rel - 0.45) ** 2
        d = abs(y - cy)
        ends = nh.smoothstep(lo, lo + 0.12, rel) * (1.0 - nh.smoothstep(0.3, 0.45, rel))
        best = max(best, (1.0 - nh.smoothstep(0.004, 0.016, d)) * ends)
    return best


def boundary_z(y, x):
    """Counter-shading line: a little below the flank midline, wavy and slightly blotchy."""
    wav = noise.noise(Vector((y * 3.2, 0.0, 1.3))) * 0.035 + noise.noise(Vector((y * 9.0, x * 4.0, 7.7))) * 0.012
    return zc(y) - hb(y) * 0.18 + wav


def fin_distance(p):
    """How far a point sits outside the body envelope (0 on the body)."""
    y = max(min(p.y, Y_PED), Y_TIP)
    ww, hz = max(w(y), 1e-3), max(ht(y) if p.z >= zc(y) else hb(y), 1e-3)
    r = math.sqrt((p.x / ww) ** 2 + ((p.z - zc(y)) / hz) ** 2)
    extra = max(0.0, p.y - Y_PED) * 1.2
    return max(0.0, r - 1.0) * min(ww, hz) + extra


def body_color(p, n):
    y = p.y
    bz = boundary_z(y, p.x)
    belly = 1.0 - nh.smoothstep(bz - 0.012, bz + 0.012, p.z)
    belly *= 1.0 - nh.smoothstep(Y_PED - 0.12, Y_PED, y)  # tail and caudal fin stay grey
    # paired fins (pectorals, pelvics): grey on top, white underneath
    if abs(p.x) > w(max(min(y, Y_PED), Y_TIP)) * 1.02 and -0.65 < y < 0.5 and fin_distance(p) > 0.02:
        belly = nh.smoothstep(0.1, -0.25, n.z)
    up = nh.smoothstep(zc(y), zc(y) + ht(y) + 0.1, p.z)
    grey = nh.lerp(FLANK, BACK, up)
    mott = noise.noise(p * 6.0) * 0.5 + 0.5
    grey = nh.lerp(grey, (grey[0] * 0.82, grey[1] * 0.85, grey[2] * 0.88), mott * 0.5)
    col = nh.lerp(grey, BELLY, belly)
    # darker fin tips and trailing edges
    fd = fin_distance(p)
    col = nh.lerp(col, FIN_TIP, nh.smoothstep(0.22, 0.48, fd) * (0.85 if belly < 0.5 else 0.6))
    # lateral line: a thin pale streak along the flank
    if Y_HINGE < y < 0.70 and abs(p.x) > w(y) * 0.6:
        lz = zc(y) + ht(y) * 0.22 - 0.05 * (y + 0.6) ** 2
        line = 1.0 - nh.smoothstep(0.003, 0.010, abs(p.z - lz))
        col = nh.lerp(col, (0.52, 0.56, 0.60), line * 0.6)
    # gill slits
    g = gill_amount(p)
    col = nh.lerp(col, GILL, g * 0.85)
    # roof of the mouth: gums along the tooth row, dark further in
    if palate(y) > 0.2 and n.z < -0.2 and p.z < jaw_top(y) + 0.04:
        inner = 1.0 - nh.smoothstep(0.62, 0.9, abs(p.x) / max(w(y), 1e-3))
        mouth = nh.lerp(GUM, THROAT, inner * 0.8)
        col = nh.lerp(col, mouth, nh.smoothstep(-0.2, -0.6, n.z) * palate(y))
    # a hint of the ampullae dots on the snout underside
    if y < -0.9 and belly > 0.5:
        dots = noise.noise(p * 40.0)
        col = nh.lerp(col, (0.70, 0.71, 0.72), nh.smoothstep(0.45, 0.6, dots) * 0.5)
    return col


def jaw_color(p, n):
    """Lower jaw, painted in its open pose: skin outside, gums on the lip, dark mouth floor."""
    col = body_color(p, n)
    if n.z > 0.2:
        q = jaw_open_matrix().inverted() @ p      # back to the closed pose to measure the lip
        half_w = max(w(q.y) * 0.95 * _u_sin(q.y, RIM_FRONT - 0.05) ** 0.6, 1e-3)
        inner = 1.0 - nh.smoothstep(0.55, 0.85, abs(q.x) / half_w)
        mouth = nh.lerp(GUM, THROAT, inner * 0.85)
        col = nh.lerp(col, mouth, nh.smoothstep(0.2, 0.55, n.z))
    return col


def skin_detail(bm, with_gills=True):
    """Fine dermal-denticle grain, subtle myomere bulges and gill-slit grooves."""
    bm.normal_update()
    for v in bm.verts:
        p = v.co
        d = noise.noise(p * 55.0) * 0.0012 + noise.noise(p * 23.0 + Vector((3, 1, 2))) * 0.0014
        if with_gills:
            d -= gill_amount(p) * 0.014
        v.co = p + v.normal * d


# ---------------------------------------------------------------- teeth

def tooth(base, down, side, out, height, width, thick, curve_back=0.0):
    """Serrated triangular blade. base: root centre; down: tip direction; side: along the jaw."""
    bm = bmesh.new()
    serr = 4
    outline = []
    # left edge up to tip, then right edge back down; small zigzag serrations
    for i in range(serr + 1):
        t = i / serr
        wv = (1.0 - t) * width * 0.5
        zig = (0.06 * width) * (1 if i % 2 else -1) * (1.0 - t) if 0 < i < serr else 0.0
        outline.append((-wv - zig, t * height))
    for i in range(serr - 1, -1, -1):
        t = i / serr
        wv = (1.0 - t) * width * 0.5
        zig = (0.06 * width) * (1 if i % 2 else -1) * (1.0 - t) if 0 < i < serr else 0.0
        outline.append((wv + zig, t * height))
    front, back = [], []
    for sx, h in outline:
        t = h / height
        p = base + side * sx + down * h + out * (curve_back * t * t * height)
        tt = thick * (1.0 - 0.75 * t)
        front.append(bm.verts.new(p + out * tt * 0.5))
        back.append(bm.verts.new(p - out * tt * 0.5))
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    m = len(outline)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new([front[i], back[i], back[j], front[j]])
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def tooth_color(base, down, height):
    def fn(co, n):
        t = max(0.0, min(1.0, (co - base).dot(down) / height))
        return nh.lerp(TOOTH_ROOT, TOOTH, nh.smoothstep(0.0, 0.35, t))
    return fn


def rim_points(count, inset, z_of, open_m=None):
    """Points along the U-shaped jaw rim (front to back on both sides) with tangent/outward dirs."""
    pts = []
    for i in range(count):
        s = -1.0 + 2.0 * (i + 0.5) / count            # -1 .. 1 (left .. right)
        phi = s * math.pi / 2
        y = RIM_FRONT + (RIM_BACK - RIM_FRONT) * (1.0 - math.cos(phi)) ** 1.15
        x = math.copysign(w(y) * inset * abs(math.sin(phi)) ** 0.75, s)
        p = Vector((x, y, z_of(y)))
        pts.append((p, s))
    out = []
    for k, (p, s) in enumerate(pts):
        a = pts[max(k - 1, 0)][0]
        b = pts[min(k + 1, len(pts) - 1)][0]
        tang = (b - a).normalized()
        outward = Vector((p.x, p.y - (Y_MOUTH + 0.25), 0.0))
        outward = (outward - tang * outward.dot(tang)).normalized()
        if open_m is not None:
            p = open_m @ p
            tang = (open_m.to_3x3() @ tang).normalized()
            outward = (open_m.to_3x3() @ outward).normalized()
        out.append((p, tang, outward, s))
    return out


def add_teeth(mb, upper):
    open_m = None if upper else jaw_open_matrix()
    if upper:
        z_of = lambda y: jaw_top(y) + 0.006  # noqa: E731
        down = Vector((0, 0, -1))
    else:
        z_of = lambda y: jaw_top(y) - 0.022  # noqa: E731  (on the lip, below the closed jaw line)
        down = Vector((0, 0, 1))
    n_teeth = 26 if upper else 24
    rows = ((0.86, 1.0, 0.0), (0.74, 0.62, 0.55)) if upper else ((0.80, 0.9, 0.0), (0.68, 0.6, 0.55))
    for row, (inset, scale, tilt) in enumerate(rows):
        for p, tang, outward, s in rim_points(n_teeth - row * 4, inset, z_of, open_m):
            front = 1.0 - abs(s)
            h = (0.04 + 0.05 * front ** 1.5) * scale
            wdt = h * 0.85
            d = down if open_m is None else (open_m.to_3x3() @ down).normalized()
            # second row folds inward (backward into the mouth)
            d = (d * math.cos(tilt) - outward * math.sin(tilt)).normalized()
            base = p - d * h * 0.18
            # upper teeth rake slightly outward, lower teeth stand more upright and inward
            mb.add(tooth(base, d, tang, outward, h, wdt, h * 0.16, curve_back=-0.08 if upper else 0.05),
                   tooth_color(base, d, h), smooth=False)


# ---------------------------------------------------------------- build

def build_body():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)  # everything is repainted after fusing
    parts.add(loft(Y_TIP, Y_PED + 0.02, 90, 56, lambda y, a: section(y, a)), grey)
    parts.add(first_dorsal(), grey)
    parts.add(small_fin(0.43, 0.52, zc(0.47) + ht(0.47) - 0.03, 0.10, 0.04), grey)
    parts.add(small_fin(0.45, 0.54, zc(0.5) - hb(0.5) + 0.03, 0.09, 0.05, up=False), grey)
    parts.add(caudal(), grey)
    for sg in (-1, 1):
        parts.add(pectoral(sg), grey)
        parts.add(pelvic(sg), grey)
        parts.add(keel(sg), grey)
    fused = parts.fuse(voxel=VOXEL, smooth=7, smooth_factor=0.5)
    skin_detail(fused)
    return fused


def build_lower_jaw():
    parts = nh.MeshBuilder()
    parts.add(loft(RIM_FRONT - 0.05, Y_HINGE + 0.06, 44, 48, lower_jaw_point), (0.5, 0.5, 0.5))
    fused = parts.fuse(voxel=JAW_VOXEL, smooth=4, smooth_factor=0.5)
    skin_detail(fused, with_gills=False)
    nh.transform(fused, jaw_open_matrix())
    fused.normal_update()
    return fused


def eye(sign):
    y = -0.86
    z = zc(y) + ht(y) * 0.22
    bm = nh.ellipsoid((0, 0, 0), (0.030, 0.034, 0.027), subdivisions=2)
    # place on the flank surface (pushed slightly in so it sits in a socket)
    x = sign * (w(y) * 0.93)
    nh.transform(bm, Matrix.Translation(Vector((x, y, z))))
    return bm


def build():
    global HINGE
    HINGE = (Y_HINGE + 0.04, jaw_top(Y_HINGE) - 0.02)
    mb = nh.MeshBuilder()

    body = build_body()
    mb.add(body, body_color)
    jaw = build_lower_jaw()
    mb.add(jaw, jaw_color)

    add_teeth(mb, upper=True)
    add_teeth(mb, upper=False)

    for sg in (-1, 1):
        mb.add(eye(sg), EYE)

    obj = mb.to_object("Megalodon", roughness=0.45)
    return obj


def closeup(obj, path, cam_loc, target, lens=55):
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
    nh.export_fbx(obj, "Megalodon")
    if "--render" in argv:
        out = Path(argv[argv.index("--render") + 1])
        nh.render_preview(obj, out, views=((35, 25), (90, 4), (30, 62)), background=(0.05, 0.18, 0.24))
        closeup(obj, out.with_name(f"{out.stem}_head.png"), (1.35, -2.45, 0.35), (0.0, -0.85, -0.1), lens=50)
        closeup(obj, out.with_name(f"{out.stem}_mouth.png"), (0.75, -2.3, -0.30), (0.0, -0.9, -0.18), lens=60)


if __name__ == "__main__":
    main()
