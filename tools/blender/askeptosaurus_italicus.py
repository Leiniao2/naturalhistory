"""
Procedural Askeptosaurus italicus (Middle Triassic thalattosaur, ~2 m) for map colonies.

A long, eel-like marine reptile from Monte San Giorgio on the Swiss-Italian border: a long,
narrow, pointed snout full of small teeth, large eyes, a slender body, short limbs with
webbed, paddle-like feet and a very long, deep, flattened tail that drove it through the
water. Built with nh_tri_tetrapod; painted brown-grey with dark bands. Faces -Y, pivot at
the body centre (swimmer).

Output: Assets/Resources/Models/Species/Askeptosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y + 0.1) / 1.1)
    return 0.12 * s * s


AXIS = [
    (-1.00, 0.000, 0.005, 0.005),
    (-0.96, 0.000, 0.010, 0.010),
    (-0.90, 0.002, 0.016, 0.015),
    (-0.84, 0.004, 0.024, 0.022),
    (-0.80, 0.004, 0.026, 0.024),
    (-0.76, 0.002, 0.020, 0.020),
    (-0.66, 0.000, 0.024, 0.026),
    (-0.50, 0.000, 0.038, 0.040),
    (-0.32, 0.000, 0.046, 0.046),
    (-0.14, 0.000, 0.042, 0.044),
    (0.00, 0.000, 0.030, 0.038, sway(0.0)),
    (0.24, 0.000, 0.020, 0.038, sway(0.24)),
    (0.50, 0.000, 0.014, 0.032, sway(0.50)),
    (0.76, 0.000, 0.008, 0.020, sway(0.76)),
    (1.00, 0.000, 0.002, 0.004, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.035, -0.46, -0.02), (0.08, -0.44, -0.035), (0.11, -0.41, -0.04)],
               radii=[0.012, 0.010, 0.008], paddle=(0.045, 0.024, 130, -5))
HIND = tt.Limb(pts=[(0.03, -0.10, -0.02), (0.075, -0.07, -0.035), (0.10, -0.04, -0.04)],
               radii=[0.014, 0.011, 0.009], paddle=(0.055, 0.028, 150, -5))

SPEC = tt.TetrapodSpec(
    name="Askeptosaurus",
    axis=AXIS, power=2.3,
    limbs=[FORE, HIND],
    voxel=0.0055, max_tris=9000,
    pivot="centre",
    mouth=(-1.0, -0.79, -0.002, 0.000, 0.003),
    teeth=(10, 0.007, 0.0018, -0.99, -0.82), lower_teeth=True,
    eyes=(-0.805, 0.016, 0.011, (0.85, 0.65, 0.20)),
    back=(0.22, 0.20, 0.17), flank=(0.46, 0.42, 0.36), belly=(0.86, 0.84, 0.76),
    pattern=("bands", (0.13, 0.12, 0.10), 26.0, 0.8, -0.7, 1.0),
)

if __name__ == "__main__":
    tt.run(SPEC)
