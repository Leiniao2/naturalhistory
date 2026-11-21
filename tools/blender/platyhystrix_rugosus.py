"""
Procedural Platyhystrix rugosus (Early Permian dissorophid temnospondyl, ~1 m) for map colonies.

A sturdy land-going amphibian with a broad, flat-topped head, short strong legs and a short
tail, crowned by a tall sail of neural spines along the back - each spine rough with bumps
and side knobs, covered in skin in life. Ochre-brown with dark blotches and a paler sail.
Built with nh_per_tetra (+ nh_b2_permian_tetra sail). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/platyhystrix_rugosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Platyhystrix.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402
import nh_b2_permian_tetra as bt  # noqa: E402

SPEC = pt.Spec(
    name="Platyhystrix",
    torso=[
        (-0.36, 0.20, 0.08, 0.06),
        (-0.28, 0.21, 0.14, 0.10),
        (-0.10, 0.22, 0.16, 0.11),
        (0.10, 0.22, 0.15, 0.105),
        (0.22, 0.21, 0.11, 0.085),
        (0.34, 0.18, 0.06, 0.05),
        (0.55, 0.12, 0.03, 0.03),
        (0.70, 0.09, 0.0, 0.0),
    ],
    head=[
        (-0.33, 0.235, 0.13, 0.065),
        (-0.43, 0.235, 0.13, 0.062),
        (-0.53, 0.222, 0.11, 0.052),
        (-0.61, 0.205, 0.075, 0.038),
        (-0.65, 0.198, 0.0, 0.0),
    ],
    head_power=2.8,
    jaw=[
        (-0.35, 0.175, 0.12, 0.026),
        (-0.55, 0.170, 0.09, 0.020),
        (-0.64, 0.172, 0.0, 0.0),
    ],
    teeth=[(-0.63, -0.42, 11, 0.009, 0.0035, True)],
    fore=pt.Limb(y=-0.22, z=0.17, x=0.13, upper=0.10, lower=0.11, sprawl=0.75, r=0.038, toes=4,
                 foot=(0.035, 0.04, 0.013), toe_len=0.032, toe_r=0.009, toe_fan=70, claw=0.4),
    hind=pt.Limb(y=0.18, z=0.17, x=0.11, upper=0.11, lower=0.11, sprawl=0.7, r=0.044,
                 foot=(0.038, 0.045, 0.013), toe_len=0.036, toe_r=0.009, claw=0.4),
    eye=(0.08, -0.47, 0.28, 0.020), nostril=(0.04, -0.63, 0.215),
    back=(0.45, 0.30, 0.15), flank=(0.60, 0.42, 0.22), belly=(0.85, 0.74, 0.46), mark=(0.20, 0.12, 0.07),
    pattern="spots", pattern_freq=13.0, pattern_amount=0.55,
    crisp=bt.sail(-0.26, 0.30, 0.32, n=17, spine_col=(0.52, 0.36, 0.20), sail_col=(0.78, 0.55, 0.30),
                  top_col=(0.88, 0.70, 0.40), knobs=4, knob_col=(0.62, 0.44, 0.24), lean=0.04, peak=0.4,
                  spine_r=0.009),
    voxel=0.006, max_tris=9000, scale_bumps=1.3, drop=0.04,
)

if __name__ == "__main__":
    pt.main(SPEC)
