"""
Procedural Terrestrisuchus gracilis (Late Triassic early crocodylomorph, ~1 m) for map
colonies.

A tiny, greyhound-like relative of crocodiles from the limestone fissures of south Wales,
about 205 million years ago. Very unlike a modern crocodile: a light, slender body
carried high on long, thin, upright legs (the hind legs much longer than the front
ones), a small, narrow, pointed head with sharp teeth, two neat rows of small scutes
down the back and a very long, whip-like tail. A fast-running hunter of insects and
small lizards. Built with the shared Triassic tetrapod recipe (nh_tri_tetrapod.py).
Painted sandy brown with a dark side stripe and a cream belly (speculative). Faces -Y,
pivot on the ground.

Usage:
  blender --background --python tools/blender/terrestrisuchus_gracilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Terrestrisuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_tri_tetrapod as tt  # noqa: E402


def sway(y):
    s = max(0.0, (y - 0.0) / 1.0)
    return 0.10 * s * s


AXIS = [
    (-1.00, 0.400, 0.005, 0.006),
    (-0.97, 0.404, 0.011, 0.014),
    (-0.91, 0.412, 0.018, 0.023),
    (-0.85, 0.420, 0.026, 0.030),
    (-0.80, 0.424, 0.031, 0.032),
    (-0.76, 0.418, 0.023, 0.025),
    (-0.70, 0.405, 0.023, 0.025),
    (-0.62, 0.398, 0.034, 0.039),
    (-0.50, 0.402, 0.046, 0.051),
    (-0.36, 0.408, 0.051, 0.055),
    (-0.24, 0.414, 0.046, 0.051),
    (-0.14, 0.414, 0.034, 0.037),
    (0.05, 0.395, 0.021, 0.022, sway(0.05)),
    (0.30, 0.360, 0.014, 0.014, sway(0.30)),
    (0.60, 0.315, 0.008, 0.008, sway(0.60)),
    (0.85, 0.280, 0.005, 0.005, sway(0.85)),
    (1.00, 0.262, 0.002, 0.002, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.035, -0.56, 0.38), (0.050, -0.55, 0.24), (0.048, -0.58, 0.07), (0.048, -0.59, 0.010)],
               radii=[0.018, 0.012, 0.009, 0.008], toes=4, toe_len=0.022, toe_r=0.005, toe_spread=40,
               stride=14, claw_len=0.010)
HIND = tt.Limb(pts=[(0.038, -0.24, 0.40), (0.056, -0.32, 0.24), (0.054, -0.22, 0.08), (0.054, -0.25, 0.010)],
               radii=[0.024, 0.015, 0.010, 0.008], toes=4, toe_len=0.035, toe_r=0.006, toe_spread=36,
               stride=-16, claw_len=0.011)

SPEC = tt.TetrapodSpec(
    name="Terrestrisuchus",
    axis=AXIS,
    blobs=[((0.034, -0.25, 0.38), (0.026, 0.05, 0.045), 25)],
    limbs=[FORE, HIND],
    voxel=0.0065, max_tris=6000,
    scale_bump=0.0009,
    mouth=(-1.0, -0.79, 0.398, 0.408, 0.003),
    teeth=(10, 0.009, 0.0026, -0.985, -0.80),
    eyes=(-0.80, 0.436, 0.0085, (0.90, 0.68, 0.15)),
    plates=[dict(xs=(0.009, -0.009), y0=-0.66, y1=0.35, step=0.04, size=0.012, wide=1.1, taper=0.7, shrink=0.3,
                 follow=sway, col=(0.30, 0.22, 0.14), keel_col=(0.48, 0.38, 0.26), height=1.0)],
    back=(0.40, 0.30, 0.20), flank=(0.66, 0.54, 0.38), belly=(0.90, 0.84, 0.70),
    pattern=("stripe", (0.24, 0.17, 0.11), 0.25, 0.25, 0.75, -0.8, 0.6),
)

if __name__ == "__main__":
    tt.run(SPEC)
