"""
Shared builder for the Arthropleura models (arthropleura_armata.py, arthropleura_cristata.py).

Arthropleura was a giant Carboniferous myriapod: a long, flat, millipede-like body
of ~30 body rings (diplosegments), each covered by a broad tergite whose sides
spread out into flat lateral lobes (paranota) with backward-pointing corners,
two pairs of short legs per ring, and a small head tucked under the first
tergite (collum) with short antennae.

  * build(spec): the whole animal from a Spec (proportions, ornament, colours).
    Each tergite is its own shingled plate: a lofted top surface (axial ridge,
    drooping paranota, optional nodes/crests in the height field) over a flat
    underside, its front tucked under the plate in front, so the segmentation
    and the saw-toothed outline stay crisp without fusing.
  * Faces -Y, pivot on the ground (feet at z = 0).
"""

import math
from dataclasses import dataclass

import bmesh
from mathutils import Vector

import nh_model as nh


@dataclass
class Spec:
    name: str
    segments: int = 30            # tergites behind the collum
    length: float = 1.9           # collum front to anal plate (model units)
    half_width: float = 0.21      # widest tergite, incl. paranota
    dome: float = 0.055           # height of the axial ridge above the paranota edge
    axial: float = 0.42           # axial (raised) part's half-width as a fraction of the tergite's
    paranota_droop: float = 0.012 # paranota edges dip below the axial base
    lobe_sweep: float = 0.85      # how far back the paranota corners reach (in tergite lengths)
    clearance: float = 0.045      # underside height above the ground
    thickness: float = 0.022      # plate edge thickness
    cols: int = 14                # grid columns across a tergite (even)
    rows: int = 4                 # grid rows along a tergite
    nodes: int = 0                # tubercle pairs per tergite (separate little domes)
    node_size: float = 0.016
    crest: float = 0.0            # transverse crest near each tergite's hind margin (height)
    keels: float = 0.0            # paired longitudinal keels along the axial part (height)
    leg_sides: int = 4
    leg_reach: float = 0.05       # how far the feet stick out past the paranota
    antenna: float = 0.11
    bend: float = 0.06            # gentle sideways S-curve of the whole body
    # colours
    axis_col: tuple = (0.30, 0.17, 0.09)
    para_col: tuple = (0.46, 0.30, 0.16)
    edge_col: tuple = (0.66, 0.50, 0.30)
    groove_col: tuple = (0.12, 0.07, 0.04)
    node_col: tuple = (0.20, 0.11, 0.06)
    crest_col: tuple = (0.62, 0.42, 0.22)
    under_col: tuple = (0.40, 0.30, 0.20)
    leg_col: tuple = (0.50, 0.34, 0.18)
    leg_tip_col: tuple = (0.32, 0.20, 0.10)


def width_profile(s, t):
    """Tergite half-width at t in [0, 1] (front to back)."""
    w = 0.80 + 0.20 * nh.smoothstep(0.0, 0.18, t)
    w *= 1.0 - 0.55 * nh.smoothstep(0.62, 1.0, t) ** 1.3
    return s.half_width * w


