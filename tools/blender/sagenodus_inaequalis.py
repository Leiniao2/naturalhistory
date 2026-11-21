"""
Procedural Sagenodus inaequalis (Carboniferous to Early Permian of Europe and North America,
a lungfish about 1 m long) for map colonies (Swim style).

An elongated lungfish: a broad, rounded, slightly flattened head with small eyes and a wide
mouth; narrow, pointed, leaf-shaped paired fins, each with a fleshy central lobe (the
archipterygial fin skeleton) fringed by fin rays; and, as in later lungfish, the second
dorsal, tail and anal fins merged into one continuous fin fringe running round the rear of
the body and tapering to a point (diphycercal). Brownish-olive mottled with dark blotches,
paler belly. Built with nh_car_fish. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/sagenodus_inaequalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sagenodus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
import nh_b2_carboniferous_fish as bf  # noqa: E402
from mathutils import Vector  # noqa: E402

# (root on the right flank, axis direction, length, half width)
PADDLES = [((0.07, -0.30, -0.055), (0.55, 1.0, -0.35), 0.24, 0.035),
           ((0.05, 0.12, -0.06), (0.45, 1.0, -0.40), 0.20, 0.03)]


def _frame(axis):
    d = Vector(axis).normalized()
    across = d.cross(Vector((0, 0, 1))).cross(d)  # in the vertical plane through the axis...
    side = d.cross(Vector((0, 0, 1))).normalized()
    # leaf plane: spanned by the axis and a mostly-horizontal across vector, tipped down a little
    a = (side * 0.85 + across.normalized() * 0.5).normalized()
    return d, a


def paddles(sp):
    """Leaf-shaped archipterygial fins: a fringe panel round a fleshy tapering lobe."""
    out = []
    for root, axis, L, hw in PADDLES:
        for sx in (-1, 1):
            r = Vector((sx * root[0], root[1], root[2]))
            ax = Vector((sx * axis[0], axis[1], axis[2]))
            d, a = _frame(ax)
            n = 10
            left, right = [], []
            for i in range(n + 1):
                t = i / n
                w = hw * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.7 * (1.0 - 0.35 * t)
                c = r + d * (L * t)
                left.append(c + a * w)
                right.append(c - a * w)
            pts = left + list(reversed(right[1:-1]))
            out.append(cf.panel(pts, d.cross(a), 0.010))
            out.append(nh.tube([r - d * 0.02, r + d * (L * 0.35), r + d * (L * 0.75), r + d * L],
                               [0.024, 0.016, 0.008, 0.002], sides=8))
    return out


def details(sp, tree):
    return (bf.mouth_line(sp, tree, -0.598, -0.50, -0.03, -0.035, r=0.004)
            + bf.dots(sp, tree, 40, (0.16, 0.14, 0.08), (-0.45, 0.45), (-0.2, 0.9), (0.016, 0.028),
                      flat=0.5))


SPEC = cf.Spec(
    name="Sagenodus",
    y1=0.66,
    mid=[(-0.6, 0.0), (0.66, 0.0)],
    height=[(-0.6, 0.0), (-0.59, 0.035), (-0.52, 0.065), (-0.40, 0.085), (-0.15, 0.095), (0.15, 0.085),
            (0.40, 0.055), (0.58, 0.02), (0.66, 0.0)],
    width=[(-0.6, 0.0), (-0.59, 0.05), (-0.52, 0.085), (-0.40, 0.095), (-0.15, 0.085), (0.15, 0.07),
           (0.40, 0.04), (0.58, 0.014), (0.66, 0.0)],
    fins=[
        # one continuous fringe: dorsal over the rear half, round the pointed tail, anal below
        ("mid", [(-0.05, 0.08), (0.05, 0.13), (0.25, 0.155), (0.45, 0.12), (0.62, 0.05), (0.72, 0.0),
                 (0.62, -0.05), (0.45, -0.11), (0.30, -0.12), (0.22, -0.07), (0.2, 0.0)]),
    ],
    fin_th=0.012,
    fused_extra=[paddles],
    back=(0.26, 0.25, 0.14), flank=(0.44, 0.40, 0.24), belly=(0.80, 0.75, 0.58),
    fin_col=(0.34, 0.31, 0.19), pattern="mottle", pattern_col=(0.17, 0.16, 0.09), pattern_scale=1.1,
    eye=(-0.50, 0.035, 0.018), iris=(0.70, 0.60, 0.30), gills=0,
    voxel=0.007, max_tris=9000,
    extra=[details],
)

if __name__ == "__main__":
    cf.run(SPEC)
