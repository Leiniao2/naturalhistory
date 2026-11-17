"""
Procedural Ophiacodon retroversus (Early Permian ophiacodontid synapsid, ~2 m) for map colonies.

A long-bodied, semi-aquatic early synapsid with a very long, tall and narrow skull (about
a quarter of its body length) lined with many sharp teeth, a long body on fairly long,
sprawling legs and a long tail. Dark olive-brown with faint darker cross-bands and a
yellowish belly.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ophiacodon_retroversus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ophiacodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Ophiacodon",
    torso=[
        (-0.50, 0.33, 0.07, 0.08),
        (-0.40, 0.32, 0.12, 0.13),
        (-0.22, 0.31, 0.15, 0.15),
        (0.00, 0.31, 0.15, 0.15),
        (0.18, 0.30, 0.12, 0.12),
        (0.32, 0.28, 0.085, 0.09),
        (0.55, 0.21, 0.055, 0.06),
        (0.80, 0.14, 0.035, 0.035),
        (1.00, 0.09, 0.018, 0.018),
        (1.12, 0.07, 0.0, 0.0),
    ],
    head=[
        (-0.50, 0.37, 0.072, 0.085),
        (-0.60, 0.375, 0.068, 0.080),
        (-0.72, 0.35, 0.052, 0.062),
        (-0.84, 0.322, 0.040, 0.048),
        (-0.92, 0.305, 0.028, 0.034),
        (-0.95, 0.30, 0.0, 0.0),
    ],
    jaw=[
        (-0.53, 0.295, 0.062, 0.035),
        (-0.70, 0.280, 0.044, 0.024),
        (-0.88, 0.272, 0.028, 0.016),
        (-0.93, 0.272, 0.0, 0.0),
    ],
    teeth=[(-0.91, -0.62, 15, 0.018, 0.0045, True), (-0.90, -0.64, 12, 0.012, 0.004, False)],
    fore=pt.Limb(y=-0.30, z=0.25, x=0.11, upper=0.17, lower=0.19, sprawl=0.72, r=0.045,
                 foot=(0.040, 0.050, 0.018), toe_len=0.045, toe_r=0.009),
    hind=pt.Limb(y=0.16, z=0.25, x=0.10, upper=0.19, lower=0.20, sprawl=0.7, r=0.055,
                 foot=(0.045, 0.060, 0.018), toe_len=0.055, toe_r=0.010),
    eye=(0.05, -0.60, 0.40, 0.017), nostril=(0.022, -0.92, 0.325),
    back=(0.22, 0.22, 0.15), flank=(0.34, 0.32, 0.21), belly=(0.74, 0.66, 0.42), mark=(0.12, 0.11, 0.08),
    pattern="bands", pattern_freq=18.0, pattern_amount=0.5,
    voxel=0.0075, max_tris=11000, drop=0.05,
)

if __name__ == "__main__":
    pt.main(SPEC)
