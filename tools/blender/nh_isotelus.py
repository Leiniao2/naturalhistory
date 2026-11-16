"""
Shared body for the Isotelus species (Ordovician asaphid trilobites) in tools/blender/.

Isotelus is an "effaced" trilobite: the head (cephalon) and tail (pygidium) are
large, smooth, gently domed shields on which the glabella and the pygidial axis
are only faint swellings, joined by a short thorax of exactly eight segments
that keeps a clearly raised axial lobe and grooved pleurae. Eyes sit on low
raised lobes towards the back of the cephalon.

  * Spec: proportions, outline shape (semicircular vs. subtriangular ends),
    genal spines (length 0 = none), dome height, eye height, colours.
  * build(spec): one lofted dorsal shell (height field over the outline) on a flat
    underside, plus crisp details: crescent eyes, optional genal spines, short
    antennae and leg tips peeking out under the thorax.
  * Faces -Y, pivot at the body centre (Swim style, like Redlichia), seen mostly from above.
"""

import math
from dataclasses import dataclass

import bmesh
from mathutils import Vector

import nh_model as nh


@dataclass
class Spec:
    name: str
    length: float = 1.6           # front of cephalon to back of pygidium
    ceph_frac: float = 0.34       # fractions of the length (thorax = the rest)
    pyg_frac: float = 0.33
    ceph_w: float = 0.50          # half-width at the genal angles
    thorax_w: float = 0.47        # half-width of the thorax (front; tapers slightly to thorax_w_back)
    thorax_w_back: float = 0.45
    pyg_w: float = 0.46           # half-width at the front of the pygidium
    ceph_p: float = 2.0           # outline: w = W * (1 - t^p)^(1/q); p=q=2 semicircle,
    ceph_q: float = 2.0           #   q -> 1 and p small = subtriangular, pointed
    pyg_p: float = 2.0
    pyg_q: float = 2.0
    dome: float = 0.11            # overall convexity
    axis_h: float = 0.05          # thoracic axial lobe height above the dome
    axis_frac: float = 0.34       # thoracic axis half-width / thorax half-width
    effacement: float = 0.85      # 1 = glabella / pygidial axis fully smoothed away
    border: float = 0.10          # width (fraction) of the flattened shield border
    eye_h: float = 0.035          # height of the palpebral (eye) lobes
    eye_x: float = 0.48           # eye position as a fraction of the cephalon half-width
    eye_y: float = 0.62           # eye position: 0 = back of cephalon, 1 = front
    eye_size: float = 1.0
    genal_spine: float = 0.0      # spine length in model units (0 = rounded genal angle)
    genal_angle: float = 0.0      # small pointed genal corner (no real spine), length
    legs: bool = True
    antenna: float = 0.18
    rows_ceph: int = 18
    rows_seg: int = 5
    rows_pyg: int = 16
    cols: int = 24                # even
    # colours
    shell: tuple = (0.52, 0.36, 0.20)
    shell_light: tuple = (0.72, 0.55, 0.33)
    axis: tuple = (0.40, 0.25, 0.13)
    groove: tuple = (0.22, 0.13, 0.07)
    eye: tuple = (0.10, 0.09, 0.08)
    under: tuple = (0.40, 0.30, 0.19)
    leg: tuple = (0.55, 0.38, 0.22)


SEGMENTS = 8


