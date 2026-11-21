"""
Procedural Clevosaurus hudsoni (Late Triassic rhynchocephalian, ~30 cm).

A tuatara relative from the limestone fissure fills of south-west England: a lizard-like
body, a deep, short-snouted head whose teeth are fused to the jaw bones and worn into
cutting blades, a low crest of soft spines down the neck and back, and sprawling legs.
Built with nh_tri_tetrapod; painted olive-green with pale speckles. Faces -Y, pivot on the
ground.

Output: Assets/Resources/Models/Species/Clevosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.0) / 1.0)
    return 0.12 * s * s


AXIS = [
    (-1.00, 0.140, 0.010, 0.016),
    (-0.97, 0.146, 0.026, 0.032),
    (-0.92, 0.155, 0.040, 0.042),
    (-0.85, 0.162, 0.050, 0.048),
    (-0.80, 0.162, 0.048, 0.046),
    (-0.74, 0.158, 0.040, 0.040),
    (-0.64, 0.158, 0.052, 0.048),
    (-0.48, 0.162, 0.078, 0.062),
    (-0.28, 0.164, 0.084, 0.066),
    (-0.10, 0.160, 0.074, 0.060),
    (0.04, 0.150, 0.050, 0.046),
    (0.22, 0.128, 0.034, 0.034, sway(0.22)),
    (0.48, 0.094, 0.020, 0.022, sway(0.48)),
    (0.76, 0.064, 0.010, 0.011, sway(0.76)),
    (1.00, 0.045, 0.002, 0.002, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.06, -0.55, 0.14), (0.15, -0.55, 0.12), (0.17, -0.58, 0.03), (0.17, -0.60, 0.008)],
               radii=[0.024, 0.019, 0.014, 0.012], toes=5, toe_len=0.04, toe_r=0.006, toe_spread=75,
               toe_yaw=20, stride=14, claw_len=0.012)
HIND = tt.Limb(pts=[(0.055, -0.04, 0.14), (0.16, -0.05, 0.12), (0.18, 0.00, 0.03), (0.18, -0.02, 0.008)],
               radii=[0.030, 0.023, 0.016, 0.013], toes=5, toe_len=0.05, toe_r=0.007, toe_spread=70,
               toe_yaw=25, stride=-14, claw_len=0.013)

SPEC = tt.TetrapodSpec(
    name="Clevosaurus",
    axis=AXIS,
    blobs=[((0.035, -0.82, 0.145), (0.03, 0.04, 0.03))],
    limbs=[FORE, HIND],
    voxel=0.0065, max_tris=9000,
    scale_bump=0.0022, scale_freq=70.0,
    mouth=(-0.995, -0.80, 0.134, 0.150, 0.004),
    eyes=(-0.85, 0.180, 0.0135, (0.20, 0.18, 0.10)),
    nostrils=(-0.98, 0.15),
    plates=[dict(xs=(0.0,), y0=-0.76, y1=0.70, step=0.024, size=0.010, kind="spike", height=2.0, taper=0.7,
                 follow=sway, col=(0.30, 0.34, 0.20), keel_col=(0.70, 0.66, 0.44))],
    back=(0.24, 0.30, 0.18), flank=(0.40, 0.46, 0.28), belly=(0.80, 0.80, 0.60),
    pattern=("spots", (0.78, 0.76, 0.52), 26.0, 0.6),
)

if __name__ == "__main__":
    tt.run(SPEC)
