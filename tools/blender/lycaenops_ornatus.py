"""
Procedural Lycaenops ornatus (Late Permian gorgonopsian, ~1 m) for map colonies.

The "wolf-face": a small, lightly built gorgonopsian with a long, narrow, low snout, long
sabre-like upper canines and notably long, slender, nearly upright limbs - one of the most
agile and cursorial predators of the Permian Karoo. A slim body, a narrow chest and a long
tapering tail. Sandy grey-ochre with dark brown saddle bands and a pale belly.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/lycaenops_ornatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Lycaenops.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Lycaenops",
    torso=[
        (-0.42, 0.50, 0.055, 0.06),
        (-0.34, 0.50, 0.095, 0.10),
        (-0.20, 0.50, 0.125, 0.135),
        (0.00, 0.50, 0.12, 0.125),
        (0.16, 0.50, 0.105, 0.105),
        (0.28, 0.49, 0.07, 0.07),
        (0.50, 0.42, 0.04, 0.04),
        (0.78, 0.32, 0.022, 0.022),
        (1.00, 0.24, 0.008, 0.008),
        (1.05, 0.23, 0.0, 0.0),
    ],
    head=[
        (-0.42, 0.55, 0.06, 0.065),
        (-0.52, 0.55, 0.06, 0.065),
        (-0.64, 0.525, 0.045, 0.05),
        (-0.76, 0.50, 0.032, 0.036),
        (-0.83, 0.49, 0.020, 0.024),
        (-0.85, 0.485, 0.0, 0.0),
    ],
    jaw=[
        (-0.45, 0.46, 0.045, 0.024),
        (-0.65, 0.452, 0.033, 0.018),
        (-0.82, 0.452, 0.018, 0.013),
        (-0.845, 0.452, 0.0, 0.0),
    ],
    teeth=[(-0.84, -0.80, 3, 0.016, 0.005, True), (-0.74, -0.60, 6, 0.010, 0.0035, True)],
    fangs=[(0.026, -0.775, 0.47, 0.085, 0.009, 0.010)],
    fore=pt.Limb(y=-0.28, z=0.44, x=0.085, upper=0.19, lower=0.24, sprawl=0.15, r=0.047, muscle=1.25,
                 foot=(0.030, 0.045, 0.013), toe_len=0.038, toe_r=0.008),
    hind=pt.Limb(y=0.18, z=0.45, x=0.085, upper=0.21, lower=0.24, sprawl=0.1, r=0.056, muscle=1.3,
                 foot=(0.032, 0.052, 0.013), toe_len=0.042, toe_r=0.0085),
    eye=(0.045, -0.60, 0.575, 0.015), nostril=(0.015, -0.84, 0.505),
    back=(0.52, 0.44, 0.30), flank=(0.66, 0.58, 0.42), belly=(0.88, 0.84, 0.72), mark=(0.24, 0.17, 0.10),
    pattern="bands", pattern_freq=26.0, pattern_amount=0.85,
    voxel=0.006, max_tris=9000, drop=0.05,
)

if __name__ == "__main__":
    pt.main(SPEC)
