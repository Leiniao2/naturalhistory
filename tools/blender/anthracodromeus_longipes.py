"""
Procedural Anthracodromeus longipes (Late Carboniferous of Ohio, a small long-limbed early reptile
about 20 cm long, the oldest known climbing amniote) for map colonies (Ground style): a small
pointed head with big eyes, a slim body, long slender legs with long clawed toes and a very
long tail; bronze-brown with pale dorsolateral stripes. Pivot on the ground.
Built with nh_car_tetrapod. Faces -Y.

Usage:
  blender --background --python tools/blender/anthracodromeus_longipes.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Anthracodromeus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Anthracodromeus",
    head_len=0.09, head_w=0.024, head_h=0.017, snout=0.3,
    neck_len=0.05, neck_r=0.015,
    trunk_len=0.26, trunk_r=0.028, trunk_h=0.85,
    tail_len=0.70, tail_r=0.015, tail_curve=0.22,
    leg_r=0.008, front=(0.075, 0.08), hind=(0.09, 0.095), foot=0.055,
    back=(0.34, 0.24, 0.12), flank=(0.50, 0.38, 0.20), belly=(0.86, 0.78, 0.58),
    pattern="stripes", pattern_col=(0.82, 0.70, 0.42),
    head_col=(0.30, 0.22, 0.12), iris=(0.85, 0.55, 0.10), eye_r=0.009, eye_at=0.6, teeth=5, tooth_len=0.004,
    voxel=0.004, max_tris=5000,
)

if __name__ == "__main__":
    tp.run(SPEC)
