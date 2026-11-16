"""
Shared builder for the dickinsoniid (proarticulate) models (dickinsonia_costata.py,
dickinsonia_tenuis.py, dickinsonia_menneri.py, yorgia_waggoneri.py).

A dickinsoniid is a flat, thin, soft-edged oval to round "quilt" lying on the microbial
mat: a central midline groove runs most of its length and the body either side of it is
divided into transverse, tube-like units (isomers) that run out to the margin. The isomers
of the two sides do not pair up: those of one side sit half a unit behind those of the
other (glide reflection). They are smallest at the front (where new ones were added) and
grow toward the back, and toward both ends they fan out round the curve of the margin.

  * build(spec): the whole animal from a Spec (outline, isomer count and size gradient,
    midline, relief, colours).
    Each side is one grid laid along its isomers: rows follow the isomer boundaries
    (a groove row then crest rows, so every isomer is a slightly raised, flat-topped
    pad), columns run from the midline groove out to the margin. An isomer row is the
    line from a point on the midline to a point on the outline; the outline points are
    spread by arclength, so the middle isomers run straight across and the end ones fan
    round the front and back. The left side's rows are shifted half an isomer against the
    right side's. The underside is a flat sole with a rounded lip round the margin.
    Colours are painted per vertex: pale crests, darker grooves and midline, a small
    random tone per isomer, a darker band and paler lip at the margin, faint mottling.
  * Asymmetric forms (Yorgia): the midline can sit off-centre (the two sides get
    different widths) and bend, the first isomers can be enlarged into a broad "head"
    zone that sweeps round the front, and the midline groove can fade out there.
  * Faces -Y (the narrow-isomer front end), about 1.6 units long (or wide). Pivot at the
    body centre (Swim style): the thickness is centred on z = 0.
"""

import bisect
import math
import random
from dataclasses import dataclass

import bmesh
from mathutils import Vector, noise

import nh_model as nh


@dataclass
class Spec:
    name: str
    half_length: float = 0.8        # Y extent of the outline (front tip at -half_length)
    half_width: float = 0.5         # X extent of the outline (each side, before asymmetry)
    width_skew: float = 0.0         # right side wider by this fraction, left narrower (Yorgia)
    front_round: float = 2.0        # superellipse exponent of the front half (2 = ellipse,
    back_round: float = 2.0         #   higher = blunter / fuller, lower = more pointed)
    front_taper: float = 0.0        # narrows the front half (fraction of half_width)
    widest: float = 0.0             # shifts the widest point back (+) or forward (-), in half lengths
    isomers: int = 36               # isomers per side
    rows_per: int = 3               # grid rows per isomer (groove + crests)
    cols: int = 9                   # grid columns from the midline to the margin
    grow: float = 1.5               # rear isomers are (1 + grow) times as wide as the front ones
    head: int = 0                   # number of enlarged anterior isomers (Yorgia "head" zone)
    head_scale: float = 1.0         # their width relative to the next isomer
    mid_front: float = 0.88         # midline starts this fraction of half_length behind the front tip
    mid_back: float = 0.82          # and ends this fraction before the back tip
    mid_offset: float = 0.0         # midline sideways offset (fraction of half_width, + = right)
    mid_bend: float = 0.0           # midline bow toward +X in the middle (fraction of half_width)
    fan: float = 1.0                # >1 spreads the outline ends more evenly (stronger fan at the ends)
    bow: float = 0.04               # isomers bow backwards in the middle of their run (fraction of length)
    sweep: float = 0.0              # head isomers' outer ends sweep back round the front (arclength fraction)
    height: float = 0.055           # dome height at the centre
    thickness: float = 0.03         # sole depth below the margin
    relief: float = 0.45            # isomer groove depth as a fraction of the local height
    groove: float = 0.55            # midline groove depth as a fraction of the local height
    groove_width: float = 0.05      # in fractions of the isomer length
    groove_fade_front: float = 0.0  # fades the midline groove out over the front (t from -1)
    seed: int = 1
    roughness: float = 0.65
    # colours
    crest: tuple = (0.86, 0.66, 0.54)
    body: tuple = (0.74, 0.53, 0.40)
    furrow: tuple = (0.42, 0.26, 0.18)
    midline: tuple = (0.36, 0.22, 0.15)
    front_tint: tuple = None        # optional tint toward the front end
    back_tint: tuple = None         # optional tint toward the back end
    margin: tuple = (0.56, 0.38, 0.27)
    lip: tuple = (0.90, 0.74, 0.62)
    sole: tuple = (0.70, 0.56, 0.46)
    isomer_tone: float = 0.07       # random brightness variation per isomer
    mottle: float = 0.06