def tergite(s, y0, L, W, H, front_low=0.82, collum=False):
    """One shingled plate. y0: front at the midline, L: ring length, W: half-width, H: dome.
    Returns (bmesh, colour fn); geometry in body space (straight, before bending)."""
    cols, rows = s.cols, s.rows
    base = s.clearance + s.thickness

    def front(u):
        a = abs(u)
        if collum:  # half-moon shield over the head
            return y0 + L * 1.2 * (a ** 2)
        return y0 + L * (0.10 * a * a + s.lobe_sweep * 0.85 * nh.smoothstep(0.55, 1.0, a) ** 1.4)

    def back(u):
        a = abs(u)
        if collum:
            return y0 + L * (1.25 + 0.30 * a ** 3)
        return y0 + L * (1.15 + s.lobe_sweep * 0.62 * nh.smoothstep(0.35, 1.0, a) ** 1.5)

    def height(u, v):
        a = abs(u)
        ax = s.axial
        # arched axial part, near-flat paranota drooping to the edge
        h = H * (1.0 - min(1.0, a / ax) ** 2) ** 0.7 if a < ax else 0.0
        h += H * 0.30 * (1.0 - a) - s.paranota_droop * nh.smoothstep(ax, 1.0, a)
        h += 0.10 * H * (1.0 - a * a)
        h *= front_low + (1.0 - front_low) * nh.smoothstep(0.0, 0.45, v)
        # rounded hind margin
        h -= 0.25 * H * nh.smoothstep(0.85, 1.0, v) * (1.0 - a)
        return base + h

    def u_at(j):
        uu = -1.0 + 2.0 * j / cols
        return math.copysign(abs(uu) ** 0.9, uu)

    bm = bmesh.new()
    top, bl, br = [], [], []
    for i in range(rows + 1):
        v = i / rows
        row = []
        for j in range(cols + 1):
            u = u_at(j)
            y = front(u) + (back(u) - front(u)) * v
            row.append(bm.verts.new((u * W, y, height(u, v))))
        top.append(row)
        yl = front(-1) + (back(-1) - front(-1)) * v
        bl.append(bm.verts.new((-W * 0.94, yl, s.clearance)))
        br.append(bm.verts.new((W * 0.94, yl, s.clearance)))
    for i in range(rows):
        for j in range(cols):
            bm.faces.new([top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]])
        bm.faces.new([bl[i], bl[i + 1], br[i + 1], br[i]])
        bm.faces.new([bl[i], top[i][0], top[i + 1][0], bl[i + 1]])
        bm.faces.new([br[i], br[i + 1], top[i + 1][cols], top[i][cols]])
    bm.faces.new([bl[0]] + top[0] + [br[0]])
    bm.faces.new([br[-1]] + list(reversed(top[-1])) + [bl[-1]])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    def color(co, n):
        if n.z < -0.4:
            return s.under_col
        a = min(1.0, abs(co.x) / W)
        c = nh.lerp(s.axis_col, s.para_col, nh.smoothstep(s.axial * 0.7, s.axial * 1.15, a))
        c = nh.lerp(c, s.edge_col, nh.smoothstep(0.78, 0.98, a))
        # groove along the axial/paranotal boundary
        c = nh.lerp(c, s.groove_col, 0.55 * math.exp(-((a - s.axial) / 0.05) ** 2))
        fy, by = front(co.x / W), back(co.x / W)
        v = (co.y - fy) / max(by - fy, 1e-4)
        c = nh.lerp(c, s.groove_col, 0.6 * (1.0 - nh.smoothstep(0.0, 0.22, v)))  # tucked front margin
        return c

    return bm, color, height, front, back


def node(c, r, h):
    """Flattened tubercle dome."""
    return nh.ellipsoid(c, (r, r * 0.9, h), subdivisions=1)


def leg(s, hip_x, y, W, out, length):
    """Short jointed leg: hip under the body, knee just past the paranota, foot on the ground."""
    hip = Vector((hip_x * out, y, s.clearance + 0.004))
    knee = Vector(((W + s.leg_reach * 0.45) * out, y + length * 0.05, s.clearance + 0.012))
    foot = Vector(((W + s.leg_reach) * out, y + length * 0.18, 0.0))
    r = 0.014 * (s.half_width / 0.21)
    parts = [(nh.tube([hip, knee], [r, r * 0.8], sides=s.leg_sides), s.leg_col),
             (nh.tube([knee, foot], [r * 0.8, r * 0.25], sides=s.leg_sides), s.leg_tip_col)]
    return parts


