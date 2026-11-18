"""
Procedural Gerrothorax pulcherrimus (Late Triassic plagiosaurid temnospondyl, ~1 m) for
map colonies (Swim style).

A flattened bottom-dwelling amphibian from the lakes and rivers of Germany, Greenland and
Sweden, about 210 million years ago. Its very broad, short, almost semicircular head had
small eyes on top set close together, it kept three pairs of feathery external gills
behind the head all its life, and its flat body was armoured with a pavement of bony
plates. It lay in wait on the bottom and snapped at passing prey by raising its skull
rather than dropping its jaw. Built with the shared Triassic tetrapod recipe
(nh_tri_tetrapod.py) plus crisp gill plumes. Painted mud-brown with darker mottling and
red gills (speculative). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/gerrothorax_pulcherrimus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gerrothorax.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

GILL = (0.72, 0.22, 0.18)
GILL_TIP = (0.92, 0.50, 0.40)


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.10 * s * s


AXIS = [
    (-1.00, 0.000, 0.120, 0.012),
    (-0.97, 0.000, 0.200, 0.018),
    (-0.92, 0.000, 0.250, 0.026),
    (-0.84, 0.002, 0.285, 0.032),
    (-0.74, 0.004, 0.300, 0.036),
    (-0.64, 0.004, 0.290, 0.040),
    (-0.56, 0.004, 0.200, 0.044),
    (-0.46, 0.006, 0.190, 0.050),
    (-0.24, 0.006, 0.200, 0.052),
    (-0.02, 0.006, 0.185, 0.050),
    (0.14, 0.004, 0.130, 0.044),
    (0.30, 0.004, 0.060, 0.050, sway(0.30)),
    (0.50, 0.004, 0.032, 0.054, sway(0.50)),
    (0.72, 0.004, 0.016, 0.040, sway(0.72)),
    (0.88, 0.004, 0.004, 0.008, sway(0.88)),
]

FORE = tt.Limb(pts=[(0.15, -0.44, -0.02), (0.24, -0.42, -0.035), (0.26, -0.46, -0.045), (0.27, -0.475, -0.045)],
               radii=[0.030, 0.024, 0.019, 0.016], toes=4, toe_len=0.032, toe_r=0.008, toe_spread=60,
               toe_yaw=35, toe_drop=0.0, claws=False)
HIND = tt.Limb(pts=[(0.14, 0.04, -0.02), (0.23, 0.08, -0.035), (0.25, 0.13, -0.045), (0.26, 0.15, -0.045)],
               radii=[0.034, 0.027, 0.021, 0.017], toes=5, toe_len=0.038, toe_r=0.008, toe_spread=60,
               toe_yaw=70, toe_drop=0.0, claws=False)


def gills(mb, surf, spec):
    for sx in (1, -1):
        for k in range(3):
            base = Vector((sx * (0.245 - k * 0.012), -0.585 + k * 0.035, 0.012))
            d = Vector((sx * 0.9, 0.45 + k * 0.25, 0.15)).normalized()
            pts = [base + d * 0.03 * i + Vector((0, 0.004 * i * i, 0)) for i in range(4)]
            mb.add(nh.tube(pts, [0.012, 0.010, 0.007, 0.0], sides=7),
                   lambda co, n, b=base: nh.lerp(GILL, GILL_TIP, nh.smoothstep(0.0, 0.09, (co - b).length)))
            # fringe filaments
            for i in range(1, 4):
                p = pts[i]
                for s2 in (-1, 1):
                    side = Vector((-d.y, d.x, 0)) * s2
                    mb.add(tt.cone(p, p + side * 0.018 + d * 0.008, 0.0035, sides=4), GILL_TIP, smooth=False)


def head_lines(co, n, c, spec):
    if co.y < -0.56 and n.z > 0.5:
        r = math.hypot(co.x * 1.0, (co.y + 0.60) * 1.2)
        k = abs(math.sin(r * 34.0))
        c = nh.lerp(c, (0.16, 0.13, 0.09), 0.35 * (1.0 - nh.smoothstep(0.0, 0.12, k)))
    return c


SPEC = tt.TetrapodSpec(
    name="Gerrothorax",
    axis=AXIS, power=2.6,
    limbs=[FORE, HIND],
    voxel=0.009, max_tris=9000,
    pivot="centre",
    mouth=(-1.0, -0.60, -0.004, -0.004, 0.005), mouth_min_x=0.15,
    eyes=(-0.80, 0.030, 0.014, (0.80, 0.68, 0.25), 0.045),
    nostrils=(-0.95, 0.015, 0.05),
    plates=[dict(xs=(x, -x), y0=-0.52, y1=0.10, step=0.045, size=0.022, wide=1.2, taper=0.2,
                 col=(0.24, 0.20, 0.14), keel_col=(0.36, 0.30, 0.22), height=0.4)
            for x in (0.025, 0.075, 0.125)],
    back=(0.30, 0.25, 0.17), flank=(0.44, 0.38, 0.26), belly=(0.78, 0.72, 0.56),
    pattern=("spots", (0.16, 0.13, 0.09), 10.0, 0.6),
    paint_extra=head_lines,
    post=gills,
)

if __name__ == "__main__":
    tt.run(SPEC)
