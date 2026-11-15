"""
Procedural Jaekelopterus rhenaniae (Early Devonian pterygotid eurypterid, the largest
known arthropod at about 2.5 m) for map colonies (Swim style).

The eurypterid body plan, seen mostly from above: a rounded, slightly trapezoidal
prosoma (head shield) with a raised rim, small kidney-shaped compound eyes at its front
corners and a pair of median ocelli; a huge pair of forward-reaching chelicerae, each a
long peduncle ending in a big pincer whose two rami (fixed outer, movable inner, held a
little open) carry rows of long, unequal, inward-pointing denticles and hooked tips;
four pairs of short spiny walking legs and a pair of long swimming legs ending in broad
oval paddles, all splayed out from under the prosoma; an opisthosoma of twelve
imbricating segments (seven broad preabdominal ones, widest in the middle, then five
narrow cylindrical postabdominal ones, the last with small lateral flanges); and a
broad, flat, spear-shaped telson with a median keel. Dark reddish-brown cuticle, paler
rear margins on each tergite, pale tan joints and underside, fine tuberculate texture.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/jaekelopterus_rhenaniae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Jaekelopterus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector, Matrix, noise  # noqa: E402

SHELL = (0.42, 0.17, 0.10)        # dark reddish-brown
SHELL_DARK = (0.24, 0.09, 0.06)
RIM = (0.72, 0.44, 0.26)          # paler rear margins
UNDER = (0.70, 0.52, 0.36)
LEG = (0.56, 0.28, 0.15)
LEG_DARK = (0.34, 0.14, 0.08)
SPINE = (0.86, 0.68, 0.46)
CLAW = (0.50, 0.22, 0.12)
DENTICLE = (0.92, 0.80, 0.60)
EYE = (0.06, 0.05, 0.05)
OCELLUS = (0.12, 0.10, 0.08)

Y_FRONT = -0.80     # front edge of the prosoma
Y_PRO = -0.44       # prosoma / opisthosoma boundary
Y_PRE = 0.30        # preabdomen / postabdomen boundary
Y_POST = 0.74       # end of the postabdomen (telson base)
Y_TELSON = 1.10     # telson tip
PRE_W = [0.205, 0.235, 0.25, 0.248, 0.232, 0.205, 0.165]   # preabdomen half-widths (segments 1-7)
POST_W = [0.105, 0.092, 0.083, 0.076, 0.072]               # postabdomen half-widths (segments 8-12)


# ---------------------------------------------------------------- prosoma

def pro_half_width(y):
    """Rounded trapezoid: narrower, rounded front; widest at the back corners."""
    t = (y - Y_FRONT) / (Y_PRO - Y_FRONT)          # 0 at the front edge, 1 at the back
    t = max(0.0, min(1.0, t))
    front = math.sqrt(max(0.0, 1.0 - (1.0 - min(1.0, t / 0.30)) ** 2))
    return max(0.012, (0.16 + 0.06 * t) * front)


EYES = [(sx * 0.125, -0.70) for sx in (-1, 1)]


def pro_height(x, y):
    w = pro_half_width(y)
    u = min(1.0, abs(x) / w)
    t = (y - Y_FRONT) / (Y_PRO - Y_FRONT)
    h = 0.065 * (1.0 - u ** 2) ** 0.8 * (0.6 + 0.4 * math.sin(min(1.0, max(0.0, t)) * math.pi * 0.8))
    h += 0.008 * nh.smoothstep(0.80, 0.93, u) * (1.0 - nh.smoothstep(0.93, 1.0, u))   # marginal rim
    for ex, ey in EYES:
        d = math.hypot((x - ex) / 0.035, (y - ey) / 0.05)
        h += 0.022 * math.exp(-d ** 2)                                              # eye lobes
    h += 0.008 * math.exp(-((x / 0.03) ** 2 + ((y + 0.60) / 0.03) ** 2))           # ocellar mound
    return h


def pro_color(co, n):
    x, y = co.x, co.y
    w = pro_half_width(y)
    u = min(1.0, abs(x) / max(w, 1e-3))
    c = nh.lerp(SHELL, SHELL_DARK, 0.35 + 0.3 * noise.noise(co * 9.0))
    c = nh.lerp(c, RIM, 0.75 * nh.smoothstep(0.86, 0.98, u))
    # faint radiating sculpture and darker cardiac lobe toward the back
    c = nh.lerp(c, SHELL_DARK, 0.4 * math.exp(-(x / 0.05) ** 2) * nh.smoothstep(-0.62, -0.46, y))
    if noise.noise(co * 55.0) > 0.4:
        c = nh.lerp(c, RIM, 0.35)
    if n.z < -0.3:
        c = UNDER
    return c


def prosoma():
    """Lofted dome on a flat underside, joined round the outline (like redlichia.py)."""
    bm = bmesh.new()
    cols = 18
    ys = [Y_FRONT + (Y_PRO - Y_FRONT) * (1 - math.cos(i / 20 * math.pi / 2)) ** 0.9 for i in range(21)]
    top, bl, br = [], [], []
    for y in ys:
        w = pro_half_width(y)
        row = []
        for j in range(cols + 1):
            uu = -1.0 + 2.0 * j / cols
            x = math.copysign(abs(uu) ** 0.85, uu) * w
            row.append(bm.verts.new((x, y, pro_height(x, y))))
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
    return bm


# ---------------------------------------------------------------- opisthosoma

def segment(y0, y1, w0, w1, h0, h1, flat, z=0.0, rings=6, sides=20):
    """One tergite + sternite ring: superellipse sections from (w0, h0) at the front to
    (w1, h1) at the back, with a flared overhanging rear margin; `flat` squashes the
    underside (1 = as deep as the top)."""
    bm = bmesh.new()
    loops = []
    for i in range(rings + 1):
        t = i / rings
        y = y0 + (y1 - y0) * t
        ww = w0 + (w1 - w0) * nh.smoothstep(0.0, 1.0, t)
        hh = h0 + (h1 - h0) * t
        if t > 0.75:   # rear margin flares out a little, overlapping the next segment
            k = 1.0 + 0.06 * math.sin((t - 0.75) / 0.25 * math.pi * 0.5)
            ww *= k
            hh *= k
        ring = []
        for k in range(sides):
            a = k / sides * math.tau
            c, s = math.cos(a), math.sin(a)
            x = ww * math.copysign(abs(c) ** 0.7, c)
            zz = hh * math.copysign(abs(s) ** 0.9, s) * (1.0 if s > 0 else flat)
            ring.append(bm.verts.new((x, y, z + zz)))
        loops.append(ring)
    for a, b in zip(loops, loops[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new([a[k], a[j], b[j], b[k]])
    for ring, rev in ((loops[0], True), (loops[-1], False)):
        bm.faces.new(list(reversed(ring)) if rev else ring)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def seg_color(y0, y1):
    def fn(co, n):
        t = (co.y - y0) / (y1 - y0)
        c = nh.lerp(SHELL_DARK, SHELL, nh.smoothstep(0.0, 0.35, t))
        c = nh.lerp(c, RIM, 0.8 * nh.smoothstep(0.78, 0.95, t))
        c = nh.lerp(c, SHELL_DARK, 0.25 * (0.5 + 0.5 * noise.noise(co * 10.0)))
        if noise.noise(co * 60.0) > 0.42:
            c = nh.lerp(c, RIM, 0.3)
        if n.z < -0.35:
            c = nh.lerp(UNDER, RIM, 0.5 * nh.smoothstep(0.75, 0.95, t))
        return c
    return fn


def opisthosoma(mb):
    seg = (Y_PRE - Y_PRO) / 7
    prev = pro_half_width(Y_PRO - 0.01) * 0.98
    for i, wb in enumerate(PRE_W):
        y0 = Y_PRO + seg * i - 0.025
        y1 = Y_PRO + seg * (i + 1)
        h = 0.068 - 0.005 * abs(i - 3)
        mb.add(segment(y0, y1, prev * 0.95, wb, h * 0.9, h, 0.45, rings=6, sides=24), seg_color(y0, y1))
        prev = wb
    seg = (Y_POST - Y_PRE) / 5
    for i, wb in enumerate(POST_W):
        y0 = Y_PRE + seg * i - 0.02
        y1 = Y_PRE + seg * (i + 1)
        h = wb * 0.62
        mb.add(segment(y0, y1, prev * 0.88, wb, h * 0.9, h, 0.85, rings=5, sides=18), seg_color(y0, y1))
        prev = wb
    # small lateral flanges on the last (pretelson) segment
    for sx in (-1, 1):
        mb.add(nh.flat_panel([(sx * 0.06, Y_POST - 0.07, 0.0), (sx * 0.115, Y_POST - 0.02, 0.0),
                              (sx * 0.10, Y_POST + 0.025, 0.0), (sx * 0.05, Y_POST, 0.0)], thickness=0.016),
               SHELL, smooth=False)


def telson(mb):
    """Broad, flat, spear-shaped telson with a raised median keel."""
    pts = []
    n = 14
    for k in range(n + 1):
        t = k / n
        y = Y_POST - 0.01 + (Y_TELSON - Y_POST + 0.01) * t
        # spade: widens quickly, widest at ~40 %, then tapers to a point
        wv = 0.105 * math.sin(math.pi * min(1.0, t ** 0.8)) ** 0.7 * (1.0 - 0.15 * t) + 0.035 * (1 - t) ** 3
        pts.append((wv, y))
    outline = [(x, y, 0.0) for x, y in pts] + [(-x, y, 0.0) for x, y in reversed(pts[1:-1])]
    bm = nh.flat_panel(outline, thickness=0.018)
    mb.add(bm, lambda co, nn: nh.lerp(SHELL, RIM, 0.6 * nh.smoothstep(0.06, 0.1, abs(co.x)))
           if nn.z > -0.3 else UNDER, smooth=False)
    mb.add(nh.tube([(0, Y_POST, 0.006), (0, Y_POST + 0.12, 0.008), (0, Y_TELSON - 0.1, 0.004),
                    (0, Y_TELSON - 0.04, 0.0)], [0.018, 0.014, 0.007, 0.0], sides=6, scale_xy=(1.0, 0.5)),
           SHELL_DARK)


# ---------------------------------------------------------------- legs

def jointed(mb, pts, radii, colors, spines=0, spine_len=0.03, sides=7):
    """Leg of podomeres between consecutive points, alternating colours, a knob at each joint
    and `spines` spines per podomere on the front/underside."""
    pts = [Vector(p) for p in pts]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ra, rb = radii[i], radii[i + 1]
        mb.add(nh.tube([a, a.lerp(b, 0.5), b], [ra, (ra + rb) * 0.55, rb], sides=sides), colors[i % 2])
        mb.add(nh.ellipsoid(b, (rb * 1.1,) * 3, subdivisions=1), UNDER)
        d = (b - a).normalized()
        for k in range(spines):
            t = (k + 0.6) / (spines + 0.2)
            base = a.lerp(b, t)
            out = (d.cross(Vector((0, 0, 1))).normalized() * 0.4 + Vector((0, 0, -1)) * 0.3 + d * 0.6).normalized()
            if (b - a).x < 0:
                out.x = -out.x
            r = ra + (rb - ra) * t
            mb.add(nh.tube([base, base + out * spine_len], [r * 0.45, 0.0], sides=4), SPINE, smooth=False)


def walking_legs(mb):
    """Appendages II-V: short, spiny, splayed out under the prosoma's sides."""
    specs = [  # (base y, length, yaw degrees from straight out, forward reach)
        (-0.66, 0.24, -55), (-0.60, 0.27, -35), (-0.54, 0.30, -10), (-0.49, 0.32, 15),
    ]
    for sx in (-1, 1):
        for by, L, yaw in specs:
            a = math.radians(yaw)
            d = Vector((sx * math.cos(a), math.sin(a), 0.0))
            base = Vector((sx * 0.07, by, -0.02))
            knee = base + d * L * 0.40 + Vector((0, 0, 0.035))
            mid = base + d * L * 0.72 + Vector((0, 0, -0.005))
            tip = base + d * L + Vector((0, 0, -0.05))
            claw = tip + d * 0.025 + Vector((0, 0, -0.012))
            jointed(mb, [base, knee, mid, tip, claw], [0.026, 0.022, 0.017, 0.012, 0.0],
                    (LEG, LEG_DARK), spines=2, spine_len=0.04)


