"""
Shared builders for the early (Silurian-Devonian) bony fishes: guiyu_oneiros.py,
psarolepis_romeri.py, andreolepis_hedei.py, eosteus_chongqingensis.py,
tungsenia_paradoxa.py (the galeaspid yongdongaspis_littoralis.py uses the scale
shell too). Builds on nh_model and nh_fish.

Fish are laid out in side view like nh_fish: length along Y (snout at -Y, facing
-Y), height along Z, thickness along X. A body is described by a Profile table of
(y, half-width, top half-height, bottom half-height, centre z) rows; the centre line
may rise toward the back for a heterocercal tail (the scaled body axis turning up
into the upper caudal lobe).

Pieces:
  * head_shell(): smooth loft of the bony head, painted by a colour function
    (dermal plates, mouth line, cosmine pores...), slightly proud of the trunk so its
    back edge reads as the gill cover.
  * scale_shell(): the trunk as a staggered lattice of separate rhombic (diamond)
    scales, each with a shiny front corner and a slightly lifted rear corner, over a
    dark underlay that shows through as the grooves between scale rows. This keeps
    the rhombic ganoid/cosmoid squamation crisp at a low triangle count.
  * median_fin(), paired_fin(), caudal_web(): thin fin slabs (nh_fish.fin) with
    optional painted fin rays; lobe() for the fleshy, scaled fin lobes of
    lobe-finned fishes; spine() for ridged fin spines; eye().

Usage: imported by the species scripts, not run on its own.
"""

import math

import bmesh
from mathutils import Vector, noise

import nh_model as nh
import nh_fish as fish


# ---------------------------------------------------------------- profile

def pchip(table, y):
    """Monotone cubic interpolation through (y, value) control points (no overshoot)."""
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


class Profile:
    """Body outline from rows (y, half_w, top_h, bot_h, centre_z). power: superellipse
    exponent of the cross-section (2 = ellipse, higher = boxier), number or fn(y)."""

    def __init__(self, rows, power=2.2):
        self.rows = rows
        self.y0, self.y1 = rows[0][0], rows[-1][0]
        self._c = [[(r[0], r[k]) for r in rows] for k in range(5)]
        self.power = power

    def W(self, y): return pchip(self._c[1], y)
    def HT(self, y): return pchip(self._c[2], y)
    def HB(self, y): return pchip(self._c[3], y)
    def CZ(self, y): return pchip(self._c[4], y)

    def n(self, y):
        return self.power(y) if callable(self.power) else self.power

    def point(self, y, a, grow=0.0):
        """Surface point at angle a (0 = +x flank, pi/2 = top). grow: radial offset."""
        c, s = math.cos(a), math.sin(a)
        ex = 2.0 / self.n(y)
        w = self.W(y) + grow
        h = (self.HT(y) if s >= 0 else self.HB(y)) + grow
        return Vector((w * math.copysign(abs(c) ** ex, c), y, self.CZ(y) + h * math.copysign(abs(s) ** ex, s)))

    def top(self, y): return self.CZ(y) + self.HT(y)
    def bot(self, y): return self.CZ(y) - self.HB(y)

    def rel(self, co):
        """(u across -1..1, v up -1..1) of a point relative to the outline at its y."""
        y = max(min(co.y, self.y1), self.y0)
        u = co.x / max(self.W(y), 1e-4)
        h = self.HT(y) if co.z >= self.CZ(y) else self.HB(y)
        return u, (co.z - self.CZ(y)) / max(h, 1e-4)


# ---------------------------------------------------------------- shells

def loft(prof, y0, y1, ny, na, grow=0.0, cap0=True, cap1=True, ease=True):
    """Lofted shell along the profile, pointed (cap) or open at either end."""
    bm = bmesh.new()
    if ease:
        ys = [y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(i / (ny - 1) * math.pi)) for i in range(ny)]
    else:
        ys = [y0 + (y1 - y0) * i / (ny - 1) for i in range(ny)]
    rings = []
    for i, y in enumerate(ys):
        ring = [prof.point(y, k / na * math.tau, grow) for k in range(na)]
        if (i == 0 and cap0) or (i == ny - 1 and cap1):
            rings.append([bm.verts.new(sum(ring, Vector()) / na)])
        else:
            rings.append([bm.verts.new(p) for p in ring])
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


