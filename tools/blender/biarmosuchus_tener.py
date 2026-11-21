"""
Procedural Biarmosuchus tener (Middle Permian biarmosuchian therapsid, ~1.5 m) for map colonies.

One of the most primitive therapsids, from the Ural foothills of Russia: a lightly built,
dog-sized hunter with a long, fairly narrow skull, big eyes, long upper canines, and
slender legs held more under the body than in the pelycosaurs, with a medium tail.
Tawny with darker stripes over the back. Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/biarmosuchus_tener.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Biarmosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Biarmosuchus",
    torso=[
        (-0.42, 0.36, 0.055, 0.065),
        (-0.34, 0.36, 0.09, 0.10),
        (-0.18, 0.355, 0.115, 0.12),
        (0.00, 0.355, 0.11, 0.115),
        (0.16, 0.35, 0.095, 0.10),
        (0.26, 0.34, 0.07, 0.07),
        (0.45, 0.27, 0.035, 0.035),
        (0.65, 0.19, 0.016, 0.016),
        (0.72, 0.17, 0.0, 0.0),
    ],
    head=[
        (-0.40, 0.40, 0.055, 0.060),
        (-0.50, 0.40, 0.055, 0.062),
        (-0.60, 0.38, 0.042, 0.050),
        (-0.69, 0.36, 0.030, 0.038),
        (-0.72, 0.355, 0.0, 0.0),
    ],
    jaw=[
        (-0.42, 0.315, 0.045, 0.022),
        (-0.60, 0.305, 0.032, 0.017),
        (-0.715, 0.307, 0.0, 0.0),
    ],
    teeth=[(-0.71, -0.68, 2, 0.016, 0.005, True), (-0.62, -0.46, 7, 0.011, 0.0035, True)],
    fangs=[(0.028, -0.655, 0.33, 0.06, 0.008, 0.004)],
    fore=pt.Limb(y=-0.26, z=0.30, x=0.085, upper=0.14, lower=0.16, sprawl=0.4, r=0.035,
                 foot=(0.028, 0.040, 0.012), toe_len=0.032, toe_r=0.007),
    hind=pt.Limb(y=0.14, z=0.30, x=0.085, upper=0.15, lower=0.16, sprawl=0.3, r=0.042,
                 foot=(0.030, 0.046, 0.012), toe_len=0.036, toe_r=0.0075),
    eye=(0.045, -0.53, 0.42, 0.020), nostril=(0.016, -0.71, 0.37),
    back=(0.50, 0.36, 0.20), flank=(0.70, 0.54, 0.32), belly=(0.88, 0.80, 0.64), mark=(0.24, 0.15, 0.08),
    pattern="bands", pattern_freq=40.0, pattern_amount=0.7,
    voxel=0.006, max_tris=9000, drop=0.02,
)

if __name__ == "__main__":
    pt.main(SPEC)
