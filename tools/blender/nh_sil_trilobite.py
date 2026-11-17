"""
Shared parametric trilobite for the Silurian batch (tag "sil"): calymene_blumenbachii.py,
dalmanites_limulurus.py, encrinurus_punctatus.py.

Unlike the effaced Isotelus (nh_isotelus.py) these are strongly sculpted trilobites,
so every part is its own height-field plate on a flat underside:
  * cephalon: outline w(y) = W (1 - t^p)^(1/q) from the front; a gentle dome plus a
    raised glabella (its width can taper forward - bell-shaped, as in Calymene - or
    expand forward, as in Dalmanites) cut by lateral glabellar furrows and an occipital
    furrow; eye lobes (small, or the tall schizochroal eyes of phacopids, painted with
    lenses); optional genal spines and tubercles (Encrinurus' "strawberry" head);
  * thorax: N segments, each with a raised axial ring, sloping pleurae with a pleural
    furrow and optionally pointed pleural tips;
  * pygidium: axis with many rings, pleural ribs, optional long terminal spine.
Short antennae and leg tips peek out underneath. Faces -Y, pivot at the body centre (Swim).
"""

import math
import random
from dataclasses import dataclass

import bmesh
from mathutils import Vector, noise

import nh_model as nh


@dataclass
class Spec:
    name: str
    length: float = 1.6
    ceph_frac: float = 0.32
    pyg_frac: float = 0.20
    segments: int = 13
    W: float = 0.50               # cephalon half-width at the genal angles
    thorax_w: float = 0.46
    thorax_w_back: float = 0.36
    pyg_w: float = 0.32
    ceph_p: float = 2.0
    ceph_q: float = 2.0
    pyg_p: float = 2.0
    pyg_q: float = 1.6
    dome: float = 0.09
    glab_front: float = 0.12      # glabella half-width at its front / back (model units)
    glab_back: float = 0.17
    glab_h: float = 0.08
    glab_len: float = 0.85        # fraction of the cephalon length covered by the glabella
    glab_furrows: int = 3
    axis_w: float = 0.16          # thoracic axis half-width (front)
    axis_h: float = 0.06
    eye: str = "small"            # small | schizo | stalk
    eye_x: float = 0.30
    eye_y: float = 0.45           # 0 = back of the cephalon, 1 = front
    eye_size: float = 1.0
    genal_spine: float = 0.0
    pleural_tips: float = 0.0     # length of pointed pleural tips
    pyg_rings: int = 6
    pyg_ribs: int = 4
    pyg_spine: float = 0.0
    tubercles: int = 0
    antenna: float = 0.15
    # colours
    shell: tuple = (0.50, 0.40, 0.28)
    shell_light: tuple = (0.70, 0.60, 0.44)
    axis: tuple = (0.40, 0.30, 0.20)
    groove: tuple = (0.18, 0.13, 0.08)
    eye_col: tuple = (0.10, 0.09, 0.08)
    under: tuple = (0.40, 0.32, 0.22)
    leg: tuple = (0.55, 0.42, 0.28)


def plate(y0, y1, wfn, hfn, rows=16, cols=22, base=-0.02):
    """Height-field plate over x in [-w(y), w(y)], y in [y0, y1], on a flat underside."""
    bm = bmesh.new()
    ys = [y0 + (y1 - y0) * i / rows for i in range(rows + 1)]
    top, bl, br = [], [], []
    for y in ys:
        w = max(wfn(y), 0.004)
        row = []
        for j in range(cols + 1):
            uu = -1.0 + 2.0 * j / cols
            x = math.copysign(abs(uu) ** 0.9, uu) * w
            row.append(bm.verts.new((x, y, hfn(x, y))))
        top.append(row)
        bl.append(bm.verts.new((-w * 0.98, y, base)))
        br.append(bm.verts.new((w * 0.98, y, base)))
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