def swimming_leg(mb, sx):
    """Appendage VI: long, sweeping back, ending in a broad oval paddle."""
    base = Vector((sx * 0.09, -0.47, -0.02))
    p1 = Vector((sx * 0.22, -0.47, 0.0))
    p2 = Vector((sx * 0.35, -0.43, 0.005))
    p3 = Vector((sx * 0.45, -0.36, 0.0))
    jointed(mb, [base, p1, p2, p3], [0.036, 0.032, 0.028, 0.026], (LEG, LEG_DARK), spines=0, sides=9)
    # paddle: podomeres 7-8 broadened into a long oval oar, sweeping back
    d = Vector((sx * 0.45, 1.0, 0.0)).normalized()
    centre = p3 + d * 0.15
    pts = []
    for k in range(18):
        a = k / 18 * math.tau
        r = 0.16 * (1.0 + 0.12 * math.sin(a))   # a little broader toward the tip
        pts.append((math.cos(a) * 0.075 * (1.0 + 0.25 * math.sin(a)), math.sin(a) * r, 0.0))
    bm = nh.flat_panel(pts, thickness=0.016)
    nh.transform(bm, Vector((0, 1, 0)).rotation_difference(d).to_matrix().to_4x4())
    nh.transform(bm, Matrix.Translation(centre))
    mb.add(bm, lambda co, n: nh.lerp(LEG, RIM, 0.7 * nh.smoothstep(0.05, 0.15, (co - centre).length)),
           smooth=False)
    # the narrow podomere running into the paddle (its "handle") and the small lobe (7a)
    mb.add(nh.tube([p3, p3 + d * 0.09, p3 + d * 0.24], [0.026, 0.024, 0.012], sides=8, scale_xy=(1.0, 0.6)), LEG_DARK)
    mb.add(nh.ellipsoid(p3 + d * 0.05 - Vector((sx * 0.03, 0, 0)), (0.025, 0.04, 0.008), subdivisions=2), LEG_DARK)


