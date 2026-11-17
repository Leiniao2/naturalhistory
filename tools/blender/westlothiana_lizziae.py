"""
Procedural Westlothiana lizziae (Early Carboniferous of East Kirkton, Scotland, a small long-bodied reptile-like tetrapod, about 20 cm long) for map colonies (Ground style).

A slender, elongated animal with a small head, a long trunk slung low between short,
widely spaced little legs and a long tail; dark olive-brown with pale speckles.
Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/westlothiana_lizziae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Westlothiana.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Westlothiana",
    head_len=0.09, head_w=0.026, head_h=0.017, snout=0.4,
    neck_len=0.035, neck_r=0.02,
    trunk_len=0.55, trunk_r=0.03, trunk_h=0.8,
    tail_len=0.55, tail_r=0.019, tail_curve=0.2,
    leg_r=0.0085, front=(0.035, 0.034), hind=(0.04, 0.036), foot=0.024,
    back=(0.24, 0.22, 0.14), flank=(0.38, 0.34, 0.22), belly=(0.70, 0.64, 0.46),
    pattern="spots", pattern_col=(0.72, 0.66, 0.44), pattern_scale=0.8,
    eye_r=0.0075, eye_at=0.58, teeth=0,
    voxel=0.0042, max_tris=5000,
)

if __name__ == "__main__":
    tp.run(SPEC)
