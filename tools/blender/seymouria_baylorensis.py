"""
Procedural Seymouria baylorensis (Early Permian seymouriamorph, ~60 cm) for map colonies.

A stocky, sturdy-limbed reptile-like tetrapod well adapted to dry land: a broad, flat,
triangular head with eyes set high, a thick-set body on strong sprawling legs, and a
medium-length tapering tail. Warm brown with darker cross-bands and a cream throat and belly.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/seymouria_baylorensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Seymouria.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Seymouria",
    torso=[
        (-0.42, 0.20, 0.07, 0.065),
        (-0.34, 0.20, 0.12, 0.10),
        (-0.15, 0.20, 0.15, 0.11),
        (0.05, 0.20, 0.14, 0.11),
        (0.20, 0.195, 0.11, 0.09),
        (0.32, 0.18, 0.07, 0.065),
        (0.55, 0.12, 0.04, 0.035),
        (0.80, 0.07, 0.018, 0.016),
        (0.92, 0.055, 0.0, 0.0),
    ],
    head=[
        (-0.40, 0.22, 0.100, 0.065),
        (-0.50, 0.215, 0.095, 0.058),
        (-0.60, 0.200, 0.070, 0.045),
        (-0.67, 0.190, 0.040, 0.030),
        (-0.70, 0.185, 0.0, 0.0),
    ],
    head_power=2.7,
    teeth=[(-0.67, -0.46, 9, 0.010, 0.0035, True)],
    fore=pt.Limb(y=-0.27, z=0.17, x=0.11, upper=0.12, lower=0.13, sprawl=0.85, r=0.040,
                 foot=(0.035, 0.040, 0.014), toe_len=0.035, toe_r=0.009),
    hind=pt.Limb(y=0.20, z=0.17, x=0.10, upper=0.13, lower=0.14, sprawl=0.8, r=0.046,
                 foot=(0.038, 0.048, 0.014), toe_len=0.042, toe_r=0.010),
    eye=(0.06, -0.52, 0.255, 0.018), nostril=(0.03, -0.665, 0.205),
    back=(0.36, 0.25, 0.15), flank=(0.50, 0.36, 0.22), belly=(0.82, 0.74, 0.56), mark=(0.16, 0.11, 0.07),
    pattern="bands", pattern_freq=24.0, pattern_amount=0.6,
    voxel=0.0055, max_tris=7000, drop=0.045,
)

if __name__ == "__main__":
    pt.main(SPEC)
