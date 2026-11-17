"""
Shared building blocks for the Cretaceous species batch (scripts tagged *cre*).

Everything here builds on nh_model: lofted bodies along a spine of control rows,
tapered limbs with toes and claws, membranes and feather vanes, teeth rows, eyes,
procedural paint helpers and a fuse -> sculpt -> decimate pipeline.

Frame (as everywhere in tools/blender): Z up, the animal faces -Y, +X is its left.
"""

import math

import bpy
import bmesh
from mathutils import Vector, Matrix, noise

import nh_model as nh

EYE_DARK = (0.03, 0.02, 0.02)
CLAW = (0.13, 0.11, 0.09)
TOOTH = (0.94, 0.91, 0.80)
MOUTH = (0.50, 0.15, 0.15)


# ---------------------------------------------------------------- lofting

def loft(sections, sides=18, power=2.0, ref=Vector((0, 0, 1)), cap_start=True, cap_end=True):
    """Skin superelliptic rings along a path. sections: (center, ra, rb); ra is the half
    extent along side = fwd x ref, rb along up = side x fwd. A zero ra makes a pointed end."""
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
        r = ref if abs(fwd.dot(ref)) < 0.95 else Vector((1, 0, 0))
        side = fwd.cross(r).normalized()
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
        if len(a) == 1 and len(b) == 1:
            continue
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


def densify(sections, steps):
    """Catmull-Rom resample of loft sections (keeps zero-radius tips only at the ends)."""
    vals = [(Vector(c), a, b) for c, a, b in sections]
    out = []
    n = len(vals)
    for i in range(n - 1):
        p0, p1 = vals[max(0, i - 1)], vals[i]
        p2, p3 = vals[i + 1], vals[min(n - 1, i + 2)]
        for k in range(steps):
            t = k / steps
            t2, t3 = t * t, t * t * t

            def cr(a, b, c, d):
                return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
            if i == 0 and k == 0:
                out.append((tuple(p1[0]), p1[1], p1[2]))
                continue
            ra = max(0.002, cr(p0[1], p1[1], p2[1], p3[1]))
            rb = max(0.002, cr(p0[2], p1[2], p2[2], p3[2]))
            out.append((tuple(cr(p0[0], p1[0], p2[0], p3[0])), ra, rb))
    out.append((tuple(vals[-1][0]), vals[-1][1], vals[-1][2]))
    return out


def axis(rows, sides=22, power=2.1, steps=3, x=0.0):
    """Body along the midline from rows (y, z, half width, half height); first and last
    rows usually have zero width (tail tip, snout tip)."""
    secs = [((x, y, z), hw, hh) for y, z, hw, hh in rows]
    return loft(densify(secs, steps), sides=sides, power=power)


def limb(points, radii, sides=12, steps=3, flat=None):
    """Smooth tapered limb through points with a radius per point; flat=(sa, sb) squashes
    the section (flippers: e.g. (1.0, 0.25))."""
    fa, fb = flat if flat else (1.0, 1.0)
    secs = [(p, r * fa, r * fb) for p, r in zip(points, radii)]
    return loft(densify(secs, steps), sides=sides, power=2.0, ref=Vector((0, 0, 1)))


def cone(base, tip, r, sides=5):
    return nh.tube([Vector(base), Vector(tip)], [r, 0.0], sides=sides)


def curved_cone(base, mid, tip, r, sides=6):
    return nh.tube([Vector(base), Vector(mid), Vector(tip)], [r, r * 0.6, 0.0], sides=sides)


def mirror(p):
    return (-p[0], p[1], p[2])


