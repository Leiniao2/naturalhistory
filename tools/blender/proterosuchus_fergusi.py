"""
Procedural Proterosuchus fergusi (Early Triassic archosauriform, ~1.6 m) for map colonies.

One of the first archosauriforms, from the Karoo of South Africa just after the end-Permian
extinction: a low, crocodile-like predator with sprawling legs, a long tail and a long
skull whose upper jaw tip hooks down over the lower jaw. Built with nh_tri_tetrapod;
painted grey-brown with darker bands. Faces -Y, pivot on the ground.

Output: Assets/Resources/Models/Species/Proterosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.0) / 1.0)
    return 0.10 * s * s


AXIS = [
    (-1.00, 0.170, 0.012, 0.018),
    (-0.97, 0.168, 0.020, 0.024),
    (-0.90, 0.175, 0.026, 0.026),
    (-0.80, 0.185, 0.036, 0.034),
    (-0.72, 0.195, 0.048, 0.042),
    (-0.66, 0.198, 0.050, 0.042),
    (-0.60, 0.195, 0.045, 0.040),
    (-0.50, 0.190, 0.058, 0.052),
    (-0.36, 0.188, 0.082, 0.066),
    (-0.20, 0.188, 0.090, 0.070),
    (-0.06, 0.185, 0.080, 0.064),
    (0.06, 0.178, 0.058, 0.050),
    (0.24, 0.160, 0.040, 0.040, sway(0.24)),
    (0.48, 0.130, 0.026, 0.028, sway(0.48)),
    (0.74, 0.100, 0.014, 0.016, sway(0.74)),
    (1.00, 0.075, 0.003, 0.003, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.07, -0.42, 0.17), (0.17, -0.42, 0.14), (0.19, -0.45, 0.035), (0.19, -0.47, 0.010)],
               radii=[0.028, 0.022, 0.017, 0.015], toes=5, toe_len=0.035, toe_r=0.007, toe_spread=70,
               toe_yaw=20, stride=14, claw_len=0.014)
HIND = tt.Limb(pts=[(0.065, 0.02, 0.17), (0.18, 0.00, 0.14), (0.20, 0.05, 0.035), (0.20, 0.03, 0.010)],
               radii=[0.036, 0.027, 0.019, 0.016], toes=5, toe_len=0.045, toe_r=0.008, toe_spread=65,
               toe_yaw=25, stride=-14, claw_len=0.016)


def hook(mb, surf, spec):
    # the down-turned premaxilla overhanging the lower jaw
    base = tt.Vector((0.0, -0.985, 0.172))
    mb.add(tt.curved_spike(base, (0, -0.35, -1.0), 0.035, 0.014, bend=(0, 0.5, 0)), spec.back)


SPEC = tt.TetrapodSpec(
    name="Proterosuchus",
    axis=AXIS,
    blobs=[((0.06, 0.03, 0.17), (0.045, 0.09, 0.05), 20)],
    limbs=[FORE, HIND],
    voxel=0.0075, max_tris=10000,
    mouth=(-0.99, -0.68, 0.158, 0.180, 0.004),
    teeth=(13, 0.012, 0.0035, -0.95, -0.70), lower_teeth=True,
    eyes=(-0.69, 0.222, 0.010, (0.80, 0.62, 0.20)),
    nostrils=(-0.94, 0.185),
    plates=[dict(xs=(0.0,), y0=-0.55, y1=0.35, step=0.03, size=0.010, kind="knob", height=0.7, taper=0.5,
                 follow=sway, col=(0.22, 0.20, 0.16))],
    back=(0.26, 0.25, 0.20), flank=(0.48, 0.45, 0.36), belly=(0.80, 0.76, 0.64),
    pattern=("bands", (0.17, 0.16, 0.13), 26.0, 0.8, -0.6, 1.0),
    post=hook,
)

if __name__ == "__main__":
    tt.run(SPEC)
