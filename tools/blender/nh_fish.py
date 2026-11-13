"""
Fish-building helpers shared by the fish species scripts (mola_mola.py,
ornate_butterflyfish.py, moorish_idol.py). Builds on nh_model.

Fish are laid out in side view: length along Y (snout at -Y, facing -Y), height
along Z (dorsal up), thickness along X. Colour functions work on side-view
coordinates, so stripes and bands read the same on both flanks.
"""

import math

import bmesh
from mathutils import Vector

import nh_model as nh


def smax(a, b, k=40.0):
    """Smooth maximum, for blending body outline parts without kinks."""
    m = max(a, b)
    return m + math.log(math.exp((a - m) * k) + math.exp((b - m) * k)) / k


def add_colored(mb, src, vcol, smooth=True):
    """Like MeshBuilder.add, but with a colour per source vertex (dict BMVert -> rgb)."""
    src.normal_update()
    vmap = {v: mb.bm.verts.new(v.co) for v in src.verts}
    for f in src.faces:
        try:
            nf = mb.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:
            continue
        nf.smooth = smooth
        for loop, sl in zip(nf.loops, f.loops):
            c = vcol[sl.vert]
            loop[mb.col] = (c[0], c[1], c[2], 1.0)
    src.free()


def surface_x(top, bot, width, y, z, ex=0.75):
    """Flank x of the body surface at side-view point (y, z)."""
    zt, zb, w = top(y), bot(y), width(y)
    hz = max(1e-6, (zt - zb) * 0.5)
    s = max(-1.0, min(1.0, (z - (zt + zb) * 0.5) / hz))
    return w * math.sqrt(1.0 - s * s) ** ex


def body(mb, top, bot, width, y0, y1, color, stations=40, ring=24, ex=0.75, close_end=True):
    """Laterally compressed body from side-view outline functions top(y), bot(y) and
    half-thickness width(y). Pointed at y0; pointed (close_end) or capped at y1.
    color(co) -> rgb."""
    bm = bmesh.new()
    rings = []
    for i in range(stations + 1):
        t = i / stations
        t = 0.65 * t + 0.35 * (0.5 - 0.5 * math.cos(math.pi * t))  # a little denser at the ends
        y = y0 + (y1 - y0) * t
        zt, zb, w = top(y), bot(y), width(y)
        zc, hz = (zt + zb) * 0.5, (zt - zb) * 0.5
        if i == 0 or (i == stations and close_end):
            rings.append([bm.verts.new((0.0, y, zc))])
            continue
        ring_verts = []
        for k in range(ring):
            a = k / ring * math.tau
            c, s = math.cos(a), math.sin(a)
            ring_verts.append(bm.verts.new((w * math.copysign(abs(c) ** ex, c), y, zc + hz * s)))
        rings.append(ring_verts)
    if not close_end:  # fan cap on the flat back end
        y = y1
        rings.append([bm.verts.new((0.0, y, (top(y) + bot(y)) * 0.5))])

    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(ring):
                bm.faces.new([a[0], b[k], b[(k + 1) % ring]])
        elif len(b) == 1:
            for k in range(ring):
                bm.faces.new([a[k], a[(k + 1) % ring], b[0]])
        else:
            for k in range(ring):
                j = (k + 1) % ring
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    vcol = {v: color(v.co) for v in bm.verts}
    add_colored(mb, bm, vcol, smooth=True)


