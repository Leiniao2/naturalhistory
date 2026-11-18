"""
Procedural Megalocephalus pachycephalus (Late Carboniferous of England, a baphetid early tetrapod
about 1.5-2 m long) for map colonies (Ground style): an enormous, broad, flat, crocodile-like
skull with big fangs, a heavy low trunk on short sprawling legs and a moderately long tail;
grey-brown with dark spots and a yellowish belly. Pivot on the ground.
Built with nh_car_tetrapod. Faces -Y.

Usage:
  blender --background --python tools/blender/megalocephalus_pachycephalus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Megalocephalus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Megalocephalus",
    head_len=0.30, head_w=0.11, head_h=0.045, snout=0.45,
    neck_len=0.03, neck_r=0.07,
    trunk_len=0.45, trunk_r=0.075, trunk_h=0.7,
    tail_len=0.45, tail_r=0.04, tail_fin=1.4, tail_curve=0.12,
    leg_r=0.018, front=(0.06, 0.055), hind=(0.07, 0.06), foot=0.045,
    back=(0.30, 0.29, 0.24), flank=(0.44, 0.42, 0.34), belly=(0.80, 0.74, 0.50),
    pattern="spots", pattern_col=(0.12, 0.11, 0.09), pattern_scale=1.4,
    head_col=(0.34, 0.32, 0.26), iris=(0.80, 0.70, 0.20), eye_r=0.016, eye_at=0.55, eye_up=0.75,
    teeth=10, tooth_len=0.018,
    voxel=0.0065, max_tris=6500,
)

if __name__ == "__main__":
    tp.run(SPEC)
