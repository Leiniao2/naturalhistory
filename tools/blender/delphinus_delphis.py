"""
Procedural short-beaked common dolphin (Delphinus delphis) for the map (Swim style).

A slender, streamlined body with a long, narrow beak set off from the rounded
melon by a sharp crease, a tall falcate dorsal fin at mid-back, small pointed
flippers, a laterally compressed tail stock and broad notched flukes.

The body, dorsal fin, flippers and flukes are lofted sections and fin slabs
fused into one seamless surface (nh_model.MeshBuilder.fuse) and repainted
analytically with the species' criss-cross "hourglass": a dark cape on the back
that dips into a V under the dorsal fin, a tan-yellow thoracic patch in front
of it and a pale grey patch behind, a white belly, a dark stripe from the
chin to the flipper, a dark eye patch joined to the beak, and dark fins.
Crisp eyes and a blowhole are added on top.

Usage:
  blender --background --python tools/blender/delphinus_delphis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CommonDolphin.fbx
Pivot at the body centre, faces -Y, dorsal fin up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

import bmesh
from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

VOXEL = 0.017

CAPE = (0.10, 0.11, 0.14)       # dark charcoal back
TAN = (0.86, 0.70, 0.38)        # yellow-ochre thoracic patch
GREY = (0.48, 0.50, 0.54)       # pale grey rear flank patch
HEAD_GREY = (0.42, 0.44, 0.48)
BELLY = (0.94, 0.94, 0.93)
STRIPE = (0.20, 0.21, 0.25)
FIN = (0.09, 0.10, 0.12)
EYE = (0.02, 0.02, 0.025)

Y_TIP, Y_PED = -1.0, 0.80      # beak tip, end of the tail stock
Y_MELON = -0.84                # beak / melon crease


# ---------------------------------------------------------------- body profile

def _interp(table, y):
    """Monotone cubic (PCHIP) interpolation through (y, value) control points."""
    if y <= table[0][0]:
        return table[0][1]
    if y >= table[-1][0]:
        return table[-1][1]
    xs = [p[0] for p in table]
    vs = [p[1] for p in table]
    n = len(xs)
    d = [(vs[i + 1] - vs[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m.append(0.0)
            continue
        h0, h1 = xs[i] - xs[i - 1], xs[i + 1] - xs[i]
        w1, w2 = 2 * h1 + h0, h1 + 2 * h0
        m.append((w1 + w2) / (w1 / d[i - 1] + w2 / d[i]))
    m.append(d[-1])
    for i in range(n - 1):
        if y <= xs[i + 1]:
            h = xs[i + 1] - xs[i]
            t = (y - xs[i]) / h
            h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
            h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
            return h00 * vs[i] + h10 * h * m[i] + h01 * vs[i + 1] + h11 * h * m[i + 1]
    return vs[-1]


HALF_W = [(-1.0, 0.010), (-0.97, 0.024), (-0.90, 0.034), (-0.85, 0.045), (-0.80, 0.080), (-0.72, 0.115),
          (-0.55, 0.150), (-0.30, 0.170), (-0.08, 0.165), (0.15, 0.140), (0.40, 0.095), (0.60, 0.052),
          (0.72, 0.034), (0.80, 0.030)]
HALF_H_TOP = [(-1.0, 0.010), (-0.97, 0.018), (-0.90, 0.024), (-0.855, 0.032), (-0.82, 0.085), (-0.76, 0.130),
              (-0.62, 0.165), (-0.38, 0.190), (-0.10, 0.188), (0.15, 0.160), (0.40, 0.120), (0.60, 0.088),
              (0.72, 0.058), (0.80, 0.036)]
HALF_H_BOT = [(-1.0, 0.010), (-0.97, 0.018), (-0.90, 0.025), (-0.85, 0.036), (-0.78, 0.075), (-0.66, 0.125),
              (-0.42, 0.175), (-0.12, 0.182), (0.15, 0.150), (0.40, 0.100), (0.60, 0.070), (0.72, 0.046),
              (0.80, 0.032)]
CENTER_Z = [(-1.0, -0.035), (-0.86, -0.03), (-0.70, -0.005), (-0.3, 0.0), (0.8, 0.0)]


def w(y): return _interp(HALF_W, y)
def ht(y): return _interp(HALF_H_TOP, y)
def hb(y): return _interp(HALF_H_BOT, y)
def zc(y): return _interp(CENTER_Z, y)


def section(y, a, n=2.25):
    """Superellipse cross-section point at angle a (0 = +x, pi/2 = up)."""
    c, s = math.cos(a), math.sin(a)
    x = w(y) * math.copysign(abs(c) ** (2.0 / n), c)
    hz = ht(y) if s >= 0 else hb(y)
    return Vector((x, y, zc(y) + hz * math.copysign(abs(s) ** (2.0 / n), s)))


def loft(y0, y1, ny, na, point):
    """Closed lofted shell between y0 and y1 (pointed caps) from point(y, angle)."""
    bm = bmesh.new()
    ys = [y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(i / (ny - 1) * math.pi)) for i in range(ny)]
    rings = []
    for i, y in enumerate(ys):
        if i == 0 or i == ny - 1:
            p = sum((point(y, k / na * math.tau) for k in range(na)), Vector()) / na
            rings.append([bm.verts.new(p)])
            continue
        rings.append([bm.verts.new(point(y, k / na * math.tau)) for k in range(na)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1:
            for k in range(na):
                bm.faces.new([a[0], b[(k + 1) % na], b[k]])
        elif len(b) == 1:
            for k in range(na):
                bm.faces.new([a[k], a[(k + 1) % na], b[0]])
        else:
            for k in range(na):
                j = (k + 1) % na
                bm.faces.new([a[k], a[j], b[j], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def fin_slab(outline, thick, frame):
    """Fin from a 2D outline [(u, v)] with a thickness per point; frame(u, v) -> (pos, normal)."""
    bm = bmesh.new()
    top, bot = [], []
    for (u, v), t in zip(outline, thick):
        p, n = frame(u, v)
        top.append(bm.verts.new(p + n * t * 0.5))
        bot.append(bm.verts.new(p - n * t * 0.5))
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    m = len(outline)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new([top[i], bot[i], bot[j], top[j]])
    bmesh.ops.triangulate(bm, faces=bm.faces, ngon_method="EAR_CLIP")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def curve(p0, p1, bulge, steps):
    """Points from p0 to p1 (exclusive of p1) bowed sideways by `bulge` (fraction of length)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    side = Vector((-d.y, d.x))
    return [tuple(p0 + d * (i / steps) + side * bulge * math.sin(i / steps * math.pi)) for i in range(steps)]


