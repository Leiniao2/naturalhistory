"""
Procedural Kenostrychus clementsi (a Silurian bristle worm, about 2-3 cm long, preserved
in three dimensions in the Herefordshire Lagerstaette of England, about 430 million
years ago) for map colonies (Swim).

A slender, many-segmented polychaete: a small head with a pair of feelers (palps) and
short tentacles, then about forty segments, each with a pair of two-branched
parapodia - an upper and a lower lobe, each with a fan of fine bristles (chaetae) -
and a slim finger-like cirrus above. It crawled and swam through the sea floor,
rowing with its parapodia. Reddish-orange body with paler bristles.
Built like burgessochaeta_setigera.py (nh_edicam helpers). Faces -Y, pivot at the body
centre.

Usage:
  blender --background --python tools/blender/kenostrychus_clementsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/KenostrychusClementsi.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "KenostrychusClementsi"
BODY = (0.74, 0.34, 0.24)
BODY_DARK = (0.50, 0.20, 0.14)
BELLY = (0.90, 0.64, 0.52)
PARA = (0.80, 0.44, 0.32)
CIRRUS = (0.92, 0.52, 0.40)
CHAETA = (0.96, 0.90, 0.70)

Y0, Y1, SEG = -0.55, 0.60, 34


def wave_x(y):
    return 0.07 * math.sin(y * 6.0)


def build():
    mb = nh.MeshBuilder()
    pts, radii = [], []
    n = SEG * 2
    for i in range(n + 1):
        y = Y0 + (Y1 - Y0) * i / n
        t = i / n
        pts.append((wave_x(y), y, 0.0))
        radii.append(0.034 * (1 - 0.55 * t ** 2) * (0.85 if i % 2 == 0 else 1.0))
    radii[-1] = 0.0
    mb.add(nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.7)),
           ec.banded(BODY, BODY_DARK, BELLY, Y0, (Y1 - Y0) / SEG, amount=0.6))
    # head: rounded prostomium with two palps and short tentacles
    hx = wave_x(Y0)
    mb.add(nh.uv_ellipsoid((hx, Y0 - 0.025, 0.004), (0.03, 0.035, 0.024), segments=10, rings=6), BODY)
    for s in (-1, 1):
        mb.add(nh.uv_ellipsoid((hx + s * 0.014, Y0 - 0.045, 0.02), (0.007, 0.007, 0.007), 6, 4), (0.05, 0.03, 0.03))
        b = Vector((hx + s * 0.016, Y0 - 0.05, -0.005))
        mb.add(nh.tube([b, b + Vector((s * 0.03, -0.06, -0.005)), b + Vector((s * 0.05, -0.10, -0.01))],
                       [0.010, 0.008, 0.0], sides=5), CIRRUS)
        t = Vector((hx + s * 0.008, Y0 - 0.05, 0.015))
        mb.add(nh.tube([t, t + Vector((s * 0.02, -0.05, 0.02))], [0.004, 0.0], sides=4), CIRRUS)
    for i in range(SEG):
        t = (i + 0.5) / SEG
        y = Y0 + (Y1 - Y0) * t
        r = 0.034 * (1 - 0.55 * t ** 2)
        x0 = wave_x(y)
        sc = 1 - 0.4 * t
        for s in (-1, 1):
            for lvl, dz in ((1, 0.012), (-1, -0.012)):     # notopodium (upper) and neuropodium (lower)
                root = Vector((x0 + s * r * 0.8, y, dz * 0.6))
                tip = root + Vector((s * 0.035 * sc, 0.0, dz))
                mb.add(nh.tube([root, tip], [0.011, 0.007], sides=5), PARA)
                for k in range(4):
                    a = math.radians(-30 + 20 * k)
                    d = Vector((s * math.cos(a), math.sin(a) * 0.6, lvl * 0.35)).normalized()
                    mb.add(nh.tube([tip, tip + d * (0.07 * sc)], [0.003, 0.0], sides=3, cap_start=False),
                           CHAETA, smooth=False)
            # dorsal cirrus
            c0 = Vector((x0 + s * r * 0.7, y, r * 0.5))
            mb.add(nh.tube([c0, c0 + Vector((s * 0.025, 0.01, 0.03)) * sc], [0.006, 0.0], sides=4), CIRRUS)
    return ec.centre(mb.to_object(NAME, roughness=0.45))


if __name__ == "__main__":
    ec.export(build, NAME)
