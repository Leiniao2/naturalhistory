"""
Procedural high-detail Tiktaalik roseae (Late Devonian elpistostegalian "fishapod") for
the map (Ground style).

Propped up on its front fins in shallow water: the flat, broad, triangular,
crocodile-like head is held up on a mobile neck (no gill cover, so the head is set off
from the shoulders by a short neck), the chest is lifted off the bottom by the
robust lobed pectoral fins (shoulder, elbow and a bent "wrist" so the distal fin lies
flat on the ground pointing forward and out), while the belly, the smaller lobed
pelvic fins and the long scaly tail rest on the ground, the tail curving a little to
one side.

The body, head, eye mounds and fleshy fin lobes are fused into one seamless surface,
then sculpted by displacement: overlapping rhombic scales on the body and tail, a
pitted dermal-bone texture on the skull roof, the mouth line and spiracle slits.
Painted olive-brown with darker blotches on top, paler flanks and a cream belly.
Crisp details on top: fringes of fin rays (lepidotrichia) along the pectoral and
pelvic fins and the dorsal/ventral fin folds of the tail, eyes on top of the head,
nostrils and small conical teeth.

Usage:
  blender --background --python tools/blender/tiktaalik_roseae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tiktaalik.fbx (map style Ground: pivot on the
ground under the belly, facing -Y). About 1.8 units long.
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

NAME = "Tiktaalik"
VOXEL = 0.0135

BACK = (0.30, 0.29, 0.17)          # olive-brown
BACK_DARK = (0.16, 0.15, 0.09)
FLANK = (0.50, 0.46, 0.30)
BELLY = (0.80, 0.74, 0.56)
SKULL = (0.40, 0.37, 0.24)
GROOVE = (0.10, 0.09, 0.06)
FIN = (0.46, 0.40, 0.26)
FIN_RAY = (0.26, 0.22, 0.13)
FIN_EDGE = (0.68, 0.60, 0.42)
TOOTH = (0.92, 0.88, 0.76)
IRIS = (0.62, 0.48, 0.16)
PUPIL = (0.02, 0.02, 0.02)
MOUTH = (0.25, 0.12, 0.10)

# Body profile along Y (snout at -Y): (y, half-width, top half-height, bottom half-height, centre z)
PROFILE = [
    (-0.86, 0.020, 0.010, 0.010, 0.205),
    (-0.83, 0.054, 0.022, 0.018, 0.208),
    (-0.76, 0.090, 0.032, 0.026, 0.214),
    (-0.66, 0.124, 0.040, 0.034, 0.218),
    (-0.57, 0.148, 0.050, 0.044, 0.214),   # back of the skull
    (-0.50, 0.130, 0.060, 0.058, 0.200),   # short neck
    (-0.42, 0.150, 0.075, 0.074, 0.176),   # shoulders
    (-0.25, 0.168, 0.088, 0.084, 0.132),
    (-0.05, 0.160, 0.088, 0.082, 0.096),
    (0.15, 0.128, 0.082, 0.076, 0.078),    # hips
    (0.35, 0.088, 0.070, 0.064, 0.072),
    (0.55, 0.050, 0.054, 0.046, 0.080),
    (0.75, 0.028, 0.036, 0.030, 0.092),
    (0.92, 0.010, 0.012, 0.012, 0.100),
]
Y_TIP, Y_END = PROFILE[0][0], PROFILE[-1][0]
Y_SKULL = -0.53     # back of the skull roof
EYE_Y = -0.66


def _interp(col, y):
    ys = [p[0] for p in PROFILE]
    vs = [p[col] for p in PROFILE]
    if y <= ys[0]:
        return vs[0]
    if y >= ys[-1]:
        return vs[-1]
    for i in range(len(ys) - 1):
        if ys[i] <= y <= ys[i + 1]:
            t = (y - ys[i]) / (ys[i + 1] - ys[i])
            t = t * t * (3 - 2 * t) * 0.6 + t * 0.4
            return vs[i] + (vs[i + 1] - vs[i]) * t
    return vs[-1]


def W(y): return _interp(1, y)
def HT(y): return _interp(2, y)
def HB(y): return _interp(3, y)
def CZ(y): return _interp(4, y)


def cx(y):
    """Tail curves gently off to the right."""
    s = max(0.0, (y - 0.15) / 0.8)
    return 0.16 * s * s


def power(y):
    return 3.2 if y < Y_SKULL else (2.6 if y < 0.2 else 2.2)   # flat, boxy skull; rounder tail


def ring_point(y, a):
    u, v = math.cos(a), math.sin(a)
    ex = 2.0 / power(y)
    x = cx(y) + W(y) * math.copysign(abs(u) ** ex, u)
    h = HT(y) if v >= 0 else HB(y)
    z = CZ(y) + h * math.copysign(abs(v) ** ex, v)
    return Vector((x, y, z))


def body_loft(sides=40):
    bm = bmesh.new()
    rings = [[bm.verts.new(Vector((cx(Y_TIP), Y_TIP - 0.012, CZ(Y_TIP))))]]
    y = Y_TIP
    while y < Y_END:
        rings.append([bm.verts.new(ring_point(y, k / sides * math.tau)) for k in range(sides)])
        y += 0.012
    rings.append([bm.verts.new(Vector((cx(Y_END + 0.02), Y_END + 0.02, CZ(Y_END))))])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(sides):
                bm.faces.new([a[0], b[(k + 1) % sides], b[k]])
        elif len(b) == 1:
            for k in range(sides):
                bm.faces.new([a[k], a[(k + 1) % sides], b[0]])
        else:
            for k in range(sides):
                j = (k + 1) % sides
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


# ---------------------------------------------------------------- fins (fleshy lobes)

def pectoral_path(s):
    """Shoulder -> elbow (out and down) -> bent wrist -> distal fin flat on the ground."""
    sh = Vector((s * 0.12, -0.37, 0.135))
    el = Vector((s * 0.26, -0.39, 0.09))
    wr = Vector((s * 0.31, -0.45, 0.026))
    tip = Vector((s * 0.35, -0.55, 0.014))
    return [sh, (sh + el) / 2 + Vector((0, 0, 0.01)), el, (el + wr) / 2, wr, (wr + tip) / 2, tip]


PEC_R = [0.056, 0.050, 0.044, 0.038, 0.032, 0.026, 0.016]


def pelvic_path(s):
    hip = Vector((s * 0.07, 0.17, 0.035))
    kn = Vector((s * 0.15, 0.24, 0.020))
    tip = Vector((s * 0.20, 0.33, 0.012))
    return [hip, (hip + kn) / 2, kn, (kn + tip) / 2, tip]


PEL_R = [0.042, 0.038, 0.032, 0.024, 0.014]


def lobes(body):
    for s in (-1, 1):
        body.add(nh.tube(pectoral_path(s), PEC_R, sides=14, scale_xy=(1.25, 0.75)), FIN)
        p = pectoral_path(s)
        body.add(nh.ellipsoid(p[2], (0.04, 0.038, 0.034), subdivisions=2), FIN)          # elbow
        body.add(nh.uv_ellipsoid(tuple(p[5]), (0.036, 0.055, 0.013), 12, 8), FIN)       # flat distal fin
        body.add(nh.tube(pelvic_path(s), PEL_R, sides=12, scale_xy=(1.3, 0.7)), FIN)
    # eye mounds (raised orbits on top of the skull) and the snout bulge over the nostrils
    for s in (-1, 1):
        y = EYE_Y
        body.add(nh.ellipsoid((s * 0.048, y, CZ(y) + HT(y) - 0.004), (0.030, 0.036, 0.018), subdivisions=3), SKULL)


# ---------------------------------------------------------------- sculpt / paint

def frac(x):
    return x - math.floor(x)


def local(co):
    y = max(min(co.y, Y_END), Y_TIP)
    u = (co.x - cx(y)) / max(W(y), 1e-3)
    v = (co.z - CZ(y)) / max(HT(y) if co.z >= CZ(y) else HB(y), 1e-3)
    return u, v


def on_body(co):
    u, v = local(co)
    return abs(u) < 1.15 and abs(v) < 1.3


def jaw_z(y):
    return CZ(y) - HB(y) * 0.15 + 0.012 * nh.smoothstep(-0.62, -0.53, y)


def scale_field(co, u, v):
    """Rhombic scale pattern: returns (groove 0..1, raised rear edge 0..1)."""
    y = co.y
    a = math.atan2(v, u)                    # around the body
    r = (W(y) + HT(y)) * 0.5
    s = a * r
    P = 0.05
    p1 = frac((y + s) / P)
    p2 = frac((y - s) / P)
    edge = min(p1, 1 - p1, p2, 1 - p2)
    groove = 1.0 - nh.smoothstep(0.0, 0.14, edge)
    rear = nh.smoothstep(0.4, 0.95, min(p1, p2))   # scales overlap: higher toward their back edge
    return groove, rear


def sculpt(bm):
    bm.normal_update()
    col = bm.loops.layers.color.get("Col")
    disp, paint = {}, {}
    for vert in bm.verts:
        co = vert.co.copy()
        n = vert.normal.copy()
        y = co.y
        u, v = local(co)
        body = on_body(co)
        fine = noise.noise(co * 60.0)
        coarse = noise.noise(co * 7.0 + Vector((1.3, 2.1, 0.7)))
        d = 0.0008 * fine
        groove = rear = 0.0
        head = y < Y_SKULL + 0.02
        if body and not head and y < Y_END - 0.04:
            groove, rear = scale_field(co, u, v)
            fade = nh.smoothstep(Y_SKULL, Y_SKULL + 0.06, y)
            groove *= fade
            rear *= fade
            d += 0.0028 * rear - 0.0028 * groove
        elif body and head and v > 0.2:
            # pitted dermal bone of the skull roof
            d += 0.0018 * noise.noise(co * 90.0) - 0.0012 * nh.smoothstep(0.3, 0.6, noise.noise(co * 35.0))
        line = 0.0
        if body and head and abs(u) > 0.6:
            dz = abs(co.z - jaw_z(y))
            line = 1.0 - nh.smoothstep(0.002, 0.007, dz)
            d -= 0.004 * line
        # spiracle slits on the skull roof behind the eyes
        spir = 0.0
        for s in (-1, 1):
            q = ((co.x - s * 0.072) * math.cos(0.5 * s) - (y + 0.565) * math.sin(0.5 * s),
                 (co.x - s * 0.072) * math.sin(0.5 * s) + (y + 0.565) * math.cos(0.5 * s))
            if v > 0.3:
                spir = max(spir, math.exp(-((q[0] / 0.004) ** 2 + (q[1] / 0.022) ** 2)))
        d -= 0.006 * spir
        disp[vert] = n * d

        # ---- colour
        if body:
            t_back = nh.smoothstep(-0.1, 0.6, v + 0.12 * coarse)
            t_belly = nh.smoothstep(-0.3, -0.7, v + 0.08 * coarse)
        else:
            t_back = nh.smoothstep(0.0, 0.8, n.z)
            t_belly = nh.smoothstep(-0.2, -0.7, n.z)
        c = nh.lerp(FLANK, BACK, t_back)
        c = nh.lerp(c, BACK_DARK, 0.6 * nh.smoothstep(0.15, 0.5, coarse) * t_back)   # blotches
        if head and body:
            c = nh.lerp(c, SKULL, 0.5 * t_back)
            below = nh.smoothstep(jaw_z(y) + 0.002, jaw_z(y) - 0.01, co.z)
            c = nh.lerp(c, nh.lerp(FLANK, BELLY, 0.5), below * 0.7)
        if not body:
            c = nh.lerp(nh.lerp(FIN, BACK, 0.4 * t_back), FIN_EDGE, 0.3 * t_belly)
        c = nh.lerp(c, BELLY, t_belly * (1.0 if body else 0.4))
        c = nh.lerp(c, GROOVE, 0.55 * groove)
        c = nh.lerp(c, FIN_EDGE, 0.25 * rear * (1.0 - t_belly))
        c = nh.lerp(c, GROOVE, 0.9 * max(line, spir))
        k = 0.9 + 0.2 * (0.5 + 0.5 * fine)
        paint[vert] = (c[0] * k, c[1] * k, c[2] * k)
    for vert, dv in disp.items():
        vert.co += dv
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
        for l in f.loops:
            c = paint[l.vert]
            l[col] = (c[0], c[1], c[2], 1.0)
    return bm


# ---------------------------------------------------------------- crisp details

def ray_panel(root, tip, thick=0.006):
    """Fin web between a root polyline and a tip polyline (same count)."""
    root = [Vector(p) for p in root]
    tip = [Vector(p) for p in tip]
    bm = bmesh.new()
    n = len(root)
    rows = 4
    grid = {}
    nrm = (tip[n // 2] - root[n // 2]).cross(root[-1] - root[0])
    nrm = nrm.normalized() if nrm.length > 1e-9 else Vector((0, 0, 1))
    for i in range(n):
        for r in range(rows + 1):
            p = root[i].lerp(tip[i], r / rows)
            th = thick * (1.0 - 0.6 * r / rows)
            grid[i, r, 0] = bm.verts.new(p + nrm * th * 0.5)
            grid[i, r, 1] = bm.verts.new(p - nrm * th * 0.5)
    for i in range(n - 1):
        for r in range(rows):
            q = [(i, r), (i + 1, r), (i + 1, r + 1), (i, r + 1)]
            bm.faces.new([grid[k + (0,)] for k in q])
            bm.faces.new([grid[k + (1,)] for k in reversed(q)])
    perim = [(i, 0) for i in range(n)] + [(n - 1, r) for r in range(1, rows + 1)] \
        + [(i, rows) for i in range(n - 2, -1, -1)] + [(0, r) for r in range(rows - 1, 0, -1)]
    for a, b in zip(perim, perim[1:] + perim[:1]):
        bm.faces.new([grid[a + (0,)], grid[b + (0,)], grid[b + (1,)], grid[a + (1,)]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # remember each vertex's (u along the root, v out to the tip) for the ray paint
    uv = {}
    for (i, r, _side), vv in grid.items():
        uv[vv] = (i / (n - 1), r / rows)
    return bm, uv, n


def add_rays(mb, root, tip):
    bm, uv, n = ray_panel(root, tip)
    vcol = {}
    for vv, (u, v) in uv.items():
        vcol[vv] = nh.lerp(FIN, FIN_EDGE, 0.6 * nh.smoothstep(0.5, 1.0, v))
    nrm = (tip[len(tip) // 2] - root[len(root) // 2]).cross(Vector(root[-1]) - Vector(root[0]))
    nrm = nrm.normalized() if nrm.length > 1e-9 else Vector((0, 0, 1))
    bm.normal_update()
    vmap = {v: mb.bm.verts.new(v.co) for v in bm.verts}
    for f in bm.faces:
        try:
            nf = mb.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:
            continue
        nf.smooth = False
        for loop, sl in zip(nf.loops, f.loops):
            c = vcol[sl.vert]
            loop[mb.col] = (c[0], c[1], c[2], 1.0)
    bm.free()
    # the bony rays themselves, as thin ribs on both faces of the web
    for a, b in zip(root, tip):
        a, b = Vector(a), Vector(b)
        for sg in (1, -1):
            off = nrm * sg * 0.003
            mb.add(nh.tube([a.lerp(b, 0.05) + off, a.lerp(b, 0.97) + off * 0.5], [0.0024, 0.0008], sides=3,
                           cap_start=False, cap_end=False), FIN_RAY, smooth=False)


def fin_rays(mb):
    for s in (-1, 1):
        p = pectoral_path(s)
        # distal fan lying on the ground around the fin tip (the "hand")
        wr, tip = p[4], p[6]
        fwd = (tip - wr).normalized()
        side = Vector((-fwd.y, fwd.x, 0)).normalized()
        root, outer = [], []
        c = wr.lerp(tip, 0.6)
        for k in range(13):
            a = math.radians(-85 + 170 * k / 12)
            d = (fwd * math.cos(a) + side * math.sin(a)).normalized()
            r0 = 0.022 + 0.02 * math.cos(a)
            root.append(Vector((c.x, c.y, 0.008)) + d * r0)
            outer.append(Vector((c.x, c.y, 0.005)) + d * (r0 + 0.05 + 0.04 * math.cos(a)))
        add_rays(mb, root, outer)
        # trailing fringe behind the upper fin (shoulder to wrist)
        root, outer = [], []
        for t in (0.12, 0.22, 0.32, 0.42, 0.52, 0.62, 0.72, 0.82, 0.9, 0.97):
            i = t * (len(p) - 1)
            k = min(int(i), len(p) - 2)
            q = p[k].lerp(p[k + 1], i - k)
            L = 0.05 + 0.06 * math.sin(math.pi * min(1.0, t * 1.2))
            root.append(q + Vector((s * 0.005, 0.03, 0.0)))
            outer.append(Vector((q.x + s * (0.02 + 0.03 * t), q.y + 0.03 + L, max(0.006, q.z - 0.5 * L))))
        add_rays(mb, root, outer)
        # pelvic fin fringe, lying back on the ground
        q = pelvic_path(s)
        root = [q[1].lerp(q[4], t) + Vector((0, 0.015, -0.004)) for t in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
        outer = [Vector((r.x + s * (0.015 + 0.035 * i / 5), r.y + 0.06 + 0.02 * i / 5, 0.006))
                 for i, r in enumerate(root)]
        add_rays(mb, root, outer)
    # dorsal and ventral fin folds along the tail
    top_r, top_o, bot_r, bot_o = [], [], [], []
    ys = [0.40 + 0.52 * k / 10 for k in range(11)]
    for y in ys:
        t = (y - 0.40) / 0.52
        h = 0.06 * math.sin(math.pi * min(1.0, t * 1.15) ** 0.8) + 0.012
        top_r.append(Vector((cx(y), y, CZ(y) + HT(y) * 0.8)))
        top_o.append(Vector((cx(y) + 0.004, y + 0.025, CZ(y) + HT(y) + h)))
        if y > 0.55:
            hb_ = 0.035 * math.sin(math.pi * min(1.0, (y - 0.55) / 0.37 * 1.1) ** 0.8) + 0.008
            bot_r.append(Vector((cx(y), y, CZ(y) - HB(y) * 0.8)))
            bot_o.append(Vector((cx(y) + 0.004, y + 0.02, max(0.008, CZ(y) - HB(y) - hb_))))
    add_rays(mb, top_r, top_o)
    add_rays(mb, bot_r, bot_o)


class Surface:
    def __init__(self, bm):
        self.tree = BVHTree.FromBMesh(bm)

    def hit(self, origin, direction):
        loc, normal, _i, _d = self.tree.ray_cast(Vector(origin), Vector(direction).normalized())
        return loc, normal


def eyes(mb, surf):
    for s in (-1, 1):
        loc, nrm = surf.hit((s * 0.052, EYE_Y - 0.004, 0.6), (0, 0, -1))
        if loc is None:
            continue
        look = Vector((s * 0.6, -0.3, 0.75)).normalized()
        centre = loc - look * 0.004

        def eye_col(co, n, c=centre, lk=look):
            k = (co - c).normalized().dot(lk)
            return PUPIL if k > 0.85 else (IRIS if k > 0.6 else (0.08, 0.07, 0.05))
        mb.add(nh.ellipsoid(centre, (0.017, 0.019, 0.015), subdivisions=3), eye_col)


def nostrils(mb, surf):
    for s in (-1, 1):
        loc, _n = surf.hit((s * 0.03, -0.815, 0.6), (0, 0, -1))
        if loc is not None:
            mb.add(nh.ellipsoid(loc + Vector((0, 0, 0.0005)), (0.006, 0.004, 0.003), subdivisions=2), GROOVE)


def teeth(mb, surf):
    """Small conical teeth along the upper jaw, a couple of bigger fangs near the front."""
    y = Y_TIP + 0.02
    while y < -0.58:
        for s in (-1, 1):
            z = jaw_z(y) + 0.003
            loc, nrm = surf.hit((cx(y) + s * 0.5, y, z), (-s, 0, 0))
            if loc is None:
                continue
            big = math.exp(-((y + 0.79) / 0.02) ** 2)
            L = 0.009 + 0.008 * big
            out = Vector((nrm.x, nrm.y, 0)).normalized() if Vector((nrm.x, nrm.y, 0)).length > 1e-4 else Vector((s, 0, 0))
            base = loc - out * 0.002
            mb.add(nh.tube([base, base + Vector((0, 0, -L)) + out * 0.002], [0.0032 + 0.002 * big, 0.0], sides=6), TOOTH)
        y += 0.022


# ---------------------------------------------------------------- build / preview

def build():
    body = nh.MeshBuilder()
    body.add(body_loft(), FLANK)
    lobes(body)
    fused = body.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5)
    fused = sculpt(fused)
    surf = Surface(fused)
    mb = nh.MeshBuilder()
    fin_rays(mb)
    eyes(mb, surf)
    nostrils(mb, surf)
    teeth(mb, surf)
    mb.add(fused)
    obj = mb.to_object(NAME, roughness=0.5)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"height {max(zs):.3f}  shoulder z {pectoral_path(1)[0].z:.3f}")
    return obj


def render_extra(obj, path):
    scene = bpy.context.scene
    cam = scene.camera
    target = Vector((0.0, -0.62, 0.15))
    for i, (az, el, dist) in enumerate(((35, 25, 0.9), (-60, 45, 0.9))):
        a, e = math.radians(az), math.radians(el)
        cam.location = target + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        out = Path(path)
        scene.render.filepath = str(out.with_name(f"{out.stem}_head{i}.png"))
        bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = build()
    nh.export_fbx(obj, NAME)
    if "--render" in argv:
        path = argv[argv.index("--render") + 1]
        nh.render_preview(obj, path, ground=(0.36, 0.34, 0.26), views=((35, 25), (-90, 8), (25, 62)))
        render_extra(obj, path)


if __name__ == "__main__":
    main()
