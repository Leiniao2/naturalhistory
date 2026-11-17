"""
Procedural Psittacosaurus mongoliensis (Early Cretaceous early ceratopsian, Mongolia and China).

A dog-sized, two-legged plant-eater with a short, deep head ending in a parrot-like beak and
a pointed horn jutting sideways from each cheek. A specimen with preserved skin shows a row
of long bristle-like quills along the top of the tail and countershaded colours: dark brown
above, paler below, with darker blotches on the shoulders.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/psittacosaurus_mongoliensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Psittacosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.30, 0.22, 0.15)
FLANK = (0.52, 0.40, 0.28)
BELLY = (0.86, 0.78, 0.62)
BEAK = (0.22, 0.20, 0.18)
HORN = (0.55, 0.48, 0.38)
QUILL = (0.35, 0.27, 0.18)


def make():
    s = dn.DinoSpec(
        name="Psittacosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=(0.18, 0.13, 0.09), spot_scale=10.0),
        hip_y=0.15, hip_z=0.42, body_len=0.40, torso_w=0.10, torso_h=0.12, belly=0.03, chest_dz=0.02,
        tail_len=0.75, tail_r=0.6, tail_droop=0.0,
        neck_len=0.12, neck_rise=0.12, neck_r=0.045, neck_s=0.015,
        head_rows=[(0.0, 0.0, 0.055, 0.06), (-0.04, 0.0, 0.06, 0.065), (-0.09, -0.01, 0.045, 0.055),
                   (-0.13, -0.03, 0.025, 0.035), (-0.155, -0.05, 0.0, 0.0)],
        head_len=0.155, head_h=0.06, head_w=0.055,
        leg_r=0.055, knee_fwd=0.09, toes=3, toe_len=0.06, toe_r=0.014, claw=0.012, stride=0.04,
        arm_len=0.17, arm_r=0.018, fingers=3, finger_len=0.03, hand_claw=0.01,
        eye_r=0.014, eye_pos=(-0.05, 0.02, 0.85), eye_col=(0.6, 0.4, 0.15), scales=0.002, voxel=0.008,
        max_tris=10000,
    )
    hb = s.head_base

    def crisp(mb, s):
        mb.add(nh.ellipsoid((0, hb.y - 0.14, hb.z - 0.04), (0.022, 0.028, 0.03), subdivisions=2), BEAK)
        for sx in (1, -1):
            p = Vector((sx * 0.062, hb.y - 0.045, hb.z - 0.035))
            mb.add(cc.cone(p, p + Vector((sx * 0.05, -0.01, -0.01)), 0.014, sides=6), HORN)
        # bristles along the top of the tail
        for k in range(14):
            u = 0.08 + 0.45 * k / 13
            c, r = dn.tail_point(s, u)
            base = c + Vector((0, 0, r * 0.8))
            ln = 0.09 * (1 - abs(k - 6) / 10)
            mb.add(cc.cone(base, base + Vector((0, 0.03, ln)), 0.004, sides=4), QUILL)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Psittacosaurus")