def ribbon(pairs, thickness=0.008, normal_hint=Vector((0, 0, 1))):
    """Thin closed strip between pairs of points [(a0, b0), (a1, b1), ...] (wing vanes,
    fins, feathers). Thickness tapers to 30% toward the b side."""
    bm = bmesh.new()
    top, bot = [], []
    for i, (a, b) in enumerate(pairs):
        a, b = Vector(a), Vector(b)
        j = min(i + 1, len(pairs) - 1)
        k = max(i - 1, 0)
        along = (Vector(pairs[j][0]) - Vector(pairs[k][0]))
        across = b - a
        n = along.cross(across)
        if n.length < 1e-9:
            n = normal_hint.copy()
        n.normalize()
        if n.dot(normal_hint) < 0:
            n = -n
        ra, rb = thickness * 0.5, thickness * 0.15
        top.append((bm.verts.new(a + n * ra), bm.verts.new(b + n * rb)))
        bot.append((bm.verts.new(a - n * ra), bm.verts.new(b - n * rb)))
    m = len(pairs)
    for i in range(m - 1):
        bm.faces.new([top[i][0], top[i + 1][0], top[i + 1][1], top[i][1]])
        bm.faces.new([bot[i][0], bot[i][1], bot[i + 1][1], bot[i + 1][0]])
        bm.faces.new([top[i][0], bot[i][0], bot[i + 1][0], top[i + 1][0]])
        bm.faces.new([top[i][1], top[i + 1][1], bot[i + 1][1], bot[i][1]])
    bm.faces.new([top[0][0], top[0][1], bot[0][1], bot[0][0]])
    bm.faces.new([top[-1][0], bot[-1][0], bot[-1][1], top[-1][1]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def membrane(lead, trail, nu=None, nv=8, thickness=0.012, billow=0.0, normal_hint=Vector((0, 0, 1))):
    """Wing/fin membrane between a leading-edge polyline and a trailing-edge polyline with the
    same number of points (resampled across in nv steps). billow sags the middle along -hint."""
    pairs_rows = []
    lead = [Vector(p) for p in lead]
    trail = [Vector(p) for p in trail]
    rows = []
    for a, b in zip(lead, trail):
        row = []
        for j in range(nv + 1):
            v = j / nv
            p = a.lerp(b, v) - normal_hint * billow * math.sin(math.pi * v)
            row.append(p)
        rows.append(row)
    bm = bmesh.new()
    n_u = len(rows)
    grid = {}
    for i in range(n_u):
        for j in range(nv + 1):
            p = rows[i][j]
            # local normal
            du = rows[min(i + 1, n_u - 1)][j] - rows[max(i - 1, 0)][j]
            dv = rows[i][min(j + 1, nv)] - rows[i][max(j - 1, 0)]
            nrm = du.cross(dv)
            if nrm.length < 1e-9:
                nrm = normal_hint.copy()
            nrm.normalize()
            if nrm.dot(normal_hint) < 0:
                nrm = -nrm
            t = thickness * (0.5 - 0.35 * j / nv)
            grid["t", i, j] = bm.verts.new(p + nrm * t)
            grid["b", i, j] = bm.verts.new(p - nrm * t)
    for i in range(n_u - 1):
        for j in range(nv):
            bm.faces.new([grid["t", i, j], grid["t", i + 1, j], grid["t", i + 1, j + 1], grid["t", i, j + 1]])
            bm.faces.new([grid["b", i, j], grid["b", i, j + 1], grid["b", i + 1, j + 1], grid["b", i + 1, j]])
    rim = ([(i, 0) for i in range(n_u)] + [(n_u - 1, j) for j in range(1, nv + 1)]
           + [(i, nv) for i in range(n_u - 2, -1, -1)] + [(0, j) for j in range(nv - 1, 0, -1)])
    for a, b in zip(rim, rim[1:] + rim[:1]):
        try:
            bm.faces.new([grid["t", a[0], a[1]], grid["b", a[0], a[1]], grid["b", b[0], b[1]], grid["t", b[0], b[1]]])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bezier_pts(p0, p1, p2, n):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2 for t in (i / (n - 1) for i in range(n))]


def polyline(points, n):
    """Resample a polyline to n points evenly by length."""
    pts = [Vector(p) for p in points]
    seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seg)
    out = []
    for k in range(n):
        d = total * k / (n - 1)
        i = 0
        while i < len(seg) - 1 and d > seg[i]:
            d -= seg[i]
            i += 1
        t = 0.0 if seg[i] == 0 else min(1.0, d / seg[i])
        out.append(pts[i].lerp(pts[i + 1], t))
    return out


# ---------------------------------------------------------------- feet, claws, teeth, eyes

def foot(ball, toes=3, length=0.1, r=0.02, spread=0.45, claw=0.03, side=1, ground=None,
         direction=(0, -1, 0), hallux=False, sickle=0.0, free=False):
    """Toes radiating forward from `ball` (they reach the ground at z = ground, default
    r * 0.8). Returns (fused_parts, claw_cones). sickle > 0 lifts the 2nd (inner) toe off the
    ground with a big hooked claw of that length (dromaeosaurs)."""
    ball = Vector(ball)
    gz = r * 0.8 if ground is None else ground
    fwd = Vector(direction).normalized()
    parts, claws = [], []
    angles = [0.0] if toes == 1 else [(-spread + 2 * spread * k / (toes - 1)) for k in range(toes)]
    for k, ang in enumerate(angles):
        d = Matrix.Rotation(-ang * side, 3, "Z") @ fwd
        mid = abs(ang) < 1e-6 or toes == 2
        ln = length * (1.0 if mid else 0.8)
        inner = (ang * side) < -1e-6 if toes > 1 else False
        if sickle > 0 and toes >= 3 and k == toes - 1:
            # the inner toe is held up, claw raised
            p1 = ball + d * ln * 0.35 + Vector((0, 0, r * 1.6))
            parts.append(nh.tube([ball, p1], [r, r * 0.8], sides=8))
            claws.append(curved_cone(p1, p1 + d * sickle * 0.6 + Vector((0, 0, sickle * 0.35)),
                                     p1 + d * sickle + Vector((0, 0, -sickle * 0.1)), r * 0.75, sides=6))
            continue
        if free:
            p1 = ball + d * ln * 0.5
            p2 = ball + d * ln
        else:
            p1 = Vector((ball.x, ball.y, gz)) + d * ln * 0.5
            p2 = Vector((ball.x, ball.y, gz * 0.9)) + d * ln
        parts.append(nh.tube([ball, p1, p2], [r * 1.05, r * 0.85, r * 0.6], sides=8))
        if claw > 0:
            cd = d if free else d + Vector((0, 0, -0.3))
            claws.append(curved_cone(p2 - d * r * 0.3, p2 + cd * claw * 0.6, p2 + cd * claw + Vector((0, 0, -claw * 0.35)), r * 0.6, sides=6))
    if hallux:
        d = Vector((-fwd.x, -fwd.y, 0))
        p = Vector((ball.x, ball.y, gz)) + d * length * 0.4
        parts.append(nh.tube([ball, p], [r * 0.8, r * 0.5], sides=6))
    return parts, claws


