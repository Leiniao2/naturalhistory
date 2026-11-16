"""
Shared ichthyosaur builder for the ichthyosaur species scripts
(shonisaurus_popularis.py, shonisaurus_sikanniensis.py, ophthalmosaurus_icenicus.py).
Builds on nh_model.

Ichthyosaurs are convergent with dolphins and tunas, so the body follows the same
recipe as delphinus_delphis.py: a lofted superellipse body along Y (snout at -Y,
facing -Y), with fin slabs for the flippers, dorsal fin and tail fluke, fused into one
seamless surface (nh_model.MeshBuilder.fuse) and repainted analytically. What differs
is ichthyosaurian:

  * a long, narrow rostrum running straight into a big skull with no neck, and a long
    mouth line reaching back below the eye; a small nostril just in front of the orbit;
  * big eyes, each set in a raised orbit and ringed by the bony plates of the
    sclerotic ring (crisp shells around a dark cornea);
  * four flippers (fore and hind sized independently), stiff hydrofoils hanging from
    the lower flank and swept back;
  * an optional fleshy dorsal fin;
  * a vertical tail fluke: the vertebral column bends down at the tail bend into the
    lower lobe (`tail_bend`), the upper lobe is fleshy; `fluke_*` set its span, sweep
    and how crescent-shaped (lunate) it is;
  * countershading (dark back, pale belly) with a slightly wavy boundary, darker fins
    and faint mottling, all from an IchthyosaurSpec's colours.

An IchthyosaurSpec holds every parameter; build(spec) returns the finished object.
Lengths are in model units with the snout tip at y = -1; the whole animal is about
2 units long and is re-centred on its bounding box (pivot at the body centre).
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh


@dataclass
class IchthyosaurSpec:
    name: str = "Ichthyosaur"
    voxel: float = 0.016
    max_tris: int = 20000
    # ---- body profile (half-widths / half-heights in model units)
    snout_len: float = 0.30      # snout tip to the front of the orbit
    snout_r: float = 0.030       # rostrum half-height at its base
    snout_tip_r: float = 0.007
    eye_r: float = 0.045         # outer radius of the sclerotic ring
    head_h: float = 0.090        # skull half-height at the orbit
    head_w: float = 0.070
    body_h: float = 0.180        # deepest point of the trunk (top half-height)
    belly_k: float = 1.05        # belly half-height relative to body_h
    body_w: float = 0.150
    y_max: float = -0.25         # where the trunk is deepest
    rear_k: float = 0.75         # trunk fullness behind the deepest point (0.5 slim .. 0.9 rotund)
    y_ped: float = 0.62          # end of the tail stock (fluke root)
    ped_h: float = 0.032
    ped_w: float = 0.022
    tail_bend: float = 18.0      # degrees the tail axis turns down at the tail bend
    y_bend: float = 0.50
    # ---- fins (lengths along the span; chords along the body)
    fore: tuple = (-0.42, 0.34, 0.12)   # (root y, length, root chord)
    fore_shape: float = 0.35            # chord bulge (0 = narrow strap, 0.6 = broad paddle)
    fore_droop: float = 32.0
    fore_sweep: float = 40.0
    hind: tuple = (0.12, 0.16, 0.07)
    hind_shape: float = 0.25
    hind_droop: float = 36.0
    hind_sweep: float = 45.0
    dorsal: tuple = (0.0, 0.16, 0.30)   # (centre y, height, base length); None = no fin
    dorsal_rake: float = 0.6            # how far back the apex leans (fraction of base)
    fluke_up: float = 0.30              # upper lobe span (z)
    fluke_down: float = 0.32            # lower lobe span
    fluke_sweep: float = 0.26           # how far back the lobe tips reach
    fluke_chord: float = 0.10           # root chord at the notch
    fluke_lunate: float = 0.12          # trailing-edge concavity
    # ---- colours
    back: tuple = (0.14, 0.15, 0.17)
    flank: tuple = (0.36, 0.37, 0.38)
    belly: tuple = (0.86, 0.84, 0.78)
    fin: tuple = (0.10, 0.11, 0.12)
    mottle: tuple = (0.24, 0.24, 0.25)
    mottle_k: float = 0.35
    stripe: tuple = None                # optional faint dark band along the flank
    shade_line: float = -0.15           # countershading boundary (-1 belly .. 1 back)
    ring: tuple = (0.70, 0.64, 0.50)    # sclerotic ring plates
    eye: tuple = (0.03, 0.03, 0.035)
    mouth: tuple = (0.08, 0.06, 0.06)
    ring_plates: int = 14
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------- generic tools

def interp(table, y):
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


def paddle_outline(length, chord, shape, n=12):
    """Planform of a stiff flipper in (u = chordwise, v = spanwise): a fairly straight,
    rounded leading edge, a convex trailing edge and a rounded tip. Root at v = 0."""
    lead, trail = [], []
    for i in range(n + 1):
        s = i / n
        c = chord * (1.0 + shape * math.sin(math.pi * min(1.0, s * 1.3))) * max(0.0, 1.0 - s ** 2.2) ** 0.55
        c = max(c, chord * 0.10) if i < n else 0.0
        lead.append((-c * 0.30, s * length))
        trail.append((c * 0.70, s * length))
    tip = (lead[-1][0] * 0.5 + trail[-1][0] * 0.5, length * 1.02)
    return lead[:-1] + [tip] + list(reversed(trail[:-1]))


def basis(u, v, n):
    """3x3 matrix whose columns are u, v, n (maps a local x/y/z shell into that frame)."""
    return Matrix((u, v, n)).transposed()


# ---------------------------------------------------------------- the animal

class Ichthyosaur:
    def __init__(self, spec):
        self.s = s = spec
        y_eye = -1.0 + s.snout_len + s.eye_r
        self.y_eye = y_eye
        y_skull = y_eye + s.eye_r * 1.9           # back of the skull / start of the trunk
        y_mid = s.y_max + (s.y_ped - s.y_max) * 0.45
        tail_h = s.ped_h + (s.body_h - s.ped_h) * s.rear_k * 0.62
        tail_w = s.ped_w + (s.body_w - s.ped_w) * s.rear_k * 0.55
        y0 = -1.0
        r0 = y0 + s.snout_len * 0.08
        r1 = y0 + s.snout_len * 0.55
        r2 = y0 + s.snout_len * 0.92
        self.HT = [(y0, s.snout_tip_r), (r0, s.snout_tip_r * 1.6), (r1, s.snout_r * 0.72),
                   (r2, s.snout_r * 1.15), (y_eye, s.head_h), (y_skull, s.head_h * 1.25 + 0.15 * s.body_h),
                   (s.y_max, s.body_h), (y_mid, tail_h), (s.y_ped - 0.10, s.ped_h * 1.6), (s.y_ped, s.ped_h)]
        self.HB = [(y0, s.snout_tip_r), (r0, s.snout_tip_r * 1.6), (r1, s.snout_r * 0.78),
                   (r2, s.snout_r * 1.25), (y_eye, s.head_h * 1.05), (y_skull, s.head_h * 1.3 + 0.2 * s.body_h),
                   (s.y_max, s.body_h * s.belly_k), (y_mid, tail_h * 0.95),
                   (s.y_ped - 0.10, s.ped_h * 1.5), (s.y_ped, s.ped_h)]
        self.W = [(y0, s.snout_tip_r * 1.1), (r0, s.snout_tip_r * 1.7), (r1, s.snout_r * 0.80),
                  (r2, s.snout_r * 1.2), (y_eye, s.head_w), (y_skull, s.head_w * 1.15 + 0.25 * s.body_w),
                  (s.y_max, s.body_w), (y_mid, tail_w), (s.y_ped - 0.10, s.ped_w * 1.5), (s.y_ped, s.ped_w)]

    # profile
    def w(self, y): return interp(self.W, y)
    def ht(self, y): return interp(self.HT, y)
    def hb(self, y): return interp(self.HB, y)

    def zc(self, y):
        s = self.s
        z = -0.01 * nh.smoothstep(-0.6, -1.0, y)    # the snout sits slightly low
        if y > s.y_bend:
            d = y - s.y_bend
            z -= math.tan(math.radians(s.tail_bend)) * d * nh.smoothstep(0.0, 0.08, d)
        return z

    def section(self, y, a, n=2.2):
        c, s_ = math.cos(a), math.sin(a)
        x = self.w(y) * math.copysign(abs(c) ** (2.0 / n), c)
        hz = self.ht(y) if s_ >= 0 else self.hb(y)
        return Vector((x, y, self.zc(y) + hz * math.copysign(abs(s_) ** (2.0 / n), s_)))

    # fins
    def flipper(self, sign, root, shape, droop, sweep):
        y_root, length, chord = root
        dr, sw = math.radians(droop), math.radians(sweep)
        span = Vector((sign * math.cos(dr) * math.cos(sw), math.sin(sw), -math.sin(dr) * math.cos(sw))).normalized()
        cdir = Vector((0.0, 1.0, 0.0))
        cdir = (cdir - span * cdir.dot(span)).normalized()
        nrm = cdir.cross(span).normalized()
        yc = y_root + chord * 0.25
        origin = Vector((sign * self.w(yc) * 0.70, y_root, self.zc(yc) - self.hb(yc) * 0.50))

        def frame(u, v):
            return origin + cdir * u + span * v, nrm

        pts = paddle_outline(length, chord, shape)
        th = []
        for u, v in pts:
            t = min(1.0, v / length)
            lead = 1.0 if u < chord * 0.15 else 0.80
            th.append(max(0.040, chord * 0.42 * (1.0 - 0.6 * t) * lead))
        return fin_slab(pts, th, frame)

    def dorsal(self):
        s = self.s
        yc, h, base = s.dorsal
        base_z = lambda y: self.zc(y) + self.ht(y) - 0.03  # noqa: E731
        front, back = (yc - base * 0.5, base_z(yc - base * 0.5)), (yc + base * 0.5, base_z(yc + base * 0.5))
        apex = (yc + base * (s.dorsal_rake - 0.5) * 0.9, self.zc(yc) + self.ht(yc) + h)
        notch = (back[0] - base * 0.08, back[1] + h * 0.18)
        pts = [front] + curve(front, apex, 0.10, 9) + curve(apex, notch, -0.10, 7) + [notch, back]
        pts += curve(back, front, 0.0, 4)[1:]
        top = self.ht(yc)
        th = [max(0.034, 0.065 - 0.03 * min(1.0, max(0.0, (v - top) / h))) for _u, v in pts]
        return fin_slab(pts, th, lambda u, v: (Vector((0.0, u, v)), Vector((1.0, 0.0, 0.0))))

    def fluke(self):
        """Vertical crescent fluke. The tail axis turns down into the lower lobe; the
        fleshy upper lobe is raised to match, so the crescent stays near-symmetric."""
        s = self.s
        y0 = s.y_ped - 0.04
        root = Vector((y0, self.zc(y0)))
        lift = (self.zc(s.y_bend) - root.y) * 0.55
        P = lambda a, b: tuple(root + Vector((a, b)))  # noqa: E731
        up_tip = P(s.fluke_sweep + 0.02, s.fluke_up + lift)
        dn_tip = P(s.fluke_sweep * 0.92, -s.fluke_down + lift)
        notch = P(s.fluke_chord + 0.04, lift * 0.3)
        top0 = P(-0.03, s.ped_h * 0.9)
        bot0 = P(-0.03, -s.ped_h * 0.9)
        pts = [top0] + curve(top0, up_tip, 0.07, 10) + curve(up_tip, notch, -s.fluke_lunate, 9) \
            + curve(notch, dn_tip, -s.fluke_lunate, 9) + curve(dn_tip, bot0, 0.07, 10)
        th = []
        for p in pts:
            d = p[1] - root.y - lift * 0.3
            span = s.fluke_up if d > 0 else s.fluke_down
            th.append(max(0.034, s.ped_w * 1.8 * (1.0 - 0.6 * min(1.0, abs(d) / span))))
        return fin_slab(pts, th, lambda u, v: (Vector((0.0, u, v)), Vector((1.0, 0.0, 0.0))))

    def orbit(self, sign):
        """Raised bony orbit that carries the eye."""
        s = self.s
        y = self.y_eye
        z = self.zc(y) + self.ht(y) * 0.22
        r = s.eye_r
        return nh.ellipsoid((sign * (self.w(y) - r * 0.35), y, z), (r * 0.55, r * 1.15, r * 1.0), subdivisions=3)

    # colour
    def rel_z(self, p):
        y = max(min(p.y, self.s.y_ped), -1.0)
        d = p.z - self.zc(y)
        return d / max(self.ht(y) if d >= 0 else self.hb(y), 1e-3)

    def outside(self, p):
        y = max(min(p.y, self.s.y_ped), -1.0)
        hz = self.ht(y) if p.z >= self.zc(y) else self.hb(y)
        r = math.sqrt((p.x / max(self.w(y), 1e-3)) ** 2 + ((p.z - self.zc(y)) / max(hz, 1e-3)) ** 2)
        return max(0.0, r - 1.0) * min(self.w(y), hz)

    def mouth_z(self, y):
        """Height of the mouth line at y (relative to the section, -1..1)."""
        return -0.18 - 0.10 * nh.smoothstep(-1.0, self.y_eye, y)

    def colour(self, p, n):
        s = self.s
        y = p.y
        r = self.rel_z(p)
        out = self.outside(p)
        wob = noise.noise(Vector((y * 5.0, 0.0, 1.7))) * 0.08 + noise.noise(Vector((y * 17.0, p.z * 9.0, 4.0))) * 0.03
        line = s.shade_line + wob
        col = nh.lerp(s.belly, s.flank, nh.smoothstep(line - 0.10, line + 0.10, r))
        col = nh.lerp(col, s.back, nh.smoothstep(line + 0.25, line + 0.75, r))
        if s.stripe is not None:
            col = nh.lerp(col, s.stripe, (1.0 - nh.smoothstep(0.06, 0.14, abs(r - line - 0.22))) * 0.45
                          * nh.smoothstep(-0.5, -0.3, y) * nh.smoothstep(0.55, 0.35, y))
        # mottling on the back and flanks
        m = noise.noise(p * 14.0 + Vector((3.0, 1.0, 0.0)))
        col = nh.lerp(col, s.mottle, nh.smoothstep(0.25, 0.55, m) * s.mottle_k * nh.smoothstep(line - 0.1, line + 0.3, r))
        # fins are dark
        tail = nh.smoothstep(s.y_ped - 0.10, s.y_ped, y)
        if out > 0.010 or tail > 0.0:
            col = nh.lerp(col, s.fin, max(nh.smoothstep(0.010, 0.030, out), tail))
        # mouth line along the rostrum, ending below the eye
        if y < self.y_eye + s.eye_r * 0.8 and out < 0.01:
            d = abs(r - self.mouth_z(y))
            k = (1.0 - nh.smoothstep(0.07, 0.15, d)) * nh.smoothstep(self.y_eye + s.eye_r * 0.8, self.y_eye, y)
            col = nh.lerp(col, s.mouth, k * 0.95)
        return col

    def groove_mouth(self, bm):
        s = self.s
        bm.normal_update()
        for v in bm.verts:
            y = v.co.y
            if y < self.y_eye + s.eye_r * 0.8 and self.outside(v.co) < 0.01:
                d = abs(self.rel_z(v.co) - self.mouth_z(y))
                k = (1.0 - nh.smoothstep(0.0, 0.10, d)) * nh.smoothstep(self.y_eye + s.eye_r * 0.8, self.y_eye, y)
                v.co -= v.normal * k * 0.004
            v.co += v.normal * noise.noise(v.co * 28.0) * 0.0007   # faint skin ripple

    # crisp details
    def eye(self, mb, sign):
        s = self.s
        y = self.y_eye
        r = s.eye_r
        c = Vector((sign * self.w(y) + sign * r * 0.28, y, self.zc(y) + self.ht(y) * 0.22))
        nrm = Vector((sign, -0.22, 0.18)).normalized()
        up = Vector((0.0, 0.0, 1.0))
        u = (up - nrm * up.dot(nrm)).normalized()
        v = nrm.cross(u).normalized()
        # dark eyeball / cornea filling the ring
        mb.add(nh.ellipsoid(c - nrm * r * 0.25, (r * 0.80, r * 0.80, r * 0.42), subdivisions=3,
                            rotation=basis(u, v, nrm)), s.eye)
        # bony sclerotic plates: a ring of overlapping slabs
        N = s.ring_plates
        for k in range(N):
            a = k / N * math.tau
            radial = u * math.cos(a) + v * math.sin(a)
            tang = nrm.cross(radial)
            p = c + radial * r * 0.80 - nrm * r * 0.06
            tilt = (nrm * 0.85 + radial * 0.5).normalized()   # plates bevel outward like a shallow cone
            rad2 = (radial - tilt * radial.dot(tilt)).normalized()
            tang2 = tilt.cross(rad2)
            shade = 0.92 + 0.08 * math.sin(a * 3.0 + 1.0)
            mb.add(nh.ellipsoid(p, (r * 0.22, r * 0.31, r * 0.07), subdivisions=2,
                                rotation=basis(rad2, tang2, tilt)), tuple(x * shade for x in s.ring))
        # a small glint
        mb.add(nh.ellipsoid(c + nrm * r * 0.17 + u * r * 0.25 - v * r * 0.18, (r * 0.09,) * 3, subdivisions=1),
               (0.65, 0.68, 0.72))

    def nostril(self, mb, sign):
        s = self.s
        y = self.y_eye - s.eye_r * 1.45
        z = self.zc(y) + self.ht(y) * 0.45
        mb.add(nh.ellipsoid((sign * self.w(y) * 0.92, y, z), (0.006, 0.016, 0.006), subdivisions=1), s.mouth)


def build(spec):
    ich = Ichthyosaur(spec)
    grey = (0.5, 0.5, 0.5)
    parts = nh.MeshBuilder()
    parts.add(loft(-1.0, spec.y_ped + 0.02, 140, 40, ich.section), grey)
    for sg in (-1, 1):
        parts.add(ich.flipper(sg, spec.fore, spec.fore_shape, spec.fore_droop, spec.fore_sweep), grey)
        parts.add(ich.flipper(sg, spec.hind, spec.hind_shape, spec.hind_droop, spec.hind_sweep), grey)
        parts.add(ich.orbit(sg), grey)
    if spec.dorsal:
        parts.add(ich.dorsal(), grey)
    parts.add(ich.fluke(), grey)
    fused = parts.fuse(voxel=spec.voxel, smooth=6, smooth_factor=0.5, max_tris=spec.max_tris)
    ich.groove_mouth(fused)

    mb = nh.MeshBuilder()
    mb.add(fused, ich.colour)
    for sg in (-1, 1):
        ich.eye(mb, sg)
        ich.nostril(mb, sg)
    obj = mb.to_object(spec.name, roughness=0.45)
    centre(obj)
    return obj


def centre(obj):
    """Moves the pivot to the middle of the bounding box (swimmers pivot at the body centre)."""
    corners = [Vector(c) for c in obj.bound_box]
    c = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= c
