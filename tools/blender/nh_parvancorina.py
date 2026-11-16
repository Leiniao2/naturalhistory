"""
Shared builder for the Parvancorina species scripts (parvancorina_minchami.py,
parvancorina_sagitta.py). Builds on nh_model.

Parvancorina is a small, low, shield-shaped Ediacaran animal whose upper surface carries a
raised anchor-shaped ridge: a midline ridge running back from near the front, joined at its
front end by a curved transverse ridge whose arms sweep back toward the sides. Either side of
the midline ridge, fine striations run obliquely back and out toward the margin.

The body is one lofted shell (like redlichia.py): rows along Y (front = -Y), columns across X,
a heightfield top joined to a flat underside around the outline. The species scripts only
supply a Shape: outline, anchor-ridge path, proportions and palette.
"""

import math
from dataclasses import dataclass, field

import bmesh
from mathutils import Vector, noise

import nh_model as nh


@dataclass
class Shape:
    name: str
    y_front: float                 # front tip (-Y)
    y_back: float                  # rear tip
    half_width: object             # fn(t) -> half-width, t = 0 at the front, 1 at the rear
    anchor: list                   # right-half polyline [(x, y), ...] of the anchor ridge, from the apex
    ridge_end: float               # y where the midline ridge fades out
    dome: float = 0.07             # overall body dome height
    ridge_h: float = 0.045         # anchor / midline ridge height
    ridge_w: float = 0.030         # ridge half-width (gaussian)
    stripes: int = 16              # lateral striations per side
    stripe_slant: float = 0.55     # how far back a striation runs per unit of x
    rows: int = 64
    cols: int = 28                 # across the whole body (even, so the midline is a column)
    palette: dict = field(default_factory=dict)


# A living, soft-bodied animal, not a fossil cast: the anchor ridge and striations are low swellings
# and creases of the same skin, shown by a slight shade change only (strong pale ridges and dark
# grooves read as a skeleton).
DEFAULT_PALETTE = {
    "body": (0.70, 0.50, 0.40),       # muted pinkish ochre
    "body_light": (0.78, 0.59, 0.47),
    "ridge": (0.80, 0.62, 0.50),      # the anchor swelling, barely lighter than the body
    "ridge_side": (0.64, 0.45, 0.36), # faint shading beside it
    "stripe": (0.65, 0.46, 0.37),     # soft creases
    "rim": (0.76, 0.58, 0.48),        # thin, slightly translucent margin
    "under": (0.62, 0.47, 0.38),
    "mottle": (0.60, 0.42, 0.34),     # blotchy skin pattern
}

UNDER_Z = -0.02


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-12
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy)), t


