"""
Procedural Euparkeria capensis (Early-Middle Triassic archosauriform, ~60 cm).

A small, lightly built predator from South Africa, close to the ancestry of crocodiles and
dinosaurs: a narrow head with sharp teeth, a slim body with a double row of small bony
plates along the back, a long tail and hind legs longer than the arms, so it may have run
short distances on its hind legs. Built with nh_tri_tetrapod; painted sandy brown with dark
flank stripes. Faces -Y, pivot on the ground.

Output: Assets/Resources/Models/Species/Euparkeria.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.0) / 1.0)
    return 0.08 * s * s


AXIS = [
    (-1.00, 0.300, 0.006, 0.010),
    (-0.96, 0.304, 0.016, 0.022),
    (-0.89, 0.312, 0.026, 0.034),
    (-0.82, 0.322, 0.034, 0.042),
    (-0.77, 0.325, 0.036, 0.042),
    (-0.72, 0.318, 0.026, 0.030),
    (-0.62, 0.305, 0.034, 0.040),
    (-0.50, 0.300, 0.056, 0.064),
    (-0.34, 0.302, 0.068, 0.074),
    (-0.18, 0.305, 0.066, 0.070),
    (-0.04, 0.305, 0.054, 0.056),
    (0.10, 0.295, 0.036, 0.038, sway(0.10)),
    (0.34, 0.255, 0.022, 0.024, sway(0.34)),
    (0.62, 0.200, 0.012, 0.013, sway(0.62)),
    (0.98, 0.140, 0.002, 0.002, sway(0.98)),
]

FORE = tt.Limb(pts=[(0.05, -0.47, 0.28), (0.08, -0.45, 0.17), (0.08, -0.49, 0.05), (0.08, -0.51, 0.010)],
               radii=[0.020, 0.016, 0.012, 0.010], toes=5, toe_len=0.030, toe_r=0.005, toe_spread=55,
               toe_yaw=8, stride=14, claw_len=0.010)
HIND = tt.Limb(pts=[(0.055, -0.04, 0.30), (0.085, -0.10, 0.18), (0.085, -0.01, 0.06), (0.085, -0.05, 0.010)],
               radii=[0.036, 0.024, 0.016, 0.012], toes=4, toe_len=0.050, toe_r=0.0065, toe_spread=45,
               toe_yaw=8, stride=-14, claw_len=0.012)


SPEC = tt.TetrapodSpec(
    name="Euparkeria",
    axis=AXIS,
    blobs=[((0.05, -0.04, 0.29), (0.040, 0.08, 0.06), 25)],
    limbs=[FORE, HIND],
    voxel=0.0065, max_tris=9000,
    mouth=(-0.995, -0.78, 0.296, 0.310, 0.003),
    teeth=(9, 0.010, 0.0028, -0.97, -0.80), lower_teeth=True,
    eyes=(-0.79, 0.336, 0.011, (0.85, 0.60, 0.15)),
    nostrils=(-0.96, 0.31),
    plates=[dict(xs=(0.012, -0.012), y0=-0.66, y1=0.55, step=0.042, size=0.010, wide=0.8, taper=0.6, shrink=0.2,
                 follow=sway, col=(0.30, 0.20, 0.10), keel_col=(0.45, 0.32, 0.16), height=1.2)],
    back=(0.38, 0.27, 0.15), flank=(0.66, 0.52, 0.32), belly=(0.90, 0.84, 0.68),
    pattern=("stripe", (0.30, 0.20, 0.10), 0.35, 0.20, 0.7, -0.7, 0.6),
)

if __name__ == "__main__":
    tt.run(SPEC)