def fin(mb, base, edge, color, rows=4, th0=0.012, th1=0.003, normal=None):
    """Thin fin slab between a base line (on the body) and an outer edge line, both
    lists of 3D points with the same count. color(u, v, co) -> rgb, u along the base
    (0..1), v from base (0) to edge (1)."""
    base = [Vector(p) for p in base]
    edge = [Vector(p) for p in edge]
    n_cols = len(base)
    if normal is None:
        n = Vector()
        for c in range(n_cols):
            along = base[min(c + 1, n_cols - 1)] - base[max(c - 1, 0)]
            n += along.cross(edge[c] - base[c])
        normal = n.normalized() if n.length > 1e-9 else Vector((1, 0, 0))
    normal = Vector(normal).normalized()

    bm = bmesh.new()
    vcol = {}
    top, bot = {}, {}
    for c in range(n_cols):
        u = c / (n_cols - 1)
        for r in range(rows + 1):
            v = r / rows
            p = base[c].lerp(edge[c], v)
            th = th0 + (th1 - th0) * v
            col = color(u, v, p)
            vt = bm.verts.new(p + normal * th * 0.5)
            vb = bm.verts.new(p - normal * th * 0.5)
            vcol[vt] = vcol[vb] = col
            top[c, r], bot[c, r] = vt, vb
    for c in range(n_cols - 1):
        for r in range(rows):
            q = [(c, r), (c + 1, r), (c + 1, r + 1), (c, r + 1)]
            for face in ([top[k] for k in q], [bot[k] for k in reversed(q)]):
                try:
                    bm.faces.new(face)
                except ValueError:
                    pass
    perim = [(c, 0) for c in range(n_cols)] + [(n_cols - 1, r) for r in range(1, rows + 1)] \
        + [(c, rows) for c in range(n_cols - 2, -1, -1)] + [(0, r) for r in range(rows - 1, 0, -1)]
    for a, b in zip(perim, perim[1:] + perim[:1]):
        try:
            bm.faces.new([top[a], top[b], bot[b], bot[a]])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    add_colored(mb, bm, vcol, smooth=False)


def mirror_x(points):
    return [(-p[0], p[1], p[2]) for p in points]


def bezier(p0, p1, p2, t):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    return p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t


def eyes(mb, y, z, x, r, ring_color, pupil=(0.03, 0.03, 0.04)):
    """A pair of eyes on the flanks at (±x, y, z): coloured ring, dark pupil, catchlight."""
    for sx in (1, -1):
        mb.add(nh.ellipsoid((sx * (x - r * 0.15), y, z), (r * 0.45, r * 1.35, r * 1.35), subdivisions=2), ring_color)
        mb.add(nh.ellipsoid((sx * (x + r * 0.1), y, z), (r * 0.5, r * 0.9, r * 0.9), subdivisions=2), pupil)
        mb.add(nh.ellipsoid((sx * (x + r * 0.5), y - r * 0.3, z + r * 0.35), (r * 0.15, r * 0.22, r * 0.22),
                            subdivisions=1), (0.95, 0.95, 0.95))


def stripe(mb, top, bot, width, centerline, half_width, color, offset=0.006, ex=0.75, inset=0.93):
    """Crisp painted stripe on both flanks: a thin strip laid just above the body surface
    along side-view `centerline` [(y, z), ...]. Diagonal stripes painted with vertex colours
    on the body grid come out jagged; this keeps them clean. Samples where the strip would
    leave the body outline (beyond `inset` of the half height) are dropped.
    color(across, along) -> rgb, across in -1..1, along in 0..1."""
    pts = [Vector((0.0, y, z)) for y, z in centerline]

    def inside(y, z):
        zt, zb = top(y), bot(y)
        hz = (zt - zb) * 0.5
        return hz > 1e-4 and abs(z - (zt + zb) * 0.5) < hz * inset

    for sx in (1, -1):
        bm = bmesh.new()
        vcol = {}
        rows = []
        for i, p in enumerate(pts):
            d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            side = Vector((0.0, -d.z, d.y))  # perpendicular within the side-view plane
            row = []
            for across in (-1.0, 0.0, 1.0):
                q = p + side * half_width * across
                if not inside(q.y, q.z):
                    row = None
                    break
                row.append((q, across))
            if row is None:
                if rows and rows[-1] is not None:
                    rows.append(None)  # gap: start a new run
                continue
            verts = []
            for q, across in row:
                v = bm.verts.new((sx * (surface_x(top, bot, width, q.y, q.z, ex) + offset), q.y, q.z))
                vcol[v] = color(across, i / max(1, len(pts) - 1))
                verts.append(v)
            rows.append(verts)
        for a, b in zip(rows, rows[1:]):
            if a is None or b is None:
                continue
            for k in range(2):
                bm.faces.new([a[k], a[k + 1], b[k + 1], b[k]])
        # face the outside of the flank
        for f in bm.faces:
            f.normal_update()
            if f.normal.x * sx < 0:
                f.normal_flip()
        add_colored(mb, bm, vcol, smooth=True)


# A dark water backdrop (dim, so it doesn't tint the colours) and views that include the high map angle
PREVIEW = dict(background=(0.04, 0.10, 0.13), views=((35, 25), (-90, 4), (30, 50)))
