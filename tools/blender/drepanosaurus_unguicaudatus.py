"""
Procedural Drepanosaurus unguicaudatus (Late Triassic drepanosaur, ~50 cm) for map
colonies.

One of the strangest reptiles of the Triassic, from northern Italy and New Mexico about
210 million years ago: a chameleon-like climber with a small, pointed, bird-like head on
a long neck, a deep, humped back, and a hugely enlarged claw on the second finger of each
hand, probably used to rip open bark and rotten wood for insects. Its long, deep tail
curled and ended in a bony hook-like claw that helped it grip branches. Built with the
shared Triassic tetrapod recipe (nh_tri_tetrapod.py) plus crisp giant hand claws and the
tail hook. Painted leaf-green with yellow-ochre bands and a pale throat (speculative).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/drepanosaurus_unguicaudatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Drepanosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

CLAW = (0.30, 0.25, 0.18)
CLAW_TIP = (0.80, 0.74, 0.60)

# the tail rises behind the hips and curls forward over itself
TAIL = [(0.30, 0.31, 0.052, 0.064), (0.44, 0.38, 0.042, 0.058), (0.55, 0.50, 0.034, 0.050),
        (0.60, 0.64, 0.028, 0.040), (0.57, 0.77, 0.022, 0.031), (0.49, 0.84, 0.017, 0.024),
        (0.40, 0.85, 0.011, 0.016), (0.33, 0.80, 0.006, 0.008)]

AXIS = [
    (-1.00, 0.440, 0.004, 0.004),
    (-0.97, 0.448, 0.013, 0.013),
    (-0.92, 0.460, 0.026, 0.026),
    (-0.86, 0.472, 0.038, 0.038),
    (-0.80, 0.468, 0.031, 0.031),
    (-0.72, 0.440, 0.027, 0.029),
    (-0.62, 0.405, 0.032, 0.036),
    (-0.52, 0.385, 0.050, 0.060),
    (-0.40, 0.400, 0.086, 0.118),
    (-0.24, 0.390, 0.106, 0.134),
    (-0.06, 0.360, 0.100, 0.118),
    (0.10, 0.325, 0.084, 0.092),
    (0.22, 0.305, 0.072, 0.080),
] + TAIL

FORE = tt.Limb(pts=[(0.08, -0.42, 0.32), (0.12, -0.40, 0.19), (0.115, -0.45, 0.07), (0.115, -0.47, 0.016)],
               radii=[0.036, 0.030, 0.024, 0.020], toes=3, toe_len=0.028, toe_r=0.008, toe_spread=40,
               stride=8, claw_len=0.012)
HIND = tt.Limb(pts=[(0.085, 0.12, 0.29), (0.13, 0.05, 0.18), (0.125, 0.14, 0.07), (0.125, 0.10, 0.016)],
               radii=[0.054, 0.040, 0.027, 0.021], toes=5, toe_len=0.045, toe_r=0.009, toe_spread=70,
               toe_yaw=10, stride=-10, claw_len=0.014)


def claws(mb, surf, spec):
    def col(co, n, b, ln):
        return nh.lerp(CLAW, CLAW_TIP, nh.smoothstep(0.3, 1.0, (co - b).length / ln))
    # giant claw of the second finger, sickle-shaped, sweeping forward and down
    for sx in (1, -1):
        foot = tt.limb_chain(FORE, sx)[-1]
        base = foot + Vector((0, -0.010, 0.022))
        pts = [base, base + Vector((0, -0.045, 0.030)), base + Vector((0, -0.095, 0.022)),
               base + Vector((0, -0.125, -0.020))]
        mb.add(nh.tube(pts, [0.017, 0.014, 0.008, 0.0], sides=8), lambda co, n, b=base: col(co, n, b, 0.15))
    # tail hook
    tip = Vector((TAIL[-1][0] * 0 + 0.0, TAIL[-1][0], TAIL[-1][1]))
    d = Vector((0, -0.4, -1.0)).normalized()
    mb.add(tt.curved_spike(tip, d, 0.08, 0.010, bend=Vector((0, 0.8, 0))),
           lambda co, n, b=tip: col(co, n, b, 0.08))


def throat(co, n, c, spec):
    if co.y < -0.55:
        c = nh.lerp(c, (0.86, 0.84, 0.62), 0.5 * nh.smoothstep(0.0, -0.6, n.z))
    return c


SPEC = tt.TetrapodSpec(
    name="Drepanosaurus",
    axis=AXIS,
    blobs=[((0.0, -0.30, 0.48), (0.075, 0.13, 0.075), -10),       # shoulder hump
           ((0.08, 0.12, 0.28), (0.05, 0.08, 0.07), 20)],
    limbs=[FORE, HIND],
    voxel=0.0085, max_tris=9000,
    mouth=(-1.0, -0.83, 0.440, 0.452, 0.004),
    eyes=(-0.85, 0.488, 0.0135, (0.90, 0.75, 0.20)),
    back=(0.20, 0.36, 0.16), flank=(0.38, 0.56, 0.26), belly=(0.80, 0.82, 0.56),
    pattern=("bands", (0.78, 0.62, 0.20), 30.0, 0.6, -0.5, 0.35),
    paint_extra=throat,
    post=claws,
)

if __name__ == "__main__":
    tt.run(SPEC)
