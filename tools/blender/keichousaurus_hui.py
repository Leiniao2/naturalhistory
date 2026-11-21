"""
Procedural Keichousaurus hui (Middle Triassic pachypleurosaur, ~25 cm) for map colonies.

A small, slender sauropterygian from Guizhou, China, one of the most common fossil
reptiles in the world: a small head with needle teeth on a long neck, a slim body, a long
tail and paddle-like limbs, the front pair broader than the hind. Some fossils hold
embryos, showing it bore live young. Built with nh_tri_tetrapod; painted dark grey-blue
above and pale below. Faces -Y, pivot at the body centre (swimmer).

Output: Assets/Resources/Models/Species/Keichousaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.2) / 0.8)
    return 0.10 * s * s


AXIS = [
    (-1.00, 0.000, 0.007, 0.006),
    (-0.96, 0.000, 0.016, 0.012),
    (-0.90, 0.002, 0.024, 0.018),
    (-0.85, 0.003, 0.027, 0.021),
    (-0.80, 0.002, 0.020, 0.018),
    (-0.62, 0.000, 0.024, 0.022),
    (-0.44, 0.000, 0.040, 0.034),
    (-0.26, 0.000, 0.060, 0.044),
    (-0.06, 0.000, 0.062, 0.045),
    (0.10, 0.000, 0.046, 0.038),
    (0.26, 0.000, 0.030, 0.030, sway(0.26)),
    (0.50, 0.000, 0.019, 0.020, sway(0.50)),
    (0.76, 0.000, 0.010, 0.011, sway(0.76)),
    (1.00, 0.000, 0.002, 0.002, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.04, -0.36, -0.02), (0.10, -0.33, -0.03), (0.14, -0.29, -0.035)],
               radii=[0.016, 0.013, 0.010], paddle=(0.060, 0.030, 125, -5))
HIND = tt.Limb(pts=[(0.04, 0.08, -0.02), (0.08, 0.12, -0.03), (0.10, 0.15, -0.032)],
               radii=[0.014, 0.011, 0.009], paddle=(0.040, 0.020, 150, -5))

SPEC = tt.TetrapodSpec(
    name="Keichousaurus",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.0055, max_tris=8000,
    pivot="centre",
    mouth=(-1.0, -0.86, -0.002, 0.000, 0.003),
    teeth=(7, 0.008, 0.0022, -0.99, -0.88), lower_teeth=True,
    eyes=(-0.865, 0.014, 0.0085, (0.85, 0.70, 0.30), 0.016),
    back=(0.16, 0.19, 0.24), flank=(0.40, 0.44, 0.50), belly=(0.88, 0.88, 0.84),
    pattern=("spots", (0.10, 0.12, 0.16), 30.0, 0.5),
)

if __name__ == "__main__":
    tt.run(SPEC)