class Body:
    """Outline + height field for one Spec."""

    def __init__(self, s):
        self.s = s
        self.y_front = -s.length / 2
        self.y_back = s.length / 2
        self.y_ceph = self.y_front + s.length * s.ceph_frac
        self.y_pyg = self.y_back - s.length * s.pyg_frac
        self.seg = (self.y_pyg - self.y_ceph) / SEGMENTS

    # ---------------------------------------------------------------- outline
    def half_width(self, y):
        s = self.s
        if y < self.y_ceph:
            t = (self.y_ceph - y) / (self.y_ceph - self.y_front)
            return max(0.03, s.ceph_w * max(0.0, 1.0 - t ** s.ceph_p) ** (1.0 / s.ceph_q))
        if y < self.y_pyg:
            t = (y - self.y_ceph) / (self.y_pyg - self.y_ceph)
            w = s.thorax_w + (s.thorax_w_back - s.thorax_w) * t
            # pleural tips: each segment's rounded end bulges a little, notched in the furrow
            w -= 0.012 * self.groove(y)
            # step in from the genal angle to the thorax, and out again to the pygidium
            w += (s.ceph_w - s.thorax_w) * math.exp(-((y - self.y_ceph) / 0.02) ** 2) * 0.5
            return w
        t = (y - self.y_pyg) / (self.y_back - self.y_pyg)
        return max(0.03, s.pyg_w * max(0.0, 1.0 - t ** s.pyg_p) ** (1.0 / s.pyg_q))

    def phase(self, y):
        if not (self.y_ceph <= y < self.y_pyg):
            return None
        f = (y - self.y_ceph) / self.seg
        return f - math.floor(f)

    def groove(self, y):
        """1 in the furrows between thoracic segments and at both shield boundaries."""
        p = self.phase(y)
        if p is None:
            return max(math.exp(-((y - self.y_ceph) / 0.012) ** 2),
                       math.exp(-((y - self.y_pyg) / 0.012) ** 2))
        d = min(p, 1.0 - p)
        return math.exp(-(d / 0.12) ** 2)

    def axis_width(self, y):
        """Half-width of the axial lobe (thorax) / faint glabella and pygidial axis."""
        s = self.s
        if y < self.y_ceph:
            t = (self.y_ceph - y) / (self.y_ceph - self.y_front)
            return s.thorax_w * s.axis_frac * (1.0 + 0.15 * t) if t < 0.75 else 0.0
        if y < self.y_pyg:
            t = (y - self.y_ceph) / (self.y_pyg - self.y_ceph)
            return s.axis_frac * (s.thorax_w + (s.thorax_w_back - s.thorax_w) * t)
        t = (y - self.y_pyg) / (self.y_back - self.y_pyg)
        return s.axis_frac * s.thorax_w_back * (1.0 - 0.75 * t) if t < 0.8 else 0.0

    def axis_strength(self, y):
        """1 on the thorax, fading to (1 - effacement) on the smooth shields."""
        s = self.s
        k = 1.0 - s.effacement
        if y < self.y_ceph:
            return k + (1 - k) * math.exp(-((y - self.y_ceph) / 0.05) ** 2)
        if y > self.y_pyg:
            return k + (1 - k) * math.exp(-((y - self.y_pyg) / 0.05) ** 2)
        return 1.0

    def eyes(self):
        s = self.s
        ey = self.y_ceph - s.eye_y * (self.y_ceph - self.y_front) * 0.5
        ex = s.eye_x * self.half_width(ey)
        return [(-ex, ey), (ex, ey)]

    # ---------------------------------------------------------------- height field
    def envelope(self, y):
        """Lengthwise falloff so the shields dip down to their rims at both ends."""
        L = self.s.length / 2
        v = abs(y) / L
        return max(0.0, 1.0 - v ** 3.5) ** 0.45

    def height(self, x, y):
        s = self.s
        w = self.half_width(y)
        u = min(1.0, abs(x) / w)
        env = self.envelope(y)
        h = s.dome * (1.0 - u ** 2) ** 0.6 * env
        # flattened border around the shields: soften the slope near the rim
        if y < self.y_ceph or y > self.y_pyg:
            h += s.dome * 0.06 * nh.smoothstep(1.0 - s.border * 1.6, 1.0 - s.border * 0.4, u) * env
        aw = self.axis_width(y)
        if aw > 0:
            k = self.axis_strength(y)
            h += s.axis_h * k * math.exp(-(x / aw) ** 4) * env ** 0.5
            h -= 0.014 * k * math.exp(-((abs(x) - aw * 1.08) / 0.03) ** 2)   # axial furrows
        # thoracic segment furrows (stronger on the axis), shield boundary grooves
        g = self.groove(y)
        h -= 0.012 * g * (1.0 - 0.4 * u)
        # pleural furrows: a shallow diagonal groove on each pleura
        p = self.phase(y)
        if p is not None and aw > 0 and abs(x) > aw:
            q = (abs(x) - aw) / max(w - aw, 1e-3)
            target = 0.45 + 0.25 * q
            h -= 0.006 * math.exp(-((p - target) / 0.12) ** 2) * (1.0 - q)
        if y < self.y_ceph:
            for ex, ey in self.eyes():
                d = math.hypot((x - ex) / (0.07 * s.eye_size), (y - ey) / (0.10 * s.eye_size))
                h += s.eye_h * math.exp(-d ** 2.5)
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
            k = self.axis_strength(y)
            c = nh.lerp(c, s.axis, k * k * math.exp(-(x / aw) ** 4))
            c = nh.lerp(c, s.groove, 0.55 * k * math.exp(-((abs(x) - aw * 1.08) / 0.03) ** 2))
        if y < self.y_ceph or y > self.y_pyg:
            c = nh.lerp(c, s.shell_light, 0.45 * nh.smoothstep(1.0 - s.border * 1.4, 1.0, u))
        c = nh.lerp(c, s.groove, 0.65 * self.groove(y))
        if y < self.y_ceph:
            for ex, ey in self.eyes():  # pale palpebral lobes
                d = math.hypot((x - ex) / (0.06 * s.eye_size), (y - ey) / (0.09 * s.eye_size))
                c = nh.lerp(c, s.shell_light, 0.6 * math.exp(-d ** 2))
        return c

    # ---------------------------------------------------------------- mesh
    def rows(self):
        s = self.s
        ys = []
        for i in range(s.rows_ceph):
            t = i / s.rows_ceph
            ys.append(self.y_front + (self.y_ceph - self.y_front) * (0.5 - 0.5 * math.cos(t * math.pi)) ** 0.8)
        for k in range(SEGMENTS):
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