def build(s: Spec):
    mb = nh.MeshBuilder()
    n = s.segments
    L = s.length / (n + 1.6)  # ring length (collum counts ~1.6 rings)
    y_front = -s.length / 2
    shells = []

    # collum: broad half-moon shield over the head
    W0 = width_profile(s, 0.0) * 0.92
    bm, col, *_ = tergite(s, y_front, L * 1.25, W0, s.dome * 0.95, front_low=0.92, collum=True)
    shells.append((bm, col))
    y = y_front + L * 1.6
    for i in range(n):
        t = (i + 0.5) / n
        W = width_profile(s, t)
        H = s.dome * (0.55 + 0.45 * (W / s.half_width))
        bm, col, height, front, back = tergite(s, y, L, W, H)
        shells.append((bm, col))
        # tubercles: pairs on the axial part and on the paranota bases
        if s.nodes:
            us = [0.16, 0.36, 0.62, 0.80][:s.nodes]
            for u in us:
                for sx in (-1, 1):
                    v = 0.55
                    py = front(u) + (back(u) - front(u)) * v
                    z = height(u, v)
                    r = s.node_size * (W / s.half_width) * (1.0 if u < 0.5 else 0.8)
                    shells.append((node((sx * u * W, py, z - r * 0.25), r, r * 0.75), s.node_col))
        # crested form: a sharp transverse crest across the hind half of the tergite, rising
        # into a pair of keel peaks either side of the midline
        if s.crest:
            pts, radii = [], []
            for k in range(7):
                u = -0.55 + 1.10 * k / 6
                v = 0.62
                py = front(u) + (back(u) - front(u)) * v
                peak = s.keels * math.exp(-((abs(u) - s.axial * 0.55) / 0.12) ** 2)
                pts.append(Vector((u * W, py, height(u, v) + peak * 0.6)))
                radii.append(s.crest * (0.55 + 0.45 * (1.0 - abs(u) / 0.55)) + peak * 0.5)
            radii[0] = radii[-1] = 0.0
            shells.append((nh.tube(pts, radii, sides=4, scale_xy=(0.40, 1.0)), s.crest_col))
        # two leg pairs per diplosegment
        if i < n - 1:
            for k in (0.25, 0.75):
                ly = y + L * k
                for out in (-1, 1):
                    shells += leg(s, W * 0.45, ly, W * 0.94, out, L)
        y += L

    # anal plate (telson) behind the last ring
    Wt = width_profile(s, 1.0) * 0.55
    shells.append((nh.uv_ellipsoid((0, y + L * 0.5, s.clearance + 0.018), (Wt, L * 1.0, 0.022), 10, 6),
                   s.axis_col))

    # head: tucked under the collum, short antennae and small stalked eyes peeking out
    hc = Vector((0.0, y_front - L * 0.1, s.clearance + 0.008))
    hw = W0 * 0.50
    shells.append((nh.uv_ellipsoid(hc, (hw, L * 1.0, 0.022 * (s.half_width / 0.21)), 12, 6),
                   s.axis_col))
    sc = s.half_width / 0.21
    for sx in (-1, 1):
        a0 = hc + Vector((sx * hw * 0.45, -L * 0.85, 0.004))
        pts = [a0 + Vector((sx * s.antenna * f * 0.45, -s.antenna * f, 0.02 * math.sin(f * 3.0) * sc))
               for f in (0.0, 0.3, 0.6, 0.85, 1.0)]
        shells.append((nh.tube(pts, [0.014 * sc, 0.013 * sc, 0.012 * sc, 0.011 * sc, 0.006 * sc],
                               sides=s.leg_sides), s.leg_tip_col))
        e0 = hc + Vector((sx * hw * 0.85, -L * 0.6, 0.006))
        e1 = e0 + Vector((sx * 0.020 * sc, -0.028 * sc, 0.006 * sc))
        shells.append((nh.tube([e0, e1], [0.006 * sc, 0.005 * sc], sides=s.leg_sides), s.leg_col))
        shells.append((nh.ellipsoid(e1, (0.009 * sc,) * 3, subdivisions=1), (0.05, 0.04, 0.03)))
    # first leg pair under the collum
    for out in (-1, 1):
        shells += leg(s, W0 * 0.4, y_front + L * 0.9, W0 * 0.9, out, L)

    for bm, col in shells:
        mb.add(bm, col, smooth=True)
    if s.bend:
        # gentle S-curve in plan view (after colouring, so the markings follow the body)
        for v in mb.bm.verts:
            t = (v.co.y - y_front) / s.length
            v.co.x += s.bend * math.sin(t * math.pi * 1.6 + 0.4)

    obj = mb.to_object(s.name, roughness=0.55)
    nh.ground_to_zero(obj)
    zs = [v.co.z for v in obj.data.vertices]
    print(f"{s.name}: height {max(zs):.3f}, hip (underside) {s.clearance:.3f} -> mapHip "
          f"{s.clearance / max(zs):.2f}")
    return obj