def head_shell(mb, prof, y_back, color, ny=22, na=30, grow=0.004):
    """Smooth bony head from the snout tip to y_back (open behind), color(co, n) -> rgb."""
    mb.add(loft(prof, prof.y0, y_back, ny, na, grow=grow, cap0=True, cap1=False), color)


def scale_shell(mb, prof, y0, y1, stations, around, paint, lift=0.004, shine=0.22, shade=0.30,
                underlay=(0.08, 0.07, 0.06), fade_y=None):
    """Trunk covered in separate rhombic scales on a staggered lattice.

    paint(centre, u, v) -> base rgb of the scale centred at `centre` (u, v from
    Profile.rel). Each diamond: front corner lighter (shine), rear corner darker and
    lifted (`lift`, scales overlap front-to-back). fade_y: optional (ya, yb) range over
    which the lift fades to 0 (e.g. on the thin tail axis)."""
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    dy = (y1 - y0) / stations

    def pos(i, c, raise_=0.0):
        y = y0 + dy * max(0, min(stations, i))
        a = c / around * math.tau
        return prof.point(y, a, raise_)

    for i in range(0, stations + 1):
        for k in range(around):
            c = k + 0.5 * ((i + 1) % 2)
            yc = y0 + dy * i
            lf = lift
            if fade_y is not None:
                lf *= 1.0 - nh.smoothstep(fade_y[0], fade_y[1], yc)
            # scale size shrinks where the body is thin, so the lift does too
            lf *= min(1.0, (prof.W(yc) + prof.HT(yc)) / 0.14)
            front = pos(i - 1, c)
            back = pos(i + 1, c, lf)
            s0, s1 = pos(i, c - 0.5), pos(i, c + 0.5)
            centre = (front + back + s0 + s1) / 4
            if (front - back).length < 1e-6:
                continue
            u, v = prof.rel(centre)
            base = paint(centre, u, v)
            light = tuple(min(1.0, x * (1.0 + shine) + 0.03) for x in base)
            dark = tuple(x * (1.0 - shade) for x in base)
            vs = [bm.verts.new(p) for p in (front, s0, back, s1)]
            try:
                f = bm.faces.new(vs)
            except ValueError:
                continue
            cols = {vs[0]: light, vs[1]: base, vs[2]: dark, vs[3]: base}
            for l in f.loops:
                c3 = cols[l.vert]
                l[col] = (c3[0], c3[1], c3[2], 1.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # make sure every scale faces outward (away from the body axis)
    for f in bm.faces:
        f.normal_update()
        ctr = f.calc_center_median()
        axis = Vector((0.0, ctr.y, prof.CZ(max(min(ctr.y, prof.y1), prof.y0))))
        if f.normal.dot(ctr - axis) < 0:
            f.normal_flip()
    bmesh.ops.triangulate(bm, faces=bm.faces)
    mb.add(bm, None, smooth=False)
    # dark underlay that shows between the scale rows
    under = loft(prof, max(prof.y0, y0 - dy * 2), min(prof.y1, y1 + dy), max(8, stations // 4), max(10, around // 2),
                 grow=-0.002, cap0=False, cap1=True, ease=False)
    mb.add(under, underlay)


# ---------------------------------------------------------------- fins

def ray_cols(n_rays):
    """Column count for a fin with n_rays painted rays (one vertex column per ray and gap)."""
    return 2 * n_rays + 1


def ray_color(base_col, ray_col, edge_col, n_rays, rays=True, ray_amount=0.55, edge_amount=0.5):
    """Fin colour fn(u, v, co): base -> edge outward, with optional dark ray stripes."""
    def fn(u, v, co):
        c = nh.lerp(base_col, edge_col, edge_amount * nh.smoothstep(0.35, 1.0, v))
        if rays:
            r = 0.5 + 0.5 * math.cos(u * n_rays * math.tau)
            c = nh.lerp(c, ray_col, ray_amount * nh.smoothstep(0.55, 0.95, r) * nh.smoothstep(0.05, 0.25, v))
        return c
    return fn


def median_fin(mb, prof, y0, y1, height, color, sign=1, sweep=0.6, cols=14, rows=4, th0=0.012, th1=0.003,
               sink=0.004):
    """Dorsal (sign=1) or anal/ventral (sign=-1) fin on the midline from y0 to y1.
    height(u) -> fin height at u in 0..1; sweep: how far back the edge leans (per unit height)."""
    base, edge = [], []
    for i in range(cols):
        u = i / (cols - 1)
        y = y0 + (y1 - y0) * u
        z = prof.top(y) if sign > 0 else prof.bot(y)
        h = height(u)
        base.append((0.0, y, z - sign * sink))
        edge.append((0.0, y + h * sweep, z + sign * h))
    fish.fin(mb, base, edge, color, rows=rows, th0=th0, th1=th1, normal=(1, 0, 0))


def paired_fin(mb, prof, sign, y0, y1, angle, length, out, down, back, color, cols=10, rows=4,
               th0=0.010, th1=0.003, sink=0.004):
    """Pectoral/pelvic fin: base along the flank at body angle `angle` (radians, 0 =
    flank, negative = lower) from y0 to y1; the edge goes out/down/back by length(u)."""
    d = Vector((sign * out, back, -down)).normalized()
    base, edge = [], []
    for i in range(cols):
        u = i / (cols - 1)
        y = y0 + (y1 - y0) * u
        p = prof.point(y, angle, -sink)
        p.x *= sign
        base.append(p)
        edge.append(p + d * length(u))
    fish.fin(mb, base, edge, color, rows=rows, th0=th0, th1=th1)


def caudal_web(mb, axis_pts, edge_pts, color, rows=5, th0=0.010, th1=0.003):
    """Caudal fin web between points along the tail axis and the lobe edge."""
    fish.fin(mb, axis_pts, edge_pts, color, rows=rows, th0=th0, th1=th1, normal=(1, 0, 0))


def lobe(mb, root, tip, r0, paint, sides=10, flat=0.6, up=(0, 0, 1)):
    """Fleshy, scaled fin lobe from root to tip: a tapering tube, flattened (`flat`)
    across the fin plane. paint(t along, angle) -> rgb, drawn as staggered scale bands."""
    root, tip = Vector(root), Vector(tip)
    pts = [root.lerp(tip, t) for t in (0.0, 0.25, 0.5, 0.75, 1.0)]
    radii = [r0, r0 * 0.92, r0 * 0.75, r0 * 0.5, 0.0]
    bm = nh.tube(pts, radii, sides=sides, scale_xy=(1.0, flat))
    length = (tip - root).length

    def col(co, n):
        t = max(0.0, min(1.0, (co - root).dot(tip - root) / max(length ** 2, 1e-9)))
        return paint(t, co)
    mb.add(bm, col)


def lobe_fringe(mb, root, tip, toward_trail, width_lead, width_trail, color, cols=9, rows=2, lead_color=None):
    """Fin web fringing a lobe: a narrow leading strip and a broad trailing one in the
    fin plane. toward_trail: rough direction of the trailing edge (made perpendicular to
    the lobe here). The trailing web uses `cols` columns (see ray_cols), the leading one 5."""
    root, tip = Vector(root), Vector(tip)
    along = (tip - root).normalized()
    t = Vector(toward_trail)
    side = (t - along * t.dot(along)).normalized()
    for sgn, wfn, n, r, colr in ((-1, width_lead, 5, 1, lead_color or color), (1, width_trail, cols, rows, color)):
        base, edge = [], []
        for i in range(n):
            u = 0.15 + 0.85 * i / (n - 1)
            p = root.lerp(tip, u)
            w = wfn(u)
            base.append(p)
            edge.append(p + side * sgn * w + along * w * 0.35)
        fish.fin(mb, base, edge, colr, rows=r, th0=0.008, th1=0.003)


def spine(mb, base, tip, r0, color, ridge=None, sides=6, bend=None, segments=5):
    """Ridged fin spine from base to tip (pointed). ridge: darker rgb for alternate
    longitudinal ridges. bend: optional offset vector for the spine's midpoint (curved spine)."""
    base, tip = Vector(base), Vector(tip)
    pts, radii = [], []
    for i in range(segments + 1):
        t = i / segments
        p = base.lerp(tip, t)
        if bend is not None:
            p = p + Vector(bend) * math.sin(math.pi * t)
        pts.append(p)
        radii.append(r0 * (1.0 - t) ** 0.8 if i < segments else 0.0)
    bm = nh.tube(pts, radii, sides=sides)
    ridge = ridge or tuple(c * 0.7 for c in color)
    axis = (tip - base).normalized()
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.9 else Vector((1, 0, 0))
    sx = axis.cross(ref).normalized()
    sy = sx.cross(axis)

    def col(co, n):
        q = co - base
        a = math.atan2(q.dot(sy), q.dot(sx))
        k = 0.5 + 0.5 * math.cos(a * sides * 0.5)
        return nh.lerp(color, ridge, k * 0.8)
    mb.add(bm, col, smooth=False)


def eye(mb, centre, look, r, iris=(0.55, 0.45, 0.22), pupil=(0.02, 0.02, 0.03), rim=(0.12, 0.10, 0.08),
        ring=None):
    """Eyeball at centre looking along `look`: dark pupil, iris, dark rim; optional bony ring."""
    centre, look = Vector(centre), Vector(look).normalized()

    def col(co, n, c=centre, lk=look):
        k = (co - c).normalized().dot(lk)
        return pupil if k > 0.86 else (iris if k > 0.62 else rim)
    mb.add(nh.uv_ellipsoid(tuple(centre), (r, r, r), 10, 8), col)
    # catchlight
    hl = centre + look * r * 0.9 + Vector((0, -r * 0.25, r * 0.3))
    mb.add(nh.uv_ellipsoid(tuple(hl), (r * 0.15, r * 0.15, r * 0.15), 6, 4), (0.92, 0.92, 0.9))
    if ring is not None:
        side = look.cross(Vector((0, 0, 1))).normalized()
        upv = side.cross(look).normalized()
        pts = [centre + look * r * 0.5 + (side * math.cos(a) + upv * math.sin(a)) * r * 1.02
               for a in [k / 12 * math.tau for k in range(13)]]
        mb.add(nh.tube(pts, [r * 0.16] * 13, sides=4, cap_start=False, cap_end=False), ring)


def surface_eye(mb, prof, y, a, r, look, sink=0.45, **kw):
    """Eye seated on the head surface at (y, body angle a), on both sides."""
    for s in (1, -1):
        p = prof.point(y, a)
        p.x *= s
        lk = Vector(look)
        lk.x *= s
        eye(mb, p - lk.normalized() * r * sink, lk, r, **kw)


# ---------------------------------------------------------------- paint helpers

def plates(seeds, y, phi, sy=1.0, sphi=0.12, width=0.012):
    """Suture groove 0..1 of a mirrored Voronoi layout of dermal plates.
    seeds: [(y, phi)] with phi = angle from the dorsal midline (0) toward the belly (pi)."""
    d = sorted([math.hypot((y - a) / sy, (phi - b) * sphi) for a, b in seeds]
               + [math.hypot((y - a) / sy, (phi + b) * sphi) for a, b in seeds if b > 0.04])
    if len(d) < 2:
        return 0.0
    return 1.0 - nh.smoothstep(width * 0.4, width, d[1] - d[0])


def phi_of(prof, co):
    """Angle from the dorsal midline (0) round to the belly (pi), mirrored."""
    u, v = prof.rel(co)
    return math.atan2(abs(u), v)


def mottle(co, scale=9.0, seed=0.0):
    return noise.noise(Vector((co.x * scale, co.y * scale, co.z * scale + seed)))


def countershade(v, back, flank, belly, co=None, blotch=None, blotch_amount=0.0):
    c = nh.lerp(flank, belly, nh.smoothstep(-0.15, -0.7, v))
    c = nh.lerp(c, back, nh.smoothstep(0.1, 0.75, v))
    if co is not None and blotch is not None:
        m = mottle(co, 6.0, 1.7)
        c = nh.lerp(c, blotch, blotch_amount * nh.smoothstep(0.1, 0.45, m) * nh.smoothstep(-0.3, 0.3, v))
    return c


PREVIEW = dict(background=(0.04, 0.10, 0.13), views=((35, 25), (-90, 4), (30, 55), (-150, 15)))


def mouth_line(mb, prof, y0, y1, zfn, color=(0.09, 0.06, 0.05), r=0.004, steps=9, grow=0.004):
    """Crisp dark mouth line (gape) on both sides of the head, from y0 back to y1 at
    height zfn(y): thin strips are clearer than painted lines on a coarse head mesh."""
    for s in (1, -1):
        pts = []
        for i in range(steps):
            y = y0 + (y1 - y0) * i / (steps - 1)
            z = zfn(y)
            best = min((abs(prof.point(y, a).z - z), a) for a in [-math.pi / 2 + k / 240 * math.pi for k in range(241)])[1]
            p = prof.point(y, best, grow)
            p.x *= s
            pts.append(p)
        radii = [r * 0.5] + [r] * (steps - 2) + [r * 0.3]
        mb.add(nh.tube(pts, radii, sides=4, scale_xy=(0.6, 1.0)), color)
