"""
Procedural Dinocephalosaurus orientalis (Middle Triassic archosauromorph, ~5 m).

A fully marine relative of Tanystropheus from Guizhou, China: a neck of over thirty long
vertebrae, longer than body and tail together, a small head with fang-like teeth, a short
body, a modest tail and flipper-like limbs. A fossil with an embryo shows it gave birth to
live young at sea. Built with nh_tri_tetrapod; painted grey-green with dark neck bands.
Faces -Y, pivot at the body centre (swimmer).

Output: Assets/Resources/Models/Species/Dinocephalosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.4) / 0.6)
    return 0.07 * s * s


def bend(y):
    # a gentle S along the neck
    if y > -0.15:
        return 0.0
    return 0.03 * tt.math.sin((y + 0.15) * 6.0)


AXIS = [
    (-1.00, 0.000, 0.004, 0.004, bend(-1.0)),
    (-0.975, 0.000, 0.011, 0.009, bend(-0.975)),
    (-0.945, 0.002, 0.017, 0.014, bend(-0.945)),
    (-0.915, 0.004, 0.020, 0.017, bend(-0.915)),
    (-0.89, 0.003, 0.014, 0.013, bend(-0.89)),
    (-0.72, 0.000, 0.016, 0.016, bend(-0.72)),
    (-0.48, 0.000, 0.022, 0.022, bend(-0.48)),
    (-0.26, 0.000, 0.034, 0.032, bend(-0.26)),
    (-0.10, 0.000, 0.060, 0.050),
    (0.06, 0.000, 0.078, 0.060),
    (0.22, 0.000, 0.070, 0.054),
    (0.36, 0.000, 0.040, 0.036),
    (0.56, 0.000, 0.022, 0.026, sway(0.56)),
    (0.78, 0.000, 0.011, 0.016, sway(0.78)),
    (0.96, 0.000, 0.002, 0.003, sway(0.96)),
]

FORE = tt.Limb(pts=[(0.05, -0.02, -0.03), (0.11, 0.00, -0.045), (0.15, 0.03, -0.05)],
               radii=[0.020, 0.016, 0.012], paddle=(0.070, 0.032, 130, -5))
HIND = tt.Limb(pts=[(0.05, 0.28, -0.03), (0.10, 0.31, -0.04), (0.13, 0.34, -0.045)],
               radii=[0.018, 0.014, 0.011], paddle=(0.060, 0.028, 150, -5))

SPEC = tt.TetrapodSpec(
    name="Dinocephalosaurus",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.0060, max_tris=9000,
    pivot="centre",
    mouth=(-1.0, -0.91, -0.002, 0.000, 0.003),
    teeth=(6, 0.012, 0.0028, -0.99, -0.925), lower_teeth=True,
    eyes=(-0.925, 0.010, 0.0075, (0.85, 0.65, 0.20), 0.012),
    back=(0.20, 0.24, 0.20), flank=(0.44, 0.48, 0.40), belly=(0.86, 0.86, 0.78),
    pattern=("bands", (0.12, 0.14, 0.12), 40.0, 0.7, -0.89, -0.12),
)

if __name__ == "__main__":
    tt.run(SPEC)
