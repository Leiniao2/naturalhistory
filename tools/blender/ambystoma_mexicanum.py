"""
Procedural axolotl (Ambystoma mexicanum, Pleistocene to today; the lakes of the
Valley of Mexico, now only the canals of Xochimilco) for map colonies.

A mole salamander about 23 cm long that never grows up: it keeps its larval
form all its life (neoteny), living and breeding in the water with three pairs
of feathery external gills behind its broad head, a wide "smiling" mouth, tiny
lidless eyes, short limbs with thin fingers and a long tail with a tall fin that
runs forward along the back. It can regrow lost limbs, its spinal cord and even
parts of its heart and brain. Wild axolotls are mottled olive-brown with gold
flecks; the gills are flushed dark red-purple with blood.

Built with nh_tri_tetrapod.py (like andrias_matthewi.py). Pivot at the body
centre, faces -Y.

Usage:
  blender --background --python tools/blender/ambystoma_mexicanum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AmbystomaMexicanum.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402

GILL = (0.62, 0.16, 0.24)
GILL_TIP = (0.85, 0.40, 0.45)


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.06 * s * s


# (y, z, half-width, half-height[, x]) snout -> tail tip; the tail fin starts on the back
AXIS = [
    (-1.00, 0.000, 0.080, 0.030),
    (-0.96, 0.000, 0.140, 0.045),
    (-0.88, 0.004, 0.175, 0.058),
    (-0.76, 0.006, 0.180, 0.066),
    (-0.66, 0.006, 0.140, 0.064),   # neck
    (-0.52, 0.006, 0.120, 0.070),
    (-0.30, 0.008, 0.120, 0.078),
    (-0.10, 0.010, 0.115, 0.090),
    (0.08, 0.012, 0.090, 0.110),
    (0.22, 0.014, 0.055, 0.140, sway(0.22)),
    (0.45, 0.014, 0.035, 0.150, sway(0.45)),
    (0.70, 0.012, 0.020, 0.120, sway(0.70)),
    (0.90, 0.010, 0.010, 0.060, sway(0.90)),
    (1.00, 0.010, 0.003, 0.010, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.10, -0.50, -0.03), (0.18, -0.50, -0.05), (0.21, -0.56, -0.06), (0.22, -0.59, -0.062)],
               radii=[0.026, 0.020, 0.016, 0.013], toes=4, toe_len=0.04, toe_r=0.007, toe_spread=70,
               toe_yaw=30, toe_drop=0.0, claws=False)
HIND = tt.Limb(pts=[(0.09, -0.02, -0.03), (0.17, 0.01, -0.05), (0.20, 0.06, -0.06), (0.21, 0.08, -0.062)],
               radii=[0.028, 0.022, 0.017, 0.014], toes=5, toe_len=0.045, toe_r=0.007, toe_spread=75,
               toe_yaw=60, toe_drop=0.0, claws=False)


def flecks(co, n, c, spec):
    # dark mottling and small gold flecks
    k = tt.nh.smoothstep(0.25, 0.5, __import__("mathutils").noise.noise(co * 18.0))
    c = nh.lerp(c, (0.15, 0.14, 0.09), 0.5 * k)
    g = __import__("mathutils").noise.noise(co * 55.0 + Vector((2, 7, 1)))
    return nh.lerp(c, (0.78, 0.66, 0.30), 0.7 * nh.smoothstep(0.55, 0.7, g) * (n.z > -0.2))


def gills(mb, surf, spec):
    """Three feathery gill stalks on each side of the head, sweeping back and up."""
    for sx in (-1, 1):
        for k, (dz, ln) in enumerate(((0.07, 0.26), (0.035, 0.30), (0.0, 0.24))):
            root = Vector((sx * 0.15, -0.69, 0.02 + dz))
            d = Vector((sx * 0.85, 0.50, 0.25 + dz * 7.0)).normalized()
            tip = root + d * ln
            mb.add(nh.tube([tuple(root), tuple(root.lerp(tip, 0.5) + Vector((0, 0, 0.015))), tuple(tip)],
                           [0.018, 0.014, 0.006], sides=6), GILL)
            # filaments fringing the back edge of each stalk
            for j in range(9):
                t = 0.15 + 0.85 * j / 8
                p = root.lerp(tip, t)
                f = (Vector((0, 0.35, -0.6)) + d * 0.3).normalized() * (0.075 * (1 - 0.4 * t))
                for side in (-1, 1):
                    q = p + Vector((side * 0.01, 0, 0))
                    mb.add(nh.tube([tuple(q), tuple(q + f + Vector((side * 0.012, 0, 0)))], [0.007, 0.0], sides=4),
                           GILL_TIP)


SPEC = tt.TetrapodSpec(
    name="AmbystomaMexicanum",
    axis=AXIS, power=2.3,
    limbs=[FORE, HIND],
    voxel=0.0085, max_tris=9000,
    pivot="centre",
    scale_bump=0.0, scale_freq=30.0,
    mouth=(-1.0, -0.80, -0.006, -0.010, 0.006), mouth_min_x=0.2,
    eyes=(-0.86, 0.045, 0.012, (0.70, 0.60, 0.25), 0.11),
    back=(0.30, 0.30, 0.20), flank=(0.40, 0.38, 0.27), belly=(0.62, 0.58, 0.46),
    paint_extra=flecks,
    post=gills,
)

if __name__ == "__main__":
    tt.run(SPEC)
