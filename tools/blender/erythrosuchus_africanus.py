"""
Procedural Erythrosuchus africanus (Early-Middle Triassic erythrosuchid, ~5 m) for map
colonies.

The largest land predator of its time in southern Africa, about 245 million years ago,
and one of the first big archosauriforms after the end-Permian extinction. A bulky,
heavy-limbed animal with an enormous head (its skull was about a metre long, a fifth of
its length), a thick neck, a deep trunk, legs held half-sprawled, and a comparatively
short tail; jaws lined with big curved teeth. Built with the shared Triassic tetrapod
recipe (nh_tri_tetrapod.py). Painted brick red ("red crocodile") with darker blotches,
a dark crown and a pale throat and belly (speculative). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/erythrosuchus_africanus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Erythrosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.25) / 0.75)
    return 0.07 * s * s


AXIS = [
    (-1.00, 0.330, 0.030, 0.036),
    (-0.965, 0.336, 0.058, 0.070),
    (-0.88, 0.352, 0.078, 0.098),
    (-0.78, 0.370, 0.094, 0.118),
    (-0.68, 0.388, 0.112, 0.132),
    (-0.60, 0.392, 0.122, 0.134),
    (-0.53, 0.385, 0.118, 0.122),
    (-0.45, 0.380, 0.132, 0.136),
    (-0.32, 0.385, 0.168, 0.162),
    (-0.14, 0.390, 0.176, 0.166),
    (0.03, 0.390, 0.160, 0.150),
    (0.16, 0.380, 0.118, 0.110),
    (0.30, 0.350, 0.074, 0.072, sway(0.30)),
    (0.48, 0.300, 0.046, 0.044, sway(0.48)),
    (0.66, 0.250, 0.024, 0.023, sway(0.66)),
    (0.82, 0.215, 0.004, 0.004, sway(0.82)),
]

FORE = tt.Limb(pts=[(0.13, -0.38, 0.32), (0.20, -0.37, 0.20), (0.205, -0.41, 0.06), (0.21, -0.43, 0.016)],
               radii=[0.074, 0.058, 0.044, 0.036], toes=5, toe_len=0.045, toe_r=0.014, toe_spread=70,
               toe_yaw=15, stride=10, claw_len=0.02)
HIND = tt.Limb(pts=[(0.13, 0.08, 0.33), (0.21, 0.02, 0.20), (0.205, 0.10, 0.06), (0.21, 0.07, 0.016)],
               radii=[0.088, 0.066, 0.048, 0.038], toes=5, toe_len=0.06, toe_r=0.015, toe_spread=60,
               toe_yaw=15, stride=-10, claw_len=0.022)

SPEC = tt.TetrapodSpec(
    name="Erythrosuchus",
    axis=AXIS,
    blobs=[((0.12, 0.08, 0.32), (0.09, 0.14, 0.12), 20),          # thigh
           ((0.08, -0.62, 0.38), (0.06, 0.09, 0.09)),              # jaw muscles
           ((0.0, -0.78, 0.30), (0.07, 0.20, 0.045), 3)],          # heavy lower jaw
    limbs=[FORE, HIND],
    voxel=0.0098, max_tris=12500,
    mouth=(-1.0, -0.60, 0.318, 0.340, 0.007),
    teeth=(11, 0.040, 0.0095, -0.985, -0.64), lower_teeth=True,
    eyes=(-0.66, 0.445, 0.016, (0.92, 0.70, 0.18)),
    nostrils=(-0.975, 0.355),
    plates=[dict(xs=(0.0,), y0=-0.50, y1=0.70, step=0.05, size=0.018, kind="knob", height=0.7, taper=0.6,
                 follow=sway, col=(0.30, 0.10, 0.07))],
    back=(0.42, 0.13, 0.08), flank=(0.66, 0.28, 0.16), belly=(0.88, 0.76, 0.60),
    pattern=("spots", (0.30, 0.09, 0.06), 9.0, 0.6),
    head=((0.30, 0.12, 0.08), -0.55, 0.25),
)

if __name__ == "__main__":
    tt.run(SPEC)