class Dickinsoniid:
    def __init__(self, s: Spec):
        self.s = s
        self.rng = random.Random(s.seed)
        # isomer boundaries in t (-1 front .. 1 back): widths grow toward the back, the first
        # `head` isomers are enlarged
        w = []
        for n in range(s.isomers):
            f = 1.0 + s.grow * (n / max(s.isomers - 1, 1))
            w.append(f)
        for n in range(min(s.head, s.isomers)):
            w[n] = w[s.head] * s.head_scale if s.head < s.isomers else w[n]
        tot = sum(w)
        self.bounds = [-1.0]
        for x in w:
            self.bounds.append(self.bounds[-1] + 2.0 * x / tot)
        self.bounds[-1] = 1.0
        self.tone = {(side, n): 1.0 + s.isomer_tone * (self.rng.random() * 2 - 1)
                     for side in (-1, 1) for n in range(-1, s.isomers + 2)}
        self._outline_tables()

    # ------------------------------------------------------------ outline
    def outline(self, side, phi):
        """Outline point on one side (side = +1 right / -1 left); phi -pi/2 front tip .. pi/2 back tip."""
        s = self.s
        c, sn = math.cos(phi), math.sin(phi)
        n = s.front_round if sn < 0 else s.back_round
        x = abs(c) ** (2.0 / n)
        y = math.copysign(abs(sn) ** (2.0 / n), sn)
        x *= 1.0 - s.front_taper * max(0.0, -y) ** 1.5
        a = s.half_width * (1.0 + side * s.width_skew)
        yy = y * s.half_length
        # shift the widest point along the body without moving the tips
        yy += s.widest * s.half_length * 0.5 * (1.0 - y * y)
        return Vector((side * a * x, yy, 0.0))

    def _outline_tables(self):
        self.tables = {}
        for side in (-1, 1):
            phis = [-math.pi / 2 + math.pi * k / 400 for k in range(401)]
            pts = [self.outline(side, p) for p in phis]
            acc = [0.0]
            for a, b in zip(pts, pts[1:]):
                acc.append(acc[-1] + (b - a).length)
            self.tables[side] = (phis, [x / acc[-1] for x in acc])

    def outline_at(self, side, f):
        """Outline point at arclength fraction f (0 front tip .. 1 back tip)."""
        phis, acc = self.tables[side]
        f = max(0.0, min(1.0, f))
        i = max(1, min(len(acc) - 1, bisect.bisect_left(acc, f)))
        u = (f - acc[i - 1]) / max(acc[i] - acc[i - 1], 1e-9)
        return self.outline(side, phis[i - 1] + (phis[i] - phis[i - 1]) * u)

    # ------------------------------------------------------------ isomer lines
    def midline(self, t):
        s = self.s
        y = t * s.half_length * (s.mid_front if t < 0 else s.mid_back)
        x = s.half_width * (s.mid_offset + s.mid_bend * (1.0 - t * t)) * (1.0 - t ** 8)
        return Vector((x, y, 0.0))

    def end_fraction(self, t):
        """Where on the outline the isomer line from midline point t ends."""
        s = self.s
        y = self.midline(t).y
        y0 = -s.half_length * s.mid_front
        y1 = s.half_length * s.mid_back
        f = (y - y0) / (y1 - y0)
        # fan: push the ends of the outermost rows round toward the tips
        g = 2.0 * f - 1.0
        g = math.copysign(abs(g) ** (1.0 / s.fan), g)
        f = 0.5 + 0.5 * g
        # head zone: the outer ends of the head isomers sweep back round the broad front, so
        # they run across the body as crescents parallel to the front margin
        f += s.sweep * self.head_weight(t) * math.sin(math.pi * min(1.0, f * 2.0))
        return max(0.0, min(1.0, f))

    def point(self, side, t, u):
        """Point on the isomer row at t, fraction u of the way from the midline to the margin.
        Returns (point, row length, edge) - edge is how close to the margin it lies (0..1)."""
        s = self.s
        th = self.bounds[s.head] if s.head else -1.0
        if t < th:
            return self.head_point(side, t, u, th)
        a = self.midline(t)
        b = self.outline_at(side, self.end_fraction(t))
        d = b - a
        p = a + d * u
        # bow the isomer backwards in the middle of its run (and keep the ends fixed)
        p.y += s.bow * d.length * math.sin(math.pi * u) * (1.0 - abs(t) ** 3)
        return p, d.length, u

    def head_point(self, side, t, u, th):
        """Head zone: the enlarged first isomers are crescents nested inside the front margin,
        running from the midline round to the side margin. r = 1 is the front margin itself,
        r = 0 the first ordinary isomer row (a straight line from the midline to the margin)."""
        r = (th - t) / (th + 1.0)
        c = self.midline(th)
        f_end = self.end_fraction(th) * (1.0 - 0.45 * r)     # the rows end spread along the side
        o = self.outline_at(side, f_end * u ** r)               # u = 0 aims at the front tip
        p = c + (o - c) * (r + (1.0 - r) * u)
        length = (self.outline_at(side, f_end) - c).length
        return p, length, max(u, r ** 2.5)

    def sigma(self, t):
        """Continuous isomer coordinate at t (0 at the front, isomers at the back)."""
        i = max(1, min(len(self.bounds) - 1, bisect.bisect_right(self.bounds, t)))
        a, b = self.bounds[i - 1], self.bounds[i]
        return (i - 1) + (t - a) / (b - a)

    def t_of_sigma(self, sg):
        sg = max(0.0, min(float(self.s.isomers), sg))
        i = min(int(sg), self.s.isomers - 1)
        return self.bounds[i] + (self.bounds[i + 1] - self.bounds[i]) * (sg - i)

    def phase(self, side, sg):
        """(0..1 position inside the isomer, isomer index) at isomer coordinate sg on a side.
        The left side is shifted half an isomer behind the right, except in the head zone,
        where the isomers run undivided across the midline (a 1.5-isomer unit joins the two)."""
        h = self.s.head
        if side > 0 or sg < h:
            return sg % 1.0, int(math.floor(sg + 1e-6))
        if h and sg < h + 1.5:
            return (sg - h) / 1.5, h
        return (sg - 0.5) % 1.0, int(math.floor(sg - 0.5 + 1e-6))

    def head_weight(self, t):
        """1 inside the enlarged head zone, 0 behind it."""
        s = self.s
        if not s.head:
            return 0.0
        th = self.bounds[s.head]
        return 1.0 - nh.smoothstep(th - 0.05, th + 0.25, t)

    # ------------------------------------------------------------ surface
    def us(self):
        """Columns from the midline (0) to the margin (1), denser at both ends."""
        s = self.s
        g = s.groove_width
        inner = [0.0, g * 0.55, g * 1.4]
        n = s.cols - 4
        mid = [g * 1.4 + (0.93 - g * 1.4) * (k / n) ** 0.9 for k in range(1, n + 1)]
        return inner + mid + [0.975, 1.0]

    def height(self, side, t, u, e, length, phase):
        s = self.s
        lmax = self.lmax
        lenf = min(1.0, length / lmax) ** 0.6
        te = max(t, self.bounds[s.head]) if s.head else t     # the head zone is bounded by the margin
        endf = (1.0 - abs(te) ** 6) ** 0.5
        prof = (1.0 - min(1.0, e) ** 2.2) ** 0.55
        h = s.height * lenf * (0.35 + 0.65 * endf) * prof
        gfade = 1.0
        if s.groove_fade_front > 0:
            gfade = nh.smoothstep(-1.0, -1.0 + s.groove_fade_front, t)
        h *= 1.0 - s.groove * gfade * math.exp(-(u / (s.groove_width * 0.8)) ** 2)
        # isomer pads: the groove row sinks, the crest rows stay up
        g = 0.5 + 0.5 * math.cos(phase * math.tau)
        g = g ** 3
        h -= s.relief * (1.0 + 0.8 * self.head_weight(t)) * g * s.height * lenf * (0.35 + 0.65 * prof) * nh.smoothstep(0.0, 0.22, u)
        return h

    def color(self, side, t, u, e, phase, isomer, co):
        s = self.s
        pad = 0.5 - 0.5 * math.cos(phase * math.tau)          # 0 in the groove, 1 mid-isomer
        c = nh.lerp(s.furrow, s.body, nh.smoothstep(0.0, 0.45, pad))
        c = nh.lerp(c, s.crest, nh.smoothstep(0.45, 1.0, pad) * (1.0 - 0.5 * nh.smoothstep(0.6, 1.0, e)))
        if s.front_tint is not None:
            c = nh.lerp(c, s.front_tint, max(nh.smoothstep(-0.3, -1.0, t) * 0.6, self.head_weight(t) * 0.75))
        if s.back_tint is not None:
            c = nh.lerp(c, s.back_tint, nh.smoothstep(0.2, 1.0, t) * 0.5)
        k = self.tone[(side, isomer)]
        c = tuple(x * k for x in c)
        gfade = 1.0
        if s.groove_fade_front > 0:
            gfade = nh.smoothstep(-1.0, -1.0 + s.groove_fade_front, t)
        c = nh.lerp(c, s.midline, math.exp(-(u / (s.groove_width * 0.9)) ** 2) * 0.85 * gfade)
        c = nh.lerp(c, s.margin, nh.smoothstep(0.78, 0.95, e) * 0.55)
        c = nh.lerp(c, s.lip, nh.smoothstep(0.95, 1.0, e) * 0.7)
        m = 1.0 + s.mottle * noise.noise(Vector((co.x * 7.0, co.y * 7.0, side * 2.0 + 0.3)))
        return tuple(min(1.0, max(0.0, x * m)) for x in c)

    def half(self, side):
        """One side of the body as a closed shell. Returns (bm, {vert: rgb})."""
        s = self.s
        bm = bmesh.new()
        vcol = {}
        off = 0.0 if side > 0 else 0.5                         # glide reflection
        h = s.head if side < 0 else 0
        R = s.rows_per
        sgs = {k / R for k in range(h * R + 1)}                # head isomers: undivided, matched
        if h:                                                  # then one 1.5-isomer transition
            sgs |= {h + 1.5 * k / R for k in range(R + 1)}
        sgs |= {k / R + off for k in range(-R, (s.isomers + 1) * R + 1) if k / R + off >= h + (1.5 if h else 0)}
        sgs = sorted({max(0.0, min(float(s.isomers), x)) for x in sgs})
        cols = self.us()
        zb = -s.thickness
        grid, soles, mids = [], [], []
        for sg in sgs:
            t = self.t_of_sigma(sg)
            phase, iso = self.phase(side, sg)
            if sg >= s.isomers - 1e-6 or sg <= 1e-6:
                phase = 0.0
            row = []
            for u in cols:
                p, length, e = self.point(side, t, u)
                if u >= 1.0:
                    z = zb * 0.35
                else:
                    z = self.height(side, t, u, e, length, phase)
                v = bm.verts.new((p.x, p.y, z))
                vcol[v] = self.color(side, t, u, e, phase, iso, v.co)
                row.append(v)
            # rounded lip, then the flat sole back to the midline
            p, _, _ = self.point(side, t, 0.985)
            vs = bm.verts.new((p.x, p.y, zb))
            p0, _, _ = self.point(side, t, 0.0)
            vm = bm.verts.new((p0.x, p0.y, zb))
            vcol[vs] = nh.lerp(s.sole, s.lip, 0.4)
            vcol[vm] = s.sole
            grid.append(row)
            soles.append(vs)
            mids.append(vm)
        nr, nc = len(grid), len(cols)
        new = []
        for j in range(nr - 1):
            a, b = grid[j], grid[j + 1]
            for i in range(nc - 1):
                new.append(([a[i], a[i + 1], b[i + 1], b[i]], 1))
            new.append(([a[-1], soles[j], soles[j + 1], b[-1]], 0))       # lip
            new.append(([soles[j], mids[j], mids[j + 1], soles[j + 1]], -1))  # sole
            new.append(([mids[j], a[0], b[0], mids[j + 1]], 0))           # midline wall
        for row, vs, vm in ((grid[0], soles[0], mids[0]), (grid[-1], soles[-1], mids[-1])):
            new.append((row + [vs, vm], 0))                                # end caps
        for verts, want in new:
            verts = list(dict.fromkeys(verts))
            if len(verts) < 3:
                continue
            try:
                f = bm.faces.new(verts)
            except ValueError:
                continue
            f.normal_update()
            if want and f.normal.z * want < 0:
                f.normal_flip()
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
        # orient the walls with the rest of the shell
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        top = [f for f in bm.faces if f.calc_center_median().z > 0.25 * s.height]
        if top and sum(f.normal.z for f in top) < 0:
            for f in bm.faces:
                f.normal_flip()
        vcol = {v: vcol.get(v, s.sole) for v in bm.verts}
        return bm, vcol

    def build(self):
        s = self.s
        self.lmax = max(self.point(side, t / 20.0, 0.0)[1] for side in (-1, 1) for t in range(-20, 21))
        import nh_fish as nf
        mb = nh.MeshBuilder()
        for side in (-1, 1):
            bm, vcol = self.half(side)
            nf.add_colored(mb, bm, vcol)
        obj = mb.to_object(s.name, roughness=s.roughness)
        # pivot at the body centre: centre the thickness on z = 0 and the outline on x/y = 0
        xs = [v.co.x for v in obj.data.vertices]
        ys = [v.co.y for v in obj.data.vertices]
        zs = [v.co.z for v in obj.data.vertices]
        c = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))
        for v in obj.data.vertices:
            v.co -= c
        return obj


def build(s: Spec):
    return Dickinsoniid(s).build()
