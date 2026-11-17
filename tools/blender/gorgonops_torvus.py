"""
Procedural Gorgonops torvus (Late Permian gorgonopsian, ~2 m) for map colonies.

The namesake gorgonopsian, a top predator of the Karoo: a long, fairly low skull with a
huge gape and long sabre-like upper canines that hang below the chin, a deep chest on long,
fairly upright legs (more erect than in earlier synapsids) and a medium-length tail.
Tawny ochre with dark brown vertical stripes over the back and flanks and a pale belly;
smaller and more lightly built than its giant Russian relative Inostrancevia.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/gorgonops_torvus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gorgonops.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Gorgonops",
    torso=[
        (-0.45, 0.43, 0.07, 0.08),
        (-0.36, 0.43, 0.12, 0.13),
        (-0.20, 0.42, 0.15, 0.15),
        (0.00, 0.42, 0.14, 0.14),
        (0.18, 0.42, 0.12, 0.12),
        (0.30, 0.41, 0.09, 0.09),
        (0.50, 0.34, 0.05, 0.05),
        (0.75, 0.24, 0.03, 0.03),
        (0.95, 0.16, 0.012, 0.012),
        (1.02, 0.14, 0.0, 0.0),
    ],
    head=[
        (-0.44, 0.48, 0.075, 0.08),
        (-0.54, 0.48, 0.075, 0.08),
        (-0.66, 0.45, 0.060, 0.065),
        (-0.76, 0.42, 0.045, 0.05),
        (-0.82, 0.40, 0.030, 0.035),
        (-0.84, 0.395, 0.0, 0.0),
    ],
    jaw=[
        (-0.47, 0.375, 0.060, 0.030),
        (-0.65, 0.362, 0.045, 0.024),
        (-0.81, 0.358, 0.025, 0.018),
        (-0.84, 0.358, 0.0, 0.0),
    ],
    teeth=[(-0.83, -0.79, 3, 0.02, 0.006, True), (-0.72, -0.58, 7, 0.012, 0.004, True)],
    fangs=[(0.036, -0.755, 0.385, 0.10, 0.012, 0.012)],
    fore=pt.Limb(y=-0.28, z=0.35, x=0.10, upper=0.17, lower=0.20, sprawl=0.3, r=0.05,
                 foot=(0.035, 0.050, 0.016), toe_len=0.04, toe_r=0.009),
    hind=pt.Limb(y=0.20, z=0.36, x=0.10, upper=0.19, lower=0.20, sprawl=0.2, r=0.06,
                 foot=(0.038, 0.060, 0.016), toe_len=0.045, toe_r=0.010),
    eye=(0.055, -0.60, 0.50, 0.017), nostril=(0.02, -0.83, 0.42),
    back=(0.50, 0.36, 0.20), flank=(0.66, 0.50, 0.30), belly=(0.86, 0.78, 0.62), mark=(0.22, 0.14, 0.08),
    pattern="bands", pattern_freq=34.0, pattern_amount=0.75,
    voxel=0.007, max_tris=11000,
)

if __name__ == "__main__":
    pt.main(SPEC)
