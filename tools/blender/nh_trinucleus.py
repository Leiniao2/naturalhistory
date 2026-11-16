"""
Shared procedural body for trinucleid trilobites (Trinucleus, Tretaspis...).

A small three-lobed shell dominated by a big horseshoe-shaped cephalon: a
swollen pear-shaped glabella flanked by convex cheeks, all ringed by a broad
pitted fringe (concentric rows of pits, done as vertex-aligned dimples plus dark
vertex-colour dots so they read at map size), long genal spines sweeping back
from the rear corners, a short thorax of six segments with blunt pleurae and a
small triangular pygidium. No eyes (optionally small eye tubercles).

Species scripts pass a params dict to build(params) - see DEFAULTS.
Faces -Y, pivot at the body centre (Swim style, like Redlichia), seen mostly
from above.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

DEFAULTS = dict(
    name="Trinucleus",
    # colours
    shell=(0.52, 0.38, 0.24),
    shell_light=(0.74, 0.60, 0.42),
    axis=(0.44, 0.29, 0.17),
    groove=(0.22, 0.14, 0.08),
    pit=(0.12, 0.08, 0.05),
    fringe=(0.68, 0.55, 0.38),
    under=(0.40, 0.30, 0.20),
    # layout along Y (front = -Y)
    ceph_w=0.42,          # half width of the cephalon incl. fringe (at the genal corners)
    ceph_l=0.44,          # cephalon length incl. fringe
    fringe_w=0.11,        # fringe width at the front
    fringe_w_side=0.09,   # fringe width at the genal corners
    thorax_l=0.20,
    pyg_l=0.13,
    thorax_w=0.27,        # thorax half width at the front
    thorax_w_back=0.22,
    segments=6,
    # relief
    glabella_h=0.13,      # inflation of the glabella above the cheeks
    glabella_w=0.12,      # max half width of the glabella (towards its front)
    cheek_h=0.07,
    fringe_slope=0.02,    # drop from inner to outer fringe edge (bigger = steeper brim)
    fringe_droop=0.0,     # extra drop of the outer part (a sloping brim)
    # pits: list of pit rows from outer (0) to inner (1) as fractions across the fringe
    pit_rows=(0.16, 0.39, 0.62, 0.85),
    pits_per_row=34,
    pit_depth=0.006,
    girder=None,          # fraction across the fringe of a raised ridge (Tretaspis), or None
    eye_tubercles=False,
    median_tubercle=False,
    # genal spines
    spine_len=0.95,       # how far back the tip reaches behind the cephalon
    spine_r=0.026,
    spine_spread=0.10,    # outward drift of the tip
)


class Trinucleid:
    def __init__(self, p):
        self.p = p
        self.y_ceph = -0.10                       # cephalon / thorax boundary
        self.y_front = self.y_ceph - p["ceph_l"]
        self.y_pyg = self.y_ceph + p["thorax_l"]
        self.y_back = self.y_pyg + p["pyg_l"]
        # inner (non-fringe) part of the cephalon: a half ellipse
        self.wi = p["ceph_w"] - p["fringe_w_side"]
        self.li = p["ceph_l"] - p["fringe_w"]

    # ------------------------------------------------------------ outline
    def half_width(self, y):
        p = self.p
        if y < self.y_ceph:
            t = (self.y_ceph - y) / self.li
            return max(0.012, self.wi * math.sqrt(max(0.0, 1.0 - min(1.0, t) ** 2.4)))
        if y < self.y_pyg:
            t = (y - self.y_ceph) / p["thorax_l"]
            return p["thorax_w"] + (p["thorax_w_back"] - p["thorax_w"]) * t
        t = (y - self.y_pyg) / p["pyg_l"]
        # triangular pygidium with a slightly rounded tip
        t = min(1.0, t)
        return max(0.008, p["thorax_w_back"] * (1.0 - t) ** 0.9 * (1.0 - 0.2 * t) + 0.03 * math.sqrt(max(0.0, 1 - t * t)))

    def axis_width(self, y):
        p = self.p
        if y < self.y_ceph:
            # pear-shaped glabella: narrow at the neck, bulbous in front
            t = (self.y_ceph - y) / self.li          # 0 at the back, 1 at the inner front
            if t > 0.97:
                return 0.0
            return p["glabella_w"] * (0.45 + 0.55 * math.sin(min(1.0, t / 0.8) * math.pi * 0.62))
        if y < self.y_pyg:
            return 0.072
        t = (y - self.y_pyg) / p["pyg_l"]
        return 0.072 * (1.0 - 0.85 * t)

    def segment_phase(self, y):
        if not (self.y_ceph <= y < self.y_pyg):
            return None
        f = (y - self.y_ceph) / self.p["thorax_l"] * self.p["segments"]
        return f - math.floor(f)

    def groove(self, y):
        ph = self.segment_phase(y)
        if ph is None:
            g = math.exp(-((y - self.y_pyg) / 0.008) ** 2) + 0.5 * math.exp(-((y - self.y_ceph - 0.006) / 0.009) ** 2)
            if y > self.y_pyg:  # pygidial rings
                f = (y - self.y_pyg) / self.p["pyg_l"] * 4
                d = min(f - math.floor(f), 1 - (f - math.floor(f)))
                g = max(g, 0.5 * math.exp(-(d / 0.12) ** 2) * (1 - (y - self.y_pyg) / self.p["pyg_l"]))
            return min(1.0, g)
        d = min(ph, 1.0 - ph)
        return math.exp(-(d / 0.13) ** 2)

    def glabella(self, x, y):
        """0..1 mask of the pear-shaped glabella (narrow neck at the back, bulb in front)."""
        aw = self.axis_width(y)
        if aw <= 0:
            return 0.0
        t = (self.y_ceph - y) / self.li
        front = 1.0 - nh.smoothstep(0.82, 1.02, t)
        return math.exp(-(x / aw) ** 2 * 1.3) * front

    def glabella_profile(self, t):
        """Height profile along the glabella: low neck, swollen bulb ahead of mid-length."""
        return 0.35 * nh.smoothstep(-0.05, 0.3, t) + 0.65 * math.exp(-((t - 0.62) / 0.33) ** 2)

    def tubercles(self):
        p = self.p
        out = []
        if p["eye_tubercles"]:
            for sx in (-1, 1):
                out.append((sx * self.wi * 0.55, self.y_ceph - self.li * 0.45, 0.032, 0.020))
        if p["median_tubercle"]:
            out.append((0.0, self.y_ceph - self.li * 0.45, 0.022, 0.016))
        return out

    def height(self, x, y):
        p = self.p
        w = self.half_width(y)
        u = min(1.0, abs(x) / w)
        if y < self.y_ceph:
            # convex cheeks: an elliptical dome falling to the fringe all round the front
            t = (self.y_ceph - y) / self.li
            r = min(1.0, math.hypot(x / self.wi, t))
            g = self.glabella(x, y)
            back = 0.45 + 0.55 * nh.smoothstep(0.0, 0.12, t)       # cheeks slope into the rear margin
            h = 0.03 + p["cheek_h"] * (1.0 - r ** 2) ** 0.5 * (back + (1 - back) * g)
            h += p["glabella_h"] * g * self.glabella_profile(t)
            aw = max(self.axis_width(y), 1e-3)
            h -= 0.010 * math.exp(-((abs(x) - aw * 1.25) / 0.03) ** 2) * (1 - nh.smoothstep(0.8, 1.0, t))
            for tx, ty, rr, th in self.tubercles():
                d = math.hypot(x - tx, y - ty) / rr
                h += th * math.exp(-d * d)
            # posterior border furrow
            h -= 0.006 * math.exp(-((y - (self.y_ceph - 0.022)) / 0.014) ** 2)
            return h
        h = 0.035 * (1.0 - u ** 2) ** 0.6 + 0.012
        aw = self.axis_width(y)
        h += 0.038 * math.exp(-(x / aw) ** 2 * 1.5)
        if y > self.y_pyg:
            h *= 1.0 - 0.55 * (y - self.y_pyg) / self.p["pyg_l"]
        h -= 0.012 * self.groove(y) * (1.0 - 0.4 * u)
        h -= 0.012 * math.exp(-((abs(x) - aw * 1.15) / 0.018) ** 2)
        return h

    def body_color(self, co, n):
        p = self.p
        x, y = co.x, co.y
        if n.z < -0.4:
            return p["under"]
        w = self.half_width(y)
        u = min(1.0, abs(x) / max(w, 1e-3))
        c = nh.lerp(p["shell_light"], p["shell"], nh.smoothstep(0.1, 0.95, u))
        aw = self.axis_width(y)
        if aw > 0:
            k = self.glabella(x, y) if y < self.y_ceph else math.exp(-(x / aw) ** 2 * 1.5)
            c = nh.lerp(c, p["axis"], k)
            c = nh.lerp(c, p["groove"], 0.3 * math.exp(-((abs(x) - aw * 1.25) / 0.032) ** 2))
        c = nh.lerp(c, p["groove"], 0.65 * self.groove(y))
        if y < self.y_ceph:
            c = nh.lerp(c, p["groove"], 0.3 * math.exp(-((y - (self.y_ceph - 0.025)) / 0.012) ** 2))
            c = nh.lerp(c, p["groove"], 0.55 * nh.smoothstep(0.9, 1.0, u))  # fringe furrow
            for tx, ty, r, _th in self.tubercles():
                d = math.hypot(x - tx, y - ty) / r
                c = nh.lerp(c, p["shell_light"], 0.6 * math.exp(-d * d * 2))
        return c

    # ------------------------------------------------------------ body shell
    def rows(self):
        ys = []
        nc = 16
        for i in range(nc):
            t = i / nc
            ys.append(self.y_front + self.p["fringe_w"] + self.li * (1 - math.cos(t * math.pi / 2)) ** 0.75)
        ys += [self.y_ceph - 0.036, self.y_ceph - 0.012]  # posterior border
        seg = self.p["thorax_l"] / self.p["segments"]
        for s in range(self.p["segments"]):
            for k in (0.0, 0.25, 0.5, 0.75):
                ys.append(self.y_ceph + seg * (s + k))
        for i in range(8):
            ys.append(self.y_pyg + self.p["pyg_l"] * i / 7)
        return sorted(ys)

    def body(self, cols=26):
        bm = bmesh.new()
        ys = self.rows()
        top, bl, br = [], [], []
        for y in ys:
            w = self.half_width(y)
            row = []
            for j in range(cols + 1):
                uu = -1.0 + 2.0 * j / cols
                x = math.copysign(abs(uu) ** 0.9, uu) * w
                row.append(bm.verts.new((x, y, self.height(x, y))))
            top.append(row)
            bl.append(bm.verts.new((-w * 0.97, y, -0.02)))
            br.append(bm.verts.new((w * 0.97, y, -0.02)))
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

    # ------------------------------------------------------------ pitted fringe
    def fringe_point(self, theta, s):
        """theta: -90..90 deg around the cephalon (0 = front); s: 0 outer .. 1 inner edge."""
        p = self.p
        a = math.radians(theta)
        side = abs(math.sin(a))
        fw = p["fringe_w"] * (1 - side) + p["fringe_w_side"] * side
        fw *= 1.0 - 0.35 * nh.smoothstep(75.0, 92.0, abs(theta))
        # outer half-ellipse, slightly squarer than a true ellipse
        ox = p["ceph_w"] * math.copysign(abs(math.sin(a)) ** 0.85, a)
        ca = math.cos(a)
        oy = self.y_ceph - p["ceph_l"] * math.copysign(abs(ca) ** 0.9, ca)
        nrm = Vector((math.sin(a) / p["ceph_w"], -math.cos(a) / p["ceph_l"], 0)).normalized()
        q = Vector((ox, oy, 0)) - nrm * fw * s
        # inner edge tucks a touch under the cheeks
        q -= nrm * 0.012 * nh.smoothstep(0.9, 1.0, s)
        return q

    def fringe_height(self, s):
        p = self.p
        h = 0.028 - p["fringe_slope"] * (1 - s) - p["fringe_droop"] * (1 - s) ** 2
        if p["girder"] is not None:
            h += 0.010 * math.exp(-((s - p["girder"]) / 0.07) ** 2)
        return h

    def fringe(self):
        p = self.p
        rows = sorted(p["pit_rows"])
        # rings: outer edge, then each pit row with a ring halfway between neighbours, inner edge
        ss = [0.0]
        prev = 0.0
        for r in rows:
            ss.append((prev + r) / 2)
            ss.append(r)
            prev = r
        ss.append((prev + 1.0) / 2)
        ss.append(1.0)
        if p["girder"] is not None:
            ss = sorted(set(ss + [p["girder"] - 0.05, p["girder"], p["girder"] + 0.05]))
        na = p["pits_per_row"] * 2
        thetas = [-92.0 + 184.0 * j / na for j in range(na + 1)]
        bm = bmesh.new()
        grid = []
        cols = {}
        for i, s in enumerate(ss):
            ring = []
            row_idx = rows.index(s) if s in rows else None
            for j, th in enumerate(thetas):
                q = self.fringe_point(th, s)
                z = self.fringe_height(s)
                dark = 0.0
                # pits sit in concentric AND radial rows, on every other vertex
                if row_idx is not None and j % 2 == 1:
                    z -= p["pit_depth"]
                    dark = 1.0
                v = bm.verts.new((q.x, q.y, z))
                base = nh.lerp(p["fringe"], p["shell"], 0.35 * (1 - s))
                if p["girder"] is not None:
                    base = nh.lerp(base, p["shell_light"], 0.6 * math.exp(-((s - p["girder"]) / 0.06) ** 2))
                base = nh.lerp(base, p["groove"], 0.6 * nh.smoothstep(0.88, 1.0, s))
                cols[v] = nh.lerp(base, p["pit"], dark * 0.92)
                ring.append(v)
            grid.append(ring)
        # underside + outer wall
        bot = []
        for j, th in enumerate(thetas):
            q = self.fringe_point(th, 0.0)
            qi = self.fringe_point(th, 1.0)
            v0 = bm.verts.new((q.x, q.y, self.fringe_height(0.0) - 0.022))
            v1 = bm.verts.new((qi.x, qi.y, -0.025))
            cols[v0] = cols[v1] = p["under"]
            bot.append((v0, v1))
        for i in range(len(ss) - 1):
            for j in range(na):
                bm.faces.new([grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]])
        for j in range(na):
            bm.faces.new([bot[j][0], grid[0][j], grid[0][j + 1], bot[j + 1][0]])     # outer wall
            bm.faces.new([bot[j][1], bot[j][0], bot[j + 1][0], bot[j + 1][1]])       # underside
            bm.faces.new([grid[-1][j], bot[j][1], bot[j + 1][1], grid[-1][j + 1]])   # inner wall
        for j in (0, na):  # end caps at the genal corners
            ring = [bot[j][0]] + [grid[i][j] for i in range(len(ss))] + [bot[j][1]]
            bm.faces.new(ring if j == na else list(reversed(ring)))
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        cl = bm.loops.layers.color.new("Col")
        for f in bm.faces:
            for lp in f.loops:
                c = cols[lp.vert]
                lp[cl] = (c[0], c[1], c[2], 1.0)
        return bm

    # ------------------------------------------------------------ genal spines
    def spine(self, sx):
        p = self.p
        corner = self.fringe_point(sx * 92.0, 0.35)
        base = Vector((corner.x - sx * 0.02, self.y_ceph - 0.05, 0.005))
        tip = Vector((sx * (p["ceph_w"] + p["spine_spread"]), self.y_ceph + p["spine_len"], -0.004))
        pts, rad = [], []
        n = 9
        for k in range(n + 1):
            t = k / n
            q = base.lerp(tip, t)
            q.x += sx * 0.05 * math.sin(t * math.pi) * (1 - t)  # slight outward bow near the base
            pts.append(q)
            r = p["spine_r"] * (1.0 - 0.72 * t ** 0.8)
            rad.append(r if k < n else 0.0)
        return nh.tube(pts, rad, sides=6, scale_xy=(1.0, 0.55))


def build(params):
    p = dict(DEFAULTS)
    p.update(params)
    t = Trinucleid(p)
    mb = nh.MeshBuilder()
    mb.add(t.body(), t.body_color)
    mb.add(t.fringe(), None)
    for sx in (-1, 1):
        mb.add(t.spine(sx), p["shell"])
    obj = mb.to_object(p["name"], roughness=0.55)
    zs = [v.co.z for v in obj.data.vertices]
    mid = (min(zs) + max(zs)) / 2
    for v in obj.data.vertices:
        v.co.z -= mid
    return obj


def run(params, views=((30, 40), (0, 85), (-90, 12))):
    nh.run(lambda: build(params), params["name"], views=views)
