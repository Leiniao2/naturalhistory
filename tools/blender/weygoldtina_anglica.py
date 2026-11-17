"""
Procedural Weygoldtina anglica (formerly Graeophonus anglicus; Late Carboniferous Coal
Measures of Coseley, England, a whip spider about 1-2 cm long) for map colonies (Ground style).

A flat amblypygid: a wide, kidney-shaped carapace with a cluster of eyes at the front, a
rounded, segmented abdomen, a pair of simple, leg-like pedipalps held forward, the first
pair of legs turned into immensely long, thin feelers sweeping out in front, and three pairs
of long, crab-like splayed walking legs. Dark brown carapace, banded legs.
Built with nh_car_arthropod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/weygoldtina_anglica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Weygoldtina.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_arthropod as ar  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

NAME = "Weygoldtina"
CARAPACE = (0.24, 0.16, 0.10)
ABDOMEN = (0.30, 0.21, 0.13)
ABD_BAND = (0.20, 0.13, 0.08)
LEG = (0.42, 0.30, 0.18)
LEG_DARK = (0.22, 0.15, 0.09)
EYE = (0.05, 0.04, 0.03)

Z = 0.07


def oval(cx, cy, rx, ry, n=24, square=0.2):
    out = []
    for k in range(n):
        a = k / n * math.tau
        c, s = math.cos(a), math.sin(a)
        e = 1.0 / (1.0 + square)
        out.append((cx + rx * math.copysign(abs(c) ** e, c), cy + ry * math.copysign(abs(s) ** e, s)))
    return out


def build():
    parts = [(ar.plate(oval(0, -0.13, 0.15, 0.11), Z, 0.03, dome=0.02), CARAPACE)]
    for i in range(7):
        t = i / 6
        y = 0.0 + t * 0.26
        w = 0.12 * math.sin(math.pi * (0.25 + 0.7 * t)) + 0.02
        parts.append((ar.plate(oval(0, y, w, 0.035, square=0.5), Z - 0.005, 0.035, dome=0.015),
                      ABD_BAND if i % 2 else ABDOMEN))
    legs = []
    # walking legs 2-4: up to the knee, then down to the ground
    for sx in (-1, 1):
        for k, yaw in enumerate((-20, 25, 60)):
            root = Vector((sx * 0.11, -0.16 + k * 0.05, Z - 0.01))
            d = Vector((sx * math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0))
            L = 0.40 + 0.05 * k
            pts = [root, root + d * L * 0.35 + Vector((0, 0, 0.09)), root + d * L * 0.75 + Vector((0, 0, 0.03)),
                   root + d * L + Vector((0, 0, -Z + 0.006))]
            legs.append((pts, 0.014, 0.006))
        # whip-like first legs: long thin feelers sweeping forward and out
        root = Vector((sx * 0.12, -0.2, Z - 0.005))
        pts = [root, root + Vector((sx * 0.12, -0.1, 0.08)), root + Vector((sx * 0.25, -0.3, 0.07)),
               root + Vector((sx * 0.33, -0.55, 0.04)), root + Vector((sx * 0.36, -0.8, 0.02))]
        legs.append((pts, 0.010, 0.002))
        # pedipalps: simple, leg-like, held forward and down
        root = Vector((sx * 0.04, -0.22, Z - 0.01))
        pts = [root, root + Vector((sx * 0.04, -0.07, 0.03)), root + Vector((sx * 0.02, -0.15, -0.02)),
               root + Vector((sx * -0.01, -0.19, -0.04))]
        legs.append((pts, 0.014, 0.007))
    for pts, r0, r1 in legs:
        parts.append((ar.leg(pts, r0, r1), LEG))
    fused = ar.fuse_parts(parts, voxel=0.0045, max_tris=6000)
    # darker leg bands
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            co = l.vert.co
            if math.hypot(co.x, co.y + 0.05) > 0.2 and (math.hypot(co.x, co.y) * 28) % 1.0 < 0.35:
                l[col] = (*LEG_DARK, 1.0)
    tree = BVHTree.FromBMesh(fused)
    details = []
    loc, nrm = ar.ray_down(tree, 0, -0.215)
    if loc is not None:
        details.append(ar.eye(loc + nrm * 0.004, 0.012, (0, -1, 0.6), iris=EYE))
    for sx in (-1, 1):
        loc, nrm = ar.ray_down(tree, sx * 0.07, -0.19)
        if loc is not None:
            details.append(ar.eye(loc + nrm * 0.003, 0.009, (sx, -0.3, 0.5), iris=EYE))
    return ar.finish(fused, details, NAME, ground=True)


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.30, 0.27, 0.18), background=(0.20, 0.28, 0.18),
           views=((35, 35), (-90, 8), (0, 85)))