# ---------------------------------------------------------------- chelicerae

def ramus(mb, root, direction, inward, length, r0, hook, teeth):
    """One pincer ramus: a tapering, slightly curved blade with hooked tip and denticles
    (unequal lengths, larger ones in between smaller ones) pointing `inward`."""
    pts, radii = [], []
    n = 8
    for k in range(n + 1):
        t = k / n
        p = root + direction * length * t + inward * (hook * t ** 3)
        pts.append(p)
        radii.append(r0 * (1.0 - 0.75 * t) + 0.002)
    radii[-1] = 0.0
    mb.add(nh.tube(pts, radii, sides=7, scale_xy=(1.0, 0.7)), CLAW)
    for k in range(teeth):
        t = 0.12 + 0.78 * k / max(1, teeth - 1)
        i = min(n - 1, int(t * n))
        p = pts[i].lerp(pts[i + 1], t * n - i)
        r = radii[i]
        big = 1.0 if k % 3 == 1 else 0.55
        L = (0.04 + 0.03 * math.sin(t * math.pi)) * big
        d = (inward + direction * 0.35).normalized()
        mb.add(nh.tube([p + inward * r * 0.5, p + inward * r * 0.5 + d * L], [0.0065 * big + 0.0025, 0.0], sides=4),
               DENTICLE, smooth=False)


