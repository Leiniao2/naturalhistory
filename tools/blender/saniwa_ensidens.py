"""
Procedural Saniwa ensidens (Eocene, ~50-46 Ma, North America and the Messel lake of Germany)
for map colonies. Built with nh_car_tetrapod.py.

An early monitor lizard (Varanidae) about 1.3 m long, much like a living monitor: a long,
narrow head with the nostrils set back, a long neck, a slim body on sprawling clawed legs
and a long, whip-like tail. Colour (unknown): olive-brown with pale cross-bands, cream belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/saniwa_ensidens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SaniwaEnsidens.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="SaniwaEnsidens",
    head_len=0.14, head_w=0.028, head_h=0.025, snout=0.38,
    neck_len=0.14, neck_r=0.026,
    trunk_len=0.36, trunk_r=0.058, trunk_h=0.8,
    tail_len=0.75, tail_r=0.036, tail_curve=0.18,
    leg_r=0.016, front=(0.07, 0.068), hind=(0.08, 0.075), foot=0.045,
    back=(0.26, 0.27, 0.16), flank=(0.38, 0.38, 0.24), belly=(0.80, 0.76, 0.58),
    pattern="bands", pattern_col=(0.72, 0.68, 0.48), pattern_scale=1.1,
    head_col=(0.30, 0.30, 0.19), iris=(0.70, 0.52, 0.18), eye_r=0.008, eye_at=0.62, eye_up=0.45,
    teeth=0, voxel=0.005, max_tris=6500,
)

if __name__ == "__main__":
    tp.run(SPEC)
