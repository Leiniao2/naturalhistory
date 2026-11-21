"""
Procedural Sphenacodon ferox (Early Permian sphenacodontid synapsid, ~3 m) for map colonies.

Dimetrodon's close relative without the tall sail: a deep, narrow skull with a strong
step in the upper jaw and long stabbing canines, a long body carried on sprawling legs,
a long tail and only a low ridge of tall neural spines along the back.
Reddish-brown with dark bands. Built with nh_per_tetra (+ nh_b2_permian_tetra crest).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/sphenacodon_ferox.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sphenacodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402
import nh_b2_permian_tetra as bt  # noqa: E402

SPEC = pt.Spec(
    name="Sphenacodon",
    torso=[
        (-0.46, 0.28, 0.06, 0.07),
        (-0.38, 0.28, 0.10, 0.11),
        (-0.20, 0.28, 0.13, 0.13),
        (0.00, 0.28, 0.13, 0.125),
        (0.18, 0.27, 0.11, 0.11),
        (0.30, 0.26, 0.08, 0.08),
        (0.55, 0.19, 0.045, 0.045),
        (0.85, 0.11, 0.022, 0.022),
        (1.10, 0.06, 0.008, 0.008),
        (1.16, 0.05, 0.0, 0.0),
    ],
    head=[
        (-0.44, 0.32, 0.060, 0.075),
        (-0.54, 0.32, 0.058, 0.075),
        (-0.66, 0.30, 0.045, 0.062),
        (-0.76, 0.28, 0.033, 0.050),
        (-0.80, 0.275, 0.0, 0.0),
    ],
    jaw=[
        (-0.46, 0.235, 0.050, 0.026),
        (-0.66, 0.225, 0.036, 0.020),
        (-0.79, 0.228, 0.0, 0.0),
    ],
    teeth=[(-0.79, -0.74, 3, 0.02, 0.005, True), (-0.68, -0.52, 8, 0.013, 0.004, True)],
    fangs=[(0.030, -0.715, 0.245, 0.075, 0.010, 0.0)],
    fore=pt.Limb(y=-0.28, z=0.22, x=0.10, upper=0.15, lower=0.15, sprawl=0.75, r=0.042,
                 foot=(0.035, 0.045, 0.015), toe_len=0.04, toe_r=0.009),
    hind=pt.Limb(y=0.16, z=0.22, x=0.10, upper=0.16, lower=0.16, sprawl=0.7, r=0.05,
                 foot=(0.038, 0.055, 0.015), toe_len=0.045, toe_r=0.010),
    eye=(0.045, -0.58, 0.34, 0.016), nostril=(0.018, -0.79, 0.29),
    back=(0.38, 0.22, 0.14), flank=(0.56, 0.34, 0.22), belly=(0.82, 0.70, 0.54), mark=(0.20, 0.11, 0.07),
    pattern="bands", pattern_freq=26.0, pattern_amount=0.6,
    crisp=bt.sail(-0.38, 0.28, 0.10, n=20, spine_col=(0.30, 0.18, 0.12), membrane=True,
                  sail_col=(0.42, 0.25, 0.16), peak=0.45),
    voxel=0.007, max_tris=10000, drop=0.03,
)

if __name__ == "__main__":
    pt.main(SPEC)