def teeth_row(mb, pts, length, r, down=True, color=TOOTH, rot=None):
    """Conical teeth at the given points, pointing down (upper jaw) or up."""
    s = -1 if down else 1
    for p in pts:
        p = Vector(p)
        tip = p + Vector((0, -length * 0.15, s * length))
        if rot is not None:
            p, tip = rot @ p, rot @ tip
        mb.add(cone(p, tip, r, sides=5), color, smooth=False)


def eye(mb, pos, r, iris=(0.85, 0.55, 0.12), pupil=EYE_DARK, ring=None):
    """Eye on both sides; pos is the right/+x one."""
    pos = Vector(pos)
    for sx in (1, -1):
        c = Vector((sx * pos.x, pos.y, pos.z))
        if ring is not None:
            mb.add(nh.ellipsoid(c + Vector((-sx * r * 0.15, 0, 0)), (r * 1.15, r * 1.3, r * 1.15), subdivisions=2), ring)
        mb.add(nh.ellipsoid(c, (r * 0.75, r, r), subdivisions=2), iris)
        mb.add(nh.ellipsoid(c + Vector((sx * r * 0.55, -r * 0.2, 0)), (r * 0.3, r * 0.45, r * 0.6), subdivisions=1), pupil)


# ---------------------------------------------------------------- paint helpers

def fbm(p, octaves=3):
    s, a, f = 0.0, 0.5, 1.0
    for _ in range(octaves):
        s += a * noise.noise(p * f)
        a *= 0.5
        f *= 2.0
    return s


def countershade(n, belly, flank, back, lo=-0.55, mid=-0.05, hi=0.75):
    c = nh.lerp(belly, flank, nh.smoothstep(lo, mid, n.z))
    return nh.lerp(c, back, nh.smoothstep(0.05, hi, n.z))


def mottle(c, co, amount=0.12, scale=14.0):
    m = noise.noise(Vector(co) * scale)
    return tuple(max(0.0, min(1.0, v * (1.0 + amount * m))) for v in c)


def stripes(co, freq, phase=0.0, sharp=(0.55, 0.85), warp=0.0):
    s = 0.5 + 0.5 * math.sin(co.y * freq + phase + warp * noise.noise(Vector(co) * 3.0))
    return nh.smoothstep(sharp[0], sharp[1], s)


def spots(co, scale, thresh=0.25):
    """1 inside spots (cellular noise)."""
    return 1.0 - nh.smoothstep(thresh * 0.6, thresh, noise.cell(Vector(co) * scale))


# ---------------------------------------------------------------- pipeline

def sculpt(bm, fn):
    bm.normal_update()
    offs = [(v, v.normal.copy() * fn(v.co, v.normal)) for v in bm.verts]
    for v, o in offs:
        v.co += o
    bm.normal_update()
    return bm


def scales_disp(amount=0.0015, scale=40.0):
    def fn(co, n):
        return amount * (1.0 - nh.smoothstep(0.0, 0.5, noise.cell(co * scale)))
    return fn


def fuzz_disp(amount=0.003, scale=60.0):
    def fn(co, n):
        return amount * noise.noise(co * scale)
    return fn


def decimate(bm, max_tris):
    mesh = bpy.data.meshes.new("_dec")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("_dec", mesh)
    bpy.context.scene.collection.objects.link(obj)
    n = sum(len(p.vertices) - 2 for p in mesh.polygons)
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.decimate_type = "COLLAPSE"
    mod.ratio = min(1.0, max_tris / max(n, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    out = bmesh.new()
    out.from_mesh(obj.evaluated_get(dg).to_mesh())
    obj.evaluated_get(dg).to_mesh_clear()
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    return out


def fuse(parts, voxel=0.012, smooth=5, max_tris=12000, disp=None):
    """parts: list of bmeshes (or (bm, color)). Returns one fused, sculpted, decimated bmesh."""
    mb = nh.MeshBuilder()
    for p in parts:
        if isinstance(p, tuple):
            mb.add(p[0], p[1])
        else:
            mb.add(p, (0.5, 0.5, 0.5))
    out = mb.fuse(voxel=voxel, smooth=smooth, smooth_factor=0.5)
    if disp is not None:
        sculpt(out, disp)
    return decimate(out, max_tris)


def centre(obj):
    corners = [Vector(c) for c in obj.bound_box]
    c = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= c


def bounds_report(obj):
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    print(f"  bounds x {min(xs):.2f}..{max(xs):.2f}  y {min(ys):.2f}..{max(ys):.2f}  z {min(zs):.2f}..{max(zs):.2f}")
