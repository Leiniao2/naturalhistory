"""
Procedural Herrerasaurus ischigualastensis (Late Triassic herrerasaurid, ~4.5 m) for map
colonies.

One of the earliest large predatory dinosaurs, from the ~231-million-year-old Ischigualasto
Formation of Argentina, caught mid-stride: a long, deep, narrow skull with a slightly open
mouth of big recurved teeth, a fairly short neck, a deep chest, a long tail held straight
out, strong grasping arms about half the length of the legs, and long, powerful hind legs
on three main toes. Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py).
Painted rusty brown with dark blotches, an ochre flank and a cream belly (speculative).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/herrerasaurus_ischigualastensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Herrerasaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.15) / 0.85)
    return -0.09 * s * s


AXIS = [
    (-1.00, 0.640, 0.006, 0.010),
    (-0.965, 0.646, 0.020, 0.032),
    (-0.89, 0.656, 0.030, 0.050),
    (-0.81, 0.668, 0.039, 0.060),
    (-0.735, 0.674, 0.047, 0.064),
    (-0.685, 0.660, 0.040, 0.054),
    (-0.61, 0.615, 0.044, 0.054),
    (-0.51, 0.565, 0.058, 0.068),
    (-0.40, 0.540, 0.082, 0.098),
    (-0.26, 0.530, 0.104, 0.125),
    (-0.10, 0.535, 0.104, 0.115),
    (0.05, 0.550, 0.090, 0.096),
    (0.20, 0.545, 0.062, 0.066),
    (0.40, 0.520, 0.040, 0.043, sway(0.40)),
    (0.60, 0.485, 0.026, 0.028, sway(0.60)),
    (0.80, 0.445, 0.014, 0.015, sway(0.80)),
    (1.00, 0.405, 0.003, 0.003, sway(1.00)),
]

LEGS = tt.Limb(pts=[(0.075, 0.02, 0.535), (0.096, -0.085, 0.35), (0.092, 0.06, 0.15), (0.092, -0.01, 0.018)],
               radii=[0.064, 0.042, 0.025, 0.018], toes=3, toe_len=0.075, toe_r=0.014, toe_spread=44,
               stride=-12, claw_len=0.026)
ARMS = tt.Limb(pts=[(0.065, -0.40, 0.50), (0.088, -0.36, 0.435), (0.078, -0.43, 0.41), (0.072, -0.455, 0.40)],
               radii=[0.030, 0.022, 0.016, 0.013], toes=3, toe_len=0.04, toe_r=0.008, toe_spread=30,
               toe_drop=0.025, claw_len=0.022, stride=8)

SPEC = tt.TetrapodSpec(
    name="Herrerasaurus",
    axis=AXIS,
    blobs=[((0.07, 0.03, 0.47), (0.064, 0.12, 0.11), 25),
           ((0.0, -0.84, 0.612), (0.030, 0.12, 0.022), 4)],
    limbs=[LEGS, ARMS],
    voxel=0.009, max_tris=12000,
    mouth=(-1.0, -0.74, 0.632, 0.642, 0.006),
    teeth=(11, 0.022, 0.0055, -0.99, -0.76), lower_teeth=True,
    eyes=(-0.745, 0.690, 0.014, (0.90, 0.55, 0.10)),
    nostrils=(-0.975, 0.66),
    back=(0.36, 0.20, 0.12), flank=(0.66, 0.45, 0.25), belly=(0.88, 0.80, 0.64),
    pattern=("spots", (0.20, 0.11, 0.07), 9.0, 0.7),
    head=((0.30, 0.16, 0.10), -0.70, 0.35),
)

if __name__ == "__main__":
    tt.run(SPEC)
