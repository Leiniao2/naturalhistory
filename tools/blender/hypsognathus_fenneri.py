"""
Procedural Hypsognathus fenneri (Late Triassic procolophonid, ~33 cm) for map colonies.

A squat, lizard-like parareptile from New Jersey and Connecticut: a broad, flat body on
short sprawling legs, a short tail and a wide, triangular head fringed at the back of the
cheeks with long bony spikes pointing out to the sides. Built with nh_tri_tetrapod;
painted earthy brown with pale spikes. Faces -Y, pivot on the ground.

Output: Assets/Resources/Models/Species/Hypsognathus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


SPIKE = (0.80, 0.74, 0.58)


def sway(y):
    s = max(0.0, (y - 0.3) / 0.7)
    return 0.06 * s * s


AXIS = [
    (-1.00, 0.180, 0.030, 0.026),
    (-0.95, 0.190, 0.070, 0.044),
    (-0.86, 0.200, 0.120, 0.060),
    (-0.76, 0.205, 0.165, 0.068),
    (-0.68, 0.205, 0.170, 0.066),
    (-0.62, 0.200, 0.120, 0.064),
    (-0.52, 0.205, 0.170, 0.090),
    (-0.34, 0.210, 0.215, 0.105),
    (-0.10, 0.210, 0.210, 0.102),
    (0.10, 0.200, 0.160, 0.088),
    (0.26, 0.180, 0.080, 0.056),
    (0.42, 0.150, 0.040, 0.034, sway(0.42)),
    (0.58, 0.120, 0.018, 0.016, sway(0.58)),
    (0.70, 0.100, 0.003, 0.003, sway(0.70)),
]

FORE = tt.Limb(pts=[(0.15, -0.44, 0.18), (0.27, -0.44, 0.15), (0.29, -0.47, 0.04), (0.29, -0.49, 0.012)],
               radii=[0.045, 0.036, 0.028, 0.024], toes=5, toe_len=0.045, toe_r=0.011, toe_spread=70,
               toe_yaw=20, stride=10, claw_len=0.02)
HIND = tt.Limb(pts=[(0.14, 0.08, 0.18), (0.27, 0.06, 0.15), (0.29, 0.11, 0.04), (0.29, 0.09, 0.012)],
               radii=[0.050, 0.040, 0.030, 0.025], toes=5, toe_len=0.05, toe_r=0.012, toe_spread=70,
               toe_yaw=25, stride=-10, claw_len=0.022)


def spikes(mb, surf, spec):
    for sx in (1, -1):
        for k, (y, z, ln, up) in enumerate(((-0.80, 0.21, 0.13, 0.15), (-0.73, 0.215, 0.17, 0.10),
                                              (-0.67, 0.21, 0.12, 0.05))):
            base = tt.Vector((sx * 0.14, y, z))
            mb.add(tt.curved_spike(base, (sx * 1.0, 0.25 + 0.15 * k, up), ln, 0.022, bend=(0, 0.4, 0)), SPIKE)


SPEC = tt.TetrapodSpec(
    name="Hypsognathus",
    axis=AXIS,
    limbs=[FORE, HIND],
    voxel=0.010, max_tris=9000,
    mouth=(-0.995, -0.74, 0.176, 0.188, 0.005),
    eyes=(-0.83, 0.252, 0.020, (0.80, 0.55, 0.15), 0.09),
    nostrils=(-0.97, 0.20),
    back=(0.34, 0.25, 0.17), flank=(0.56, 0.44, 0.30), belly=(0.84, 0.76, 0.60),
    pattern=("spots", (0.20, 0.14, 0.09), 14.0, 0.5),
    post=spikes,
)

if __name__ == "__main__":
    tt.run(SPEC)
