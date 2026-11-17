"""
Procedural Nothosaurus mirabilis (Middle Triassic nothosaur, ~3.5 m) for map colonies
(Swim style).

A long-necked marine reptile of the Muschelkalk sea of Germany, about 240 million years
ago, and a forerunner of the plesiosaurs. A long, flat, narrow skull with a mouth full
of long, outward-pointing fangs that interlocked like a fish trap, eyes set high on the
head, a long neck, a slim body, a long tail, and webbed, paddle-like limbs (the front
pair larger) that it rowed with while also undulating its body. It probably hunted fish
and could haul out on shore like a seal. Built with the shared Triassic tetrapod recipe
(nh_tri_tetrapod.py). Painted dark slate above, grey flanks and a pale belly
(speculative). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/nothosaurus_mirabilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Nothosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.25) / 0.75)
    return 0.10 * s * s


AXIS = [
    (-1.00, 0.000, 0.010, 0.006),
    (-0.95, 0.000, 0.023, 0.014),
    (-0.86, 0.000, 0.031, 0.020),
    (-0.78, 0.002, 0.040, 0.026),
    (-0.72, 0.004, 0.045, 0.030),
    (-0.68, 0.002, 0.034, 0.029),
    (-0.50, 0.000, 0.042, 0.040),
    (-0.34, 0.000, 0.070, 0.060),
    (-0.18, 0.000, 0.108, 0.078),
    (0.02, 0.000, 0.114, 0.080),
    (0.18, 0.000, 0.090, 0.065),
    (0.32, 0.000, 0.055, 0.046, sway(0.32)),
    (0.55, 0.000, 0.034, 0.034, sway(0.55)),
    (0.80, 0.000, 0.018, 0.022, sway(0.80)),
    (1.02, 0.000, 0.003, 0.004, sway(1.02)),
]

FORE = tt.Limb(pts=[(0.08, -0.28, -0.03), (0.17, -0.24, -0.05), (0.22, -0.20, -0.055)],
               radii=[0.034, 0.027, 0.021], paddle=(0.085, 0.042, 125, -5))
HIND = tt.Limb(pts=[(0.07, 0.15, -0.03), (0.14, 0.20, -0.04), (0.17, 0.25, -0.045)],
               radii=[0.030, 0.022, 0.017], paddle=(0.065, 0.032, 150, -5))

SPEC = tt.TetrapodSpec(
    name="Nothosaurus",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.0075, max_tris=10000,
    pivot="centre",
    mouth=(-1.0, -0.74, -0.003, 0.000, 0.004),
    teeth=(12, 0.020, 0.0042, -0.99, -0.79), lower_teeth=True,
    eyes=(-0.755, 0.026, 0.011, (0.80, 0.65, 0.20), 0.025),
    back=(0.17, 0.20, 0.24), flank=(0.42, 0.45, 0.48), belly=(0.86, 0.85, 0.80),
    pattern=("mottle", (0.12, 0.14, 0.17), 10.0, 0.4),
)

if __name__ == "__main__":
    tt.run(SPEC)
