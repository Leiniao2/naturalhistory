"""
Procedural Sharovipteryx mirabilis (Middle-Late Triassic gliding archosauromorph, ~25 cm)
for map colonies (Swarm style, shown gliding).

A tiny reptile from the Madygen Formation of Kyrgyzstan with the strangest wings of any
glider: a skin membrane stretched mainly between its very long hind legs and the base of
its long tail, making it a living delta wing, with perhaps a small front membrane by the
short forelimbs. A small head with a long, slender neck. Built with the shared Triassic
tetrapod recipe (nh_tri_tetrapod.py) in a spread-eagled gliding pose, plus thin membrane
panels. Painted brown with a pale belly; the membrane warm orange-brown with darker
edges (speculative). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/sharovipteryx_mirabilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sharovipteryx.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

MEMBRANE = (0.72, 0.44, 0.22)
EDGE = (0.30, 0.18, 0.10)

AXIS = [
    (-1.00, 0.0, 0.005, 0.005),
    (-0.96, 0.0, 0.022, 0.018),
    (-0.90, 0.0, 0.032, 0.026),
    (-0.84, 0.0, 0.034, 0.028),
    (-0.78, 0.0, 0.020, 0.018),
    (-0.68, 0.0, 0.022, 0.020),
    (-0.58, 0.0, 0.040, 0.034),
    (-0.40, 0.0, 0.055, 0.044),
    (-0.25, 0.0, 0.050, 0.040),
    (-0.10, 0.0, 0.030, 0.025),
    (0.20, 0.0, 0.018, 0.015),
    (0.60, 0.0, 0.010, 0.009),
    (1.00, 0.0, 0.002, 0.002),
]

HIND = tt.Limb(pts=[(0.035, -0.25, 0.0), (0.30, -0.16, 0.01), (0.55, -0.03, 0.0), (0.60, 0.0, 0.0)],
               radii=[0.022, 0.014, 0.010, 0.008], toes=5, toe_len=0.05, toe_r=0.004, toe_spread=60,
               toe_yaw=125, toe_drop=0.0, claws=False)
FORE = tt.Limb(pts=[(0.03, -0.56, 0.0), (0.09, -0.60, -0.01), (0.12, -0.66, -0.01), (0.13, -0.68, -0.01)],
               radii=[0.012, 0.009, 0.007, 0.006], toes=4, toe_len=0.025, toe_r=0.0035, toe_spread=60,
               toe_yaw=20, toe_drop=0.0, claws=False)


def membranes(mb, surf, spec):
    for sx in (1, -1):
        hip, knee, ankle, foot = tt.limb_chain(HIND, sx)
        out = [hip + Vector((0, 0.02, 0)), knee, ankle, foot + Vector((sx * 0.02, 0.03, 0)),
               Vector((sx * 0.42, 0.18, 0)), Vector((sx * 0.22, 0.34, 0)), Vector((sx * 0.012, 0.50, 0)),
               Vector((sx * 0.012, -0.10, 0))]

        def col(co, _n):
            d = abs(co.x) / 0.6
            return nh.lerp(MEMBRANE, EDGE, nh.smoothstep(0.65, 0.95, d) * 0.7 + 0.3 * nh.smoothstep(0.3, 0.5, co.y))
        mb.add(tt.panel(out if sx > 0 else list(reversed(out)), 0.006), col)
        # small front membrane between forelimb and neck
        sh, el, wr, hd = tt.limb_chain(FORE, sx)
        mb.add(tt.panel([sh, el, wr, Vector((sx * 0.01, -0.70, 0)), Vector((sx * 0.01, -0.56, 0))], 0.004), col)


SPEC = tt.TetrapodSpec(
    name="Sharovipteryx",
    axis=AXIS,
    limbs=[HIND, FORE],
    voxel=0.007, max_tris=7000,
    pivot="centre",
    scale_bump=0.0008, scale_freq=80.0,
    mouth=(-0.995, -0.88, -0.004, -0.002, 0.002),
    eyes=(-0.875, 0.008, 0.012, (0.85, 0.60, 0.15)),
    back=(0.32, 0.22, 0.14), flank=(0.50, 0.36, 0.22), belly=(0.86, 0.78, 0.62),
    pattern=("bands", (0.18, 0.12, 0.07), 30.0, 0.6, 0.0, 1.0),
    post=membranes,
)

if __name__ == "__main__":
    tt.run(SPEC, views=((35, 35), (-90, 6), (10, 80)), background=(0.45, 0.62, 0.78))
