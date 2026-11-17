"""
Shared body for the Devonian phacopid trilobites (phacops_latifrons.py,
walliserops_trifurcatus.py).

Phacopids have a cephalon dominated by a big, inflated glabella that widens forward,
large schizochroal eyes (separate, big lenses arranged in vertical rows on a
crescent-shaped visual surface), a thorax of 11 segments with a raised axial lobe and
grooved pleurae, and a small rounded pygidium.

  * Spec: proportions, number of segments, glabella inflation, eye size, genal spines,
    optional dorsal spines (axial/pleural), colours.
  * build(spec, extras=None): height-field dorsal shell over the outline on a flat
    underside (as nh_isotelus.py), lens-studded eyes, genal spines, antennae and leg tips;
    extras(mb, body) adds species-specific pieces (e.g. a frontal trident).
  * Faces -Y, pivot at the body centre (Swim style like the other trilobites).
"""

import math
from dataclasses import dataclass

import bmesh
from mathutils import Vector

import nh_model as nh


@dataclass
class Spec:
    name: str
    length: float = 1.6
    ceph_frac: float = 0.34
    pyg_frac: float = 0.18
    segments: int = 11
    ceph_w: float = 0.52
    thorax_w: float = 0.50
    pyg_w: float = 0.36
    dome: float = 0.10
    axis_frac: float = 0.33
    glabella: float = 0.11          # extra height of the inflated glabella
    glabella_w: float = 0.20        # half-width at its front
    eye_size: float = 1.0
    eye_x: float = 0.58
    eye_h: float = 0.08
    genal_spine: float = 0.0
    axial_spines: float = 0.0       # length of a spine on each thoracic axial ring (0 = none)
    pleural_spines: float = 0.0     # length of the free pleural tips (0 = rounded)
    tubercles: float = 0.0          # amount of painted tubercles
    rows_ceph: int = 22
    rows_seg: int = 4
    rows_pyg: int = 10
    cols: int = 28
    shell: tuple = (0.50, 0.38, 0.24)
    shell_light: tuple = (0.70, 0.56, 0.38)
    axis: tuple = (0.42, 0.30, 0.18)
    groove: tuple = (0.18, 0.12, 0.07)
    lens: tuple = (0.16, 0.14, 0.12)
    lens_light: tuple = (0.62, 0.58, 0.50)
    under: tuple = (0.42, 0.33, 0.22)
    leg: tuple = (0.55, 0.40, 0.26)


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
            return max(0.03, s.ceph_w * max(0.0, 1.0 - t ** 2.2) ** 0.5)
        if y < self.y_pyg:
            t = (y - self.y_ceph) / (self.y_pyg - self.y_ceph)
            return s.thorax_w + (s.pyg_w * 1.05 - s.thorax_w) * t ** 1.4 - 0.012 * self.groove(y)
        t = (y - self.y_pyg) / (self.y_back - self.y_pyg)
        return max(0.03, s.pyg_w * max(0.0, 1.0 - t ** 2.0) ** 0.6)

    def phase(self, y):
        if not (self.y_ceph <= y < self.y_pyg):
            return None
        f = (y - self.y_ceph) / self.seg
        return f - math.floor(f)

    def groove(self, y):
        p = self.phase(y)
        if p is None:
            return max(math.exp(-((y - self.y_ceph) / 0.012) ** 2), math.exp(-((y - self.y_pyg) / 0.012) ** 2))
        d = min(p, 1.0 - p)
        return math.exp(-(d / 0.14) ** 2)

    def axis_width(self, y):
        s = self.s
        if y < self.y_ceph:
            # glabella widens forward
            t = (self.y_ceph - y) / (self.y_ceph - self.y_front)
            return (s.thorax_w * s.axis_frac) + (s.glabella_w - s.thorax_w * s.axis_frac) * min(1.0, t * 1.2)
        return s.axis_frac * self.half_width(min(y, self.y_pyg - 1e-4)) * (1.0 if y < self.y_pyg else
                                                                            max(0.0, 1.0 - (y - self.y_pyg) / (self.y_back - self.y_pyg)))

    def eyes(self):
        s = self.s
        ey = self.y_ceph - 0.40 * (self.y_ceph - self.y_front)
        return [(-s.eye_x * self.half_width(ey), ey), (s.eye_x * self.half_width(ey), ey)]

    def envelope(self, y):
        v = abs(y) / (self.s.length / 2)
        return max(0.0, 1.0 - v ** 4) ** 0.45

    def height(self, x, y):
        s = self.s
        w = self.half_width(y)
        u = min(1.0, abs(x) / w)
        env = self.envelope(y)
        h = s.dome * (1.0 - u ** 2) ** 0.6 * env
        aw = self.axis_width(y)
        if y < self.y_ceph:
            # inflated glabella: a big dome over the axis, highest toward the front
            t = (self.y_ceph - y) / (self.y_ceph - self.y_front)
            g = s.glabella * math.sin(math.pi * min(1.0, 0.15 + t * 0.95)) ** 0.6 * nh.smoothstep(0.0, 0.25, t)
            h += g * math.exp(-(x / aw) ** 4)
            h -= 0.02 * math.exp(-((abs(x) - aw * 1.05) / 0.025) ** 2)
            for ex, ey in self.eyes():
                d = math.hypot((x - ex) / (0.08 * s.eye_size), (y - ey) / (0.11 * s.eye_size))
                h += s.eye_h * math.exp(-d ** 2.5)
        elif aw > 0:
            h += 0.05 * math.exp(-(x / aw) ** 4) * env ** 0.5
            h -= 0.014 * math.exp(-((abs(x) - aw * 1.08) / 0.03) ** 2)
        h -= 0.014 * self.groove(y) * (1.0 - 0.4 * u)
        return h

    def color(self, co, n):
        s = self.s
        x, y = co.x, co.y
        if n.z < -0.3:
            return s.under
        w = self.half_width(y)
        u = min(1.0, abs(x) / max(w, 1e-3))
        c = nh.lerp(s.shell_light, s.shell, nh.smoothstep(0.0, 0.85, u))
        aw = self.axis_width(y)
        if aw > 0:
            c = nh.lerp(c, s.axis, 0.7 * math.exp(-(x / aw) ** 4))
            c = nh.lerp(c, s.groove, 0.55 * math.exp(-((abs(x) - aw * 1.08) / 0.03) ** 2))
        c = nh.lerp(c, s.groove, 0.65 * self.groove(y))
        if s.tubercles > 0:
            k = (0.5 + 0.5 * math.sin(x * 90) * math.sin(y * 90)) ** 6
            c = nh.lerp(c, s.shell_light, s.tubercles * k)
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
                x = math.copysign(abs(uu) ** 0.8, uu) * w
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


