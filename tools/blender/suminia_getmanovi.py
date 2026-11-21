"""
Procedural Suminia getmanovi (Late Permian anomodont, ~50 cm) for map colonies.

The oldest known tree-climbing vertebrate: a slender little plant eater with a short, deep
head, serrated chopping teeth, long limbs with long grasping fingers and toes (an
opposable-like first digit) and a very long, prehensile tail, curled at the tip.
Leaf-green-olive above with paler belly and dark speckles, for life among branches.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/suminia_getmanovi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Suminia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Suminia",
    torso=[
        (-0.36, 0.27, 0.045, 0.05),
        (-0.30, 0.27, 0.075, 0.08),
        (-0.16, 0.27, 0.095, 0.095),
        (0.00, 0.27, 0.09, 0.09),
        (0.12, 0.265, 0.075, 0.075),
        (0.20, 0.25, 0.045, 0.045),
        (0.40, 0.20, 0.03, 0.03),
        (0.62, 0.20, 0.022, 0.022),
        (0.80, 0.28, 0.017, 0.017),
        (0.86, 0.38, 0.014, 0.014),
        (0.82, 0.45, 0.012, 0.012),
        (0.75, 0.43, 0.010, 0.010),
        (0.73, 0.38, 0.0, 0.0),
    ],
    head=[
        (-0.34, 0.31, 0.06, 0.065),
        (-0.42, 0.31, 0.058, 0.065),
        (-0.49, 0.29, 0.042, 0.052),
        (-0.53, 0.27, 0.025, 0.036),
        (-0.545, 0.262, 0.0, 0.0),
    ],
    jaw=[
        (-0.36, 0.255, 0.05, 0.022),
        (-0.50, 0.248, 0.03, 0.016),
        (-0.54, 0.25, 0.0, 0.0),
    ],
    teeth=[(-0.535, -0.44, 6, 0.008, 0.003, True)],
    fore=pt.Limb(y=-0.22, z=0.22, x=0.07, upper=0.12, lower=0.13, sprawl=0.6, r=0.026,
                 foot=(0.025, 0.03, 0.009), toe_len=0.055, toe_r=0.006, toe_fan=110, claw=1.2),
    hind=pt.Limb(y=0.10, z=0.22, x=0.07, upper=0.12, lower=0.13, sprawl=0.55, r=0.030,
                 foot=(0.027, 0.034, 0.009), toe_len=0.06, toe_r=0.0065, toe_fan=110, claw=1.2),
    eye=(0.05, -0.43, 0.345, 0.020), nostril=(0.018, -0.535, 0.29),
    back=(0.32, 0.36, 0.18), flank=(0.48, 0.50, 0.28), belly=(0.82, 0.80, 0.60), mark=(0.16, 0.17, 0.08),
    pattern="spots", pattern_freq=34.0, pattern_amount=0.6,
    voxel=0.005, max_tris=8000, drop=0.03,
)

if __name__ == "__main__":
    pt.main(SPEC)
