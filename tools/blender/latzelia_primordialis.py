"""
Procedural Latzelia primordialis (Late Carboniferous of Mazon Creek, Illinois, a scutigeromorph
centipede about 4 cm long) for map colonies (Ground style).

Built like a modern house centipede: a short, slightly flattened body under eight broad
dorsal plates (tan with dark hind bands), a rounded head with dark compound eyes, a pair
of forcipules (poison claws) curving in under the head, very long whip-like antennae,
and fifteen pairs of very long, thin, many-jointed legs that arch high above the body and
reach the ground far out to the sides, getting longer toward the back; the last pair trails
straight behind like a second set of antennae. Legs banded light and dark.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/latzelia_primordialis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Latzelia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "Latzelia"
PLATE = (0.66, 0.54, 0.38)
BAND = (0.22, 0.16, 0.12)
UNDER = (0.74, 0.66, 0.52)
LEG_A = (0.78, 0.68, 0.52)
LEG_B = (0.30, 0.22, 0.16)
HEAD = (0.58, 0.46, 0.32)
EYE = (0.05, 0.04, 0.04)
FANG = (0.30, 0.16, 0.08)

BODY_L = 0.62
Y0 = -0.28
Z = 0.13
W = 0.075


def banded(base, length, n=5):
    def col(co, nn):
        t = (co - base).length / max(length, 1e-6)
        return LEG_B if (t * n) % 1.0 < 0.3 else LEG_A
    return col


def build():
    mb = nh.MeshBuilder()
    # body: underside spindle + 8 dorsal plates
    mb.add(nh.uv_ellipsoid((0, Y0 + BODY_L / 2, Z - 0.01), (W * 0.85, BODY_L / 2, 0.03), 14, 8), UNDER)
    for i in range(8):
        t = (i + 0.5) / 8
        y = Y0 + t * BODY_L
        w = W * (0.85 + 0.25 * math.sin(math.pi * t))
        L = BODY_L / 8 * 0.68

        def pc(co, n, y=y, L=L):
            return BAND if co.y - y > L * 0.45 else PLATE
        mb.add(nh.uv_ellipsoid((0, y, Z + 0.012), (w, L, 0.03), 12, 6), pc)
        # spiracle dot
        mb.add(nh.ellipsoid((0, y + L * 0.3, Z + 0.042), (0.008, 0.008, 0.004), 1), BAND)
    # head
    hy = Y0 - 0.035
    mb.add(nh.uv_ellipsoid((0, hy, Z + 0.005), (W * 0.8, 0.05, 0.035), 12, 8), HEAD)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * W * 0.62, hy - 0.005, Z + 0.02), (0.022, 0.026, 0.02), 2), EYE)
        # antennae: long, thin, sweeping forward and out
        a0 = Vector((sx * 0.02, hy - 0.045, Z + 0.02))
        pts = [a0]
        d = Vector((sx * 0.35, -1, 0.25)).normalized()
        for k in range(1, 9):
            d = (d + Vector((sx * 0.06, 0, -0.06))).normalized()
            pts.append(pts[-1] + d * 0.075)
        mb.add(nh.tube(pts, [0.006 - 0.0005 * k for k in range(len(pts) - 1)] + [0.0], sides=4), banded(a0, 0.6, 8))
        # forcipules
        f0 = Vector((sx * 0.03, hy + 0.01, Z - 0.03))
        mb.add(nh.tube([f0, f0 + Vector((sx * 0.03, -0.04, -0.005)), f0 + Vector((sx * 0.005, -0.075, -0.005))],
                       [0.010, 0.007, 0.0], sides=4), FANG)
    # 15 leg pairs, arching high, longer toward the back
    for i in range(15):
        t = i / 14
        y = Y0 + 0.02 + t * (BODY_L - 0.04)
        Lg = 0.42 + 0.30 * t
        for sx in (-1, 1):
            root = Vector((sx * W * 0.8, y, Z - 0.01))
            sweep = -0.35 + 0.9 * t     # front legs reach forward, hind legs back
            out = Vector((sx * 1.0, sweep, 0)).normalized()
            if i == 14:
                # last pair: trailing straight back, held off the ground
                pts = [root, root + Vector((sx * 0.04, 0.1, 0.01)), root + Vector((sx * 0.1, 0.35, 0.0)),
                       root + Vector((sx * 0.15, 0.62, -0.03))]
                mb.add(nh.tube(pts, [0.012, 0.009, 0.006, 0.0], sides=4), banded(root, 0.65, 6))
                continue
            knee = root + out * Lg * 0.35 + Vector((0, 0, 0.12 + 0.03 * t))
            ankle = root + out * Lg * 0.72 + Vector((0, 0, 0.02 - Z * 0.4))
            foot = root + out * Lg + Vector((0, 0, -Z + 0.002))
            mb.add(nh.tube([root, knee, ankle, foot], [0.014, 0.011, 0.008, 0.004], sides=4), banded(root, Lg, 5))

    obj = mb.to_object(NAME, roughness=0.5)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, ground=(0.24, 0.22, 0.14), background=(0.20, 0.28, 0.18),
           views=((35, 35), (0, 80), (-90, 10)))
