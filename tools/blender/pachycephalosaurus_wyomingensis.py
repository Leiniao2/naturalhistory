"""
Procedural Pachycephalosaurus wyomingensis (Late Cretaceous pachycephalosaur, western
North America).

A bipedal plant-eater about 4.5 metres long whose skull roof was a solid dome of bone up to
25 cm thick, ringed by bony knobs and short spikes at the back of the head and along the
snout. Short neck, small arms, deep body, stiffened tail. Sandy-brown with darker blotches
and a pale belly, the dome pale bone-grey.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pachycephalosaurus_wyomingensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pachycephalosaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.42, 0.33, 0.22)
FLANK = (0.60, 0.50, 0.35)
BELLY = (0.88, 0.82, 0.66)
BLOTCH = (0.25, 0.18, 0.11)
DOME = (0.80, 0.76, 0.66)
KNOB = (0.30, 0.25, 0.20)


def make():
    s = dn.DinoSpec(
        name="Pachycephalosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=BLOTCH, spot_scale=12.0),
        hip_y=0.15, hip_z=0.55, body_len=0.45, torso_w=0.13, torso_h=0.16, belly=0.04, chest_dz=-0.02,
        tail_len=0.85, tail_r=0.6, tail_droop=0.0,
        neck_len=0.14, neck_rise=0.12, neck_r=0.055, neck_s=0.02,
        head_len=0.18, head_h=0.06, head_w=0.055, snout_h=0.5, snout_w=0.45, snout_drop=0.03,
        leg_r=0.075, knee_fwd=0.11, toes=3, toe_len=0.07, toe_r=0.018, claw=0.015, stride=0.05,
        arm_len=0.16, arm_r=0.02, fingers=3, finger_len=0.03, hand_claw=0.012,
        eye_r=0.012, eye_pos=(-0.07, 0.01, 0.9), eye_col=(0.75, 0.5, 0.15), scales=0.002, voxel=0.01,
        max_tris=12000,
    )
    hb = s.head_base

    def crisp(mb, s):
        dome_c = Vector((0, hb.y - 0.035, hb.z + 0.045))
        mb.add(nh.ellipsoid(dome_c, (0.06, 0.075, 0.06), subdivisions=3), DOME)
        # knobs around the back of the dome and along the snout
        for k in range(9):
            a = math.pi * (0.1 + 0.8 * k / 8)
            p = Vector((math.cos(a) * 0.06, hb.y + 0.03 + math.sin(a) * 0.02, hb.z + 0.01 + 0.012 * math.sin(a)))
            mb.add(cc.cone(p, p + Vector((math.cos(a) * 0.02, 0.025, 0.0)), 0.009, sides=5), KNOB)
        for k in range(4):
            c, hw, hh = s.head_at(0.55 + 0.1 * k)
            for sx in (1, -1):
                p = Vector((sx * hw * 0.6, c.y, c.z + hh * 0.7))
                mb.add(cc.cone(p, p + Vector((sx * 0.006, 0, 0.012)), 0.006, sides=5), KNOB)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Pachycephalosaurus")
