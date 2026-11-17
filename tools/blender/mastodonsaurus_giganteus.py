"""
Procedural Mastodonsaurus giganteus (Middle Triassic capitosaur temnospondyl, ~5 m) for
map colonies (Swim style).

One of the largest amphibians that ever lived, from the Ladinian (about 240 million
years ago) lake and delta deposits of southern Germany. Its huge, flat, broadly
triangular skull was over a metre long, a quarter of its length, with eyes on top and a
pair of big tusks in the lower jaw whose tips poked up through holes in the snout. A
flattened body, small, weak limbs and a deep, finned tail: it lived in the water like a
giant salamander or crocodile, ambushing fish and anything else that came near. Built
with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py). Painted olive-brown with
dark blotches, a pale belly and lateral-line grooves on the head (speculative). Faces -Y,
pivot at the body centre.

Usage:
  blender --background --python tools/blender/mastodonsaurus_giganteus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mastodonsaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.1) / 0.9)
    return 0.12 * s * s


AXIS = [
    (-1.00, 0.000, 0.050, 0.012),
    (-0.96, 0.000, 0.110, 0.018),
    (-0.88, 0.000, 0.160, 0.026),
    (-0.78, 0.000, 0.198, 0.033),
    (-0.66, 0.002, 0.222, 0.040),
    (-0.57, 0.004, 0.226, 0.044),
    (-0.51, 0.004, 0.180, 0.050),
    (-0.40, 0.004, 0.185, 0.062),
    (-0.20, 0.004, 0.195, 0.066),
    (0.00, 0.004, 0.185, 0.062),
    (0.12, 0.004, 0.145, 0.056),
    (0.25, 0.004, 0.080, 0.060, sway(0.25)),
    (0.45, 0.004, 0.048, 0.070, sway(0.45)),
    (0.70, 0.004, 0.028, 0.060, sway(0.70)),
    (0.92, 0.004, 0.012, 0.034, sway(0.92)),
    (1.00, 0.004, 0.002, 0.004, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.15, -0.40, -0.02), (0.25, -0.37, -0.04), (0.27, -0.42, -0.05), (0.28, -0.44, -0.05)],
               radii=[0.038, 0.031, 0.024, 0.020], toes=4, toe_len=0.04, toe_r=0.009, toe_spread=60,
               toe_yaw=35, toe_drop=0.0, claws=False)
HIND = tt.Limb(pts=[(0.13, 0.08, -0.02), (0.24, 0.12, -0.04), (0.26, 0.18, -0.05), (0.27, 0.20, -0.05)],
               radii=[0.044, 0.034, 0.026, 0.021], toes=5, toe_len=0.05, toe_r=0.010, toe_spread=60,
               toe_yaw=70, toe_drop=0.0, claws=False)


def tusks(mb, surf, spec):
    for sx in (1, -1):
        loc, n = surf.hit((sx * 0.06, -0.955, 1.0), (0, 0, -1))
        if loc is not None:
            mb.add(tt.cone(loc - Vector((0, 0, 0.01)), loc + Vector((0, 0.005, 0.022)), 0.008), tt.TOOTH, smooth=False)


def head_lines(co, n, c, spec):
    # lateral-line sensory grooves on the skull roof
    if co.y < -0.58 and n.z > 0.6:
        import math
        r = math.hypot(co.x * 1.2, (co.y + 0.58) * 0.9)
        k = abs(math.sin(r * 38.0))
        c = tt.nh.lerp(c, (0.18, 0.16, 0.10), 0.35 * (1.0 - tt.nh.smoothstep(0.0, 0.12, k)))
    return c


SPEC = tt.TetrapodSpec(
    name="Mastodonsaurus",
    axis=AXIS, power=2.4,
    limbs=[FORE, HIND],
    voxel=0.0095, max_tris=10000,
    pivot="centre",
    mouth=(-1.0, -0.57, -0.006, -0.004, 0.005), mouth_min_x=0.15,
    teeth=(16, 0.016, 0.0045, -0.99, -0.60),
    eyes=(-0.63, 0.035, 0.016, (0.80, 0.65, 0.20), 0.075),
    back=(0.24, 0.24, 0.15), flank=(0.40, 0.38, 0.24), belly=(0.80, 0.76, 0.60),
    pattern=("spots", (0.13, 0.13, 0.08), 8.0, 0.65),
    paint_extra=head_lines,
    post=tusks,
)

if __name__ == "__main__":
    tt.run(SPEC)
