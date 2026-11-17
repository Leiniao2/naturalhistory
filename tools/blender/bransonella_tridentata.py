"""
Procedural Bransonella tridentata (Carboniferous bransonelliform shark) for the map (Swim style).

Bransonella is known only from small teeth (no more than about 2 mm): three cusps (hence
"tridentata") with an inverted-V ornament on their outer face. The type species was described
in 1933 from the Lower Pennsylvanian (Bashkirian) Johns Valley Shale of the Ouachita
Mountains, Oklahoma - at first mistaken for a conodont - and the genus ranges from the middle
Mississippian to the middle Permian, mostly in marine rocks. It gives its name to the
Bransonelliformes, the primitive sister group of the xenacanth sharks. The tiny teeth suggest
a small animal, probably well under a metre long.

With no body fossils, the body is a conservative reconstruction after xenacanths such as
Xenacanthus and Orthacanthus: an elongate, eel-like shark with a broad, flattened head, a
terminal mouth and small eyes; a long, low dorsal fin running from mid-back almost to the
tail; a tapering, diphycercal tail with fin folds above and a deeper one below; two small anal
fins; lobed pectoral and pelvic fins; and a slender spine behind the head. The head spine is
borrowed from xenacanths and is not known for Bransonella itself. Muted brown-grey above with
faint darker mottling, paler underneath.

The body and all median fins are lofted / slabbed (helpers from otodus_megalodon.py), fused into
one seamless surface (nh_model.MeshBuilder.fuse), given gill grooves and a fine denticle grain,
decimated and repainted procedurally. Paired fins (crisp gridded nh_fish fins - oblique thin
fins come out ragged when fused), the head spine, eyes and mouth are crisp shells.

Usage:
  blender --background --python tools/blender/bransonella_tridentata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Bransonella.fbx
Pivot at the body centre, faces -Y, dorsal fin up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_fish as fish  # noqa: E402  (crisp gridded fins)
import otodus_megalodon as om  # noqa: E402  (loft / fin-slab / interpolation helpers)
import mola_mola as mola  # noqa: E402  (decimate helper)

VOXEL = 0.013
MAX_TRIS = 4000

BACK = (0.30, 0.27, 0.23)
FLANK = (0.44, 0.40, 0.34)
BELLY = (0.80, 0.76, 0.67)
FIN_EDGE = (0.20, 0.18, 0.15)
GILL = (0.16, 0.13, 0.11)
MOUTH = (0.18, 0.10, 0.09)
LIP = (0.60, 0.50, 0.42)
SPINE = (0.72, 0.66, 0.54)
EYE = (0.05, 0.05, 0.04)
EYE_RING = (0.55, 0.50, 0.34)

Y_TIP, Y_END = -1.00, 1.00

HALF_W = [(-1.00, 0.02), (-0.96, 0.07), (-0.88, 0.10), (-0.75, 0.115), (-0.55, 0.11), (-0.25, 0.098),
          (0.10, 0.078), (0.40, 0.055), (0.70, 0.030), (1.00, 0.004)]
HALF_H_TOP = [(-1.00, 0.015), (-0.96, 0.038), (-0.88, 0.055), (-0.75, 0.075), (-0.55, 0.095),
              (-0.25, 0.100), (0.10, 0.088), (0.40, 0.064), (0.70, 0.036), (1.00, 0.004)]
HALF_H_BOT = [(-1.00, 0.015), (-0.96, 0.032), (-0.88, 0.048), (-0.75, 0.062), (-0.55, 0.082),
              (-0.25, 0.088), (0.10, 0.074), (0.40, 0.054), (0.70, 0.030), (1.00, 0.004)]
CENTER_Z = [(-1.00, -0.01), (-0.7, 0.0), (0.4, 0.0), (1.00, 0.005)]


def w(y): return om._interp(HALF_W, y)
def ht(y): return om._interp(HALF_H_TOP, y)
def hb(y): return om._interp(HALF_H_BOT, y)
def zc(y): return om._interp(CENTER_Z, y)
def top_z(y): return zc(y) + ht(y)
def bot_z(y): return zc(y) - hb(y)


def section(y, a):
    """Flattened head (wide, low), becoming a rounder, laterally compressed body toward the tail."""
    c, s = math.cos(a), math.sin(a)
    n = 2.4 if s >= 0 else 2.9
    x = w(y) * math.copysign(abs(c) ** (2.0 / n), c)
    hz = ht(y) if s >= 0 else hb(y)
    return Vector((x, y, zc(y) + hz * math.copysign(abs(s) ** (2.0 / n), s)))


def median_fin(y0, y1, height, up=True, peak=0.6, tip_h=0.15):
    """Low median fin along the midline: rises to `height` at `peak` of its length, then falls
    to tip_h * height at the back. Rooted inside the body so it fuses."""
    s = 1 if up else -1
    edge_z = top_z if up else bot_z
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        prof = math.sin(math.pi * 0.5 * t / peak) if t < peak else 1.0 - (1.0 - tip_h) * ((t - peak) / (1 - peak)) ** 1.4
        pts.append((y, edge_z(y) + s * height * max(prof, 0.0)))
    pts += [(y1, edge_z(y1) - s * 0.02), (y0, edge_z(y0) - s * 0.02)]
    th = [0.034 - 0.006 * i / len(pts) for i in range(len(pts))]
    return om.fin_slab(pts, th, om.midline_frame)


def caudal():
    """Diphycercal tail: fin folds above and (deeper) below the tapering axis, meeting at a point."""
    y0 = 0.64
    top = lambda y: top_z(y) + 0.045 * math.sin(math.pi * min(1.0, (y - y0) / (Y_END + 0.04 - y0)))  # noqa: E731
    bot = lambda y: bot_z(y) - 0.085 * math.sin(math.pi * min(1.0, (y - y0) / (Y_END + 0.04 - y0)) ** 0.8)  # noqa: E731
    n = 12
    ys = [y0 + (Y_END + 0.04 - y0) * i / n for i in range(n + 1)]
    pts = [(y, top(y)) for y in ys] + [(y, bot(y)) for y in reversed(ys[1:-1])]
    th = [0.032] * len(pts)
    return om.fin_slab(pts, th, om.midline_frame)


def small_anal(y0, y1, height):
    a, b = (y0, bot_z(y0) + 0.02), (y1, bot_z(y1) + 0.02)
    apex = (y0 + (y1 - y0) * 0.55, bot_z((y0 + y1) / 2) - height)
    trail = (y1 + 0.01, bot_z(y1) - height * 0.3)
    pts = [a] + om.curve(a, apex, 0.12, 4) + om.curve(apex, trail, -0.08, 3) + [trail, b]
    th = om.taper(pts, -a[1], -apex[1], 0.036, 0.03)
    return om.fin_slab(pts, th, om.midline_frame)


def fleshy_lobe(sign, y, length, r):
    """Muscular base of a lobed (archipterygial) paired fin, sticking out of the flank."""
    x0 = w(y) * 0.6
    z0 = bot_z(y) + hb(y) * 0.35
    pts = [(sign * x0, y, z0), (sign * (x0 + length * 0.55), y + length * 0.45, z0 - length * 0.12),
           (sign * (x0 + length * 0.85), y + length * 0.85, z0 - length * 0.18)]
    return nh.tube(pts, [r, r * 0.75, 0.0], sides=8)


def paired_fin(mb, sign, y, length, width, droop_deg):
    """Broad, rounded paddle around a central axis (archipterygium-like), as a crisp gridded fin:
    base = front edge, edge = back edge, both running from the root to the tip."""
    droop = math.radians(droop_deg)
    x0 = w(y) * 0.6
    z0 = bot_z(y) + hb(y) * 0.35

    def at(u, v):  # u along the axis (root -> tip), v across (+ = back)
        d = Vector((math.cos(droop) * 0.75, 0.66, -math.sin(droop) * 0.75)).normalized()
        across = Vector((-0.55, 1.0, 0.0)).normalized()
        across = (across - d * across.dot(d)).normalized()
        p = Vector((x0, y, z0)) + d * u + across * v
        return (sign * p.x, p.y, p.z)

    n = 12
    front, back = [], []
    for i in range(n):
        t = i / (n - 1)
        u = length * t
        half = width * (0.55 * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.7 + 0.25 * (1 - t))
        front.append(at(u, -half * 0.55))
        back.append(at(u, half))
    flank = nh.lerp(FLANK, BACK, 0.3)
    fish.fin(mb, front, back, lambda u, v, co: nh.lerp(flank, FIN_EDGE, nh.smoothstep(0.5, 1.0, max(u, v)) * 0.7),
             rows=4, th0=0.022, th1=0.010)


GILL_YS = [-0.70, -0.675, -0.65, -0.625, -0.60, -0.575]
EYE_Y = -0.86


def gill_amount(p):
    y = p.y
    if abs(p.x) < w(y) * 0.6 or not (-0.74 < y < -0.55):
        return 0.0
    rel = (p.z - zc(y)) / max(hb(y), 1e-3)
    if not -0.75 < rel < 0.35:
        return 0.0
    best = 0.0
    for gy in GILL_YS:
        d = abs(y - (gy + 0.015 * (rel - 0.35)))
        ends = nh.smoothstep(-0.75, -0.55, rel) * (1.0 - nh.smoothstep(0.15, 0.35, rel))
        best = max(best, (1.0 - nh.smoothstep(0.002, 0.007, d)) * ends)
    return best


def body_color(p, n):
    y = max(min(p.y, Y_END), Y_TIP)
    belly = nh.smoothstep(-0.05, -0.6, n.z) * (1.0 - 0.6 * nh.smoothstep(0.5, 0.9, p.y))
    up = nh.smoothstep(zc(y), top_z(y) + 0.06, p.z)
    c = nh.lerp(FLANK, BACK, up)
    mott = noise.noise(p * 9.0) * 0.5 + 0.5
    c = nh.lerp(c, tuple(v * 0.78 for v in c), nh.smoothstep(0.55, 0.75, mott) * 0.6 * (1 - belly))
    c = nh.lerp(c, BELLY, belly)
    out = max(0.0, p.z - top_z(y) - 0.02) + max(0.0, bot_z(y) - p.z - 0.02)
    c = nh.lerp(c, FIN_EDGE, nh.smoothstep(0.02, 0.07, out) * 0.6)
    c = nh.lerp(c, GILL, gill_amount(p) * 0.85)
    return c


def skin_detail(bm):
    bm.normal_update()
    for v in bm.verts:
        p = v.co
        d = noise.noise(p * 70.0) * 0.0006 - gill_amount(p) * 0.005
        v.co = p + v.normal * d


def build_body():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    parts.add(om.loft(Y_TIP, Y_END, 110, 28, section), grey)
    parts.add(median_fin(-0.30, 0.62, 0.075, up=True, peak=0.35, tip_h=0.45), grey)   # long, low dorsal
    parts.add(caudal(), grey)
    parts.add(small_anal(0.36, 0.44, 0.045), grey)
    parts.add(small_anal(0.50, 0.58, 0.040), grey)
    for sg in (-1, 1):
        parts.add(fleshy_lobe(sg, -0.56, 0.10, 0.024), grey)   # pectoral base
        parts.add(fleshy_lobe(sg, 0.16, 0.07, 0.018), grey)    # pelvic base
    fused = parts.fuse(voxel=VOXEL, smooth=5, smooth_factor=0.5)
    skin_detail(fused)
    return mola.decimate(fused, MAX_TRIS)


def head_details(mb, bvh):
    # slender spine behind the head, sloping back over the shoulders (after xenacanths)
    y0 = -0.62
    pts = [Vector((0, y0, top_z(y0) - 0.03)), Vector((0, y0 + 0.06, top_z(y0 + 0.06) + 0.012)),
           Vector((0, y0 + 0.16, top_z(y0 + 0.16) + 0.035)), Vector((0, y0 + 0.26, top_z(y0 + 0.26) + 0.05))]
    mb.add(nh.tube(pts, [0.011, 0.009, 0.006, 0.0], sides=6), SPINE)
    for sx in (-1, 1):
        x = sx * w(EYE_Y) * 0.78
        z = zc(EYE_Y) + ht(EYE_Y) * 0.6
        mb.add(nh.ellipsoid((x, EYE_Y, z), (0.012, 0.016, 0.011), subdivisions=2), EYE_RING)
        mb.add(nh.ellipsoid((x + sx * 0.005, EYE_Y - 0.002, z + 0.002), (0.009, 0.011, 0.008), subdivisions=2), EYE)
    # wide, nearly terminal mouth across the front of the flat snout (placed on the surface by
    # casting rays at the snout from the front)
    arc, lip = [], []
    for k in range(11):
        t = -1.0 + 2.0 * k / 10
        x = t * 0.075
        z = zc(-0.96) - hb(-0.96) * 0.55 + 0.012 * t * t
        hit = bvh.ray_cast(Vector((x, -2.0, z)), Vector((0, 1, 0)))[0]
        if hit is None:
            continue
        arc.append((hit.x, hit.y - 0.004, hit.z))
        lip.append((hit.x, hit.y - 0.003, hit.z - 0.006))
    m = len(arc)
    mb.add(nh.tube(lip, [0.0] + [0.007] * (m - 2) + [0.0], sides=6, scale_xy=(1.0, 0.6)), LIP)
    mb.add(nh.tube(arc, [0.0] + [0.0055] * (m - 2) + [0.0], sides=6, scale_xy=(1.0, 0.5)), MOUTH)


def build():
    mb = nh.MeshBuilder()
    body = build_body()
    bvh = BVHTree.FromBMesh(body)
    mb.add(body, body_color)
    head_details(mb, bvh)
    for sg in (-1, 1):
        paired_fin(mb, sg, -0.56, 0.27, 0.16, 12)   # pectoral
        paired_fin(mb, sg, 0.16, 0.17, 0.10, 20)    # pelvic
    return mb.to_object("Bransonella", roughness=0.5)


if __name__ == "__main__":
    nh.run(build, "Bransonella", background=(0.05, 0.16, 0.20),
           views=((35, 25), (90, 4), (30, 62), (-160, -35)))