# ---------------------------------------------------------------- fins

def dorsal():
    """Tall falcate dorsal fin: convex leading edge, deeply concave trailing edge."""
    base_z = lambda y: zc(y) + ht(y) - 0.04  # noqa: E731
    front, back = (-0.16, base_z(-0.16)), (0.16, base_z(0.16))
    apex = (0.18, ht(0.0) + 0.26)
    notch = (0.13, base_z(0.13) + 0.06)
    pts = [front] + curve(front, apex, 0.08, 10) + curve(apex, notch, -0.16, 9) + [notch, back]
    pts += curve(back, front, 0.0, 4)[1:]
    th = [0.07 - 0.035 * min(1.0, max(0.0, (v - ht(0.0)) / 0.26)) for _u, v in pts]
    return fin_slab(pts, th, lambda u, v: (Vector((0.0, u, v)), Vector((1.0, 0.0, 0.0))))


def flukes():
    """Broad horizontal flukes, swept back to pointed tips with a median notch."""
    half = [(0.0, 0.72), (0.04, 0.76)] + curve((0.04, 0.76), (0.33, 0.99), -0.10, 9) \
        + curve((0.33, 0.99), (0.03, 0.935), -0.05, 8) + [(0.03, 0.935), (0.0, 0.915)]
    pts = half + [(-x, y) for x, y in reversed(half[1:-1])]
    th = [0.055 - 0.025 * min(1.0, abs(x) / 0.33) for x, _y in pts]
    return fin_slab(pts, th, lambda u, v: (Vector((u, v, zc(Y_PED))), Vector((0.0, 0.0, 1.0))))


def flipper(sign):
    """Small, pointed, swept-back pectoral flipper hanging below the flank."""
    droop, sweep = math.radians(38), 0.95
    def frame(u, v):
        x = sign * (w(u) * 0.75 + v * math.cos(droop))
        z = zc(u) - hb(u) * 0.55 - v * math.sin(droop)
        return Vector((x, u + v * sweep, z)), Vector((sign * math.sin(droop), 0.0, math.cos(droop)))
    a, b = (-0.62, 0.0), (-0.52, 0.0)
    tip = (-0.60, 0.24)
    pts = [a] + curve(a, tip, 0.18, 8) + curve(tip, b, 0.10, 7) + [b]
    th = [0.05 - 0.02 * min(1.0, v / 0.24) for _u, v in pts]
    return fin_slab(pts, th, frame)


# ---------------------------------------------------------------- colour

def rel_z(p):
    """-1 (belly) .. 1 (back) across the flank at the point's y."""
    y = max(min(p.y, Y_PED), Y_TIP)
    d = p.z - zc(y)
    return d / max(ht(y) if d >= 0 else hb(y), 1e-3)


def outside(p):
    """How far a point sits outside the body envelope (0 on the body), to find the fins."""
    y = max(min(p.y, Y_PED), Y_TIP)
    hz = ht(y) if p.z >= zc(y) else hb(y)
    r = math.sqrt((p.x / max(w(y), 1e-3)) ** 2 + ((p.z - zc(y)) / max(hz, 1e-3)) ** 2)
    return max(0.0, r - 1.0) * min(w(y), hz)


