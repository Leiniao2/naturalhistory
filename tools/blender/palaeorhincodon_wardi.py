"""
Procedural Palaeorhincodon wardi (Eocene orectolobiform shark) for the map (Swim style).

Known only from small teeth, so the body is a conservative carpet / nurse-shark plan: a
broad, flattened head with a blunt, rounded snout; a small transverse mouth close to the snout
tip with a pair of fleshy nasal barbels hanging from the nostrils in front of it; small eyes
set high on the head with spiracles behind them; five short gill slits; broad rounded
pectoral and pelvic fins; two similar, spineless dorsal fins set far back over and behind the
pelvics, a small anal fin, and a long tail ending in a low caudal fin with hardly any lower
lobe (the "flag" tail of a bottom-dweller). Muted brown above with scattered pale spots,
pale cream underneath.

The body (with all fins) is lofted and slabbed using the helpers from otodus_megalodon.py,
fused into one seamless surface (nh_model.MeshBuilder.fuse), given gill grooves and a faint
denticle grain, then repainted procedurally. Eyes, mouth and barbels are crisp shells.

Usage:
  blender --background --python tools/blender/palaeorhincodon_wardi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Palaeorhincodon.fbx
Pivot at the body centre, faces -Y, dorsal fins up (+Z). About 2 units long.
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, Matrix, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import otodus_megalodon as om  # noqa: E402  (loft / fin-slab helpers)

VOXEL = 0.021
MAX_TRIS = None   # no decimation: an even voxel grid keeps the spot edges clean

BACK = (0.38, 0.28, 0.19)       # muted brown
FLANK = (0.52, 0.40, 0.28)
BELLY = (0.88, 0.82, 0.70)
SPOT = (0.80, 0.72, 0.56)       # pale spots
FIN_EDGE = (0.27, 0.20, 0.14)
GILL = (0.18, 0.13, 0.09)
MOUTH = (0.20, 0.10, 0.09)
LIP = (0.66, 0.52, 0.42)
BARBEL = (0.62, 0.50, 0.38)
EYE = (0.05, 0.05, 0.04)
EYE_RING = (0.62, 0.55, 0.36)

Y_TIP, Y_END = -0.95, 1.02

# Side-view outline (half-width, top and bottom half-heights, centre line), snout to tail tip.
HALF_W = [(-0.95, 0.03), (-0.92, 0.10), (-0.85, 0.15), (-0.72, 0.18), (-0.55, 0.19), (-0.35, 0.18),
          (-0.10, 0.16), (0.15, 0.13), (0.38, 0.09), (0.60, 0.055), (0.85, 0.03), (1.02, 0.008)]
HALF_H_TOP = [(-0.95, 0.025), (-0.92, 0.06), (-0.85, 0.085), (-0.72, 0.11), (-0.55, 0.13),
              (-0.30, 0.145), (-0.05, 0.14), (0.20, 0.115), (0.40, 0.08), (0.60, 0.05), (0.85, 0.03),
              (1.02, 0.008)]
HALF_H_BOT = [(-0.95, 0.02), (-0.92, 0.045), (-0.85, 0.06), (-0.72, 0.075), (-0.55, 0.09),
              (-0.30, 0.105), (-0.05, 0.10), (0.20, 0.08), (0.40, 0.06), (0.60, 0.04), (0.85, 0.025),
              (1.02, 0.008)]
CENTER_Z = [(-0.95, -0.02), (-0.7, 0.0), (0.0, 0.0), (0.6, 0.0), (1.02, 0.01)]


def w(y): return om._interp(HALF_W, y)
def ht(y): return om._interp(HALF_H_TOP, y)
def hb(y): return om._interp(HALF_H_BOT, y)
def zc(y): return om._interp(CENTER_Z, y)


def section(y, a):
    """Cross-section: rounded back, flattened belly (a squarer superellipse underneath)."""
    c, s = math.cos(a), math.sin(a)
    n = 2.3 if s >= 0 else 3.2
    x = w(y) * math.copysign(abs(c) ** (2.0 / n), c)
    hz = ht(y) if s >= 0 else hb(y)
    z = zc(y) + hz * math.copysign(abs(s) ** (2.0 / n), s)
    return Vector((x, y, z))


def top_z(y): return zc(y) + ht(y)
def bot_z(y): return zc(y) - hb(y)


def dorsal(y0, y1, height, rake):
    """Rounded, spineless dorsal fin on the midline (orectolobiform dorsals are similar in size)."""
    a, b = (y0, top_z(y0) - 0.03), (y1, top_z(y1) - 0.03)
    apex = (y0 + (y1 - y0) * 0.45 + rake, top_z(y0) + height)
    trail = (y1 + rake * 0.5, top_z(y1) + height * 0.18)
    pts = [a] + om.curve(a, apex, 0.16, 6) + om.curve(apex, trail, 0.14, 5) + [trail, b]
    th = om.taper(pts, a[1], apex[1], 0.065, 0.045)
    return om.fin_slab(pts, th, om.midline_frame)


def anal():
    y0, y1 = 0.50, 0.64
    a, b = (y0, bot_z(y0) + 0.02), (y1, bot_z(y1) + 0.02)
    apex = (y0 + 0.07, bot_z(y0) - 0.07)
    trail = (y1 + 0.02, bot_z(y1) - 0.015)
    pts = [a] + om.curve(a, apex, 0.12, 4) + om.curve(apex, trail, -0.06, 3) + [trail, b]
    th = om.taper(pts, -a[1], -apex[1], 0.055, 0.04)
    return om.fin_slab(pts, th, om.midline_frame)


def caudal():
    """Low, elongate caudal fin along the end of the tail: a long upper margin barely raised
    above the axis, a weak lower lobe and a small terminal lobe."""
    yr = 0.66
    top_root, bot_root = (yr, top_z(yr) - 0.015), (yr, bot_z(yr) + 0.015)
    tip = (Y_END + 0.04, zc(Y_END) + 0.02)
    term = (Y_END - 0.04, zc(Y_END) - 0.07)       # terminal lobe below the tip
    notch = (Y_END - 0.10, zc(0.92) - 0.035)        # subterminal notch
    low = (0.80, bot_z(0.80) - 0.085)               # weak ventral lobe
    pts = ([top_root] + om.curve(top_root, tip, -0.04, 7) + om.curve(tip, term, 0.1, 3)
           + om.curve(term, notch, 0.0, 2) + om.curve(notch, low, 0.06, 4) + om.curve(low, bot_root, -0.05, 4))
    th = [0.06 - 0.018 * min(1.0, (u - yr) / 0.35) for u, _ in pts]
    return om.fin_slab(pts, th, om.midline_frame)


def paired(sign, y_front, y_back, span, sweep, droop_deg, root_frac, tip_shift):
    """Broad, rounded paired fin (pectoral / pelvic) spreading out to the side."""
    droop = math.radians(droop_deg)

    def frame(u, v):
        x = sign * (w(u) * root_frac + v * math.cos(droop))
        z = bot_z(u) + hb(u) * 0.35 - v * math.sin(droop)
        return Vector((x, u + v * sweep, z)), Vector((sign * math.sin(droop), 0.0, math.cos(droop)))

    ra, rb = (y_front, 0.0), (y_back, 0.0)
    tip = (y_front + tip_shift, span)
    pts = [ra] + om.curve(ra, tip, 0.18, 6) + om.curve(tip, rb, 0.30, 6) + [rb]
    th = om.taper(pts, 0.0, span, 0.06, 0.04)
    return om.fin_slab(pts, th, frame)


GILL_YS = [-0.60, -0.565, -0.53, -0.495, -0.46]
EYE_Y = -0.76
SPIRACLE_Y = -0.70


def gill_amount(p):
    y = p.y
    if abs(p.x) < w(y) * 0.6 or not (-0.66 < y < -0.42):
        return 0.0
    rel = (p.z - zc(y)) / max(hb(y), 1e-3)
    if not -0.6 < rel < 0.35:
        return 0.0
    best = 0.0
    for gy in GILL_YS:
        d = abs(y - (gy + 0.02 * (rel - 0.35)))
        ends = nh.smoothstep(-0.6, -0.45, rel) * (1.0 - nh.smoothstep(0.2, 0.35, rel))
        best = max(best, (1.0 - nh.smoothstep(0.003, 0.010, d)) * ends)
    return best


def body_color(p, n):
    y = max(min(p.y, Y_END), Y_TIP)
    # counter-shading: pale where the surface faces down
    belly = nh.smoothstep(-0.05, -0.55, n.z)
    belly *= 1.0 - 0.6 * nh.smoothstep(0.6, 0.95, p.y)
    up = nh.smoothstep(zc(y), top_z(y) + 0.08, p.z)
    c = nh.lerp(FLANK, BACK, up)
    mott = noise.noise(p * 7.0) * 0.5 + 0.5
    c = nh.lerp(c, (c[0] * 0.85, c[1] * 0.85, c[2] * 0.85), mott * 0.35)
    # scattered pale spots on the back, flanks and fins (distance to voronoi points -> round dots)
    d = noise.voronoi(p * 11.0 + Vector((1.7, 3.1, 0.4)))[0][0]
    c = nh.lerp(c, SPOT, (1.0 - nh.smoothstep(0.2, 0.3, d)) * 0.8 * (1.0 - belly))
    c = nh.lerp(c, BELLY, belly)
    # darker fin margins
    out = max(0.0, abs(p.x) - w(y) * 1.05) + max(0.0, p.z - top_z(y) - 0.04) + max(0.0, bot_z(y) - p.z - 0.04)
    c = nh.lerp(c, FIN_EDGE, nh.smoothstep(0.08, 0.2, out) * 0.6)
    c = nh.lerp(c, GILL, gill_amount(p) * 0.85)
    return c


def skin_detail(bm):
    bm.normal_update()
    for v in bm.verts:
        p = v.co
        d = noise.noise(p * 60.0) * 0.0008 - gill_amount(p) * 0.008
        # shallow spiracle pits behind the eyes
        for sx in (-1, 1):
            q = Vector((sx * w(SPIRACLE_Y) * 0.62, SPIRACLE_Y, zc(SPIRACLE_Y) + ht(SPIRACLE_Y) * 0.72))
            d -= 0.008 * math.exp(-((p - q).length / 0.012) ** 2)
        v.co = p + v.normal * d


def build_body():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    parts.add(om.loft(Y_TIP, Y_END, 80, 40, section), grey)
    parts.add(dorsal(0.14, 0.32, 0.17, 0.05), grey)      # first dorsal over the pelvic fins
    parts.add(dorsal(0.42, 0.56, 0.12, 0.04), grey)      # second dorsal, nearly as big
    parts.add(anal(), grey)
    parts.add(caudal(), grey)
    for sg in (-1, 1):
        parts.add(paired(sg, -0.48, -0.30, 0.30, 0.30, 18, 0.75, 0.10), grey)   # pectoral
        parts.add(paired(sg, 0.08, 0.24, 0.15, 0.20, 22, 0.55, 0.07), grey)     # pelvic
    fused = parts.fuse(voxel=VOXEL, smooth=6, smooth_factor=0.5, max_tris=MAX_TRIS)
    skin_detail(fused)
    return fused


def head_details(mb):
    for sx in (-1, 1):
        # small eyes set high on the sides of the broad head
        x = sx * w(EYE_Y) * 0.80
        z = zc(EYE_Y) + ht(EYE_Y) * 0.55
        mb.add(nh.ellipsoid((x, EYE_Y, z), (0.020, 0.026, 0.016), subdivisions=2), EYE_RING)
        mb.add(nh.ellipsoid((x + sx * 0.008, EYE_Y - 0.002, z + 0.004), (0.014, 0.018, 0.011), subdivisions=2), EYE)
        # nostrils with fleshy nasal barbels hanging down in front of the mouth
        nb = Vector((sx * 0.045, -0.905, bot_z(-0.905) + 0.012))
        mb.add(nh.ellipsoid(nb + Vector((sx * 0.004, 0.006, -0.002)), (0.016, 0.010, 0.005), subdivisions=1), MOUTH)
        pts = [nb, nb + Vector((sx * 0.004, 0.004, -0.03)), nb + Vector((sx * 0.006, 0.014, -0.058)),
               nb + Vector((sx * 0.004, 0.028, -0.075))]
        mb.add(nh.tube(pts, [0.009, 0.007, 0.005, 0.0], sides=6), BARBEL)
    # small transverse mouth close to the snout tip, on the underside: dark slit with pale lips
    ym = -0.865
    zm = bot_z(ym)
    arc, lip = [], []
    for k in range(9):
        t = -1.0 + 2.0 * k / 8
        x = t * 0.075
        y = ym + 0.025 * t * t
        arc.append((x, y, zm + 0.002))
        lip.append((x, y - 0.006, zm + 0.0))
    mb.add(nh.tube(lip, [0.0] + [0.012] * 7 + [0.0], sides=6, scale_xy=(1.0, 0.5)), LIP)
    mb.add(nh.tube(arc, [0.0] + [0.008] * 7 + [0.0], sides=6, scale_xy=(1.0, 0.45)), MOUTH)


def build():
    mb = nh.MeshBuilder()
    mb.add(build_body(), body_color)
    head_details(mb)
    return mb.to_object("Palaeorhincodon", roughness=0.5)


if __name__ == "__main__":
    nh.run(build, "Palaeorhincodon", background=(0.05, 0.16, 0.20),
           views=((35, 25), (90, 4), (30, 62), (-160, -35)))
