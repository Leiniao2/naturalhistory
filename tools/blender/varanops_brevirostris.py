"""
Procedural Varanops brevirostris (Early Permian varanopid synapsid, ~1.2 m) for map colonies.

A slender, long-legged, monitor-lizard-like hunter: a narrow, fairly long head with sharp,
recurved teeth, a supple body held higher off the ground than in other early synapsids and
a long whip-like tail. Sandy buff with rows of dark brown spots and banded tail.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/varanops_brevirostris.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Varanops.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Varanops",
    torso=[
        (-0.45, 0.25, 0.048, 0.052),
        (-0.36, 0.25, 0.085, 0.085),
        (-0.20, 0.24, 0.10, 0.095),
        (0.00, 0.24, 0.10, 0.095),
        (0.15, 0.235, 0.085, 0.085),
        (0.25, 0.225, 0.06, 0.06),
        (0.50, 0.17, 0.035, 0.035),
        (0.80, 0.10, 0.02, 0.02),
        (1.05, 0.05, 0.008, 0.008),
        (1.12, 0.04, 0.0, 0.0),
    ],
    head=[
        (-0.43, 0.27, 0.050, 0.050),
        (-0.50, 0.275, 0.048, 0.046),
        (-0.60, 0.26, 0.035, 0.036),
        (-0.68, 0.245, 0.024, 0.024),
        (-0.71, 0.24, 0.0, 0.0),
    ],
    jaw=[
        (-0.45, 0.232, 0.040, 0.020),
        (-0.60, 0.226, 0.028, 0.014),
        (-0.69, 0.226, 0.0, 0.0),
    ],
    teeth=[(-0.69, -0.50, 11, 0.014, 0.0035, True)],
    fore=pt.Limb(y=-0.24, z=0.20, x=0.07, upper=0.13, lower=0.15, sprawl=0.6, r=0.030,
                 foot=(0.025, 0.035, 0.012), toe_len=0.035, toe_r=0.006),
    hind=pt.Limb(y=0.12, z=0.20, x=0.07, upper=0.14, lower=0.16, sprawl=0.55, r=0.036,
                 foot=(0.028, 0.040, 0.012), toe_len=0.042, toe_r=0.0065),
    eye=(0.038, -0.52, 0.29, 0.013), nostril=(0.016, -0.68, 0.258),
    back=(0.50, 0.40, 0.25), flank=(0.64, 0.53, 0.35), belly=(0.84, 0.78, 0.62), mark=(0.20, 0.13, 0.08),
    pattern="spots", pattern_freq=30.0, pattern_amount=0.75,
    voxel=0.006, max_tris=8000, drop=0.035,
)

if __name__ == "__main__":
    pt.main(SPEC)
