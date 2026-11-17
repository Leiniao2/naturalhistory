"""
Procedural Mamenchisaurus hochuanensis (Late Jurassic Sichuan, China) for map colonies.

A sauropod with one of the longest necks of any animal, about half its 22 m length,
built of 19 elongated vertebrae and held raised in a long, gentle curve. Deep body with
the shoulders about as high as the hips, a medium tail, a small head with spoon-shaped
teeth, and pillar legs. Rusty red-brown back with darker mottling, warm tan flanks and a
cream throat and belly. Built with nh_jur_quadruped. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/mamenchisaurus_hochuanensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mamenchisaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_quadruped as qd  # noqa: E402

SPEC = qd.Spec(
    name="Mamenchisaurus",
    paint=kit.paint(back=(0.40, 0.22, 0.14), flank=(0.66, 0.48, 0.32), belly=(0.90, 0.84, 0.70),
                    spots=(0.26, 0.14, 0.09), spot_scale=5.0, spot_amt=0.5, mottle_scale=7.0),
    hip_h=1.0, shoulder_h=1.0, body_len=1.2, body_hw=0.31, body_hh=0.36, belly_drop=0.06,
    tail_len=2.4, tail_droop=0.5, tail_r=0.7, tail_exp=1.3,
    neck=((0.0, -0.6, 0.3), (0.0, -1.3, 0.85), (0.0, -2.0, 1.3), (0.0, -2.7, 1.55)), neck_r=(0.2, 0.13, 0.095, 0.07),
    head_len=0.2, head_h=0.06, head_w=0.055, head_pitch=35, snout_taper=0.3,
    thigh_r=0.15, shin_r=0.1, foot_r=0.11, arm_r=0.13, forearm_r=0.09, hand_r=0.09,
    front_nails=1, hind_nails=3, voxel=0.02, max_tris=17000, stride=0.14,
)

if __name__ == "__main__":
    nh.run(lambda: qd.build(SPEC), "Mamenchisaurus", **qd.PREVIEW)
