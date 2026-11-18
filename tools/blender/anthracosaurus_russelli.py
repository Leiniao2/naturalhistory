"""
Procedural Anthracosaurus russelli (Late Carboniferous coal swamps of Scotland and England, a
large embolomere about 3 m long) for map colonies (Swim style): a big, deep, broad skull armed
with huge fangs, a long eel-like trunk on small legs and a tall, flattened swimming tail;
dark olive-brown with blackish blotches and a pale belly. Pivot at the body centre.
Built with nh_car_tetrapod. Faces -Y.

Usage:
  blender --background --python tools/blender/anthracosaurus_russelli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Anthracosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Anthracosaurus",
    head_len=0.26, head_w=0.08, head_h=0.06, snout=0.48,
    neck_len=0.03, neck_r=0.06,
    trunk_len=0.55, trunk_r=0.06, trunk_h=1.0,
    tail_len=0.6, tail_r=0.034, tail_fin=2.4, tail_curve=0.08,
    leg_r=0.012, front=(0.035, 0.03), hind=(0.05, 0.04), foot=0.03, swim=True,
    back=(0.30, 0.31, 0.19), flank=(0.48, 0.46, 0.30), belly=(0.72, 0.66, 0.48),
    pattern="blotches", pattern_col=(0.14, 0.14, 0.08),
    head_col=(0.34, 0.32, 0.20), iris=(0.85, 0.60, 0.12), eye_r=0.016, eye_at=0.5, eye_up=0.6,
    teeth=9, tooth_len=0.022,
    lateral_line=True, voxel=0.007, max_tris=6500,
)

if __name__ == "__main__":
    tp.run(SPEC)
