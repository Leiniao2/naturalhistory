"""
Procedural Macrauchenia patachonica (Late Pleistocene of South America) for map
colonies: a litoptern, one of South America's native hoofed mammals.

Camel-like in build, with long legs ending in three-toed feet, a long neck and
a small head whose nostrils sat high between the eyes - usually reconstructed
with a short trunk or tapir-like proboscis hanging over the mouth. Short tail.
Sandy brown coat with a paler belly. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/macrauchenia_patachonica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MacraucheniaPatachonica.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="MacraucheniaPatachonica",
    leg_f=0.92, leg_h=0.92, length=0.85, girth=(0.20, 0.25),
    leg_r=(0.060, 0.070), leg_taper=0.55, foot="hoof", foot_r=1.2, stride=0.14,
    neck_len=0.70, neck_angle=55, neck_r=(0.14, 0.085),
    head_len=0.36, head_r=(0.08, 0.085), snout_r=(0.05, 0.05), head_pitch=40,
    ears="point", ear_size=0.07,
    trunk_len=0.18, trunk_r=0.04, trunk_curl=0.2,
    tail_len=0.25, tail_r=0.025, tail_tuft=0.03, tail_droop=0.9,
    coat=(0.62, 0.48, 0.33), dark=(0.42, 0.31, 0.20), pale=(0.85, 0.77, 0.63),
    shag=0.005, voxel=0.017,
)

if __name__ == "__main__":
    q.main(SPEC)
