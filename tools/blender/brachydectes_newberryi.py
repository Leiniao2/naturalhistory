"""
Procedural Brachydectes newberryi (Late Carboniferous coal swamps of North America, a
lysorophian lepospondyl about 30 cm long) for map colonies (Ground style, slithering): a small,
blunt, wedge-shaped burrowing head, a long eel-like body with tiny vestigial limbs and a short
tail; grey-brown above with a pinkish-cream belly. Pivot on the ground.
Built with nh_car_tetrapod, bent into an S-wave by nh_car_serpent. Faces -Y.

Usage:
  blender --background --python tools/blender/brachydectes_newberryi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Brachydectes.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_car_serpent as sn  # noqa: E402

SPEC = tp.Spec(
    name="Brachydectes",
    head_len=0.07, head_w=0.024, head_h=0.017, snout=0.55,
    neck_len=0.02, neck_r=0.02,
    trunk_len=0.85, trunk_r=0.022, trunk_h=0.95,
    tail_len=0.18, tail_r=0.017, tail_curve=0.1,
    leg_r=0.004, front=(0.012, 0.01), hind=(0.014, 0.012), foot=0.008, toes=3, body_z=0.022,
    back=(0.40, 0.32, 0.30), flank=(0.62, 0.48, 0.44), belly=(0.90, 0.74, 0.68),
    pattern="spots", pattern_col=(0.20, 0.17, 0.14), pattern_scale=0.7,
    head_col=(0.36, 0.30, 0.25), iris=(0.40, 0.30, 0.20), eye_r=0.005, eye_at=0.45, teeth=0,
    voxel=0.004, max_tris=5000,
)

if __name__ == "__main__":
    sn.run(SPEC, amp=0.045, wavelength=0.6)