def spine(base, tip, r, bend=(0, 0, 0)):
    b, t = Vector(base), Vector(tip)
    mid = (b + t) / 2 + Vector(bend)
    pts = [b, b.lerp(mid, 0.6), mid, mid.lerp(t, 0.6), t]
    return nh.tube(pts, [r, r * 0.8, r * 0.6, r * 0.3, 0.0], sides=6)


def build(s, extras=None):
    body = Body(s)
    mb = nh.MeshBuilder()
    mb.add(body.shell(), body.color)
    for sx in (-1, 1):
        if s.genal_spine > 0:
            yb = body.y_ceph - 0.05
            w = body.half_width(yb)
            mb.add(spine((sx * (w - 0.03), yb, 0.0), (sx * (w + 0.06), body.y_ceph + s.genal_spine, -0.02),
                         0.03, bend=(sx * 0.03, 0, 0)), s.shell)
        # schizochroal eye: lenses in rows on the outward-facing crescent
        ex, ey = body.eyes()[0 if sx < 0 else 1]
        r = 0.016 * s.eye_size
        for a_i in range(9):
            a = math.radians(-70 + 140 * a_i / 8)
            for row in range(3):
                rr = 0.055 * s.eye_size * (1.0 - 0.18 * row)
                x = ex + sx * rr * math.cos(a)
                y = ey + 0.085 * s.eye_size * math.sin(a)
                z = body.height(x, y) + 0.004 + row * 0.022 * s.eye_size
                mb.add(nh.ellipsoid((x, y, z), (r, r, r), 1),
                       lambda co, n, c=Vector((x, y, z)): s.lens_light if n.z > 0.6 else s.lens)
        # antennae and leg tips
        yf = body.y_front
        mb.add(nh.tube([(sx * 0.06, yf + 0.06, -0.02), (sx * 0.12, yf - 0.04, -0.018),
                        (sx * 0.22, yf - 0.12, -0.012)], [0.010, 0.008, 0.0], sides=5), s.groove)
        for k in range(s.segments):
            y = body.y_ceph + body.seg * (k + 0.5)
            w = body.half_width(y)
            mb.add(nh.tube([(sx * (w - 0.08), y, -0.03), (sx * (w + 0.02), y + 0.02, -0.05)],
                           [0.010, 0.0], sides=4), s.leg)
            if s.axial_spines > 0:
                aw = body.axis_width(y)
                if sx > 0:
                    z = body.height(0, y)
                    mb.add(spine((0, y, z - 0.01), (0, y + s.axial_spines * 0.5, z + s.axial_spines), 0.012),
                           s.shell)
            if s.pleural_spines > 0:
                mb.add(spine((sx * (w - 0.04), y, -0.002), (sx * (w + s.pleural_spines * 0.6), y + s.pleural_spines,
                                                             -0.01), 0.014), s.shell)
    if extras:
        extras(mb, body)
    obj = mb.to_object(s.name, roughness=0.5)
    vs = obj.data.vertices
    xs, ys, zs = [v.co.x for v in vs], [v.co.y for v in vs], [v.co.z for v in vs]
    off = Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj
