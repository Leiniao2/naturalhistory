"""
Procedural Cyamodus hildegardis (Middle Triassic armoured placodont, ~1.3 m) for map
colonies (Swim style).

A turtle-like shell-crusher from the Muschelkalk sea of Switzerland and northern Italy,
about 240 million years ago. Its broad, flattened trunk was roofed by a heart-shaped
carapace of fused polygonal bony plates studded with knobs, and a second, smaller
shield covered the hips and base of the tail. The broad, triangular skull held a few
huge, flat crushing tooth plates for cracking clams and brachiopods. Built with the
shared Triassic tetrapod recipe (nh_tri_tetrapod.py) plus two crisp dome shells (like
henodus_chelyops.py) and rows of knobs. Painted olive-brown with pale plate seams
(speculative). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/cyamodus_hildegardis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cyamodus.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.36, 0.30, 0.18)
SHELL_DARK = (0.20, 0.17, 0.10)
SEAM = (0.70, 0.62, 0.44)
KNOB = (0.50, 0.42, 0.28)
SC = Vector((0.0, -0.22, 0.02))       # main carapace
RX, RY = 0.40, 0.40
PC = Vector((0.0, 0.30, 0.00))        # pelvic shield
PRX, PRY = 0.17, 0.12

AXIS = [
    (-1.00, 0.000, 0.040, 0.020),
    (-0.96, 0.002, 0.070, 0.030),
    (-0.88, 0.006, 0.105, 0.038),
    (-0.80, 0.008, 0.128, 0.042),
    (-0.74, 0.008, 0.120, 0.044),
    (-0.68, 0.006, 0.090, 0.046),
    (-0.58, 0.008, 0.140, 0.056),
    (-0.22, 0.010, 0.300, 0.070),
    (0.12, 0.008, 0.170, 0.056),
    (0.32, 0.004, 0.090, 0.044),
    (0.55, 0.000, 0.040, 0.030),
    (0.78, -0.004, 0.018, 0.016),
    (0.95, -0.006, 0.003, 0.003),
]

FORE = tt.Limb(pts=[(0.24, -0.46, -0.02), (0.36, -0.49, -0.035), (0.42, -0.50, -0.04)],
               radii=[0.036, 0.029, 0.024], paddle=(0.075, 0.042, 115, 0))
HIND = tt.Limb(pts=[(0.14, 0.16, -0.02), (0.26, 0.21, -0.035), (0.31, 0.24, -0.04)],
               radii=[0.036, 0.029, 0.024], paddle=(0.070, 0.040, 140, 0))

rng = random.Random(11)
CENTRES = [(rng.uniform(-RX, RX), rng.uniform(SC.y - RY, SC.y + RY)) for _ in range(90)]
CENTRES += [(rng.uniform(-PRX, PRX), rng.uniform(PC.y - PRY, PC.y + PRY)) for _ in range(16)]


def shell_col(co, n):
    c = nh.lerp(SHELL, SHELL_DARK, nh.smoothstep(-0.2, 0.6, noise.noise(co * 5.0)))
    if n.z < -0.2:
        c = nh.lerp(c, (0.76, 0.70, 0.54), 0.6)
    return nh.lerp(c, SEAM, 0.65 * tt.voronoi_edge(co, CENTRES, 0.018))


def heart(x, y):
    """Extra height: a low median keel."""
    return 0.010 * max(0.0, 1.0 - abs(x) / 0.08)


def shells(mb, surf, spec):
    mb.add(tt.dome(SC, RX, RY, 0.090, 0.040, power=2.6, segments=96, rings=40, ridge=heart), shell_col)
    mb.add(tt.dome(PC, PRX, PRY, 0.060, 0.030, power=2.4, segments=48, rings=20), shell_col)
    # knobs on the plate centres (top only)
    for cx, cy in CENTRES[::2]:
        if (cx / RX) ** 2 + ((cy - SC.y) / RY) ** 2 < 0.8:
            z0 = SC.z + 0.090 * math.sqrt(max(0.0, 1.0 - abs(cx / RX) ** 2.6 - abs((cy - SC.y) / RY) ** 2.6))
            mb.add(nh.ellipsoid((cx, cy, z0 + heart(cx, cy) - 0.002), (0.014, 0.014, 0.010), subdivisions=2), KNOB)


SPEC = tt.TetrapodSpec(
    name="Cyamodus",
    axis=AXIS, power=2.8,
    limbs=[FORE, HIND],
    voxel=0.010, max_tris=8000,
    pivot="centre",
    mouth=(-1.0, -0.80, -0.006, 0.000, 0.004), mouth_min_x=0.0,
    eyes=(-0.80, 0.040, 0.015, (0.75, 0.58, 0.20), 0.08),
    back=(0.32, 0.28, 0.20), flank=(0.48, 0.44, 0.34), belly=(0.80, 0.76, 0.62),
    pattern=("spots", (0.22, 0.19, 0.13), 20.0, 0.5),
    post=shells,
)

if __name__ == "__main__":
    tt.run(SPEC)
