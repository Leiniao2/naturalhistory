"""
Shared helpers for the Cambroctoconus models (cambroctoconus_orientalis.py,
cambroctoconus_kyrgyzstanicus.py): an octagonal, cup-shaped calcareous corallite built as one
closed ring-stack along a (gently curved) axis, with eight-fold septa inside the calyx.

The cross-section is a regular octagon (corners at multiples of 45 degrees) whose faces can be
made concave, so the corners stand out as longitudinal ribs (angulations). Going up the axis:
the outer wall (with faint transverse growth wrinkles), a rounded rim, then the inner wall of
the calyx following the axis back down to a dark floor. Septa are thin plates projecting inward
from the corners of the calyx: "paired" (two lamellae per corner, rim to floor, as in
C. orientalis), or "spines" (one short, broad ridge per corner near the rim only).
All colour is painted per vertex from the palette passed in.
"""

import math

import bmesh
from mathutils import Vector, noise

import nh_model as nh

SIDES = 24           # around each cup: 3 per octagon face, corners on every 3rd vertex
UP = Vector((0, 0, 1))
WARP = Vector((3.7, 8.1, 1.9))


def bezier(p0, p1, p2, n):
    return [p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t for t in (i / (n - 1) for i in range(n))]


def frames_along(pts):
    """Parallel-transported (point, forward, side, up) frames along a polyline."""
    out, prev = [], None
    for i, p in enumerate(pts):
        fwd = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        if prev is None:
            ref = Vector((1, 0, 0)) if abs(fwd.x) < 0.9 else Vector((0, 1, 0))
            side = fwd.cross(ref).normalized()
        else:
            side = (prev - fwd * prev.dot(fwd)).normalized()
        prev = side
        out.append((p, fwd, side, side.cross(fwd).normalized()))
    return out


def octagon(a, concave=0.0, rib=0.0):
    """Radial multiplier of an octagon with corners at k*45 deg. concave dishes the faces,
    rib pushes the corners out a little (sharper longitudinal angulations)."""
    phi = a % (math.pi / 4)
    r = math.cos(math.pi / 8) / math.cos(phi - math.pi / 8)
    r *= 1.0 - concave * math.sin(phi * 4)
    if phi < 1e-4 or phi > math.pi / 4 - 1e-4:
        r *= 1.0 + rib
    return r