def chelicera(mb, sx):
    """Basal peduncle reaching forward from under the front of the prosoma, then the pincer."""
    base = Vector((sx * 0.05, Y_FRONT + 0.06, -0.015))
    j1 = Vector((sx * 0.08, Y_FRONT - 0.10, 0.0))
    j2 = Vector((sx * 0.13, Y_FRONT - 0.24, 0.01))
    mb.add(nh.tube([base, (base + j1) / 2, j1], [0.036, 0.036, 0.034], sides=10), LEG)
    mb.add(nh.ellipsoid(j1, (0.038,) * 3, subdivisions=2), UNDER)
    mb.add(nh.tube([j1, (j1 + j2) / 2, j2], [0.034, 0.038, 0.038], sides=10), LEG_DARK)
    # the "hand": swollen base of the fixed ramus
    fwd = Vector((sx * 0.2, -1.0, 0.03)).normalized()
    side = Vector((sx, 0, 0))
    inward = (-side - fwd * (-side).dot(fwd)).normalized()
    palm_c = j2 + fwd * 0.06
    palm = nh.uv_ellipsoid((0, 0, 0), (0.052, 0.085, 0.036), 14, 10)
    nh.transform(palm, Vector((0, -1, 0)).rotation_difference(fwd).to_matrix().to_4x4())
    nh.transform(palm, Matrix.Translation(palm_c))
    mb.add(palm, lambda co, n: nh.lerp(LEG, LEG_DARK, 0.4 * (0.5 + 0.5 * noise.noise(co * 20.0))))
    # fixed ramus (outer) and movable ramus (inner), opened about 22 degrees
    tip_root = palm_c + fwd * 0.07
    open_a = math.radians(26)
    fixed_dir = (fwd + side * 0.05).normalized()
    mov_dir = (fwd * math.cos(open_a) + inward * math.sin(open_a)).normalized()
    ramus(mb, tip_root + side * 0.024, fixed_dir, inward, 0.38, 0.026, 0.06, 12)
    mov_in = (-inward - mov_dir * (-inward).dot(mov_dir)).normalized()
    ramus(mb, tip_root - side * 0.014, mov_dir, mov_in, 0.35, 0.024, 0.06, 11)


