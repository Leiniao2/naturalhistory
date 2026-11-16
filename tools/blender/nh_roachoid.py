"""
Shared builder for the Palaeozoic roachoid models (archimylacris_eggintoni.py,
progonoblattina_clarkii.py, sysciophlebia_praepilata.py, anthracoblattina_ensifera.py).

Roachoids were the stem-group cockroaches of the Carboniferous coal forests: a
flat, broad insect with a shield-like pronotum hiding the head, two long
leathery forewings (tegmina) folded flat over the abdomen, long antennae,
spiny running legs and a pair of cerci; females of many species also carried a
long external ovipositor. Most species are known from their forewings, so the
models differ chiefly in the tegmen outline, its venation and colour pattern,
the pronotum shape and the body proportions. Same style as
archimylacris_acadica.py (which stays a standalone script):

  * build(spec): the whole animal from a Spec.
  * Tegmina: a flat membrane slab per wing, with crisp vein ribbons on top. The
    venation is generated per field (Sc, R, M, CuA, the arched claval furrow
    CuP and the anal veins of the clavus), each a curved stem with a comb of
    branches running to its stretch of the wing margin (margin positions are
    angles: -90 = wing base, 0 = middle of the outer/costal margin, 90 = apex,
    180 = middle of the inner margin). Colour patterns are thin "decal" slabs
    between membrane and veins (bands, longitudinal stripes, spots), laid out in
    wing (u, v) space: u from base (0) to apex (1), v from the inner margin (0)
    to the costal margin (1). The left tegmen overlaps the right.
  * Pronotum: a domed superellipse disc (separate front / hind squareness, a
    taper that narrows the front) with a pale rim and an optional dark marking.
  * Faces -Y, pivot on the ground (feet at z = 0). All six legs stay below the
    hip line (Ground leg animation, mapLegs 3); build() prints the measured
    mapHip.
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Vector

import nh_model as nh

LIGHT_DIR = Vector((-0.45, -0.55, 0.70)).normalized()
EYE = (0.05, 0.04, 0.04)
T_WING, T_DECAL, T_VEIN = 0.006, 0.0074, 0.010


@dataclass
class Vein:
    """One venation field: a stem from `start` (u, v) to the margin at angle `end`, plus `n`
    branches leaving the stem between stem fractions t0..t1 and reaching the margin at angles
    spread from a0 to a1. bow bends the stem sideways (+ toward the costal margin);
    sigmoid adds an S-bend (as in Progonoblattina's M and CuA)."""
    start: tuple
    end: float
    n: int = 0
    a0: float = 0.0
    a1: float = 0.0
    t0: float = 0.35
    t1: float = 0.85
    bow: float = 0.0
    sigmoid: float = 0.0
    width: float = 0.0040
    twig: float = 0.0             # >0: each branch forks again near the margin (+-twig degrees)


def default_veins():
    return [
        Vein((0.04, 0.80), -28, 2, -55, -8, 0.30, 0.70, bow=0.03, width=0.0040),   # Sc
        Vein((0.04, 0.66), 74, 4, 8, 60, 0.40, 0.90, bow=0.02, width=0.0045),     # R
        Vein((0.04, 0.50), 104, 1, 86, 86, 0.65, 0.65, width=0.0040),             # M
        Vein((0.06, 0.38), 162, 2, 128, 146, 0.40, 0.75, bow=-0.03, width=0.0038),  # CuA
        Vein((0.02, 0.32), 196, bow=-0.10, width=0.0042),                         # CuP (claval furrow)
        Vein((0.03, 0.22), 214, 2, 204, 226, 0.0, 0.0, bow=-0.05, width=0.0026),  # anal veins
    ]


@dataclass
class Spec:
    name: str
    base: float = 0.055           # underside of the body above the ground
    # tegmina
    wing_y0: float = -0.20
    wing_len: float = 0.80
    wing_w: float = 0.215         # width of one tegmen (from the midline out)
    wing_cx: float = 0.40         # tegmen centre line, as a fraction of wing_w out from the midline
    wing_narrow: float = 0.40     # how much narrower the base is than the middle
    wing_apex: float = 0.0        # shifts the apex outward (+) / toward the midline (-), x wing_w
    wing_tip: float = 2.0         # tip superellipse exponent (2 = round, >2 blunter, <2 pointed)
    wing_droop: float = 0.045     # outer margin bends down by this much
    wing_spread: float = 0.0      # degrees the tegmina splay apart behind
    veins: list = field(default_factory=default_veins)
    decals: list = field(default_factory=list)   # ("region", u0, u1, v0, v1, col) | ("stripe", [(u, v)...], w0, w1, col) | ("spot", (u, v), r, col)
    vein_scale: float = 1.0
    wing_col: tuple = (0.46, 0.30, 0.15)
    wing_base_col: tuple = (0.30, 0.18, 0.09)
    vein_col: tuple = (0.17, 0.10, 0.05)
    # pronotum
    pron_y: float = -0.315
    pron_rx: float = 0.205
    pron_ry: float = 0.150
    pron_dome: float = 0.040
    pron_front: float = 2.0       # superellipse exponent of the front half (>2 squarer)
    pron_hind: float = 2.0
    pron_taper: float = 0.0       # >0 narrows the front, widens the hind margin
    pron_col: tuple = (0.30, 0.18, 0.09)
    pron_rim: tuple = (0.66, 0.52, 0.32)
    pron_rim_at: float = 0.80     # rim starts at this fraction of the radius
    pron_mark: str = ""           # "", "disc", "pair", "bar"
    pron_mark_col: tuple = (0.10, 0.06, 0.03)
    # body
    body_col: tuple = (0.24, 0.15, 0.08)
    body_band_col: tuple = None   # pale hind edges of the abdominal segments (seen from the side)
    abd_len: float = 0.68         # abdomen length as a fraction of the wing length
    body_rx: float = 0.15
    head_col: tuple = None
    antenna_len: float = 0.62
    antenna_curl: float = 0.20
    # legs: (hip y, knee (x, dy), foot (x, dy)) per pair, right side
    legs: tuple = ((-0.25, (0.20, -0.06), (0.25, -0.16)),
                   (-0.15, (0.24, 0.02), (0.36, 0.06)),
                   (-0.05, (0.25, 0.12), (0.37, 0.32)))
    leg_col: tuple = (0.42, 0.26, 0.13)
    leg_dark: tuple = (0.22, 0.13, 0.06)
    leg_thick: float = 1.0
    spines: int = 3
    # cerci and ovipositor
    cerci_len: float = 0.20
    cerci_spread: float = 1.0
    ovipositor: float = 0.0       # length behind the abdomen (0 = none)
    ovi_lift: float = 0.04        # how much the blade curves up toward its tip
    ovi_col: tuple = (0.20, 0.10, 0.05)
    ovi_tip_col: tuple = (0.55, 0.36, 0.18)


# ---------------------------------------------------------------- helpers

def ribbon(points, w0, w1, thickness):
    """Tapered flat strip along a 2D polyline (vein, stripe): top and bottom sheets only."""
    pts = [Vector((p[0], p[1])) for p in points]
    bm = bmesh.new()
    rows = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = Vector((-d.y, d.x))
        w = w0 + (w1 - w0) * i / max(len(pts) - 1, 1)
        rows.append([bm.verts.new((q.x, q.y, z)) for q in (p + nrm * w, p - nrm * w)
                     for z in (thickness / 2, -thickness / 2)])
    for (lt, lb, rt, rb), (lt2, lb2, rt2, rb2) in zip(rows, rows[1:]):
        bm.faces.new([lt, rt, rt2, lt2])
        bm.faces.new([lb, lb2, rb2, rb])
    return bm


def bezier(a, c, b, n=6):
    a, c, b = Vector(a), Vector(c), Vector(b)
    return [a * (1 - t) ** 2 + c * 2 * t * (1 - t) + b * t * t for t in (k / n for k in range(n + 1))]


def _spow(x, p):
    return math.copysign(abs(x) ** p, x)


class Wing:
    """Outline and (u, v) frame of the right tegmen (x out from the midline, flat at z = 0)."""

    def __init__(self, s):
        self.s = s
        self.cx = s.wing_w * s.wing_cx
        self.cy = s.wing_y0 + s.wing_len * 0.5
        self.outline = [self.point(math.radians(-90 + 360 * k / 44)) for k in range(44)]

    def point(self, a):
        s = self.s
        sa, ca = math.sin(a), math.cos(a)
        if sa > 0:  # apical half: superellipse tip
            p = 2.0 / s.wing_tip
            sa, ca = _spow(sa, p), _spow(ca, p)
        narrow = 1.0 - s.wing_narrow * max(0.0, -math.sin(a)) ** 2
        x = self.cx + s.wing_w * 0.5 * ca * narrow + s.wing_apex * s.wing_w * max(0.0, sa) ** 3
        y = self.cy + s.wing_len * 0.5 * sa
        return Vector((x, y))

    def chord(self, y):
        xs = []
        o = self.outline
        for i in range(len(o)):
            a, b = o[i], o[(i + 1) % len(o)]
            if (a.y - y) * (b.y - y) <= 0 and a.y != b.y:
                xs.append(a.x + (b.x - a.x) * (y - a.y) / (b.y - a.y))
        if len(xs) < 2:
            return self.cx, self.cx
        return min(xs), max(xs)

    def uv(self, u, v):
        s = self.s
        u = min(max(u, 0.004), 0.996)
        y = s.wing_y0 + u * s.wing_len
        x0, x1 = self.chord(y)
        return Vector((x0 + (x1 - x0) * v, y))

    def to_uv(self, co):
        s = self.s
        u = (co.y - s.wing_y0) / s.wing_len
        x0, x1 = self.chord(min(max(co.y, s.wing_y0 + 1e-4), s.wing_y0 + s.wing_len - 1e-4))
        return u, (co.x - x0) / max(x1 - x0, 1e-6)

    def end(self, deg):
        """Point just inside the margin at angle deg."""
        p = self.point(math.radians(deg))
        c = Vector((self.cx, self.cy))
        return c + (p - c) * 0.965


def build_wing(s):
    """[(bmesh, colour)] for the right tegmen (flat, z = 0 before draping)."""
    w = Wing(s)

    def membrane(co, n):
        u, v = w.to_uv(co)
        return nh.lerp(s.wing_base_col, s.wing_col, nh.smoothstep(0.0, 0.3, u))
    parts = [(nh.flat_panel([(p.x, p.y, 0.0) for p in w.outline], T_WING), membrane)]

    # colour pattern decals
    for i, d in enumerate(s.decals):
        t = T_DECAL + 0.0003 * i
        if d[0] == "region":
            _, u0, u1, v0, v1, col = d
            n = 8
            poly = [w.uv(u0 + (u1 - u0) * k / n, v1) for k in range(n + 1)]
            poly += [w.uv(u1 - (u1 - u0) * k / n, v0) for k in range(n + 1)]
            # drop duplicate points where the chord collapses at the apex
            clean = []
            for p in poly:
                if not clean or (p - clean[-1]).length > 1e-4:
                    clean.append(p)
            if len(clean) >= 3:
                parts.append((nh.flat_panel([(p.x, p.y, 0.0) for p in clean], t), col))
        elif d[0] == "stripe":
            _, uvs, w0, w1, col = d
            pts = [w.uv(*q) for q in uvs]
            dense = []
            for a, b in zip(pts, pts[1:]):
                dense += [a.lerp(b, k / 3) for k in range(3)]
            dense.append(pts[-1])
            parts.append((ribbon(dense, w0, w1, t), col))
        elif d[0] == "spot":
            _, (u, v), r, col = d
            c = w.uv(u, v)
            disc = [(c.x + math.cos(k / 8 * math.tau) * r, c.y + math.sin(k / 8 * math.tau) * r * 1.3, 0.0)
                    for k in range(8)]
            parts.append((nh.flat_panel(disc, t), col))

    # venation
    k = s.vein_scale

    def vein(pts, w0, w1):
        parts.append((ribbon(pts, w0 * k, w1 * k, T_VEIN), s.vein_col))

    for f in s.veins:
        a = w.uv(*f.start)
        b = w.end(f.end)
        d = (b - a)
        side = Vector((d.y, -d.x)).normalized()  # toward +x (costal side) for a vein running +y
        if side.x < 0:
            side = -side
        ctrl = a.lerp(b, 0.5) + side * f.bow * s.wing_w
        stem = bezier(a, ctrl, b, 8)
        if f.sigmoid:
            stem = [p + side * f.sigmoid * s.wing_w * math.sin(i / 8 * math.tau) for i, p in enumerate(stem)]
        vein(stem, f.width, f.width * 0.6)
        for j in range(f.n):
            tt = f.t0 + (f.t1 - f.t0) * (j / max(f.n - 1, 1) if f.n > 1 else 0.5)
            ang = f.a0 + (f.a1 - f.a0) * (j / max(f.n - 1, 1) if f.n > 1 else 0.5)
            i = tt * 8
            i0 = min(int(i), 7)
            o = stem[i0].lerp(stem[i0 + 1], i - i0)
            e = w.end(ang - f.twig) if f.twig else w.end(ang)
            c = o.lerp(e, 0.45) + (stem[i0 + 1] - stem[i0]).normalized() * 0.02
            br = bezier(o, c, e, 4)
            vein(br, f.width * 0.65, f.width * 0.40)
            if f.twig:
                tw = br[2].lerp(br[3], 0.4)
                vein(bezier(tw, tw.lerp(w.end(ang + f.twig), 0.5), w.end(ang + f.twig), 2),
                     f.width * 0.42, f.width * 0.32)
    return parts


def place_wing(mb, s, parts, mirror, lift):
    spread = math.radians(s.wing_spread)
    piv = Vector((0.0, s.wing_y0))
    for bm, col in parts:
        for v in bm.verts:
            if spread:
                p = Vector((v.co.x, v.co.y)) - piv
                v.co.x = piv.x + p.x * math.cos(spread) + p.y * math.sin(spread)
                v.co.y = piv.y - p.x * math.sin(spread) + p.y * math.cos(spread)
            u = max(0.0, v.co.x) / s.wing_w
            v.co.z += s.base + 0.062 - s.wing_droop * u * u + lift
            if mirror:
                v.co.x = -v.co.x
        if mirror:
            bmesh.ops.reverse_faces(bm, faces=bm.faces)
        mb.add(bm, col, smooth=False)


# ---------------------------------------------------------------- body

def head_centre(s):
    return Vector((0, s.pron_y - s.pron_ry * 0.70, s.base + 0.018))


def build_body(mb, s):
    B = s.base
    abd_c = s.wing_y0 + s.wing_len * s.abd_len * 0.5 + 0.02
    abd_ry = s.wing_len * s.abd_len * 0.5
    band = s.body_band_col

    def abd_col(co, n):
        if band is None:
            return s.body_col
        ph = ((co.y - (abd_c - abd_ry)) / (abd_ry * 2 / 8)) % 1.0
        return band if ph > 0.78 and n.z < 0.6 else s.body_col
    mb.add(nh.uv_ellipsoid((0, abd_c, B + 0.022), (s.body_rx, abd_ry, 0.024), 14, 8), abd_col)
    mb.add(nh.uv_ellipsoid((0, s.wing_y0 + 0.04, B + 0.03), (s.body_rx * 0.87, 0.12, 0.035), 12, 6), s.body_col)
    hc = head_centre(s)
    head = s.head_col or s.pron_col
    mb.add(nh.uv_ellipsoid(hc, (0.075, 0.060, 0.040), 12, 8), head)
    for sd in (-1, 1):
        mb.add(nh.uv_ellipsoid(hc + Vector((sd * 0.058, -0.012, 0.010)), (0.022, 0.030, 0.022), 8, 5), EYE)
        mb.add(nh.tube([hc + Vector((sd * 0.02, -0.05, -0.02)), hc + Vector((sd * 0.03, -0.07, -0.032))],
                       [0.010, 0.004], sides=4), s.leg_dark)
        # long filiform antennae curving forward and out
        a0 = hc + Vector((sd * 0.035, -0.055, 0.012))
        L = s.antenna_len
        pts = []
        for k in range(9):
            t = k / 8
            pts.append(a0 + Vector((sd * (0.08 * t + s.antenna_curl * t * t) * L / 0.62,
                                    (-0.58 * t + 0.08 * t * t) * L / 0.62,
                                    0.05 * math.sin(t * math.pi * 0.9))))
        mb.add(nh.tube(pts, [0.008 - 0.0055 * k / 8 for k in range(9)], sides=4), s.leg_dark)
    return abd_c + abd_ry


def build_pronotum(mb, s):
    c = Vector((0.0, s.pron_y, s.base + 0.055))
    rx, ry, dome = s.pron_rx, s.pron_ry, s.pron_dome
    bm = bmesh.new()
    rings, sides = 9, 28
    centre = bm.verts.new((c.x, c.y, c.z + dome))
    prev = None
    for i in range(1, rings + 1):
        r = i / rings
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            ca, sa = math.cos(a), math.sin(a)
            p = 2.0 / (s.pron_hind if sa > 0 else s.pron_front)
            ex, ey = _spow(ca, p), _spow(sa, p)
            x = ex * rx * r * (1.0 + s.pron_taper * ey)
            y = ey * ry * r
            z = dome * (1 - r * r) + 0.006 * nh.smoothstep(0.75, 1.0, r)
            ring.append(bm.verts.new((c.x + x, c.y + y, c.z + z)))
        for k in range(sides):
            j = (k + 1) % sides
            if prev is None:
                bm.faces.new([centre, ring[k], ring[j]])
            else:
                bm.faces.new([prev[k], ring[k], ring[j], prev[j]])
        prev = ring
    under = [bm.verts.new((v.co.x * 0.92, c.y + (v.co.y - c.y) * 0.92, c.z - 0.012)) for v in prev]
    for k in range(sides):
        j = (k + 1) % sides
        bm.faces.new([prev[j], prev[k], under[k], under[j]])
    bm.faces.new(list(reversed(under)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def col(co, n):
        dx, dy = (co.x - c.x) / rx, (co.y - c.y) / ry
        r = math.hypot(dx, dy)
        k = s.pron_col
        if s.pron_mark == "disc":
            k = nh.lerp(s.pron_mark_col, k, nh.smoothstep(0.30, 0.50, r))
        elif s.pron_mark == "pair":
            q = min(math.hypot(dx - 0.30, (dy + 0.05) * 0.8), math.hypot(dx + 0.30, (dy + 0.05) * 0.8))
            k = nh.lerp(s.pron_mark_col, k, nh.smoothstep(0.16, 0.30, q))
        elif s.pron_mark == "bar":
            k = nh.lerp(s.pron_mark_col, k, nh.smoothstep(0.10, 0.18, abs(dx)) if r < 0.85 else 1.0)
        k = nh.lerp(k, s.pron_rim, nh.smoothstep(s.pron_rim_at, s.pron_rim_at + 0.17, r))
        h = max(0.0, n.dot(LIGHT_DIR)) ** 12
        return nh.lerp(k, (0.62, 0.48, 0.34), h * 0.45)
    mb.add(bm, col)


# ---------------------------------------------------------------- legs, cerci, ovipositor

def spiny_leg(mb, s, sd, hip, knee, foot):
    k = s.leg_thick
    tarsus = foot + Vector((sd * 0.04, (foot - knee).normalized().y * 0.05, 0.0))
    mb.add(nh.tube([hip, hip.lerp(knee, 0.5) + Vector((0, 0, 0.008)), knee],
                   [0.017 * k, 0.020 * k, 0.013 * k], sides=5, scale_xy=(1.0, 0.6)), s.leg_col)
    mb.add(nh.tube([knee, foot], [0.011 * k, 0.008 * k], sides=4), s.leg_col)
    mb.add(nh.tube([foot, tarsus], [0.006, 0.003], sides=4), s.leg_dark)
    d = foot - knee
    for j in range(s.spines):
        p = knee + d * ((j + 0.7) / (s.spines + 0.5))
        # spines splay out and back, staying under the tegmina
        out = Vector((sd, 0, 0.35)).normalized()
        mb.add(nh.tube([p, p + out * 0.028 + d.normalized() * 0.012], [0.004, 0.0], sides=3), s.leg_dark)
        mb.add(nh.tube([p, p + Vector((-sd * 0.5, 0, -0.6)).normalized() * 0.022 + d.normalized() * 0.012],
                       [0.0035, 0.0], sides=3), s.leg_dark)


def build_legs(mb, s, tail_y):
    B = s.base
    hip_x = s.body_rx * 0.47
    for sd in (-1, 1):
        for y, (kx, kdy), (fx, fdy) in s.legs:
            hip = Vector((sd * hip_x, y, B + 0.005))
            # knees stay under the drooping tegmen margin
            under_wing = B + 0.062 - s.wing_droop * min(1.0, kx / s.wing_w) ** 2 - 0.035
            knee = Vector((sd * kx, y + kdy, min(B + 0.035, max(B + 0.018, under_wing))))
            foot = Vector((sd * fx, y + fdy, 0.0))
            spiny_leg(mb, s, sd, hip, knee, foot)
    # cerci: beaded, splayed, from the abdomen tip
    L = s.cerci_len
    for sd in (-1, 1):
        b = Vector((sd * 0.03, tail_y - 0.04, B + 0.022))
        pts = [b + Vector((sd * 0.25 * s.cerci_spread * L * j / 4, L * j / 4, 0.006 * j)) for j in range(5)]
        mb.add(nh.tube(pts, [0.012, 0.011, 0.009, 0.007, 0.0], sides=4), s.leg_dark)
        for p in pts[1:-1]:
            mb.add(nh.ellipsoid(p, (0.010,) * 3, 1), s.leg_dark)
    if s.ovipositor > 0:
        # a long, laterally flattened, sword-like ovipositor: two valves side by side, slightly upcurved
        L = s.ovipositor
        for sd in (-1, 1):
            b = Vector((sd * 0.012, tail_y - 0.06, B + 0.030))
            pts = [b + Vector((0, (L + 0.06) * t, s.ovi_lift * t * t)) for t in (0, 0.25, 0.5, 0.75, 0.92, 1.0)]
            radii = [0.030, 0.029, 0.026, 0.021, 0.013, 0.0]

            def col(co, n, y0=b.y):
                return nh.lerp(s.ovi_col, s.ovi_tip_col, nh.smoothstep(0.55, 1.0, (co.y - y0) / (L + 0.06)))
            mb.add(nh.tube(pts, radii, sides=6, scale_xy=(0.55, 1.0)), col)


def build(s):
    mb = nh.MeshBuilder()
    tail_y = build_body(mb, s)
    build_legs(mb, s, tail_y)
    place_wing(mb, s, build_wing(s), mirror=False, lift=0.0)
    place_wing(mb, s, build_wing(s), mirror=True, lift=0.008)   # left tegmen overlaps the right
    build_pronotum(mb, s)
    obj = mb.to_object(s.name, roughness=0.45)
    zmin = min(v.co.z for v in obj.data.vertices)
    nh.ground_to_zero(obj)
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    hip = s.base + 0.005 - zmin
    print(f"height {max(zs):.3f}, hip {hip:.3f} -> mapHip {hip / max(zs):.2f}")
    # which third of the body length (the leg animation's pair buckets) each foot falls in
    y0, y1 = min(ys), max(ys)
    buckets = [min(int((y + fdy - y0) / (y1 - y0) * 3), 2) for y, _k, (_fx, fdy) in s.legs]
    print(f"length {y1 - y0:.3f}, foot buckets (front->hind) {buckets}")
    return obj
