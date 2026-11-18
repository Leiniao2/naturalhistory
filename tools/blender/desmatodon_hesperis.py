"""
Procedural Desmatodon hesperis (Late Carboniferous of Colorado, one of the oldest plant-eating
land vertebrates, a diadectid about 1.5 m long) for map colonies (Ground style): a short, deep,
blunt-snouted head, a massive barrel-shaped trunk carried on short, stout, sprawling limbs and a
short, thick tail; reddish-brown above with darker bands and a pale belly. Pivot on the ground.
Built with nh_car_tetrapod. Faces -Y.

Usage:
  blender --background --python tools/blender/desmatodon_hesperis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Desmatodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Desmatodon",
    head_len=0.15, head_w=0.065, head_h=0.055, snout=0.62,
    neck_len=0.04, neck_r=0.07,
    trunk_len=0.48, trunk_r=0.13, trunk_h=0.85,
    tail_len=0.42, tail_r=0.065, tail_curve=0.08,
    leg_r=0.03, front=(0.08, 0.09), hind=(0.09, 0.095), foot=0.05,
    back=(0.36, 0.24, 0.16), flank=(0.52, 0.38, 0.26), belly=(0.82, 0.72, 0.56),
    pattern="bands", pattern_col=(0.22, 0.14, 0.09), pattern_scale=1.5,
    head_col=(0.40, 0.28, 0.18), iris=(0.70, 0.45, 0.15), eye_r=0.012, eye_at=0.55, eye_up=0.6,
    teeth=0,
    voxel=0.007, max_tris=6500,
)

if __name__ == "__main__":
    tp.run(SPEC)
