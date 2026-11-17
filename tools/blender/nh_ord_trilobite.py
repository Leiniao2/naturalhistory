"""
Parametric trilobite body for the Ordovician trilobite batch (asaphus_kowalewskii.py,
ampyx_priscus.py, selenopeltis_buchii.py, ceraurus_pleurexanthemus.py,
flexicalymene_meeki.py). Generalises nh_isotelus.py (which has a fixed eight-segment
thorax and an effaced head) to any number of thoracic segments, a raised and optionally
furrowed glabella, and the spines that set these genera apart.

  * Spec: proportions, outline exponents, segment count, glabella shape (width, forward
    expansion, height, lateral furrows), eyes (lobe, stalk height, or blind), spines
    (genal, pleural, frontal glabellar, pygidial pairs, occipital), colours.
  * build(spec): a lofted dorsal shell (height field over the outline) on a flat
    underside, plus crisp details: eyes / eye stalks, spines, antennae, leg tips.
  * Faces -Y, pivot at the body centre (Swim style, like the Isotelus species).
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Vector

import nh_model as nh


@dataclass
class Spec:
    name: str
    length: float = 1.6           # front of cephalon to back of pygidium (spines excluded)
    segments: int = 8
    ceph_frac: float = 0.34
    pyg_frac: float = 0.25
    ceph_w: float = 0.55          # half-width at the genal angles
    thorax_w: float = 0.50
    thorax_w_back: float = 0.42
    pyg_w: float = 0.38
    ceph_p: float = 2.0           # outline: w = W * (1 - t^p)^(1/q)
    ceph_q: float = 2.0
    pyg_p: float = 2.0
    pyg_q: float = 2.0
    dome: float = 0.08
    axis_frac: float = 0.30       # thoracic axis half-width / thorax half-width
    axis_h: float = 0.07
    pyg_axis: float = 0.8         # pygidial axis length (fraction of pygidium)
    pyg_ribs: int = 4             # rings on the pygidial axis / pleural ribs
    glab_w: float = 0.30          # glabella half-width at the back (fraction of ceph_w)
    glab_front: float = 1.0       # front width / back width (>1 = expanding forward)
    glab_len: float = 0.85        # fraction of the cephalon length
    glab_h: float = 0.09
    glab_furrows: int = 0         # pairs of lateral glabellar furrows
    eye_size: float = 1.0         # 0 = blind
    eye_x: float = 0.55
    eye_y: float = 0.45           # 0 = back of cephalon, 1 = front
    eye_h: float = 0.03           # palpebral lobe height
    eye_stalk: float = 0.0        # stalk height (Asaphus kowalewskii)
    genal_spine: float = 0.0      # length (model units)
    genal_spread: float = 0.15    # outward lean of the genal spines (x per unit length)
    genal_r: float = 0.035
    pleural_spine: float = 0.0    # length of the pleural spines (0 = rounded tips)
    pleural_grow: float = 0.0     # extra length per segment towards the back (fraction)
    pleural_back: float = 0.6     # 0 = straight out, 1 = straight back
    pleural_r: float = 0.022
    frontal_spine: float = 0.0    # glabellar spine forward (Ampyx)
    frontal_rise: float = 0.05
    occipital_spine: float = 0.0
    pyg_spines: list = field(default_factory=list)   # [(x fraction of pyg_w at the root, length, spread)]
    border: float = 0.12          # cephalic border rim
    antenna: float = 0.18
    legs: bool = True
    rows_ceph: int = 18
    rows_seg: int = 4
    rows_pyg: int = 12
    cols: int = 26
    shell: tuple = (0.50, 0.36, 0.22)
    shell_light: tuple = (0.70, 0.55, 0.36)
    axis: tuple = (0.40, 0.27, 0.15)
    groove: tuple = (0.20, 0.13, 0.08)
    eye: tuple = (0.10, 0.09, 0.08)
    under: tuple = (0.42, 0.32, 0.22)
    leg: tuple = (0.55, 0.40, 0.25)
    spine: tuple = None            # defaults to shell


class Body:
    def __init__(self, s):
        self.s = s
        self.y_front = -s.length / 2
        self.y_back = s.length / 2
        self.y_ceph = self.y_front + s.length * s.ceph_frac
        self.y_pyg = self.y_back - s.length * s.pyg_frac
        self.seg = (self.y_pyg - self.y_ceph) / s.segments

    def half_width(self, y):
        s = self.s
        if y < self.y_ceph:
            t = (self.y_ceph - y) / (self.y_ceph - self.y_front)
            return max(0.02, s.ceph_w * max(0.0, 1.0 - t ** s.ceph_p) ** (1.0 / s.ceph_q))
        if y < self.y_pyg:
            t = (y - self.y_ceph) / (self.y_pyg - self.y_ceph)
            w = s.thorax_w + (s.thorax_w_back - s.thorax_w) * t
            w -= 0.012 * self.groove(y)
            return w
        t = (y - self.y_pyg) / (self.y_back - self.y_pyg)
        return max(0.02, s.pyg_w * max(0.0, 1.0 - t ** s.pyg_p) ** (1.0 / s.pyg_q))

    def phase(self, y):
        if not (self.y_ceph <= y < self.y_pyg):
            return None
        f = (y - self.y_ceph) / self.seg
        return f - math.floor(f)

    def groove(self, y):
        p = self.phase(y)
        if p is None:
            return max(math.exp(-((y - self.y_ceph) / 0.010) ** 2),
                       math.exp(-((y - self.y_pyg) / 0.010) ** 2))
        d = min(p, 1.0 - p)
        return math.exp(-(d / 0.13) ** 2)

    def pyg_groove(self, y):
        s = self.s
        if y <= self.y_pyg or s.pyg_ribs <= 0:
            return 0.0
        t = (y - self.y_pyg) / ((self.y_back - self.y_pyg) * s.pyg_axis)
        if t > 1.0:
            return 0.0
        f = t * s.pyg_ribs
        d = min(f - math.floor(f), 1 - (f - math.floor(f)))
        return math.exp(-(d / 0.14) ** 2) * (1.0 - t)

    def glabella(self, x, y):
        """0..1 glabella mask on the cephalon."""
        s = self.s
        clen = self.y_ceph - self.y_front
        y0 = self.y_ceph - clen * s.glab_len
        if y < y0 - 0.05 or y > self.y_ceph:
            return 0.0
        t = (self.y_ceph - y) / (clen * s.glab_len)          # 0 back, 1 front
        gw = s.ceph_w * s.glab_w * (1.0 + (s.glab_front - 1.0) * min(1.0, t))
        # rounded front
        front = 1.0 - nh.smoothstep(0.75, 1.05, t)
        w = gw * max(0.05, math.sqrt(max(0.0, 1.0 - max(0.0, (t - 0.7) / 0.35) ** 2)))
        return math.exp(-(x / max(w, 1e-3)) ** 6) * (front if t > 0.75 else 1.0)

    def axis_width(self, y):
        s = self.s
        if self.y_ceph <= y < self.y_pyg:
            t = (y - self.y_ceph) / (self.y_pyg - self.y_ceph)
            return s.axis_frac * (s.thorax_w + (s.thorax_w_back - s.thorax_w) * t)
        if y >= self.y_pyg:
            t = (y - self.y_pyg) / ((self.y_back - self.y_pyg) * s.pyg_axis)
            return s.axis_frac * s.thorax_w_back * (1.0 - 0.7 * t) if t < 1.0 else 0.0
        return 0.0

    def eyes(self):
        s = self.s
        ey = self.y_ceph - s.eye_y * (self.y_ceph - self.y_front)
        ex = s.eye_x * self.half_width(ey)
        return [(-ex, ey), (ex, ey)]

    def envelope(self, y):
        L = self.s.length / 2
        v = abs(y) / L
        return max(0.0, 1.0 - v ** 4) ** 0.5

    def height(self, x, y):
        s = self.s
        w = self.half_width(y)
        u = min(1.0, abs(x) / w)
        env = self.envelope(y)
        h = s.dome * (1.0 - u ** 2) ** 0.7 * env
        if y < self.y_ceph:
            # raised cephalic border with a furrow inside it
            h += s.dome * 0.25 * nh.smoothstep(1.0 - s.border, 1.0 - s.border * 0.3, u) * (1 - nh.smoothstep(0.97, 1.0, u))
            g = self.glabella(x, y)
            h += s.glab_h * g * env ** 0.3
            if s.glab_furrows and g > 0.05:
                clen = (self.y_ceph - self.y_front) * s.glab_len
                t = (self.y_ceph - y) / clen
                f = t * (s.glab_furrows + 1.2)
                d = min(f - math.floor(f), 1 - (f - math.floor(f)))
                side = nh.smoothstep(0.15, 0.6, abs(x) / max(s.ceph_w * s.glab_w, 1e-3))
                h -= 0.03 * math.exp(-(d / 0.12) ** 2) * side * g * (1 if 0.12 < t < 0.85 else 0)
            # occipital furrow
            h -= 0.02 * math.exp(-((y - (self.y_ceph - 0.04)) / 0.012) ** 2) * g
            if s.eye_size > 0:
                for ex, ey in self.eyes():
                    d = math.hypot((x - ex) / (0.07 * s.eye_size), (y - ey) / (0.09 * s.eye_size))
                    h += s.eye_h * math.exp(-d ** 2.5)
        aw = self.axis_width(y)
        if aw > 0:
            h += s.axis_h * math.exp(-(x / aw) ** 4) * env ** 0.5
            h -= 0.016 * math.exp(-((abs(x) - aw * 1.08) / 0.025) ** 2)
        g = self.groove(y)
        h -= 0.016 * g * (1.0 - 0.3 * u)
        h -= 0.010 * self.pyg_groove(y)
        p = self.phase(y)
        if p is not None and aw > 0 and abs(x) > aw:
            q = (abs(x) - aw) / max(w - aw, 1e-3)
            h -= 0.008 * math.exp(-((p - (0.45 + 0.2 * q)) / 0.12) ** 2) * (1.0 - q)
        return h

    def color(self, co, n):
        s = self.s
        x, y = co.x, co.y
        if n.z < -0.3:
            return s.under
        w = self.half_width(y)
        u = min(1.0, abs(x) / max(w, 1e-3))
        c = nh.lerp(s.shell_light, s.shell, nh.smoothstep(0.0, 0.9, u))
        aw = self.axis_width(y)
        if aw > 0:
            c = nh.lerp(c, s.axis, math.exp(-(x / aw) ** 4))
            c = nh.lerp(c, s.groove, 0.6 * math.exp(-((abs(x) - aw * 1.08) / 0.025) ** 2))
        if y < self.y_ceph:
            g = self.glabella(x, y)
            c = nh.lerp(c, s.axis, 0.85 * g)
            c = nh.lerp(c, s.shell_light, 0.5 * nh.smoothstep(1.0 - s.border * 0.8, 1.0, u))
        c = nh.lerp(c, s.groove, 0.7 * self.groove(y))
        c = nh.lerp(c, s.groove, 0.5 * self.pyg_groove(y))
        return c

    def rows(self):
        s = self.s
        ys = []
        for i in range(s.rows_ceph):
            t = i / s.rows_ceph
            ys.append(self.y_front + (self.y_ceph - self.y_front) * (0.5 - 0.5 * math.cos(t * math.pi)) ** 0.8)
        for k in range(s.segments):
            for r in range(s.rows_seg):
                ys.append(self.y_ceph + self.seg * (k + r / s.rows_seg))
        for i in range(s.rows_pyg + 1):
            t = i / s.rows_pyg
            ys.append(self.y_back - (self.y_back - self.y_pyg) * (0.5 - 0.5 * math.cos((1 - t) * math.pi)) ** 0.8)
        return ys

    def shell(self):
        s = self.s
        bm = bmesh.new()
        ys = self.rows()
        cols = s.cols
        top, bl, br = [], [], []
        zb = -0.025
        for y in ys:
            w = self.half_width(y)
            row = []
            for j in range(cols + 1):
                uu = -1.0 + 2.0 * j / cols
                x = math.copysign(abs(uu) ** 0.85, uu) * w
                row.append(bm.verts.new((x, y, self.height(x, y))))
            top.append(row)
            bl.append(bm.verts.new((-w * 0.97, y, zb)))
            br.append(bm.verts.new((w * 0.97, y, zb)))
        n = len(ys)
        for i in range(n - 1):
            for j in range(cols):
                bm.faces.new([top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]])
            bm.faces.new([bl[i], bl[i + 1], br[i + 1], br[i]])
            bm.faces.new([bl[i], top[i][0], top[i + 1][0], bl[i + 1]])
            bm.faces.new([br[i], br[i + 1], top[i + 1][cols], top[i][cols]])
        bm.faces.new([bl[0]] + top[0] + [br[0]])
        bm.faces.new([br[-1]] + list(reversed(top[-1])) + [bl[-1]])
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm


def spine(base, tip, r, bend=(0.0, 0.0, 0.0), sides=6, flat=0.55):
    b, t = Vector(base), Vector(tip)
    mid = (b + t) / 2 + Vector(bend)
    pts = [b, b.lerp(mid, 0.5), mid, mid.lerp(t, 0.5), t]
    return nh.tube(pts, [r, r * 0.8, r * 0.6, r * 0.35, 0.0], sides=sides, scale_xy=(1.0, flat))


def build(s):
    body = Body(s)
    sc = s.spine or s.shell
    mb = nh.MeshBuilder()
    mb.add(body.shell(), body.color)

    for sx in (-1, 1):
        # genal spines continue the cephalic margin backwards
        if s.genal_spine > 0:
            yb = body.y_ceph - 0.06
            w = body.half_width(yb)
            tip = (sx * (w + s.genal_spread * s.genal_spine), body.y_ceph + s.genal_spine, -0.01)
            mb.add(spine((sx * (w - 0.03), yb, 0.0), tip, s.genal_r,
                         bend=(sx * 0.03 * s.genal_spine, 0, 0)), sc)
        # pleural spines, one per thoracic segment
        if s.pleural_spine > 0:
            for k in range(s.segments):
                y = body.y_ceph + body.seg * (k + 0.5)
                w = body.half_width(y)
                L = s.pleural_spine * (1.0 + s.pleural_grow * k)
                a = math.radians(90 * s.pleural_back * (0.6 + 0.4 * k / max(1, s.segments - 1)))
                d = Vector((sx * math.cos(a), math.sin(a), -0.05))
                base = Vector((sx * (w - 0.04), y, body.height(sx * (w - 0.04), y) * 0.5))
                mb.add(spine(base, base + d * L, s.pleural_r,
                             bend=(0, 0.08 * L * (1 - s.pleural_back), 0)), sc)
        # eyes
        if s.eye_size > 0:
            ex, ey = body.eyes()[0 if sx < 0 else 1]
            zb = body.height(ex, ey)
            if s.eye_stalk > 0:
                top = Vector((ex + sx * 0.01, ey - 0.01, zb + s.eye_stalk))
                mb.add(nh.tube([(ex, ey, zb - 0.01), (ex, ey, zb + s.eye_stalk * 0.5), top],
                               [0.04 * s.eye_size, 0.03 * s.eye_size, 0.028 * s.eye_size], sides=8), s.shell)
                mb.add(nh.uv_ellipsoid(tuple(top + Vector((0, 0, 0.02 * s.eye_size))),
                                       (0.045 * s.eye_size, 0.05 * s.eye_size, 0.04 * s.eye_size), 10, 6),
                       lambda co, n: s.eye if n.z < 0.75 else s.shell_light)
            else:
                arc = []
                for k in range(9):
                    a = math.radians(-75 + 150 * k / 8)
                    x = ex + sx * 0.045 * s.eye_size * math.cos(a)
                    y = ey + 0.07 * s.eye_size * math.sin(a)
                    arc.append((x, y, body.height(x, y) + 0.004))
                r = 0.014 * s.eye_size
                mb.add(nh.tube(arc, [r * 0.4, r * 0.8, r, r, r, r, r, r * 0.8, r * 0.4], sides=6), s.eye)
        if s.antenna > 0:
            yf = body.y_front
            mb.add(nh.tube([(sx * 0.06, yf + 0.06, -0.02), (sx * 0.10, yf - 0.04, -0.018),
                            (sx * 0.17, yf - 0.11, -0.012), (sx * 0.25, yf - s.antenna, -0.008)],
                           [0.012, 0.010, 0.007, 0.0], sides=5), s.groove)
        if s.legs:
            for k in range(s.segments):
                y = body.y_ceph + body.seg * (k + 0.5)
                w = body.half_width(y)
                mb.add(nh.tube([(sx * (w - 0.08), y, -0.03), (sx * (w - 0.005), y + 0.012, -0.04),
                                (sx * (w + 0.025), y + 0.03, -0.055)],
                               [0.013, 0.010, 0.0], sides=4), s.leg)
        for xf, L, spread in s.pyg_spines:
            y = body.y_pyg + (body.y_back - body.y_pyg) * 0.3
            w = body.half_width(y) * xf
            base = Vector((sx * w, y, body.height(sx * w, y) * 0.5))
            mb.add(spine(base, base + Vector((sx * spread * L, L, -0.01)), s.pleural_r * 1.3), sc)

    if s.frontal_spine > 0:
        clen = body.y_ceph - body.y_front
        y0 = body.y_ceph - clen * s.glab_len * 0.8
        z0 = body.height(0, y0)
        mb.add(spine((0, y0, z0 - 0.01), (0, body.y_front - s.frontal_spine, z0 + s.frontal_rise),
                     s.genal_r * 1.1, flat=1.0), sc)
    if s.occipital_spine > 0:
        y0 = body.y_ceph - 0.05
        z0 = body.height(0, y0)
        mb.add(spine((0, y0, z0 - 0.01), (0, y0 + s.occipital_spine, z0 + s.occipital_spine * 0.5),
                     0.03, flat=1.0), sc)

    obj = mb.to_object(s.name, roughness=0.5)
    vs = obj.data.vertices
    zs = [v.co.z for v in vs]
    ys = [v.co.y for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


VIEWS = dict(background=(0.05, 0.18, 0.22), views=((30, 40), (0, 85), (-90, 12)))
