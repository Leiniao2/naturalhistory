"""
Procedural Kalligramma haeckeli (Late Jurassic kalligrammatid lacewing, Solnhofen) for map colonies.

One of the "butterflies of the Jurassic": a giant lacewing with a wingspan of up to about
25 cm, its four broad wings dense with fine veins and each marked with a large, dark
eyespot ringed in pale, much like the eyespots of modern butterflies (which evolved them
some 100 million years later). Relatives had long tubular mouthparts for feeding on
fluids from seed plants. Here with wings spread flat: smoky-brown wings, cream rings
around black eyespots, a dark slender body. Faces -Y, pivot at the body centre (Swarm).

Usage:
  blender --background --python tools/blender/kalligramma_haeckeli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kalligramma.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmesh  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector  # noqa: E402

WING = (0.50, 0.38, 0.24)
VEIN = (0.30, 0.22, 0.14)
RING = (0.92, 0.86, 0.66)
SPOT = (0.06, 0.05, 0.05)
BODY = (0.16, 0.12, 0.10)


def wing_color(spot):
    sx_, sy_ = spot

    def fn(co, n):
        d = math.hypot(abs(co.x) - sx_, co.y - sy_)
        if d < 0.06:
            return SPOT if d < 0.045 else RING
        c = WING
        if math.sin(abs(co.x) * 110 + co.y * 30) > 0.85:
            c = VEIN
        return nh.lerp(c, (0.36, 0.26, 0.16), nh.smoothstep(0.4, 0.6, abs(co.x)))
    return fn


def wing(outline, sx, z):
    pts = [(sx * x, y, z + abs(x) * 0.05) for x, y in outline]
    if sx < 0:
        pts = list(reversed(pts))
    bm = nh.flat_panel(pts, thickness=0.006)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=6, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    return bm


FORE = [(0.03, -0.1), (0.2, -0.16), (0.42, -0.15), (0.6, -0.08), (0.62, 0.0), (0.5, 0.06), (0.3, 0.06), (0.1, 0.0), (0.03, -0.04)]
HIND = [(0.03, -0.02), (0.15, 0.0), (0.35, 0.03), (0.52, 0.1), (0.52, 0.2), (0.38, 0.26), (0.2, 0.22), (0.07, 0.12), (0.03, 0.04)]


def build():
    mb = nh.MeshBuilder()
    for sx in (1, -1):
        mb.add(wing(FORE, sx, 0.0), wing_color((0.4, -0.05)), smooth=False)
        mb.add(wing(HIND, sx, -0.006), wing_color((0.33, 0.13)), smooth=False)
    rows = [(0, 0.42, 0.0, 0, 0), (0, 0.3, 0.0, 0.025, 0.025), (0, 0.05, 0.0, 0.035, 0.035), (0, -0.08, 0.0, 0.045, 0.04),
            (0, -0.15, 0.0, 0.03, 0.03), (0, -0.2, 0.0, 0.035, 0.03), (0, -0.23, 0.0, 0, 0)]
    mb.add(kit.Spine(rows).mesh(sides=10), BODY)
    kit.eyes(mb, (0.03, -0.2, 0.005), 0.014, iris=(0.25, 0.25, 0.18), pupil=(0.05, 0.05, 0.04))
    for sx in (1, -1):
        mb.add(nh.tube([(sx * 0.01, -0.22, 0.01), (sx * 0.06, -0.38, 0.03), (sx * 0.1, -0.45, 0.03)], [0.003, 0.002, 0.001], sides=4), BODY)
        for y in (-0.12, -0.08, -0.04):
            mb.add(nh.tube([(sx * 0.03, y, -0.02), (sx * 0.1, y - 0.02, -0.06), (sx * 0.12, y, -0.1)], [0.004, 0.003, 0.002], sides=4), BODY)
    return kit.finish(mb, "Kalligramma", pivot="center", roughness=0.6)


if __name__ == "__main__":
    nh.run(build, "Kalligramma", background=(0.45, 0.58, 0.70), views=((35, 30), (0, 89), (-90, 5)))
