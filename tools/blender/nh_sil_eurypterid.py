"""
Shared parametric chelicerate body for the Silurian batch (tag "sil"): eurypterids
(eurypterus_remipes.py, acutiramus_macrophthalmus.py, slimonia_acuminata.py,
mixopterus_kiaeri.py), the early scorpion proscorpius_osborni.py, the small
Herefordshire chelicerate offacolus_kingi.py and the trigonotarbid palaeotarbus_jerami.py.

One Spec describes:
  * prosoma: rounded-trapezoid / horseshoe head shield (height field over the outline
    on a flat underside) with compound eyes (kidney-shaped, big marginal or tiny
    clusters) and a median ocellar / eye tubercle;
  * opisthosoma: a list of broad preabdominal segment widths and narrow postabdominal
    ones (each an overlapping ring with a paler rear margin); the postabdomen + telson
    can curl up over the back (scorpions, Mixopterus) by bending the finished tail
    geometry along a circular arc;
  * telson: "spike" (long styliform), "blade" (Slimonia's serrated, flattened spatula),
    "paddle" (pterygotid spear-shaped fin), "sting" (bulb + curved aculeus) or "none";
  * appendages: chelicerae (tiny, or the huge toothed pterygotid pincers), scorpion
    pedipalp chelae, walking legs (list of LegSpec: length, spines, splay) and optional
    swimming paddles (appendage VI).
mode "swim": legs splayed flat, pivot at the body centre (Swim style).
mode "ground": legs arch down to z = 0, pivot on the ground (Ground style).
Faces -Y.
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Vector, Matrix, noise

import nh_model as nh


@dataclass
class LegSpec:
    y: float                  # base position along the prosoma (0 = front edge, 1 = back edge)
    length: float
    yaw: float                # degrees: 0 = straight out sideways, negative = forward, positive = back
    spines: int = 1           # spines per podomere
    spine_len: float = 0.03
    r: float = 0.022
    paddle: float = 0.0       # > 0: swimming paddle of this length at the end


@dataclass
class Spec:
    name: str
    mode: str = "swim"
    y_front: float = -0.80
    y_pro: float = -0.48          # back of the prosoma
    pro_wf: float = 0.15          # prosoma half-width near the front / at the back
    pro_wb: float = 0.20
    pro_round: float = 0.30       # fraction of the prosoma length over which the front is rounded
    pro_h: float = 0.06
    pre_len: float = 0.70         # preabdomen length
    pre_w: list = field(default_factory=lambda: [0.21, 0.24, 0.25, 0.25, 0.23, 0.20, 0.16])
    pre_h: float = 0.065
    post_len: float = 0.45
    post_w: list = field(default_factory=lambda: [0.10, 0.09, 0.08, 0.075, 0.07])
    post_round: float = 0.62      # postabdomen height / width
    curl: float = 0.0             # total upward bend of postabdomen + telson (degrees)
    curl_start: float = 0.0       # fraction into the postabdomen where the curl begins
    telson: str = "spike"
    telson_len: float = 0.40
    telson_w: float = 0.03
    eye: str = "kidney"           # kidney | marginal | tubercle | none
    eye_x: float = 0.55           # fraction of the local half-width
    eye_y: float = 0.30           # fraction of the prosoma length from the front
    eye_size: float = 1.0
    chelicera: str = "small"      # small | giant
    claw_len: float = 0.36
    pedipalp: float = 0.0         # scorpion chela arm length (0 = none)
    legs: list = field(default_factory=list)
    leg_lift: float = 0.10        # ground mode: body underside height
    body_dark_line: bool = False  # trigonotarbid: median + lateral plate divisions
    tubercles: float = 0.0        # amount of light tubercle speckles
    # colours
    shell: tuple = (0.42, 0.17, 0.10)
    shell_dark: tuple = (0.24, 0.09, 0.06)
    rim: tuple = (0.72, 0.44, 0.26)
    under: tuple = (0.70, 0.52, 0.36)
    leg: tuple = (0.56, 0.28, 0.15)
    leg_dark: tuple = (0.34, 0.14, 0.08)
    spine: tuple = (0.86, 0.68, 0.46)
    eye_col: tuple = (0.06, 0.05, 0.05)
    pattern: str = "plain"        # plain | spots | bands


class Body:
    def __init__(self, s):
        self.s = s
        self.L = s.y_pro - s.y_front
        self.y_pre = s.y_pro + s.pre_len
        self.y_post = self.y_pre + s.post_len

    def pro_w(self, y):
        s = self.s
        t = max(0.0, min(1.0, (y - s.y_front) / self.L))
        r = max(1e-3, s.pro_round)
        front = math.sqrt(max(0.0, 1.0 - (1.0 - min(1.0, t / r)) ** 2))
        return max(0.012, (s.pro_wf + (s.pro_wb - s.pro_wf) * t) * front)

    def eye_pos(self):
        s = self.s
        y = s.y_front + self.L * s.eye_y
        return s.eye_x * self.pro_w(y), y

    def pro_height(self, x, y):
        s = self.s
        w = self.pro_w(y)
        u = min(1.0, abs(x) / w)
        t = max(0.0, min(1.0, (y - s.y_front) / self.L))
        h = s.pro_h * (1.0 - u ** 2) ** 0.8 * (0.65 + 0.35 * math.sin(t * math.pi * 0.85))
        h += s.pro_h * 0.12 * nh.smoothstep(0.80, 0.93, u) * (1.0 - nh.smoothstep(0.93, 1.0, u))
        if s.eye == "kidney":
            ex, ey = self.eye_pos()
            d = math.hypot((abs(x) - ex) / (0.035 * s.eye_size), (y - ey) / (0.05 * s.eye_size))
            h += 0.02 * s.eye_size * math.exp(-d ** 2)
        if s.eye == "tubercle":
            ey = s.y_front + self.L * s.eye_y
            h += 0.022 * s.eye_size * math.exp(-((x / 0.03) ** 2 + ((y - ey) / 0.035) ** 2))
        return h


def spotty(s, c, co, n):
    if s.pattern == "spots":
        m = noise.noise(co * 14.0 + Vector((3.1, 1.2, 0.4)))
        c = nh.lerp(c, s.shell_dark, 0.75 * nh.smoothstep(0.25, 0.45, m))
    if s.tubercles > 0 and noise.noise(co * 60.0) > 0.42:
        c = nh.lerp(c, s.rim, s.tubercles)
    return c


# ---------------------------------------------------------------- prosoma

def prosoma(b):
    s = b.s
    bm = bmesh.new()
    cols = 18
    ys = [s.y_front + b.L * (1 - math.cos(i / 20 * math.pi / 2)) ** 0.9 for i in range(21)]
    top, bl, br = [], [], []
    for y in ys:
        w = b.pro_w(y)
        row = []
        for j in range(cols + 1):
            uu = -1.0 + 2.0 * j / cols
            x = math.copysign(abs(uu) ** 0.85, uu) * w
            row.append(bm.verts.new((x, y, b.pro_height(x, y))))
        top.append(row)
        bl.append(bm.verts.new((-w * 0.97, y, -0.025)))
        br.append(bm.verts.new((w * 0.97, y, -0.025)))
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

    def color(co, nn):
        w = b.pro_w(co.y)
        u = min(1.0, abs(co.x) / max(w, 1e-3))
        c = nh.lerp(s.shell, s.shell_dark, 0.3 + 0.3 * noise.noise(co * 9.0))
        c = nh.lerp(c, s.rim, 0.75 * nh.smoothstep(0.86, 0.98, u))
        c = spotty(s, c, co, nn)
        if s.body_dark_line and abs(co.x) < 0.006:
            c = s.shell_dark
        if nn.z < -0.3:
            c = s.under
        return c
    return bm, color


# ---------------------------------------------------------------- opisthosoma

def segment(y0, y1, w0, w1, h0, h1, flat, rings=5, sides=20):
    bm = bmesh.new()
    loops = []
    for i in range(rings + 1):
        t = i / rings
        y = y0 + (y1 - y0) * t
        ww = w0 + (w1 - w0) * nh.smoothstep(0.0, 1.0, t)
        hh = h0 + (h1 - h0) * t
        if t > 0.75:
            k = 1.0 + 0.06 * math.sin((t - 0.75) / 0.25 * math.pi * 0.5)
            ww *= k
            hh *= k
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            c, sn = math.cos(a), math.sin(a)
            x = ww * math.copysign(abs(c) ** 0.7, c)
            zz = hh * math.copysign(abs(sn) ** 0.9, sn) * (1.0 if sn > 0 else flat)
            ring.append(bm.verts.new((x, y, zz)))
        loops.append(ring)
    for a, bb in zip(loops, loops[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([a[k], a[j], bb[j], bb[k]])
    bm.faces.new(list(reversed(loops[0])))
    bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def seg_color(s, y0, y1, w):
    def fn(co, n):
        t = (co.y - y0) / (y1 - y0)
        c = nh.lerp(s.shell_dark, s.shell, nh.smoothstep(0.0, 0.35, t))
        c = nh.lerp(c, s.rim, 0.8 * nh.smoothstep(0.78, 0.95, t))
        c = nh.lerp(c, s.shell_dark, 0.25 * (0.5 + 0.5 * noise.noise(co * 10.0)))
        c = spotty(s, c, co, n)
        if s.body_dark_line:
            u = abs(co.x) / max(w, 1e-3)
            if u < 0.04 or abs(u - 0.55) < 0.04:
                c = nh.lerp(c, s.shell_dark, 0.8)
        if n.z < -0.35:
            c = nh.lerp(s.under, s.rim, 0.5 * nh.smoothstep(0.75, 0.95, t))
        return c
    return fn


def preabdomen(mb, b):
    s = b.s
    n = len(s.pre_w)
    seg = s.pre_len / n
    prev = b.pro_w(s.y_pro - 0.01) * 0.98
    for i, wb in enumerate(s.pre_w):
        y0 = s.y_pro + seg * i - 0.025
        y1 = s.y_pro + seg * (i + 1)
        h = s.pre_h * (1.0 - 0.06 * abs(i - n / 2))
        mb.add(segment(y0, y1, prev * 0.95, wb, h * 0.9, h, 0.45, rings=5, sides=22), seg_color(s, y0, y1, wb))
        prev = wb
    return prev


def tail(b, prev):
    """Postabdomen + telson into their own builder (so they can be curled)."""
    s = b.s
    tb = nh.MeshBuilder()
    n = len(s.post_w)
    y_end = b.y_pre
    if n:
        seg = s.post_len / n
        for i, wb in enumerate(s.post_w):
            y0 = b.y_pre + seg * i - 0.02
            y1 = b.y_pre + seg * (i + 1)
            h = wb * s.post_round
            tb.add(segment(y0, y1, prev * 0.88, wb, h * 0.9, h, 0.85, rings=4, sides=16), seg_color(s, y0, y1, wb))
            prev = wb
        y_end = b.y_post
    yT = y_end + s.telson_len
    if s.telson == "spike":
        tb.add(nh.tube([(0, y_end - 0.02, 0), (0, y_end + s.telson_len * 0.3, 0.0),
                        (0, y_end + s.telson_len * 0.8, -0.004), (0, yT, -0.01)],
                       [s.telson_w, s.telson_w * 0.75, s.telson_w * 0.35, 0.0], sides=8, scale_xy=(1.0, 0.7)),
               lambda co, n: nh.lerp(s.shell, s.rim, 0.5 * nh.smoothstep(y_end, yT, co.y)))
    elif s.telson in ("paddle", "blade"):
        pts = []
        m = 14
        for k in range(m + 1):
            t = k / m
            y = y_end - 0.01 + (yT - y_end + 0.01) * t
            if s.telson == "paddle":
                wv = s.telson_w * math.sin(math.pi * min(1.0, t ** 0.8)) ** 0.7 * (1.0 - 0.15 * t) + 0.035 * (1 - t) ** 3
            else:   # long, nearly parallel-sided, serrated, then a short point
                wv = s.telson_w * (0.75 + 0.25 * math.sin(math.pi * t)) * (1.0 - nh.smoothstep(0.75, 1.0, t))
                if 0.1 < t < 0.8:
                    wv *= 1.0 + 0.12 * (k % 2)
            pts.append((max(wv, 0.0), y))
        outline = [(x, y, 0.0) for x, y in pts] + [(-x, y, 0.0) for x, y in reversed(pts[1:-1])]
        tb.add(nh.flat_panel(outline, thickness=0.018),
               lambda co, nn: nh.lerp(s.shell, s.rim, 0.6 * nh.smoothstep(s.telson_w * 0.6, s.telson_w, abs(co.x)))
               if nn.z > -0.3 else s.under, smooth=False)
        tb.add(nh.tube([(0, y_end, 0.006), (0, y_end + 0.12, 0.009), (0, yT - 0.08, 0.004), (0, yT - 0.02, 0.0)],
                       [0.016, 0.013, 0.006, 0.0], sides=6, scale_xy=(1.0, 0.5)), s.shell_dark)
    elif s.telson == "sting":
        r = s.telson_w
        c = Vector((0, y_end + r * 1.1, 0.0))
        tb.add(nh.uv_ellipsoid(tuple(c), (r * 0.9, r * 1.3, r * 0.85), 12, 8),
               lambda co, n: nh.lerp(s.shell, s.rim, 0.4))
        # aculeus curving down (it curls forward once the tail is bent)
        pts = [c + Vector((0, r * 1.0, 0)), c + Vector((0, r * 1.9, -r * 0.3)), c + Vector((0, r * 2.4, -r * 1.0)),
               c + Vector((0, r * 2.4, -r * 1.7))]
        tb.add(nh.tube(pts, [r * 0.42, r * 0.28, r * 0.15, 0.0], sides=7), s.shell_dark)
    if s.curl:
        bend(tb.bm, b.y_pre + s.post_len * s.curl_start, math.radians(s.curl), yT - b.y_pre - s.post_len * s.curl_start)
    return tb.bm


def bend(bm, y0, angle, length):
    """Bends everything behind y0 up over the back along a circular arc of total `angle`."""
    k = angle / max(length, 1e-6)
    for v in bm.verts:
        sdist = v.co.y - y0
        if sdist <= 0:
            continue
        th = k * sdist
        z = v.co.z
        py = y0 + math.sin(th) / k
        pz = (1 - math.cos(th)) / k
        v.co.y = py - z * math.sin(th)
        v.co.z = pz + z * math.cos(th)


# ---------------------------------------------------------------- appendages

def jointed(mb, s, pts, radii, spines=0, spine_len=0.03, sides=7):
    pts = [Vector(p) for p in pts]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ra, rb = radii[i], radii[i + 1]
        mb.add(nh.tube([a, a.lerp(b, 0.5), b], [ra, (ra + rb) * 0.55, rb], sides=sides),
               s.leg if i % 2 == 0 else s.leg_dark)
        if rb > 0:
            mb.add(nh.ellipsoid(b, (rb * 1.1,) * 3, subdivisions=1), s.under)
        d = (b - a).normalized()
        for k in range(spines):
            t = (k + 0.6) / (spines + 0.2)
            base = a.lerp(b, t)
            out = (d * 0.55 + Vector((0, 0, -0.35)) + Vector((0, -0.4, 0))).normalized()
            r = ra + (rb - ra) * t
            mb.add(nh.tube([base, base + out * spine_len], [max(r * 0.45, 0.003), 0.0], sides=4), s.spine,
                   smooth=False)


def legs(mb, b):
    s = b.s
    ground = s.mode == "ground"
    for sx in (-1, 1):
        for L in s.legs:
            y = s.y_front + b.L * L.y
            a = math.radians(L.yaw)
            d = Vector((sx * math.cos(a), math.sin(a), 0.0))
            base = Vector((sx * b.pro_w(y) * 0.45, y, -0.02))
            if ground:
                foot_z = -s.leg_lift - 0.02
                knee = base + d * L.length * 0.38 + Vector((0, 0, 0.07))
                mid = base + d * L.length * 0.70 + Vector((0, 0, 0.02))
                tip = base + d * L.length * 0.92 + Vector((0, 0, foot_z * 0.7))
                claw = base + d * L.length + Vector((0, 0, foot_z + 0.02))
                claw.z = foot_z
            else:
                knee = base + d * L.length * 0.40 + Vector((0, 0, 0.035))
                mid = base + d * L.length * 0.72 + Vector((0, 0, -0.005))
                tip = base + d * L.length + Vector((0, 0, -0.05))
                claw = tip + d * 0.025 + Vector((0, 0, -0.012))
            if L.paddle > 0:
                pts = [base, base + d * L.length * 0.33 + Vector((0, 0, 0.01)), base + d * L.length * 0.66,
                       base + d * L.length]
                jointed(mb, s, pts, [L.r, L.r * 0.9, L.r * 0.8, L.r * 0.75], sides=8)
                dd = (d + Vector((0, 1.0, 0))).normalized()
                centre = pts[-1] + dd * L.paddle * 0.5
                outl = []
                for k in range(18):
                    t = k / 18 * math.tau
                    outl.append((math.cos(t) * L.paddle * 0.24 * (1.0 + 0.25 * math.sin(t)),
                                 math.sin(t) * L.paddle * 0.5 * (1.0 + 0.12 * math.sin(t)), 0.0))
                pb = nh.flat_panel(outl, thickness=0.014)
                nh.transform(pb, Vector((0, 1, 0)).rotation_difference(dd).to_matrix().to_4x4())
                nh.transform(pb, Matrix.Translation(centre))
                mb.add(pb, lambda co, n, c=centre: nh.lerp(s.leg, s.rim,
                       0.7 * nh.smoothstep(0.03, L.paddle * 0.5, (co - c).length)), smooth=False)
                mb.add(nh.tube([pts[-1], pts[-1] + dd * L.paddle * 0.6], [L.r * 0.75, L.r * 0.3], sides=7,
                               scale_xy=(1.0, 0.6)), s.leg_dark)
                continue
            r = L.r
            jointed(mb, s, [base, knee, mid, tip, claw], [r, r * 0.85, r * 0.65, r * 0.45, 0.0],
                    spines=L.spines, spine_len=L.spine_len)


def ramus(mb, s, root, direction, inward, length, r0, hook, teeth, col):
    pts, radii = [], []
    n = 8
    for k in range(n + 1):
        t = k / n
        pts.append(root + direction * length * t + inward * (hook * t ** 3))
        radii.append(r0 * (1.0 - 0.75 * t) + 0.002)
    radii[-1] = 0.0
    mb.add(nh.tube(pts, radii, sides=7, scale_xy=(1.0, 0.7)), col)
    for k in range(teeth):
        t = 0.12 + 0.78 * k / max(1, teeth - 1)
        i = min(n - 1, int(t * n))
        p = pts[i].lerp(pts[i + 1], t * n - i)
        r = radii[i]
        big = 1.0 if k % 3 == 1 else 0.55
        Lt = (0.03 + 0.03 * math.sin(t * math.pi)) * big * length / 0.36
        dd = (inward + direction * 0.35).normalized()
        mb.add(nh.tube([p + inward * r * 0.5, p + inward * r * 0.5 + dd * Lt], [0.006 * big + 0.002, 0.0], sides=4),
               s.spine, smooth=False)


def pincer(mb, s, sx, base, j1, j2, scale, length, teeth, palm_col=None):
    """Peduncle base -> j1 -> j2, a swollen hand and two rami (fixed outer, movable inner)."""
    r = 0.036 * scale
    mb.add(nh.tube([base, (base + j1) / 2, j1], [r, r, r * 0.95], sides=9), s.leg)
    mb.add(nh.ellipsoid(j1, (r * 1.05,) * 3, subdivisions=2), s.under)
    mb.add(nh.tube([j1, (j1 + j2) / 2, j2], [r * 0.95, r * 1.05, r * 1.05], sides=9), s.leg_dark)
    fwd = (j2 - j1).normalized()
    side = Vector((sx, 0, 0))
    inward = (-side - fwd * (-side).dot(fwd)).normalized()
    palm_c = j2 + fwd * 0.06 * scale
    palm = nh.uv_ellipsoid((0, 0, 0), (0.052 * scale, 0.085 * scale, 0.036 * scale), 12, 8)
    nh.transform(palm, Vector((0, -1, 0)).rotation_difference(-fwd).to_matrix().to_4x4())
    nh.transform(palm, Matrix.Translation(palm_c))
    mb.add(palm, palm_col or s.leg)
    tip_root = palm_c + fwd * 0.07 * scale
    open_a = math.radians(24)
    mov_dir = (fwd * math.cos(open_a) + inward * math.sin(open_a)).normalized()
    ramus(mb, s, tip_root + side * 0.024 * scale, fwd, inward, length, 0.026 * scale, 0.05 * scale, teeth, s.leg_dark)
    mov_in = (-inward - mov_dir * (-inward).dot(mov_dir)).normalized()
    ramus(mb, s, tip_root - side * 0.014 * scale, mov_dir, mov_in, length * 0.92, 0.024 * scale, 0.05 * scale,
          max(0, teeth - 1), s.leg_dark)


def chelicerae(mb, b):
    s = b.s
    for sx in (-1, 1):
        if s.chelicera == "giant":
            base = Vector((sx * 0.05, s.y_front + 0.06, -0.015))
            j1 = Vector((sx * 0.08, s.y_front - 0.10, 0.0))
            j2 = Vector((sx * 0.13, s.y_front - 0.24, 0.01))
            pincer(mb, s, sx, base, j1, j2, 1.0, s.claw_len, 12)
        elif s.chelicera == "small":
            p = Vector((sx * 0.025, s.y_front - 0.005, -0.012))
            mb.add(nh.tube([p + Vector((0, 0.03, 0)), p, p + Vector((sx * 0.005, -0.035, -0.005))],
                           [0.016, 0.014, 0.0], sides=6), s.leg_dark)
        if s.pedipalp > 0:
            P = s.pedipalp
            base = Vector((sx * 0.06, s.y_front + 0.05, -0.01))
            j1 = base + Vector((sx * P * 0.45, -P * 0.20, 0.03))
            j2 = j1 + Vector((-sx * P * 0.05, -P * 0.45, 0.0))
            pincer(mb, s, sx, base, j1, j2, P * 1.6, P * 0.55, 0, palm_col=s.shell)


def eyes(mb, b):
    s = b.s
    if s.eye == "kidney":
        for sx in (-1, 1):
            ex, ey = b.eye_pos()
            ex *= sx
            arc = []
            for k in range(6):
                a = math.radians(-60 + 120 * k / 5)
                x = ex + sx * 0.016 * s.eye_size * math.cos(a)
                y = ey + 0.035 * s.eye_size * math.sin(a)
                arc.append((x, y, b.pro_height(x, y) + 0.006))
            r = 0.012 * s.eye_size
            mb.add(nh.tube(arc, [r * 0.5, r * 0.9, r, r, r * 0.9, r * 0.5], sides=6), s.eye_col)
    elif s.eye == "marginal":
        for sx in (-1, 1):
            ex, ey = b.eye_pos()
            ex *= sx
            z = b.pro_height(ex, ey) * 0.6
            mb.add(nh.uv_ellipsoid((ex, ey, z), (0.03 * s.eye_size, 0.045 * s.eye_size, 0.028 * s.eye_size), 10, 7),
                   lambda co, n: s.eye_col if n.z > -0.2 else s.under)
    elif s.eye == "tubercle":
        ey = s.y_front + b.L * s.eye_y
        z = b.pro_height(0, ey)
        for sx in (-1, 1):
            mb.add(nh.ellipsoid((sx * 0.012 * s.eye_size, ey - 0.005, z), (0.010 * s.eye_size,) * 3, 1), s.eye_col)
            # tiny lateral eye clusters at the front corners
            yy = s.y_front + b.L * 0.1
            for k in range(2):
                xx = sx * (b.pro_w(yy) * 0.8 - k * 0.012)
                mb.add(nh.ellipsoid((xx, yy + k * 0.006, b.pro_height(xx, yy) + 0.002), (0.006,) * 3, 1), s.eye_col)
    # ocelli
    if s.eye in ("kidney", "marginal"):
        y = s.y_front + b.L * 0.45
        for sx in (-1, 1):
            mb.add(nh.ellipsoid((sx * 0.01, y, b.pro_height(0.01, y) + 0.002), (0.005, 0.005, 0.004), 1), s.eye_col)


# ---------------------------------------------------------------- build

def build(s):
    b = Body(s)
    mb = nh.MeshBuilder()
    bm, col = prosoma(b)
    mb.add(bm, col)
    prev = preabdomen(mb, b)
    mb.add(tail(b, prev), None)
    mb.add(nh.uv_ellipsoid((0, s.y_pro - b.L * 0.2, -0.035), (0.06, b.L * 0.3, 0.018), 10, 6), s.under)
    legs(mb, b)
    chelicerae(mb, b)
    eyes(mb, b)
    obj = mb.to_object(s.name, roughness=0.5)
    vs = obj.data.vertices
    if s.mode == "ground":
        nh.ground_to_zero(obj)
        ys = [v.co.y for v in vs]
        off = -(min(ys) + max(ys)) / 2
        for v in vs:
            v.co.y += off
    else:
        zs = [v.co.z for v in vs]
        ys = [v.co.y for v in vs]
        off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
        for v in vs:
            v.co += off
    return obj


VIEWS = dict(background=(0.05, 0.20, 0.24), views=((30, 40), (0, 85), (-90, 10)))
GROUND_VIEWS = dict(background=(0.12, 0.14, 0.12), ground=(0.30, 0.26, 0.20), views=((30, 30), (0, 85), (-90, 8)))
