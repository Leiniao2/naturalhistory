"""
Procedural Prionosuchus plummeri (Early Permian archegosaurid temnospondyl, ~5.5-9 m),
swimming, for map colonies.

The largest amphibian known, from the Pedra de Fogo lakes and rivers of north-eastern Brazil:
a gharial-like aquatic ambusher with an extremely long, narrow snout lined with many sharp,
conical teeth, a broad, flat head behind the eyes, small eyes set high on top, a long, low
body, small limbs tucked back against the flanks and a long, deep, sideways-flattened
swimming tail. Dark olive-green above with blackish blotches, a yellowish belly.
Built with nh_per_tetra. Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/prionosuchus_plummeri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Prionosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Prionosuchus",
    torso=[
        (-0.42, 0.0, 0.085, 0.050),
        (-0.34, 0.0, 0.115, 0.060),
        (-0.15, 0.0, 0.125, 0.065),
        (0.05, 0.0, 0.115, 0.062),
        (0.20, 0.0, 0.085, 0.058),
        (0.40, 0.0, 0.040, 0.060),
        (0.65, 0.0, 0.022, 0.050),
        (0.85, 0.0, 0.010, 0.032),
        (0.95, 0.0, 0.0, 0.0),
    ],
    head=[
        (-0.40, 0.012, 0.095, 0.040),
        (-0.50, 0.012, 0.085, 0.035),
        (-0.58, 0.006, 0.045, 0.024),
        (-0.75, 0.0, 0.028, 0.018),
        (-0.95, -0.004, 0.022, 0.015),
        (-1.03, -0.005, 0.026, 0.016),
        (-1.06, -0.005, 0.0, 0.0),
    ],
    head_power=2.6,
    teeth=[(-1.04, -0.48, 34, 0.016, 0.0035, True)],
    fore=pt.Limb(y=-0.28, z=-0.02, x=0.10, upper=0.06, lower=0.06, sprawl=1.0, r=0.02, grounded=False,
                 foot=(0.02, 0.025, 0.007), toe_len=0.02, toe_r=0.005, claw=0.0, toes=4),
    hind=pt.Limb(y=0.18, z=-0.02, x=0.07, upper=0.07, lower=0.07, sprawl=1.0, r=0.024, grounded=False,
                 foot=(0.022, 0.03, 0.007), toe_len=0.025, toe_r=0.005, claw=0.0),
    eye=(0.032, -0.47, 0.045, 0.012), nostril=(0.012, -1.03, 0.008),
    back=(0.28, 0.31, 0.18), flank=(0.44, 0.45, 0.28), belly=(0.74, 0.70, 0.42), mark=(0.12, 0.13, 0.08),
    pattern="spots", pattern_freq=11.0, pattern_amount=0.7,
    pivot="centre", voxel=0.0055, max_tris=9000,
)

if __name__ == "__main__":
    pt.main(SPEC)
