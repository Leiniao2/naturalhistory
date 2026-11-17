"""
Procedural Effigia okeeffeae (Late Triassic shuvosaurid pseudosuchian, ~2.5 m) for map
colonies.

A crocodile-line archosaur from the Ghost Ranch quarry of New Mexico that looked
astonishingly like a later ostrich dinosaur: a small, toothless head with a horny beak
and big eyes on a long neck, a short deep body, tiny arms, long hind legs walking on
two legs and a very long tail. Built with the shared Triassic tetrapod recipe
(nh_tri_tetrapod.py). Painted rusty ochre with a darker back, faint stripes and a pale
belly, the beak horn-coloured (speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/effigia_okeeffeae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Effigia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402

BEAK = (0.30, 0.26, 0.20)


def sway(y):
    s = max(0.0, (y - 0.15) / 0.85)
    return 0.09 * s * s


AXIS = [
    (-1.00, 0.800, 0.004, 0.004),
    (-0.97, 0.809, 0.012, 0.014),
    (-0.925, 0.822, 0.021, 0.025),
    (-0.875, 0.834, 0.031, 0.036),
    (-0.83, 0.836, 0.030, 0.034),
    (-0.795, 0.815, 0.020, 0.024),
    (-0.75, 0.755, 0.021, 0.025),
    (-0.68, 0.665, 0.027, 0.031),
    (-0.58, 0.585, 0.040, 0.046),
    (-0.46, 0.545, 0.068, 0.080),
    (-0.30, 0.535, 0.090, 0.106),
    (-0.14, 0.540, 0.092, 0.100),
    (0.02, 0.555, 0.076, 0.080),
    (0.20, 0.550, 0.048, 0.050),
    (0.40, 0.525, 0.030, 0.031, sway(0.40)),
    (0.60, 0.495, 0.018, 0.019, sway(0.60)),
    (0.80, 0.465, 0.010, 0.010, sway(0.80)),
    (0.98, 0.435, 0.002, 0.002, sway(0.98)),
]

LEGS = tt.Limb(pts=[(0.065, 0.00, 0.55), (0.082, -0.095, 0.37), (0.080, 0.045, 0.15), (0.080, -0.02, 0.016)],
               radii=[0.052, 0.032, 0.019, 0.014], toes=3, toe_len=0.07, toe_r=0.012, toe_spread=40,
               stride=12, claw_len=0.018)
ARMS = tt.Limb(pts=[(0.05, -0.42, 0.50), (0.062, -0.40, 0.455), (0.056, -0.44, 0.435), (0.052, -0.45, 0.43)],
               radii=[0.018, 0.013, 0.010, 0.008], toes=2, toe_len=0.018, toe_r=0.005, toe_spread=20,
               toe_drop=0.01, claw_len=0.01)


def beak(co, n, c, spec):
    c = nh.lerp(c, BEAK, nh.smoothstep(-0.93, -0.96, co.y))
    return c


SPEC = tt.TetrapodSpec(
    name="Effigia",
    axis=AXIS,
    blobs=[((0.06, 0.01, 0.49), (0.052, 0.11, 0.09), 25)],
    limbs=[LEGS, ARMS],
    voxel=0.0085, max_tris=11000,
    mouth=(-0.995, -0.905, 0.800, 0.818, 0.003),
    eyes=(-0.865, 0.845, 0.0145, (0.75, 0.45, 0.10)),
    back=(0.42, 0.22, 0.10), flank=(0.74, 0.50, 0.26), belly=(0.92, 0.84, 0.66),
    pattern=("stripe", (0.30, 0.15, 0.08), 0.35, 0.18, 0.55, -0.6, 0.5),
    paint_extra=beak,
)

if __name__ == "__main__":
    tt.run(SPEC)