class Body:
    def __init__(self, shape):
        self.s = shape
        self.pal = dict(DEFAULT_PALETTE, **shape.palette)
        a = shape.anchor
        self.apex_y = a[0][1]
        # cumulative length along the anchor arm, so the ridge can taper toward the arm tips
        self.arm_len = [0.0]
        for p, q in zip(a, a[1:]):
            self.arm_len.append(self.arm_len[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))

    def t_of(self, y):
        s = self.s
        return (y - s.y_front) / (s.y_back - s.y_front)

    def hw(self, y):
        return max(0.01, self.s.half_width(max(0.0, min(1.0, self.t_of(y)))))

    def anchor_dist(self, x, y):
        """(distance to the anchor arm, 0..1 position along it) for the mirrored right half."""
        x = abs(x)
        a = self.s.anchor
        best, pos = 1e9, 0.0
        for i in range(len(a) - 1):
            d, t = _seg_dist(x, y, a[i][0], a[i][1], a[i + 1][0], a[i + 1][1])
            if d < best:
                best = d
                pos = (self.arm_len[i] + t * (self.arm_len[i + 1] - self.arm_len[i])) / self.arm_len[-1]
        return best, pos

    def ridges(self, x, y):
        """0..1 ridge strength of the anchor (transverse arc + midline ridge) at (x, y),
        and a 0..1 'trough' just outside the ridges."""
        s = self.s
        w = s.ridge_w
        d, pos = self.anchor_dist(x, y)
        arc_w = w * (1.0 - 0.45 * pos)                 # the arms thin toward their tips
        arc = math.exp(-(d / arc_w) ** 2) * (1.0 - 0.5 * nh.smoothstep(0.7, 1.0, pos))
        mid = 0.0
        if y > self.apex_y - w:
            fade = nh.smoothstep(s.ridge_end, s.ridge_end - 0.25 * (s.ridge_end - self.apex_y), y)
            mid = math.exp(-(x / (w * 1.15)) ** 2) * fade
        r = max(arc, mid)
        dm = abs(x) if y > self.apex_y else 1e9
        trough = max(math.exp(-((d - arc_w * 1.7) / (arc_w * 0.6)) ** 2),
                     math.exp(-((dm - w * 2.0) / (w * 0.7)) ** 2) * (mid > 0.05))
        return r, trough * (1.0 - r)

    def stripe(self, x, y):
        """Fine lateral striations behind the transverse ridge, between the midline ridge and the
        margin: 0..1 groove strength."""
        s = self.s
        u = abs(x) / self.hw(y)
        span = s.y_back - self.apex_y
        q = (y - self.apex_y - s.stripe_slant * abs(x)) / span * s.stripes
        g = (0.5 + 0.5 * math.cos(q * math.tau)) ** 3.0   # narrow, shallow creases
        d, _ = self.anchor_dist(x, y)
        mask = nh.smoothstep(0.10, 0.22, u) * nh.smoothstep(0.96, 0.82, u)
        mask *= nh.smoothstep(s.ridge_w * 2.2, s.ridge_w * 3.5, d)       # keep clear of the arc
        mask *= nh.smoothstep(self.apex_y, self.apex_y + 0.08, y - s.stripe_slant * abs(x) * 0.3)
        mask *= nh.smoothstep(s.y_back, s.y_back - 0.12, y)
        return g * mask

    def height(self, x, y):
        s = self.s
        w = self.hw(y)
        u = min(1.0, abs(x) / w)
        t = self.t_of(y)
        end = min(1.0, min(t, 1.0 - t) / 0.10) ** 0.5           # round off the front/rear tips
        h = (s.dome * (1.0 - u ** 2.0) ** 0.65 * (1.0 - 0.35 * t) + 0.006) * end
        h += 0.006 * nh.smoothstep(0.86, 0.95, u) * (1.0 - nh.smoothstep(0.95, 1.0, u))  # soft rim
        r, trough = self.ridges(x, y)
        h += s.ridge_h * r * (1.0 - nh.smoothstep(0.85, 1.0, u))
        h -= 0.002 * trough
        return h

    def color(self, co, n):
        p = self.pal
        x, y = co.x, co.y
        w = self.hw(y)
        u = min(1.0, abs(x) / w)
        c = nh.lerp(p["body_light"], p["body"], nh.smoothstep(0.1, 0.85, u))
        m = noise.noise(Vector((x * 5.0, y * 5.0, 3.1)))
        c = nh.lerp(c, p["mottle"], nh.smoothstep(0.15, 0.55, m) * 0.45)
        c = nh.lerp(c, p["stripe"], self.stripe(x, y) * 0.25)
        r, trough = self.ridges(x, y)
        c = nh.lerp(c, p["ridge_side"], trough * 0.3)
        c = nh.lerp(c, p["ridge"], r * 0.6)
        c = nh.lerp(c, p["rim"], nh.smoothstep(0.88, 1.0, u) * 0.6)
        if n.z < -0.3:
            c = p["under"]
        k = 1.0 + 0.06 * noise.noise(co * 20.0)
        return tuple(min(1.0, a * k) for a in c)

    def row_ys(self):
        s = self.s
        ys = []
        L = s.y_back - s.y_front
        for i in range(s.rows + 1):
            t = i / s.rows
            # a little denser at both rounded ends
            ys.append(s.y_front + L * (0.35 * (0.5 - 0.5 * math.cos(t * math.pi)) + 0.65 * t))
        return ys

    def shell(self):
        """Lofted top surface + flat underside, joined around the outline."""
        s = self.s
        bm = bmesh.new()
        ys = self.row_ys()
        top, bl, br = [], [], []
        for y in ys:
            w = self.hw(y)
            row = []
            for j in range(s.cols + 1):
                uu = -1.0 + 2.0 * j / s.cols
                x = math.copysign(abs(uu) ** 0.9, uu) * w
                row.append(bm.verts.new((x, y, self.height(x, y))))
            top.append(row)
            bl.append(bm.verts.new((-w * 0.97, y, UNDER_Z)))
            br.append(bm.verts.new((w * 0.97, y, UNDER_Z)))
        n = len(ys)
        C = s.cols
        for i in range(n - 1):
            for j in range(C):
                bm.faces.new([top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]])
            bm.faces.new([bl[i], bl[i + 1], br[i + 1], br[i]])
            bm.faces.new([bl[i], top[i][0], top[i + 1][0], bl[i + 1]])
            bm.faces.new([br[i], br[i + 1], top[i + 1][C], top[i][C]])
        bm.faces.new([bl[0]] + top[0] + [br[0]])
        bm.faces.new([br[-1]] + list(reversed(top[-1])) + [bl[-1]])
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm


def build(shape):
    body = Body(shape)
    mb = nh.MeshBuilder()
    mb.add(body.shell(), body.color)
    obj = mb.to_object(shape.name, roughness=0.6)
    # pivot at the body centre: centre the thickness on z = 0
    zs = [v.co.z for v in obj.data.vertices]
    mid = (min(zs) + max(zs)) / 2
    for v in obj.data.vertices:
        v.co.z -= mid
    return obj


def arc_anchor(apex_y, half_span, sweep, hook=120.0, n=16):
    """Anchor polyline for the right half: an elliptical arc from the apex on the midline,
    bowed forward, curving out to `half_span` and back by `sweep`; past 90 degrees (up to
    `hook`) the arm curls back and slightly inward, parallel to the margin."""
    pts = []
    for k in range(n + 1):
        a = math.radians(hook) * k / n
        pts.append((half_span * math.sin(a), apex_y + sweep * (1.0 - math.cos(a))))
    return pts
