"""
Procedural Hovasaurus boulei (Late Permian tangasaurid, ~60 cm) swimming, for map colonies.

An aquatic early diapsid from the lakes of Madagascar: a lizard-like reptile with a small,
pointed head, a slim body and an enormously long, deep, sideways-flattened tail (about two
thirds of its length) that it swung to drive itself through the water; it swallowed pebbles
as ballast. Small legs tucked against the body while swimming, the hind feet broad.
Dark olive-brown above with a pale greenish belly and faint dark bands on the tail.
Built with nh_per_tetra. Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/hovasaurus_boulei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hovasaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Hovasaurus",
    torso=[
        (-0.40, 0.0, 0.035, 0.035),
        (-0.32, 0.0, 0.055, 0.050),
        (-0.18, 0.0, 0.065, 0.055),
        (-0.04, 0.0, 0.058, 0.052),
        (0.04, 0.0, 0.040, 0.050),
        (0.20, 0.0, 0.022, 0.055),
        (0.50, 0.0, 0.014, 0.058),
        (0.80, 0.0, 0.009, 0.042),
        (1.00, 0.0, 0.004, 0.025),
        (1.06, 0.0, 0.0, 0.0),
    ],
    head=[
        (-0.38, 0.008, 0.035, 0.030),
        (-0.45, 0.008, 0.034, 0.028),
        (-0.52, 0.002, 0.022, 0.019),
        (-0.57, -0.002, 0.010, 0.010),
        (-0.585, -0.002, 0.0, 0.0),
    ],
    teeth=[(-0.57, -0.47, 8, 0.008, 0.0018, True)],
    fore=pt.Limb(y=-0.28, z=-0.01, x=0.045, upper=0.05, lower=0.05, sprawl=1.0, r=0.012, grounded=False,
                 foot=(0.012, 0.016, 0.005), toe_len=0.02, toe_r=0.003, claw=0.0),
    hind=pt.Limb(y=-0.02, z=-0.01, x=0.04, upper=0.06, lower=0.06, sprawl=1.0, r=0.016, grounded=False,
                 foot=(0.02, 0.03, 0.006), paddle=True, claw=0.0),
    eye=(0.026, -0.46, 0.022, 0.010), nostril=(0.008, -0.57, 0.008),
    back=(0.22, 0.24, 0.15), flank=(0.36, 0.38, 0.24), belly=(0.74, 0.76, 0.58), mark=(0.10, 0.11, 0.07),
    pattern="bands", pattern_freq=28.0, pattern_amount=0.5,
    pivot="centre", voxel=0.0045, max_tris=6000,
)

if __name__ == "__main__":
    pt.main(SPEC)
