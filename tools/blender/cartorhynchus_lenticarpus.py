"""
Procedural Cartorhynchus lenticarpus (Early Triassic ichthyosauriform, ~40 cm).

A tiny early relative of the ichthyosaurs from Anhui, China, about 248 million years old:
a short, blunt, toothless snout (it probably sucked in soft prey), a stout body, large
flippers with flexible wrists that may have let it crawl ashore like a seal, and a long
tail without the later ichthyosaurs' fish-like fin. Built with nh_tri_tetrapod; painted
dark grey above, pale below. Faces -Y, pivot at the body centre (swimmer).

Output: Assets/Resources/Models/Species/Cartorhynchus.fbx
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
    (-1.00, -0.010, 0.012, 0.012),
    (-0.96, -0.004, 0.030, 0.030),
    (-0.90, 0.004, 0.050, 0.048),
    (-0.82, 0.008, 0.066, 0.060),
    (-0.74, 0.008, 0.072, 0.066),
    (-0.66, 0.006, 0.076, 0.072),
    (-0.52, 0.004, 0.104, 0.096),
    (-0.32, 0.004, 0.124, 0.112),
    (-0.10, 0.004, 0.118, 0.106),
    (0.08, 0.002, 0.090, 0.084),
    (0.24, 0.000, 0.058, 0.060, sway(0.24)),
    (0.46, 0.000, 0.036, 0.040, sway(0.46)),
    (0.72, 0.000, 0.018, 0.022, sway(0.72)),
    (0.96, 0.000, 0.003, 0.004, sway(0.96)),
]

FORE = tt.Limb(pts=[(0.08, -0.44, -0.04), (0.16, -0.42, -0.07), (0.21, -0.38, -0.08)],
               radii=[0.030, 0.024, 0.019], paddle=(0.110, 0.055, 125, -8))
HIND = tt.Limb(pts=[(0.07, 0.04, -0.04), (0.13, 0.08, -0.06), (0.16, 0.11, -0.065)],
               radii=[0.024, 0.019, 0.015], paddle=(0.070, 0.036, 145, -8))

SPEC = tt.TetrapodSpec(
    name="Cartorhynchus",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.0080, max_tris=9000,
    pivot="centre",
    mouth=(-1.0, -0.90, -0.012, -0.004, 0.004),
    eyes=(-0.82, 0.040, 0.019, (0.25, 0.25, 0.30)),
    nostrils=(-0.94, 0.025),
    back=(0.18, 0.20, 0.24), flank=(0.38, 0.40, 0.44), belly=(0.86, 0.86, 0.82),
    pattern=("mottle", (0.12, 0.13, 0.16), 9.0, 0.3),
)

if __name__ == "__main__":
    tt.run(SPEC)
