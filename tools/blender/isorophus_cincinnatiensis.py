"""
Procedural Isorophus cincinnatiensis (Late Ordovician edrioasteroid, Cincinnati region)
for map colonies (Fixed style).

An echinoderm that lived stuck to shells on the sea floor: a low, flexible, coin-sized
disc of overlapping plates with a raised rim of small plates round its edge and five
food grooves (ambulacra) curving out from the central mouth like the arms of a pinwheel,
each roofed by a double row of tiny cover plates that opened to let tube feet catch
food from the water. Shown attached to an old brachiopod shell lying on the mud. Orange-
tan disc, reddish ambulacra. Pivot on the sea floor (z = 0), facing -Y.

Usage:
  blender --background --python tools/blender/isorophus_cincinnatiensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/IsorophusCincinnatiensis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "IsorophusCincinnatiensis"
PLATE = (0.78, 0.60, 0.40)
PLATE_DARK = (0.56, 0.40, 0.25)
AMB = (0.70, 0.30, 0.20)
AMB_LIGHT = (0.88, 0.52, 0.36)
RIM = (0.90, 0.78, 0.58)
HOST = (0.64, 0.64, 0.60)
HOST_RIB = (0.50, 0.50, 0.46)

RD = 0.40      # disc radius
Z0 = 0.10      # disc base height (top of the host shell)
CURVE = 1.9    # ambulacral curvature (radians over the disc radius)


def amb_dist(x, y):
    r = math.hypot(x, y)
    th = math.atan2(y, x)
    best = 9.0
    for k in range(5):
        c = k / 5 * math.tau + math.pi / 2 + CURVE * (r / RD)
        d = math.atan2(math.sin(th - c), math.cos(th - c)) * r
        best = min(best, abs(d))
    return best, r


def h(x, y):
    d, r = amb_dist(x, y)
    t = r / RD
    z = Z0 + 0.10 * max(0.0, 1.0 - t ** 2) ** 0.8
    z += 0.025 * math.exp(-(d / 0.03) ** 2) * (1.0 - nh.smoothstep(0.75, 0.82, t)) * nh.smoothstep(0.0, 0.08, t)
    z += 0.03 * math.exp(-((t - 0.92) / 0.06) ** 2)
    return z


def col(co, n):
    x, y = co.x, co.y
    d, r = amb_dist(x, y)
    t = r / RD
    if n.z < 0.1:
        return PLATE_DARK
    e, k = kit.voronoi_plates(co, 28.0, 1.0)
    c = nh.lerp(PLATE, PLATE_DARK, 0.4 * k + 0.6 * e)
    if t > 0.84:
        e2, k2 = kit.voronoi_plates(co, 40.0, 4.0)
        c = nh.lerp(RIM, PLATE_DARK, 0.7 * e2)
    w = 0.03
    if d < w and t < 0.82:
        th = math.atan2(y, x)
        chevron = 0.5 + 0.5 * math.sin(r * 120 + (d / w) * 2.0)
        c = nh.lerp(AMB, AMB_LIGHT, 0.6 * nh.smoothstep(0.6, 1.0, chevron))
        c = nh.lerp(c, PLATE_DARK, 0.7 * (1 - nh.smoothstep(0.0, 0.006, d)))
    if r < 0.04:
        c = PLATE_DARK
    return c


def build():
    mb = nh.MeshBuilder()
    kit.mud(mb, 0.9)
    # host: an old, worn strophomenid brachiopod shell, convex up
    def outline(a):
        r = 1.0 / math.sqrt((math.cos(a) / 0.62) ** 2 + (math.sin(a) / 0.52) ** 2)
        if math.sin(a) > 1e-3:
            r = min(r, 0.2 / math.sin(a))
        return r
    hb = kit.valve(outline, 0.09, side=1, peak=(0, 0.3), power=0.6, frame=lambda u, v, w: (u, v, w + 0.02))
    mb.add(hb, lambda co, n: nh.lerp(HOST, HOST_RIB, 0.5 * nh.smoothstep(0.6, 1.0,
                                     0.5 + 0.5 * math.cos(math.atan2(co.x, 0.2 - co.y) * 60))))
    disc = kit.heightfield_disc(RD, h, n_r=36, n_a=120)
    nh.transform(disc, Matrix.Translation((0, 0, -0.01)))
    mb.add(disc, col)
    return kit.finish_fixed(mb, NAME)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