def seg_dist(p, a, b):
    p, a, b = Vector(p), Vector(a), Vector(b)
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.dot(ab)))
    return (p - (a + ab * t)).length


def body_color(p, n):
    y = p.y
    yc = max(min(y, Y_PED), Y_TIP)
    # fins are dark
    if y > Y_PED + 0.02 or (outside(p) > 0.012 and y > 0.55):
        return FIN
    if outside(p) > 0.012:
        return nh.lerp(FIN, STRIPE, nh.smoothstep(0.3, -0.5, n.z) * 0.4) if p.z < zc(yc) else FIN

    r = rel_z(p)
    wob = noise.noise(Vector((y * 4.0, 0.0, 2.1))) * 0.05
    # dark cape on the back, dipping in a V below the dorsal fin
    v_dip = max(0.0, 1.0 - abs(y - 0.0) / 0.32) ** 1.2
    cape_b = 0.55 - 0.85 * v_dip + wob
    cape_b -= 0.25 * nh.smoothstep(-0.66, -0.80, y)    # cape covers more of the head toward the beak
    # white belly, rising toward the crossing point and falling again behind it
    belly_b = -0.42 + 0.26 * max(0.0, 1.0 - abs(y - 0.0) / 0.4) - 0.6 * nh.smoothstep(0.42, 0.68, y)
    belly_b -= 0.25 * nh.smoothstep(-0.7, -0.85, y)
    # tan in front of the crossing, grey behind (the split leans forward toward the belly)
    split = 0.02 + 0.10 * r
    flank = nh.lerp(TAN, GREY, nh.smoothstep(split - 0.025, split + 0.025, y))
    flank = nh.lerp(HEAD_GREY, flank, nh.smoothstep(-0.70, -0.60, y))
    # tan patch is brightest along its centre, fading a little toward the back
    flank = nh.lerp(flank, (0.70, 0.58, 0.36), nh.smoothstep(-0.2, 0.0, y) * nh.smoothstep(split + 0.02, split - 0.05, y) * 0.4)

    col = nh.lerp(flank, BELLY, 1.0 - nh.smoothstep(belly_b - 0.04, belly_b + 0.04, r))
    col = nh.lerp(col, CAPE, nh.smoothstep(cape_b - 0.05, cape_b + 0.05, r))

    side = Vector((y, r * 0.15))
    # dark stripe from the lower jaw to the flipper
    col = nh.lerp(col, STRIPE, (1.0 - nh.smoothstep(0.006, 0.014, seg_dist(side, (-0.84, -0.10 * 0.15), (-0.60, -0.62 * 0.15)))) * 0.9)
    # dark eye patch, joined to the beak by a thin line
    col = nh.lerp(col, STRIPE, 1.0 - nh.smoothstep(0.016, 0.026, seg_dist(side, (-0.72, 0.03 * 0.15), (-0.70, 0.03 * 0.15))))
    col = nh.lerp(col, STRIPE, (1.0 - nh.smoothstep(0.004, 0.010, seg_dist(side, (-0.85, 0.12 * 0.15), (-0.72, 0.03 * 0.15)))) * 0.85)
    # beak: dark above, a thin dark lip line, paler below
    if y < Y_MELON + 0.02:
        beak = CAPE if r > 0.05 else nh.lerp(HEAD_GREY, BELLY, nh.smoothstep(-0.2, -0.8, r) * 0.6)
        col = nh.lerp(col, beak, nh.smoothstep(Y_MELON + 0.02, Y_MELON - 0.01, y))
        col = nh.lerp(col, STRIPE, 1.0 - nh.smoothstep(0.03, 0.12, abs(r)))
    return col


def skin_detail(bm):
    """Very faint ripple so the big smooth flanks don't look like plastic."""
    bm.normal_update()
    for v in bm.verts:
        v.co = v.co + v.normal * noise.noise(v.co * 30.0) * 0.0008


def build():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)   # repainted after fusing
    parts.add(loft(Y_TIP, Y_PED + 0.02, 110, 40, section), grey)
    parts.add(dorsal(), grey)
    parts.add(flukes(), grey)
    for sg in (-1, 1):
        parts.add(flipper(sg), grey)
    fused = parts.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5)
    skin_detail(fused)

    mb = nh.MeshBuilder()
    mb.add(fused, body_color)
    for sg in (-1, 1):
        y = -0.71
        z = zc(y) + ht(y) * 0.05
        mb.add(nh.ellipsoid((sg * w(y) * 0.93, y, z), (0.012, 0.016, 0.012), subdivisions=2), EYE)
    # blowhole: a small dark crescent on top of the head
    y = -0.60
    mb.add(nh.ellipsoid((0, y, zc(y) + ht(y) - 0.002), (0.018, 0.006, 0.006), subdivisions=1), (0.05, 0.05, 0.06))

    return mb.to_object("CommonDolphin", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "CommonDolphin", background=(0.05, 0.18, 0.24),
           views=((35, 25), (-90, 4), (90, 4), (30, 62), (180, -40)))