def build(s):
    mb = nh.MeshBuilder()
    yf = -s.length / 2
    yb = s.length / 2
    yc = yf + s.length * s.ceph_frac
    yp = yb - s.length * s.pyg_frac
    CL = yc - yf
    seg = (yp - yc) / s.segments

    # ------------------------------------------------ cephalon
    def wc(y):
        t = max(0.0, min(1.0, (yc - y) / CL))
        return s.W * max(0.0, 1.0 - t ** s.ceph_p) ** (1.0 / s.ceph_q)

    g_front = yc - CL * s.glab_len

    def glab_w(y):
        t = max(0.0, min(1.0, (yc - y) / (yc - g_front)))
        return s.glab_back + (s.glab_front - s.glab_back) * t

    ex_y = yc - CL * s.eye_y

    def hc(x, y):
        w = max(wc(y), 1e-3)
        u = min(1.0, abs(x) / w)
        h = s.dome * (1.0 - u ** 2) ** 0.7
        h += 0.01 * nh.smoothstep(0.82, 0.92, u) * (1 - nh.smoothstep(0.92, 1.0, u))   # border rim
        if g_front - 0.02 < y:
            gw = glab_w(y)
            k = 1.0 - nh.smoothstep(gw * 0.8, gw * 1.05, abs(x))
            tg = (y - g_front) / (yc - g_front)
            k *= nh.smoothstep(-0.05, 0.15, tg)
            g = s.glab_h * k * (0.8 + 0.2 * math.sin(min(1.0, tg) * math.pi))
            # lateral glabellar furrows (cut in from the sides) and the occipital furrow
            for i in range(s.glab_furrows):
                fy = yc - (yc - g_front) * (0.25 + 0.55 * i / max(1, s.glab_furrows))
                g -= s.glab_h * 0.55 * math.exp(-((y - fy) / 0.02) ** 2) * nh.smoothstep(gw * 0.3, gw * 0.65, abs(x)) * k
            g -= s.glab_h * 0.6 * math.exp(-((y - (yc - CL * 0.10)) / 0.016) ** 2) * k
            h += g
        if s.eye == "small":
            d = math.hypot((abs(x) - s.eye_x) / (0.04 * s.eye_size), (y - ex_y) / (0.05 * s.eye_size))
            h += 0.035 * s.eye_size * math.exp(-d ** 2)
        return h

    def ceph_col(co, n):
        c = nh.lerp(s.shell, s.shell_light, 0.3 + 0.3 * noise.noise(co * 12.0))
        gw = glab_w(co.y)
        if abs(co.x) < gw * 1.05 and co.y > g_front:
            c = nh.lerp(c, s.axis, 0.5)
        # furrows are where the surface dips: darken steep inward-facing slopes
        if co.z < hc(co.x, co.y) - 0.002 or (abs(co.x) < gw * 1.1 and n.z < 0.6 and co.z > 0.02):
            c = nh.lerp(c, s.groove, 0.5)
        w = max(wc(co.y), 1e-3)
        c = nh.lerp(c, s.shell_light, 0.5 * nh.smoothstep(0.85, 0.95, abs(co.x) / w))
        if n.z < -0.4:
            c = s.under
        return c

    mb.add(plate(yf, yc, wc, hc, rows=20, cols=26), ceph_col)

    # eyes
    for sx in (-1, 1):
        if s.eye == "small":
            p = Vector((sx * s.eye_x, ex_y, hc(s.eye_x, ex_y) + 0.004))
            mb.add(nh.uv_ellipsoid(tuple(p), (0.022 * s.eye_size, 0.035 * s.eye_size, 0.012), 8, 5), s.eye_col)
        elif s.eye == "schizo":
            base_z = hc(s.eye_x, ex_y)
            c = Vector((sx * s.eye_x, ex_y, base_z + 0.03 * s.eye_size))

            def lens(co, n, c=c):
                # hexagonal-ish lens pattern on the outer face, pale palpebral lid on top
                if n.z > 0.7:
                    return s.shell_light
                a = math.atan2(co.y - c.y, abs(co.x - c.x))
                z = co.z - c.z
                k = math.sin(a * 14.0) * math.sin(z * 260.0)
                return (0.85, 0.80, 0.62) if k > 0.35 else s.eye_col
            mb.add(nh.uv_ellipsoid(tuple(c), (0.04 * s.eye_size, 0.07 * s.eye_size, 0.045 * s.eye_size), 12, 8,
                                   deform=lambda v: 1.0 - 0.3 * max(0.0, -v.z)), lens)
        elif s.eye == "stalk":
            base = Vector((sx * s.eye_x, ex_y, hc(s.eye_x, ex_y) - 0.005))
            tip = base + Vector((sx * 0.01, 0, 0.05 * s.eye_size))
            mb.add(nh.tube([base, tip], [0.018 * s.eye_size, 0.014 * s.eye_size], sides=6), s.shell)
            mb.add(nh.uv_ellipsoid(tuple(tip + Vector((0, 0, 0.01))), (0.024 * s.eye_size,) * 3, 8, 6), s.eye_col)
        if s.genal_spine > 0:
            b0 = Vector((sx * s.W * 0.96, yc - 0.03, 0.0))
            mb.add(nh.tube([b0, b0 + Vector((sx * 0.04, s.genal_spine * 0.5, -0.005)),
                            b0 + Vector((sx * 0.05, s.genal_spine, -0.01))], [0.03, 0.018, 0.0], sides=7,
                           scale_xy=(1.0, 0.5)), s.shell)

    # tubercles
    rnd = random.Random(7)
    for _ in range(s.tubercles):
        x = rnd.uniform(-1, 1)
        y = yc - CL * rnd.uniform(0.1, 0.9)
        x *= wc(y) * 0.8
        z = hc(x, y)
        r = rnd.uniform(0.010, 0.016)
        mb.add(nh.ellipsoid((x, y, z), (r, r, r * 0.8), 1), nh.lerp(s.shell, s.shell_light, 0.5))

    # ------------------------------------------------ thorax
    for i in range(s.segments):
        y0 = yc + seg * i - 0.004
        y1 = yc + seg * (i + 1) + 0.004
        t = i / max(1, s.segments - 1)
        W = s.thorax_w + (s.thorax_w_back - s.thorax_w) * t
        aw = s.axis_w * (1.0 - 0.3 * t)
        ym = (y0 + y1) / 2

        def hs(x, y, W=W, aw=aw, ym=ym):
            u = min(1.0, abs(x) / W)
            h = s.dome * (1.0 - u ** 2) ** 0.7
            k = 1.0 - nh.smoothstep(aw * 0.75, aw * 1.05, abs(x))
            h += s.axis_h * k * (1.0 - 0.4 * ((y - ym) / (seg * 0.5)) ** 2)
            # pleural furrow
            h -= 0.012 * (1 - k) * math.exp(-((y - ym) / (seg * 0.18)) ** 2) * (1 - nh.smoothstep(0.7, 0.95, u))
            return h

        def scol(co, n, W=W, aw=aw, y0=y0, y1=y1, ym=ym):
            tt = (co.y - y0) / (y1 - y0)
            ax = abs(co.x) < aw
            c = s.axis if ax else s.shell
            c = nh.lerp(c, s.shell_light, 0.35 * nh.smoothstep(0.5, 0.9, tt))
            c = nh.lerp(c, s.groove, 0.8 * (1 - nh.smoothstep(0.0, 0.18, tt)))
            if not ax:
                c = nh.lerp(c, s.groove, 0.5 * math.exp(-((co.y - ym) / (seg * 0.15)) ** 2))
            if abs(abs(co.x) - aw) < 0.012:
                c = nh.lerp(c, s.groove, 0.6)
            if n.z < -0.4:
                c = s.under
            return c

        mb.add(plate(y0, y1, lambda y, W=W: W, hs, rows=4, cols=24), scol)
        if s.pleural_tips > 0:
            for sx in (-1, 1):
                b0 = Vector((sx * W * 0.95, ym, 0.0))
                mb.add(nh.tube([b0, b0 + Vector((sx * s.pleural_tips * 0.6, s.pleural_tips * 0.8, -0.01))],
                               [seg * 0.35, 0.0], sides=5, scale_xy=(1.0, 0.5)), s.shell)
        # legs (tips peeking out)
        for sx in (-1, 1):
            b0 = Vector((sx * W * 0.6, ym, -0.02))
            tip = Vector((sx * (W + 0.05), ym + 0.03, -0.05))
            mb.add(nh.tube([b0, tip], [0.012, 0.0], sides=4), s.leg)

    # ------------------------------------------------ pygidium
    PL = yb - yp

    def wp(y):
        t = max(0.0, min(1.0, (y - yp) / PL))
        return s.pyg_w * max(0.0, 1.0 - t ** s.pyg_p) ** (1.0 / s.pyg_q)

    def hp(x, y):
        w = max(wp(y), 1e-3)
        u = min(1.0, abs(x) / w)
        t = (y - yp) / PL
        h = s.dome * (1.0 - u ** 2) ** 0.7 * (1.0 - 0.4 * t)
        aw = s.axis_w * 0.7 * (1.0 - 0.8 * t)
        k = (1.0 - nh.smoothstep(aw * 0.7, aw * 1.05, abs(x))) * (1 - nh.smoothstep(0.8, 0.95, t))
        h += s.axis_h * k * (0.85 + 0.15 * math.cos(t * s.pyg_rings * math.tau))
        if s.pyg_ribs:
            h -= 0.008 * (1 - k) * max(0.0, math.cos(t * s.pyg_ribs * math.tau)) * (1 - nh.smoothstep(0.75, 0.95, u))
        return h

    def pcol(co, n):
        t = (co.y - yp) / PL
        aw = s.axis_w * 0.7 * (1.0 - 0.8 * t)
        c = s.axis if abs(co.x) < aw else s.shell
        ring = s.pyg_rings if abs(co.x) < aw else s.pyg_ribs
        c = nh.lerp(c, s.groove, 0.6 * nh.smoothstep(0.6, 0.95, math.cos(t * ring * math.tau)) * (t < 0.85))
        if n.z < -0.4:
            c = s.under
        return c

    mb.add(plate(yp - 0.004, yb, wp, hp, rows=16, cols=22), pcol)
    if s.pyg_spine > 0:
        mb.add(nh.tube([(0, yb - 0.04, 0.012), (0, yb + s.pyg_spine * 0.5, 0.01), (0, yb + s.pyg_spine, 0.02)],
                       [0.025, 0.014, 0.0], sides=7), s.shell)

    # antennae
    for sx in (-1, 1):
        p0 = Vector((sx * 0.06, yf + 0.04, -0.015))
        mb.add(nh.tube([p0, p0 + Vector((sx * 0.06, -s.antenna * 0.6, 0)), p0 + Vector((sx * 0.14, -s.antenna, 0.0))],
                       [0.009, 0.006, 0.0], sides=4), s.leg)

    obj = mb.to_object(s.name, roughness=0.55)
    vs = obj.data.vertices
    zs = [v.co.z for v in vs]
    ys = [v.co.y for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


VIEWS = dict(background=(0.05, 0.20, 0.24), views=((30, 40), (0, 85), (-90, 12)))
