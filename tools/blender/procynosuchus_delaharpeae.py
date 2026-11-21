"""
Procedural Procynosuchus delaharpeae (Late Permian cynodont, ~60 cm) for map colonies.

One of the earliest cynodonts, the group that led to mammals: a low, long-bodied animal
with a broad, fox-like head, long canines, a widened, flattened tail (perhaps used to
swim, otter-fashion) and sprawling legs with broad feet. Probably partly hair-covered:
warm brown with darker back and pale throat.
Built with nh_per_tetra. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/procynosuchus_delaharpeae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Procynosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_per_tetra as pt  # noqa: E402

SPEC = pt.Spec(
    name="Procynosuchus",
    torso=[
        (-0.42, 0.20, 0.07, 0.07),
        (-0.34, 0.20, 0.11, 0.10),
        (-0.18, 0.20, 0.13, 0.11),
        (0.02, 0.20, 0.13, 0.105),
        (0.18, 0.19, 0.11, 0.09),
        (0.28, 0.18, 0.08, 0.06),
        (0.45, 0.14, 0.065, 0.032),
        (0.65, 0.10, 0.045, 0.022),
        (0.80, 0.07, 0.02, 0.012),
        (0.85, 0.06, 0.0, 0.0),
    ],
    head=[
        (-0.40, 0.24, 0.085, 0.065),
        (-0.50, 0.24, 0.080, 0.063),
        (-0.60, 0.22, 0.055, 0.050),
        (-0.68, 0.20, 0.034, 0.036),
        (-0.70, 0.195, 0.0, 0.0),
    ],
    jaw=[
        (-0.42, 0.170, 0.065, 0.024),
        (-0.62, 0.162, 0.038, 0.018),
        (-0.695, 0.165, 0.0, 0.0),
    ],
    teeth=[(-0.69, -0.66, 2, 0.012, 0.004, True), (-0.61, -0.46, 7, 0.009, 0.003, True)],
    fangs=[(0.030, -0.635, 0.18, 0.045, 0.007, 0.0)],
    fore=pt.Limb(y=-0.25, z=0.15, x=0.11, upper=0.10, lower=0.11, sprawl=0.7, r=0.035,
                 foot=(0.035, 0.040, 0.012), toe_len=0.03, toe_r=0.008),
    hind=pt.Limb(y=0.14, z=0.15, x=0.10, upper=0.11, lower=0.11, sprawl=0.6, r=0.040,
                 foot=(0.040, 0.050, 0.012), toe_len=0.035, toe_r=0.009),
    eye=(0.06, -0.52, 0.27, 0.017), nostril=(0.016, -0.695, 0.215),
    back=(0.30, 0.20, 0.12), flank=(0.50, 0.35, 0.22), belly=(0.84, 0.74, 0.58), mark=(0.20, 0.13, 0.08),
    pattern="mottle", pattern_freq=12.0, pattern_amount=0.3, scale_bumps=0.4,
    voxel=0.006, max_tris=8000, drop=0.02,
)

if __name__ == "__main__":
    pt.main(SPEC)
