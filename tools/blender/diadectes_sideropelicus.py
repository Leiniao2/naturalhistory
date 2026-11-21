"""
Procedural Diadectes sideropelicus (Early Permian diadectid, ~3 m) for map colonies.

One of the first large plant-eating land vertebrates: a heavy, barrel-shaped body slung
low between short, massive sprawling legs, a short, deep, blunt head with peg-like front
teeth and a short thick tail. Olive-brown with paler belly and faint darker bands.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/diadectes_sideropelicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Diadectes.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Diadectes",
    torso=[
        (-0.42, 0.25, 0.08, 0.08),
        (-0.34, 0.26, 0.15, 0.14),
        (-0.18, 0.26, 0.23, 0.165),
        (0.02, 0.26, 0.25, 0.17),
        (0.20, 0.25, 0.21, 0.15),
        (0.34, 0.23, 0.12, 0.10),
        (0.50, 0.17, 0.06, 0.055),
        (0.68, 0.11, 0.025, 0.025),
        (0.76, 0.09, 0.0, 0.0),
    ],
    head=[
        (-0.38, 0.29, 0.095, 0.085),
        (-0.46, 0.29, 0.090, 0.082),
        (-0.54, 0.27, 0.072, 0.066),
        (-0.59, 0.245, 0.050, 0.046),
        (-0.61, 0.235, 0.0, 0.0),
    ],
    jaw=[
        (-0.40, 0.225, 0.08, 0.035),
        (-0.55, 0.215, 0.055, 0.025),
        (-0.60, 0.218, 0.0, 0.0),
    ],
    teeth=[(-0.605, -0.56, 3, 0.012, 0.006, True)],
    fore=pt.Limb(y=-0.24, z=0.19, x=0.18, upper=0.14, lower=0.15, sprawl=0.85, r=0.065,
                 foot=(0.050, 0.055, 0.018), toe_len=0.035, toe_r=0.013, claw=0.6),
    hind=pt.Limb(y=0.20, z=0.19, x=0.16, upper=0.15, lower=0.15, sprawl=0.8, r=0.072,
                 foot=(0.055, 0.065, 0.018), toe_len=0.04, toe_r=0.014, claw=0.6),
    eye=(0.07, -0.49, 0.32, 0.018), nostril=(0.03, -0.595, 0.27),
    back=(0.34, 0.29, 0.17), flank=(0.50, 0.42, 0.27), belly=(0.74, 0.68, 0.50), mark=(0.22, 0.20, 0.13),
    pattern="bands", pattern_freq=16.0, pattern_amount=0.4,
    voxel=0.008, max_tris=10000, drop=0.03,
)

if __name__ == "__main__":
    pt.main(SPEC)