def spine(base, tip, r, bend=0.0):
    b, t = Vector(base), Vector(tip)
    mid = (b + t) / 2 + Vector((bend, 0, 0))
    pts = [b, b.lerp(mid, 0.6), mid, mid.lerp(t, 0.6), t]
    return nh.tube(pts, [r, r * 0.8, r * 0.6, r * 0.3, 0.0], sides=6, scale_xy=(1.0, 0.4))


def build(s):
    body = Body(s)
    mb = nh.MeshBuilder()
    mb.add(body.shell(), body.color)

    for sx in (-1, 1):
        w = body.half_width(body.y_ceph - 0.005)
        if s.genal_spine > 0:
            # genal spines continue the cephalon's curved margin back alongside the thorax
            yb = body.y_ceph - 0.12
            wb = body.half_width(yb)
            mb.add(spine((sx * (wb - 0.035), yb, 0.0),
                         (sx * (w + 0.035), body.y_ceph + s.genal_spine, -0.01),
                         0.04, bend=sx * 0.02), s.shell)
        elif s.genal_angle > 0:
            mb.add(spine((sx * (w - 0.04), body.y_ceph - 0.05, -0.002),
                         (sx * (w + 0.01), body.y_ceph + s.genal_angle, -0.01), 0.04), s.shell)

        # crescent eyes: a dark visual surface on the outer flank of each eye lobe
        ex, ey = body.eyes()[0 if sx < 0 else 1]
        arc = []
        for k in range(9):
            a = math.radians(-75 + 150 * k / 8)
            x = ex + sx * 0.05 * s.eye_size * math.cos(a)
            y = ey + 0.075 * s.eye_size * math.sin(a)
            arc.append((x, y, body.height(x, y) + 0.004))
        r = 0.012 * s.eye_size
        mb.add(nh.tube(arc, [r * 0.4, r * 0.8, r, r, r, r, r, r * 0.8, r * 0.4], sides=6), s.eye)

        if s.antenna > 0:
            yf = body.y_front
            mb.add(nh.tube([(sx * 0.06, yf + 0.06, -0.02), (sx * 0.10, yf - 0.04, -0.018),
                            (sx * 0.17, yf - 0.11, -0.012), (sx * 0.25, yf - s.antenna, -0.008)],
                           [0.012, 0.010, 0.007, 0.0], sides=5), s.groove)
        if s.legs:
            # walking-leg tips just peeking out under the pleurae, one pair per segment
            for k in range(SEGMENTS):
                y = body.y_ceph + body.seg * (k + 0.5)
                w = body.half_width(y)
                mb.add(nh.tube([(sx * (w - 0.08), y, -0.03), (sx * (w - 0.005), y + 0.012, -0.04),
                                (sx * (w + 0.025), y + 0.03, -0.055)],
                               [0.013, 0.010, 0.0], sides=4), s.leg)

    obj = mb.to_object(s.name, roughness=0.5)
    zs = [v.co.z for v in obj.data.vertices]
    mid = (min(zs) + max(zs)) / 2
    for v in obj.data.vertices:
        v.co.z -= mid
    return obj
