"""
Parametric megalograptid eurypterid (sea scorpion) for the Ordovician batch
(megalograptus_ohioensis.py, pentecopterus_decorahensis.py). Seen mostly from above.

Megalograptids differ from the pterygotids (jaekelopterus_rhenaniae.py) in having small
chelicerae and instead long, robust front walking legs (appendages II-IV) armed with
pairs of very long, movable spines, used as a cage to trap prey; appendage V is short
and appendage VI is the swimming paddle. The opisthosoma has seven broad preabdominal
and five narrow postabdominal segments, ending in a spine-like telson, flanked in
Megalograptus by a pair of serrated cercal blades.

  * Spec: prosoma size/shape, segment widths, leg lengths and spine counts, paddle size,
    telson length, cercal blades, colours.
  * Faces -Y, pivot at the body centre (Swim style).
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Matrix, Vector, noise

import nh_model as nh
from jaekelopterus_rhenaniae import segment   # generic tergite ring


@dataclass
class Spec:
    name: str
    y_front: float = -0.78
    y_pro: float = -0.46
    y_pre: float = 0.28
    y_post: float = 0.66
    telson_len: float = 0.42
    pro_w: float = 0.21            # prosoma half-width at the back
    pro_front: float = 0.70        # front half-width / back half-width
    pro_corner: float = 0.30       # rounding of the front corners (0 = square)
    pre_w: tuple = (0.215, 0.24, 0.25, 0.245, 0.23, 0.20, 0.16)
    post_w: tuple = (0.11, 0.095, 0.085, 0.078, 0.072)
    eye_x: float = 0.13
    eye_y: float = 0.22            # fraction of the prosoma length from the front
    legs: tuple = (0.55, 0.62, 0.62)   # appendages II-IV lengths (spiny raptorial legs)
    leg_spines: int = 5            # spine pairs per leg
    spine_len: float = 0.14
    leg_v: float = 0.30            # appendage V
    paddle: float = 0.15           # paddle half-length
    cercal: float = 0.0            # cercal blade length (0 = none)
    telson_w: float = 0.03
    shell: tuple = (0.45, 0.30, 0.18)
    shell_dark: tuple = (0.27, 0.17, 0.10)
    rim: tuple = (0.70, 0.52, 0.34)
    under: tuple = (0.70, 0.56, 0.40)
    leg: tuple = (0.55, 0.36, 0.20)
    leg_dark: tuple = (0.36, 0.22, 0.12)
    spine: tuple = (0.85, 0.70, 0.48)
    eye: tuple = (0.06, 0.05, 0.05)
    pattern: float = 0.0           # 0..1 strength of dark mottled blotches on tergites


class Eury:
    def __init__(self, s):
        self.s = s

    def pro_half_width(self, y):
        s = self.s
        t = max(0.0, min(1.0, (y - s.y_front) / (s.y_pro - s.y_front)))
        w = s.pro_w * (s.pro_front + (1.0 - s.pro_front) * t)
        front = math.sqrt(max(0.0, 1.0 - (1.0 - min(1.0, t / max(s.pro_corner, 0.05))) ** 2))
        return max(0.012, w * front)

    def eyes(self):
        s = self.s
        y = s.y_front + (s.y_pro - s.y_front) * s.eye_y
        return [(sx * s.eye_x, y) for sx in (-1, 1)]

    def pro_height(self, x, y):
        s = self.s
        w = self.pro_half_width(y)
        u = min(1.0, abs(x) / w)
        t = (y - s.y_front) / (s.y_pro - s.y_front)
        h = 0.06 * (1.0 - u ** 2) ** 0.8 * (0.6 + 0.4 * math.sin(min(1.0, max(0.0, t)) * math.pi * 0.8))
        h += 0.008 * nh.smoothstep(0.80, 0.93, u) * (1.0 - nh.smoothstep(0.93, 1.0, u))
        for ex, ey in self.eyes():
            d = math.hypot((x - ex) / 0.04, (y - ey) / 0.05)
            h += 0.025 * math.exp(-d ** 2)
        return h

    def pro_color(self, co, n):
        s = self.s
        w = self.pro_half_width(co.y)
        u = min(1.0, abs(co.x) / max(w, 1e-3))
        c = nh.lerp(s.shell, s.shell_dark, 0.3 + 0.3 * noise.noise(co * 9.0))
        c = nh.lerp(c, s.rim, 0.75 * nh.smoothstep(0.86, 0.98, u))
        if n.z < -0.3:
            c = s.under
        return c

    def prosoma(self):
        s = self.s
        bm = bmesh.new()
        cols = 18
        ys = [s.y_front + (s.y_pro - s.y_front) * (1 - math.cos(i / 20 * math.pi / 2)) ** 0.9 for i in range(21)]
        top, bl, br = [], [], []
        for y in ys:
            w = self.pro_half_width(y)
            row = []
            for j in range(cols + 1):
                uu = -1.0 + 2.0 * j / cols
                x = math.copysign(abs(uu) ** 0.85, uu) * w
                row.append(bm.verts.new((x, y, self.pro_height(x, y))))
            top.append(row)
            bl.append(bm.verts.new((-w * 0.97, y, -0.025)))
            br.append(bm.verts.new((w * 0.97, y, -0.025)))
        for i in range(len(ys) - 1):
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

    def seg_color(self, y0, y1, i):
        s = self.s

        def fn(co, n):
            t = (co.y - y0) / (y1 - y0)
            c = nh.lerp(s.shell_dark, s.shell, nh.smoothstep(0.0, 0.35, t))
            c = nh.lerp(c, s.rim, 0.8 * nh.smoothstep(0.78, 0.95, t))
            if s.pattern > 0:
                m = noise.noise(Vector((co.x * 7.0, co.y * 4.0, i * 1.3)))
                c = nh.lerp(c, s.shell_dark, s.pattern * nh.smoothstep(0.0, 0.3, m))
            if n.z < -0.35:
                c = s.under
            return c
        return fn

    def opisthosoma(self, mb):
        s = self.s
        seg = (s.y_pre - s.y_pro) / len(s.pre_w)
        prev = self.pro_half_width(s.y_pro - 0.01) * 0.98
        for i, wb in enumerate(s.pre_w):
            y0 = s.y_pro + seg * i - 0.025
            y1 = s.y_pro + seg * (i + 1)
            h = 0.065 - 0.005 * abs(i - 3)
            mb.add(segment(y0, y1, prev * 0.95, wb, h * 0.9, h, 0.45, rings=5, sides=22), self.seg_color(y0, y1, i))
            prev = wb
        seg = (s.y_post - s.y_pre) / len(s.post_w)
        for i, wb in enumerate(s.post_w):
            y0 = s.y_pre + seg * i - 0.02
            y1 = s.y_pre + seg * (i + 1)
            h = wb * 0.62
            mb.add(segment(y0, y1, prev * 0.88, wb, h * 0.9, h, 0.85, rings=4, sides=16),
                   self.seg_color(y0, y1, i + 7))
            prev = wb

    def telson(self, mb):
        s = self.s
        y0, y1 = s.y_post - 0.02, s.y_post + s.telson_len
        mb.add(nh.tube([(0, y0, 0), (0, y0 + 0.1, 0.0), (0, y1 - 0.12, -0.01), (0, y1, -0.015)],
                       [s.telson_w * 1.6, s.telson_w, s.telson_w * 0.6, 0.0], sides=8, scale_xy=(1.0, 0.6)),
               s.shell_dark)
        if s.cercal > 0:
            for sx in (-1, 1):
                pts = []
                n = 10
                for k in range(n + 1):
                    t = k / n
                    pts.append((sx * (0.04 + 0.05 * t) + sx * 0.012 * (k % 2), y0 + s.cercal * t, 0.0))
                inner = [(sx * (0.025 + 0.04 * t), y0 + s.cercal * t, 0.0) for t in [k / n for k in range(n, -1, -1)]]
                mb.add(nh.flat_panel(pts + inner, thickness=0.014), s.shell, smooth=False)

    def jointed(self, mb, pts, radii, spines=0, spine_len=0.1, sx=1):
        s = self.s
        pts = [Vector(p) for p in pts]
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            ra, rb = radii[i], radii[i + 1]
            mb.add(nh.tube([a, a.lerp(b, 0.5), b], [ra, (ra + rb) * 0.55, rb], sides=7),
                   (s.leg, s.leg_dark)[i % 2])
            if rb > 0:
                mb.add(nh.ellipsoid(b, (rb * 1.1,) * 3, subdivisions=1), s.under)
        if spines:
            # paired long spines on the distal podomeres, pointing forward-inward and down
            for k in range(spines):
                t = 0.30 + 0.65 * k / max(1, spines - 1)
                seglen = len(pts) - 1
                f = t * seglen
                i = min(seglen - 1, int(f))
                p = pts[i].lerp(pts[i + 1], f - i)
                d = (pts[i + 1] - pts[i]).normalized()
                inward = Vector((-sx, 0, 0))
                for side in (-1, 1):
                    out = (d * 0.75 + inward * 0.45 * side + Vector((0, 0, -0.25))).normalized()
                    L = spine_len * (0.7 + 0.3 * math.sin(t * math.pi))
                    mb.add(nh.tube([p, p + out * L * 0.5, p + out * L], [0.008, 0.005, 0.0], sides=4),
                           s.spine, smooth=False)

    def legs(self, mb):
        s = self.s
        yaws = (-60, -38, -18)
        bys = (-0.70, -0.64, -0.58)
        for sx in (-1, 1):
            for L, yaw, by in zip(s.legs, yaws, bys):
                a = math.radians(yaw)
                d = Vector((sx * math.cos(a), math.sin(a), 0.0))
                base = Vector((sx * 0.06, by, -0.02))
                knee = base + d * L * 0.35 + Vector((0, 0, 0.04))
                mid = base + d * L * 0.65 + Vector((0, -0.03, 0.0))
                tip = base + d * L + Vector((0, -0.08, -0.04))
                self.jointed(mb, [base, knee, mid, tip], [0.03, 0.026, 0.02, 0.01],
                             spines=s.leg_spines, spine_len=s.spine_len, sx=sx)
            # appendage V: short
            a = math.radians(20)
            d = Vector((sx * math.cos(a), math.sin(a), 0.0))
            base = Vector((sx * 0.07, -0.52, -0.02))
            self.jointed(mb, [base, base + d * s.leg_v * 0.5 + Vector((0, 0, 0.02)), base + d * s.leg_v
                              + Vector((0, 0, -0.03))], [0.025, 0.02, 0.0])
            # appendage VI: swimming paddle
            base = Vector((sx * 0.09, -0.49, -0.02))
            p1 = Vector((sx * 0.22, -0.48, 0.0))
            p2 = Vector((sx * 0.33, -0.43, 0.005))
            self.jointed(mb, [base, p1, p2], [0.034, 0.030, 0.026])
            dd = Vector((sx * 0.5, 1.0, 0.0)).normalized()
            centre = p2 + dd * s.paddle
            pts = []
            for k in range(18):
                ang = k / 18 * math.tau
                pts.append((math.cos(ang) * s.paddle * 0.5, math.sin(ang) * s.paddle, 0.0))
            bm = nh.flat_panel(pts, thickness=0.016)
            nh.transform(bm, Vector((0, 1, 0)).rotation_difference(dd).to_matrix().to_4x4())
            nh.transform(bm, Matrix.Translation(centre))
            mb.add(bm, lambda co, n, c=centre: nh.lerp(s.leg, s.rim, 0.6 * nh.smoothstep(0.03, s.paddle, (co - c).length)),
                   smooth=False)
            # small chelicerae
            mb.add(nh.tube([(sx * 0.03, s.y_front + 0.03, -0.015), (sx * 0.04, s.y_front - 0.04, -0.01),
                            (sx * 0.03, s.y_front - 0.07, -0.012)], [0.018, 0.014, 0.0], sides=6), s.leg_dark)

    def build(self):
        s = self.s
        mb = nh.MeshBuilder()
        mb.add(self.prosoma(), self.pro_color)
        self.opisthosoma(mb)
        self.telson(mb)
        self.legs(mb)
        for ex, ey in self.eyes():
            sx = 1 if ex > 0 else -1
            arc = []
            for k in range(6):
                a = math.radians(-60 + 120 * k / 5)
                x = ex + sx * 0.018 * math.cos(a)
                y = ey + 0.04 * math.sin(a)
                arc.append((x, y, self.pro_height(x, y) + 0.006))
            mb.add(nh.tube(arc, [0.007, 0.013, 0.015, 0.015, 0.013, 0.007], sides=6), s.eye)
        obj = mb.to_object(s.name, roughness=0.5)
        vs = obj.data.vertices
        zs = [v.co.z for v in vs]
        ys = [v.co.y for v in vs]
        off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
        for v in vs:
            v.co += off
        return obj


def build(spec):
    return Eury(spec).build()


VIEWS = dict(background=(0.05, 0.20, 0.24), views=((30, 40), (0, 85), (-90, 10)))
