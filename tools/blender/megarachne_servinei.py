"""
Procedural Megarachne servinei (Late Carboniferous of Argentina, a large freshwater
eurypterid about 54 cm long, first misidentified as a giant spider) for map colonies
(Swim style).

A broad, flat sea-scorpion of the sweep-feeding mycteroptid kind: a big, rounded head
shield with small eyes near its centre, a wide, segmented, oval body tapering to a short
tail spine, and long walking legs, the front pairs fringed with forward-raking spines for
combing prey out of the mud. Dark chestnut-brown, the segments edged paler.
Built with nh_car_arthropod. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/megarachne_servinei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Megarachne.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_arthropod as ar  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "Megarachne"
SHIELD = (0.30, 0.18, 0.10)
SEG = (0.34, 0.21, 0.12)
SEG_EDGE = (0.55, 0.40, 0.24)
LEG = (0.36, 0.24, 0.14)
SPINE = (0.20, 0.12, 0.07)
EYE = (0.08, 0.06, 0.05)


def oval(cx, cy, rx, ry, n=24, square=0.35):
    out = []
    for k in range(n):
        a = k / n * math.tau
        c, s = math.cos(a), math.sin(a)
        e = 1.0 / (1.0 + square)
        out.append((cx + rx * math.copysign(abs(c) ** e, c), cy + ry * math.copysign(abs(s) ** e, s)))
    return out


def build():
    parts = []
    # head shield (prosoma): broad, rounded in front
    parts.append((ar.plate(oval(0, -0.42, 0.24, 0.17, square=0.15), 0.06, 0.03, dome=0.05), SHIELD))
    # opisthosoma: 11 overlapping tergites, widest near the front, tapering back
    n = 11
    for i in range(n):
        t = i / (n - 1)
        y = -0.25 + t * 0.62
        w = 0.25 * (1 - t ** 2.0) ** 0.6 + 0.03
        z = 0.06 + 0.012 * math.sin(math.pi * t)
        parts.append((ar.plate(oval(0, y, w, 0.045, square=0.6), z, 0.03, dome=0.035 * (1 - 0.6 * t)),
                      SEG if i % 2 else nh.lerp(SEG, SEG_EDGE, 0.25)))
    # tail spine
    parts.append((nh.tube([(0, 0.38, 0.06), (0, 0.5, 0.055), (0, 0.62, 0.05)], [0.03, 0.018, 0.0], sides=8), SHIELD))
    # legs: 4 pairs from under the head shield
    legs = []
    for sx in (-1, 1):
        for k, (yaw, L, spiny) in enumerate(((-55, 0.36, True), (-25, 0.40, True), (15, 0.42, False), (50, 0.46, False))):
            root = Vector((sx * 0.12, -0.46 + k * 0.06, 0.03))
            d = Vector((sx * math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0))
            pts = ar.jointed(root, [L * 0.3, L * 0.35, L * 0.35], d + Vector((0, 0, 0.35)),
                             [(0, 0), (sx * 8, -35), (sx * 8, -25)])
            parts.append((ar.leg(pts, 0.022, 0.009), LEG))
            legs.append((pts, spiny, sx))
    fused = ar.fuse_parts(parts, voxel=0.007, max_tris=6500)
    details = []
    for pts, spiny, sx in legs:
        if not spiny:
            continue
        for a, b in zip(pts[1:], pts[2:]):
            for k in range(4):
                p = a.lerp(b, (k + 0.5) / 4)
                d = (b - a).normalized()
                details.append((nh.tube([p, p + (Vector((0, -1, -0.3)) + d * 0.3).normalized() * 0.04],
                                        [0.006, 0.0], sides=4), SPINE))
    from mathutils.bvhtree import BVHTree
    tree = BVHTree.FromBMesh(fused)
    for sx in (-1, 1):
        loc, nrm = ar.ray_down(tree, sx * 0.04, -0.43)
        if loc is not None:
            details.append(ar.eye(loc + nrm * 0.004, 0.016, (sx, -0.3, 0.6), iris=EYE))
    return ar.finish(fused, details, NAME, ground=False)


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.10, 0.20, 0.20), views=((35, 35), (-90, 8), (0, 85)))
