"""
Procedural Hyperodapedon gordoni (Late Triassic rhynchosaur, ~1.3 m) for map colonies.

A stocky, barrel-bodied plant-eating archosauromorph from the Lossiemouth Sandstone of
Scotland (about 230 million years ago); its relatives are so common in Late Triassic
rocks of India, Brazil and Argentina that they make up most fossils in some beds. Its
skull is very broad at the back and narrows to a hooked, beak-like pair of tusk-like
premaxillae; the jaws held rows of teeth that sheared tough plants like secateurs. Short,
sprawling legs with clawed feet (the hind feet used for scratch-digging) and a short,
thick tail. Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py). Painted
grey-brown with pale yellowish spots and a cream belly (speculative). Faces -Y, pivot on
the ground.

Usage:
  blender --background --python tools/blender/hyperodapedon_gordoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hyperodapedon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402

BEAK = (0.30, 0.26, 0.20)


def sway(y):
    s = max(0.0, (y - 0.15) / 0.8)
    return 0.07 * s * s


AXIS = [
    (-1.00, 0.230, 0.012, 0.020),
    (-0.97, 0.250, 0.032, 0.045),
    (-0.90, 0.270, 0.062, 0.064),
    (-0.82, 0.282, 0.098, 0.074),
    (-0.75, 0.287, 0.122, 0.074),
    (-0.70, 0.278, 0.094, 0.070),
    (-0.62, 0.285, 0.112, 0.090),
    (-0.50, 0.295, 0.172, 0.135),
    (-0.32, 0.305, 0.215, 0.165),
    (-0.12, 0.305, 0.215, 0.160),
    (0.05, 0.295, 0.170, 0.125),
    (0.18, 0.275, 0.100, 0.080),
    (0.35, 0.245, 0.064, 0.054, sway(0.35)),
    (0.55, 0.205, 0.040, 0.034, sway(0.55)),
    (0.75, 0.165, 0.022, 0.018, sway(0.75)),
    (0.92, 0.135, 0.004, 0.004, sway(0.92)),
]

FORE = tt.Limb(pts=[(0.15, -0.45, 0.22), (0.265, -0.43, 0.17), (0.28, -0.47, 0.045), (0.28, -0.49, 0.014)],
               radii=[0.050, 0.040, 0.030, 0.026], toes=5, toe_len=0.04, toe_r=0.011, toe_spread=70,
               toe_yaw=20, stride=12, claw_len=0.02)
HIND = tt.Limb(pts=[(0.13, 0.03, 0.24), (0.26, 0.0, 0.18), (0.27, 0.06, 0.045), (0.27, 0.035, 0.014)],
               radii=[0.060, 0.046, 0.033, 0.027], toes=5, toe_len=0.05, toe_r=0.012, toe_spread=70,
               toe_yaw=25, stride=-12, claw_len=0.026)


def beak(mb, surf, spec):
    # the hooked premaxillary 'beak' curving down at the snout tip
    for sx in (1, -1):
        base = tt.Vector((sx * 0.012, -0.985, 0.235))
        mb.add(tt.curved_spike(base, (0, -0.4, -1.0), 0.055, 0.013, bend=(0, 0.5, 0)), BEAK)


def paint_extra(co, n, c, spec):
    return nh.lerp(c, BEAK, nh.smoothstep(-0.95, -0.99, co.y))


SPEC = tt.TetrapodSpec(
    name="Hyperodapedon",
    axis=AXIS,
    blobs=[((0.07, -0.78, 0.25), (0.06, 0.07, 0.05))],
    limbs=[FORE, HIND],
    voxel=0.0095, max_tris=10000,
    mouth=(-0.97, -0.76, 0.225, 0.250, 0.005),
    eyes=(-0.80, 0.322, 0.016, (0.75, 0.55, 0.15)),
    back=(0.32, 0.28, 0.24), flank=(0.52, 0.44, 0.36), belly=(0.84, 0.78, 0.62),
    pattern=("spots", (0.86, 0.78, 0.48), 20.0, 0.6),
    paint_extra=paint_extra,
    post=beak,
)

if __name__ == "__main__":
    tt.run(SPEC)
