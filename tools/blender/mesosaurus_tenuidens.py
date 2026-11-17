"""
Procedural Mesosaurus tenuidens (Early Permian mesosaur, ~1 m) for map colonies, swimming.

One of the first reptiles to return to the water: a slender body, a very long, narrow
snout bristling with long needle-like teeth (for straining or snapping up small
crustaceans), a long, deep, side-flattened tail for sculling, and broad webbed hind feet
used as paddles, the smaller forelimbs tucked back along the body. Dark grey-brown above,
pale below. Built with nh_per_tetra. Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/mesosaurus_tenuidens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mesosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Mesosaurus",
    torso=[
        (-0.40, 0.0, 0.045, 0.045),
        (-0.30, 0.0, 0.070, 0.065),
        (-0.10, 0.0, 0.080, 0.072),
        (0.10, 0.0, 0.072, 0.068),
        (0.22, 0.0, 0.052, 0.055),
        (0.45, 0.0, 0.028, 0.050),
        (0.75, 0.0, 0.014, 0.040),
        (0.95, 0.0, 0.005, 0.020),
        (1.00, 0.0, 0.0, 0.0),
    ],
    head=[
        (-0.38, 0.010, 0.045, 0.038),
        (-0.46, 0.010, 0.040, 0.033),
        (-0.55, 0.002, 0.022, 0.019),
        (-0.75, -0.004, 0.012, 0.011),
        (-0.85, -0.008, 0.006, 0.006),
        (-0.87, -0.008, 0.0, 0.0),
    ],
    teeth=[(-0.84, -0.50, 26, 0.020, 0.0018, True)],
    fore=pt.Limb(y=-0.26, z=-0.02, x=0.05, upper=0.06, lower=0.06, sprawl=1.0, r=0.016, grounded=False,
                 foot=(0.015, 0.02, 0.006), toe_len=0.02, toe_r=0.004, claw=0.0),
    hind=pt.Limb(y=0.18, z=-0.02, x=0.045, upper=0.08, lower=0.08, sprawl=1.0, r=0.022, grounded=False,
                 foot=(0.03, 0.04, 0.007), paddle=True, claw=0.0),
    eye=(0.030, -0.45, 0.028, 0.011), nostril=(0.008, -0.56, 0.018),
    back=(0.22, 0.22, 0.20), flank=(0.36, 0.35, 0.31), belly=(0.80, 0.78, 0.70), mark=(0.14, 0.14, 0.12),
    pattern="none", pivot="centre", voxel=0.005, max_tris=6000,
)

if __name__ == "__main__":
    pt.main(SPEC)
