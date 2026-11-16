"""
Shared builder for the leech models (hirudo_nipponia.py, whitmania_pigra.py,
ozobranchus_margoi.py, haemadipsa_japonica.py).

A leech is a flattened, tapering annelid of a fixed 34 segments, each divided into
several narrow rings (annuli), with a small oral sucker around the mouth at the
narrow front end and a larger caudal sucker under the broad hind end. Eye spots sit
in an arc on the first few segments.

  * build(spec): the whole animal from a Spec (proportions, annuli, suckers, gills,
    colours and dorsal pattern).
    The body is one lofted shell (no fusing, so the annuli stay crisp): a flattened
    cross-section (domed back, flatter belly, thin lateral margin) swept along the
    long axis, every annulus a crest ring plus a slightly narrower groove ring. The
    width profile, head lobe and "neck" come from the Spec. The pattern is painted
    procedurally along the body (longitudinal stripes, rows of spots, fine lines,
    paler margins and belly), sampled with more vertices across the back than the
    belly so stripes stay sharp.
    Crisp extras: the caudal sucker disc (overlapping the tail end), the rim of the
    oral sucker under the head, eye spots, and optional finger-like gill tufts along
    the sides (Ozobranchus).
  * The body is straight along Y: on the map the shader (MapFeatureFlap.cginc,
    ApplyUndulate) bends it into a travelling wave, for swimmers and for Slither gaits.
  * Faces -Y (head), about 1.8 units long. Pivot at the body centre for swimmers,
    on the ground (belly and caudal sucker at z = 0) for crawlers (spec.ground).
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh


@dataclass
class Spec:
    name: str
    length: float = 1.8
    half_width: float = 0.13        # widest point (model units)
    top: float = 0.45               # back dome height as a fraction of the local half-width
    belly: float = 0.25             # belly depth as a fraction of the local half-width
    dome: float = 2.4               # cross-section exponent (2 = elliptical, higher = flatter back, sharper margin)
    # half-width profile along the body, (t, fraction of half_width), t = 0 head .. 1 tail
    profile: list = field(default_factory=lambda: [
        (0.0, 0.18), (0.04, 0.32), (0.08, 0.30), (0.20, 0.55), (0.45, 0.86),
        (0.70, 1.00), (0.85, 0.88), (0.95, 0.55), (1.0, 0.32)])
    annuli: int = 56                # annuli modelled (real leeches have ~100, the map can't show more)
    annuli_per_segment: int = 5     # for the spot rhythm
    groove: float = 0.97           # groove ring scale
    sides_top: int = 20             # vertices round the back (even, so one sits on the midline)
    sides_belly: int = 8            # and round the belly
    oral: float = 0.6               # oral sucker rim radius as a fraction of the head half-width
    caudal: float = 1.05            # caudal sucker radius as a fraction of half_width
    caudal_offset: float = 0.6     # how far forward of the tail tip the sucker centre sits (in radii)
    eye_pairs: int = 5
    eye_size: float = 0.012
    ground: bool = False
    gills: int = 0                  # pairs of lateral gill tufts
    gill_span: tuple = (0.40, 0.86) # t range they occupy
    gill_fingers: int = 3
    gill_length: float = 0.9        # finger length as a fraction of the local half-width
    gill_radius: float = 0.016
    roughness: float = 0.35
    # colours
    back: tuple = (0.20, 0.26, 0.12)
    back_head: tuple = None         # optional tint toward the front
    belly_col: tuple = (0.55, 0.50, 0.25)
    margin_col: tuple = None        # paler lateral margin
    margin_width: float = 0.12      # in fractions of the half-width
    groove_dark: float = 0.82       # colour multiplier on the groove rings
    mottle: float = 0.18
    # dorsal stripes: (centre, half-width) in fractions of the half-width from the midline
    # (mirrored), colour, strength
    stripes: list = field(default_factory=list)
    # spot rows: (centre, radius) in half-width fractions, colour, every n annuli, phase,
    # length in annuli
    spots: list = field(default_factory=list)
    # belly spots: (centre, radius) on the underside, colour, every n annuli, length in annuli
    belly_spots: list = field(default_factory=list)
    sucker_col: tuple = None        # caudal/oral sucker colour (default: belly/back blend)
    gill_col: tuple = (0.80, 0.55, 0.52)
    eye_col: tuple = (0.03, 0.03, 0.03)


def _interp(table, t):
    if t <= table[0][0]:
        return table[0][1]
    for (t0, v0), (t1, v1) in zip(table, table[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            u = u * u * (3 - 2 * u)
            return v0 + (v1 - v0) * u
    return table[-1][1]


class Leech:
    def __init__(self, s: Spec):
        self.s = s
        self.y0 = -s.length * 0.5
        self.cap_f = 0.022   # rounded caps at the ends (fractions of the length)
        self.cap_b = 0.03

    # ------------------------------------------------------------ shape
    def t_of(self, y):
        return (y - self.y0) / self.s.length

    def w(self, t):
        s = self.s
        r = _interp(s.profile, t) * s.half_width
        # round the two ends
        if t < self.cap_f:
            r *= math.sqrt(max(0.0, 1 - ((self.cap_f - t) / self.cap_f) ** 2))
        if t > 1 - self.cap_b:
            r *= math.sqrt(max(0.0, 1 - ((t - (1 - self.cap_b)) / self.cap_b) ** 2))
        return r

    def ht(self, t):
        return self.w_noncap(t) * self.s.top * self._capk(t)

    def hb(self, t):
        return self.w_noncap(t) * self.s.belly * self._capk(t)

    def w_noncap(self, t):
        return _interp(self.s.profile, t) * self.s.half_width

    def _capk(self, t):
        k = 1.0
        if t < self.cap_f:
            k = math.sqrt(max(0.0, 1 - ((self.cap_f - t) / self.cap_f) ** 2))
        if t > 1 - self.cap_b:
            k = math.sqrt(max(0.0, 1 - ((t - (1 - self.cap_b)) / self.cap_b) ** 2))
        return k

    def section(self, t, a, g=1.0):
        """Point on the cross-section at angle a (0 = right margin, pi/2 = back), groove scale g.
        x is spaced more evenly than a circle would give so the back gets more vertices."""
        s = self.s
        w = self.w(t) * g
        c = math.cos(a)
        top = math.sin(a) >= 0
        lin = 1 - 2 * ((a % math.tau) / math.pi if top else (math.tau - a % math.tau) / math.pi)
        xr = 0.45 * c + 0.55 * lin
        x = w * xr
        m = s.dome if top else 2.0
        z = (1 - abs(xr) ** m) ** (1 / m)
        z *= (self.ht(t) if top else -self.hb(t)) * g
        return Vector((x, self.y0 + t * s.length, z))

    # ------------------------------------------------------------ body loft
    def rings_t(self):
        """(t, groove scale, annulus index) for every ring, head to tail."""
        s = self.s
        out = []
        for i in range(1, 4):
            out.append((self.cap_f * (1 - math.cos(i / 4 * math.pi / 2)), 1.0, -1))
        a0, a1 = self.cap_f, 1 - self.cap_b
        da = (a1 - a0) / s.annuli
        for k in range(s.annuli):
            out.append((a0 + k * da, s.groove, k))
            out.append((a0 + (k + 0.5) * da, 1.0, k))
        out.append((a1, s.groove, s.annuli))
        for i in range(1, 4):
            out.append((a1 + self.cap_b * math.sin(i / 4 * math.pi / 2), 1.0, -1))
        return out

    def body(self):
        s = self.s
        bm = bmesh.new()
        nt, nb = s.sides_top, s.sides_belly
        na = nt + nb
        angles = [math.pi * k / nt for k in range(nt)] + [math.pi + math.pi * k / nb for k in range(nb)]
        tip_f = bm.verts.new(Vector((0, self.y0, 0)))
        rings = [[tip_f]]
        for t, g, _k in self.rings_t():
            rings.append([bm.verts.new(self.section(t, a, g)) for a in angles])
        rings.append([bm.verts.new(Vector((0, self.y0 + s.length, 0)))])
        for a, b in zip(rings, rings[1:]):
            for k in range(na):
                j = (k + 1) % na
                if len(a) == 1:
                    bm.faces.new([a[0], b[j], b[k]])
                elif len(b) == 1:
                    bm.faces.new([a[k], a[j], b[0]])
                else:
                    bm.faces.new([a[k], a[j], b[j], b[k]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm

    # ------------------------------------------------------------ paint
    def annulus_at(self, t):
        a0, a1 = self.cap_f, 1 - self.cap_b
        return (t - a0) / (a1 - a0) * self.s.annuli

    def body_color(self, co, n):
        s = self.s
        t = min(1.0, max(0.0, self.t_of(co.y)))
        w = max(self.w(t), 1e-4)
        rx = co.x / w
        ax = abs(rx)
        dorsal = co.z >= -1e-5
        ka = self.annulus_at(t)
        groove = abs(ka - round(ka)) < 0.2 and 0 < ka < s.annuli

        back = s.back
        if s.back_head is not None:
            back = nh.lerp(s.back_head, back, nh.smoothstep(0.0, 0.25, t))
        if dorsal:
            c = back
            for (pos, hw), col, k in s.stripes:
                d = abs(ax - pos) if pos > 0 else ax
                c = nh.lerp(c, col, k * (1 - nh.smoothstep(hw * 0.6, hw, d)))
            for (pos, r), col, every, phase, ln in s.spots:
                kk = (ka - phase) / every
                dk = (kk - round(kk)) * every          # in annuli
                if ka < 2 or ka > s.annuli - 1:
                    continue
                d = math.hypot((ax - pos) / r, dk / ln)
                c = nh.lerp(c, col, 1 - nh.smoothstep(0.7, 1.0, d))
            if s.margin_col is not None:
                c = nh.lerp(c, s.margin_col, nh.smoothstep(1 - s.margin_width * 1.6, 1 - s.margin_width * 0.4, ax))
            # back to belly colour round the margin
            c = nh.lerp(c, s.belly_col, nh.smoothstep(0.93, 1.0, ax) * 0.6)
        else:
            c = s.belly_col
            for (pos, r), col, every, ln in s.belly_spots:
                kk = ka / every
                dk = (kk - round(kk)) * every
                d = math.hypot((ax - pos) / r, dk / ln)
                c = nh.lerp(c, col, 1 - nh.smoothstep(0.7, 1.0, d))
            if s.margin_col is not None:
                c = nh.lerp(c, s.margin_col, nh.smoothstep(1 - s.margin_width, 1.0, ax) * 0.7)
        m = noise.noise(Vector((co.x * 14, co.y * 9, co.z * 14)) + Vector((3, 1, 7))) * s.mottle
        c = tuple(min(1.0, max(0.0, x * (1 + m))) for x in c)
        if groove:
            c = tuple(x * s.groove_dark for x in c)
        return c

    # ------------------------------------------------------------ extras
    def caudal_sucker(self):
        s = self.s
        R = s.caudal * s.half_width
        tail = 1 - self.cap_b * 0.5
        y = self.y0 + s.length - R * s.caudal_offset
        zb = -max(self.hb(t / 50) for t in range(51))  # lowest point of the belly
        zt = -self.hb(self.t_of(y)) * 0.3
        h = max((zt - zb) * 0.5, R * 0.14)
        bm = nh.uv_ellipsoid((0, y, zb + h), (R, R * 0.96, h), segments=22, rings=8,
                             deform=lambda v: 1.0 - 0.08 * max(0.0, -v.z) ** 4)
        del tail
        return bm, (y, R, zb)

    def sucker_color(self, centre_y, R, zb):
        s = self.s
        base = s.sucker_col or nh.lerp(s.back, s.belly_col, 0.5)

        def fn(co, n):
            r = math.hypot(co.x, co.y - centre_y) / R
            c = base
            if n.z < -0.3:     # sole: a pale rim round a darker cup
                c = nh.lerp(tuple(x * 0.7 for x in base), s.belly_col, nh.smoothstep(0.6, 0.9, r))
            else:
                # faint radial ribs on top
                ang = math.atan2(co.x, co.y - centre_y)
                c = tuple(x * (0.92 + 0.08 * math.sin(ang * 18)) for x in c)
            return c
        return fn

    def oral_rim(self):
        """A ring round the mouth on the underside of the head."""
        s = self.s
        t = 0.045
        r = self.w(t) * s.oral
        yc = self.y0 + t * s.length
        pts = []
        for k in range(17):
            a = k / 16 * math.tau
            y = yc + math.sin(a) * r * 1.1
            tt = self.t_of(y)
            pts.append(Vector((math.cos(a) * r, y, -self.hb(tt) * 0.95 + 0.001)))
        rad = [r * 0.18] * len(pts)
        return nh.tube(pts, rad, sides=4, cap_start=False, cap_end=False)

    def eyes(self):
        """Eye spots in an arc on the head (pairs spread back over the first annuli)."""
        s = self.s
        out = []
        for i in range(s.eye_pairs):
            f = (i + 0.5) / max(s.eye_pairs, 1)
            t = 0.022 + 0.06 * f
            fx = 0.22 + 0.45 * math.sin(f * math.pi * 0.5)
            for sd in (-1, 1):
                x = sd * self.w(t) * fx
                xr = x / self.w(t)
                z = self.ht(t) * (1 - abs(xr) ** s.dome) ** (1 / s.dome)
                r = s.eye_size * (1.0 - 0.25 * f)
                out.append(nh.uv_ellipsoid((x, self.y0 + t * s.length, z - r * 0.25),
                                           (r, r * 1.2, r * 0.55), segments=6, rings=4))
        return out

    def gills(self):
        """Finger-like gill tufts sticking out of the lateral margins (pairs on successive segments)."""
        s = self.s
        out = []
        for i in range(s.gills):
            t = s.gill_span[0] + (s.gill_span[1] - s.gill_span[0]) * i / max(s.gills - 1, 1)
            w = self.w(t)
            y = self.y0 + t * s.length
            L = w * s.gill_length
            for sd in (-1, 1):
                base = Vector((sd * w * 0.85, y, self.ht(t) * 0.15))
                # a short common stalk, then the digits fanning out from its tip
                stalk_d = Vector((sd, 0.0, 0.30)).normalized()
                fork = base + stalk_d * L * 0.38
                out.append(nh.tube([base, base.lerp(fork, 0.5), fork + stalk_d * s.gill_radius],
                                   [s.gill_radius * k for k in (1.4, 1.2, 0.8)], sides=5,
                                   cap_start=False, cap_end=True))
                for f in range(s.gill_fingers):
                    u = (f - (s.gill_fingers - 1) / 2) / max(s.gill_fingers - 1, 1)  # -0.5 .. 0.5
                    ang = u * 1.0                                  # fan along the body
                    lift = 0.30 + 0.25 * (1 - abs(u) * 2)
                    d = Vector((sd * math.cos(ang), math.sin(ang), lift)).normalized()
                    ll = L * 0.62 * (1.0 - 0.2 * abs(u) * 2)
                    pts = [fork + d * ll * k / 4 + Vector((0, 0, -0.15 * ll * (k / 4) ** 2)) for k in range(5)]
                    rr = [s.gill_radius * (1.0 - 0.35 * k / 4) for k in range(5)]
                    out.append(nh.tube(pts, rr, sides=5, cap_start=False, cap_end=True))
        return out


def build(s: Spec):
    L = Leech(s)
    mb = nh.MeshBuilder()
    mb.add(L.body(), L.body_color)
    sucker, (cy, R, zb) = L.caudal_sucker()
    mb.add(sucker, L.sucker_color(cy, R, zb))
    rim_col = s.sucker_col or nh.lerp(s.belly_col, s.back, 0.35)
    mb.add(L.oral_rim(), rim_col)
    for e in L.eyes():
        mb.add(e, s.eye_col)
    for g in L.gills():
        def gcol(co, n, base=s.gill_col):
            return tuple(x * (0.85 + 0.15 * n.z) for x in base)
        mb.add(g, gcol)
    obj = mb.to_object(s.name, roughness=s.roughness)
    if s.ground:
        nh.ground_to_zero(obj)
    return obj