def cup(pts, radii, pal, concave=0.04, rib=0.0, wall=0.12, depth=0.55, septa="paired",
        septum_len=0.42, rot=0.0, seed=0.0):
    """One corallite. pts/radii: axis polyline (base -> rim) and outer radius per point.
    pal: dict with WALL, WALL_DARK, RIM, CALYX, SEPTUM, PORE.
    depth: calyx depth as a fraction of the axis length. Returns (bm with "Col", top frame, rim r)."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    fr = frames_along(pts)
    vcol, rows = {}, []
    warp = WARP + Vector((seed, seed * 0.7, seed * 1.3))

    def ring(f, r, offset, colfn):
        p, fwd, side, up = f
        vs = []
        for k in range(SIDES):
            a = k / SIDES * math.tau
            m = octagon(a, concave, rib)
            v = bm.verts.new(p + fwd * offset + (side * math.cos(a + rot) + up * math.sin(a + rot)) * r * m)
            vcol[v] = colfn(k, v.co)
            vs.append(v)
        rows.append(vs)

    def wall_col(t, wrinkle):
        def fn(k, co):
            c = nh.lerp(pal["WALL"], pal["WALL_DARK"], 0.45 * max(0.0, wrinkle) + 0.5 * (1 - t) ** 3)
            if k % 3 == 0:  # corners catch the light a little more
                c = nh.lerp(c, pal["RIM"], 0.3)
            # mottled pores of the perforate wall
            pore = nh.smoothstep(0.35, 0.6, noise.noise(co * 40 + warp))
            return nh.lerp(c, pal["PORE"], 0.45 * pore * nh.smoothstep(0.05, 0.25, t))
        return fn

    n = len(pts)
    lengths = [0.0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    total = lengths[-1]
    for i in range(n):
        t = i / (n - 1)
        wrinkle = (1.0 if i % 2 else -1.0) if 1 <= i <= n - 2 else 0.0
        r = radii[i] * (1 + 0.035 * wrinkle * nh.smoothstep(0.1, 0.3, t))
        ring(fr[i], r, 0.0, wall_col(t, wrinkle))
    top, rt = fr[-1], radii[-1]

    def r_at_depth(d):
        """Outer radius a distance d below the rim (along the axis)."""
        s = max(0.0, total - d)
        for i in range(n - 1):
            if lengths[i + 1] >= s:
                u = (s - lengths[i]) / max(1e-9, lengths[i + 1] - lengths[i])
                return radii[i] + (radii[i + 1] - radii[i]) * u
        return radii[-1]

    def frame_at(d):
        """Axis frame a distance d below the rim (d < 0: above the rim plane)."""
        if d <= 0:
            p, fwd, side, up = top
            return (p - fwd * d, fwd, side, up)
        s = max(0.0, total - d)
        for i in range(n - 1):
            if lengths[i + 1] >= s:
                u = (s - lengths[i]) / max(1e-9, lengths[i + 1] - lengths[i])
                fa, fb = fr[i], fr[i + 1]
                return (fa[0].lerp(fb[0], u),) + tuple(fa[k].lerp(fb[k], u).normalized() for k in (1, 2, 3))
        return fr[0]

    lip = rt * wall * 0.5
    ring(top, rt * 0.985, lip * 0.6, lambda k, co: pal["RIM"])
    ring(top, rt * (1 - wall * 0.55), lip, lambda k, co: pal["RIM"])
    ring(top, rt * (1 - wall), lip * 0.4, lambda k, co: pal["RIM"])
    d_cal = total * depth
    calyx_rows = ((0.25, 0.25), (0.65, 0.65), (1.0, 0.95))
    for fd, dark in calyx_rows:
        d = d_cal * fd
        ring(frame_at(d), r_at_depth(d) * (1 - wall * (1 + 0.6 * fd)), 0.0,
             lambda k, co, dk=dark: nh.lerp(pal["SEPTUM"], pal["CALYX"], dk))
    floor = bm.verts.new(frame_at(d_cal * 1.04)[0])
    vcol[floor] = pal["CALYX"]
    for a, b in zip(rows, rows[1:]):
        for k in range(SIDES):
            j = (k + 1) % SIDES
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(rows[0])))
    for k in range(SIDES):
        bm.faces.new([rows[-1][k], rows[-1][(k + 1) % SIDES], floor])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        for lp in f.loops:
            c = vcol[lp.vert]
            lp[col] = (c[0], c[1], c[2], 1.0)

    out = [(bm, None)]
    inner_r = lambda d: r_at_depth(d) * (1 - wall * (1 + 0.6 * min(1.0, d / d_cal)))  # noqa: E731
    if septa == "paired":
        for k in range(8):
            for s in (-1, 1):
                out.append((septum(frame_at, rot + k * math.pi / 4 + s * 0.045, inner_r, lip * 0.2,
                                   d_cal * 0.98, septum_len, rt * 0.04, pal), None))
    elif septa == "spines":
        for k in range(8):
            out.append((septum(frame_at, rot + k * math.pi / 4, inner_r, -d_cal * 0.06,
                               d_cal * 0.45, septum_len, rt * 0.07, pal, taper=True), None))
    merged = out[0][0]
    for extra, _ in out[1:]:
        _append(merged, extra)
    return merged, top, rt


def septum(frame_at, a, inner_r, z_top, d_bot, length, thick, pal, taper=False):
    """Thin radial plate in the calyx at angle a (axis-frame coords), from z_top (offset above the
    rim plane, may be negative) down to depth d_bot; reaches `length` of the local inner radius
    toward the axis (the inner edge is shorter at the bottom if taper)."""
    p, fwd, side, up = frame_at(-z_top)
    tng = fwd.cross(side * math.cos(a) + up * math.sin(a)).normalized()
    bm = bmesh.new()
    colr = bm.loops.layers.color.new("Col")
    corners = []
    for depth, frac in ((-z_top, length), (d_bot, length * (0.45 if taper else 0.85))):
        r = inner_r(max(0.0, depth))
        o, f_, s_, u_ = frame_at(depth)
        d = s_ * math.cos(a) + u_ * math.sin(a)
        corners.append((o + d * r * 1.04, o + d * r * (1 - frac)))
    (a0, a1), (b0, b1) = corners
    quad = [a0, a1, b1, b0]
    vs = [bm.verts.new(q + tng * thick * s) for s in (-0.5, 0.5) for q in quad]
    for f in ([0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]):
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        for lp in f.loops:
            # pale at the top edge, darker deep in the calyx
            t = (p - lp.vert.co).dot(fwd) / max(1e-6, d_bot + z_top)
            c = nh.lerp(pal["SEPTUM"], pal["CALYX"], 0.6 * nh.smoothstep(0.2, 1.0, t))
            lp[colr] = (c[0], c[1], c[2], 1.0)
    return bm


def _append(dst, src):
    """Copies src (with its "Col" layer) into dst and frees src."""
    dc = dst.loops.layers.color["Col"]
    sc = src.loops.layers.color["Col"]
    vmap = {v: dst.verts.new(v.co) for v in src.verts}
    for f in src.faces:
        nf = dst.faces.new([vmap[v] for v in f.verts])
        for l, sl in zip(nf.loops, f.loops):
            l[dc] = sl[sc]
    src.free()


def holdfast(center, radius, pal, height=0.06, seed=0.0):
    """Solid, expanded attachment foot: a flattened, lumpy lens."""
    s = Vector((seed, seed * 1.7, 2.0))
    bm = nh.ellipsoid(center, (radius, radius * 0.92, height), subdivisions=2,
                      deform=lambda n: 1.0 + 0.12 * noise.noise(n * 2.2 + s))

    def color(co, n):
        return nh.lerp(pal["WALL_DARK"], pal["HOLDFAST"], 0.5 + 0.5 * noise.noise(co * 14 + s))
    return bm, color


def axis_point(pts, radii, t):
    """Point and radius at fraction t (by index) along a cup's axis polyline."""
    m = len(pts) - 1
    i = min(m - 1, int(t * m))
    u = t * m - i
    return pts[i].lerp(pts[i + 1], u), radii[i] + (radii[i + 1] - radii[i]) * u