# ---------------------------------------------------------------- build

def build():
    mb = nh.MeshBuilder()
    mb.add(prosoma(), pro_color)
    opisthosoma(mb)
    telson(mb)
    # metastoma and the coxae under the prosoma
    mb.add(nh.uv_ellipsoid((0, -0.53, -0.04), (0.07, 0.11, 0.022), 12, 8), UNDER)
    walking_legs(mb)
    for sx in (-1, 1):
        swimming_leg(mb, sx)
        chelicera(mb, sx)
        # small kidney-shaped compound eyes at the front corners
        ex, ey = EYES[0 if sx < 0 else 1]
        arc = []
        for k in range(6):
            a = math.radians(-60 + 120 * k / 5)
            x = ex + sx * 0.016 * math.cos(a)
            y = ey + 0.035 * math.sin(a)
            arc.append((x, y, pro_height(x, y) + 0.006))
        mb.add(nh.tube(arc, [0.006, 0.011, 0.013, 0.013, 0.011, 0.006], sides=6), EYE)
        mb.add(nh.ellipsoid((sx * 0.012, -0.60, pro_height(0.012, -0.60) + 0.002), (0.006, 0.006, 0.004),
                            subdivisions=1), OCELLUS)

    obj = mb.to_object("Jaekelopterus", roughness=0.5)
    vs = obj.data.vertices
    zs = [v.co.z for v in vs]
    ys = [v.co.y for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, "Jaekelopterus", background=(0.05, 0.20, 0.24), views=((30, 40), (0, 85), (-90, 10)))
