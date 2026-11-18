"""
Procedural Majungasaurus crenatissimus (Late Cretaceous abelisaurid, Madagascar).

A stocky 7-metre theropod with a short, deep, blunt skull whose thick roof bears a single
rounded horn-knob and rough, bumpy skin, a thick muscular neck, absurdly tiny arms and short,
powerful legs. Dark red-brown with a grey-tan flank, rows of large feature scales and a
pale belly; the knob and face darker.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/majungasaurus_crenatissimus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Majungasaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.36, 0.16, 0.12)
FLANK = (0.56, 0.42, 0.32)
BELLY = (0.86, 0.78, 0.64)
FACE = (0.24, 0.12, 0.10)
KNOB = (0.62, 0.50, 0.40)


def make():
    s = dn.DinoSpec(
        name="Majungasaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=(0.22, 0.10, 0.08), freq=22.0, stripe_amt=0.45,
                            head=FACE, head_y=-0.58, y_range=(-0.58, 1.2)),
        hip_y=0.18, hip_z=0.52, body_len=0.50, torso_w=0.15, torso_h=0.18, belly=0.04,
        tail_len=0.85, tail_r=0.7, tail_droop=-0.03,
        neck_len=0.14, neck_rise=0.12, neck_r=0.09, neck_s=0.02,
        head_len=0.24, head_h=0.09, head_w=0.075, snout_h=0.72, snout_w=0.7, snout_drop=0.02,
        jaw=True, jaw_open=12, teeth=6, tooth_len=0.02,
        leg_r=0.085, knee_fwd=0.11, toes=3, toe_len=0.08, toe_r=0.024, claw=0.022, stride=0.05,
        arm_len=0.05, arm_r=0.016, fingers=2, finger_len=0.015, hand_claw=0.0,
        eye_r=0.013, eye_col=(0.90, 0.70, 0.15), scales=0.0025, voxel=0.01, max_tris=13000,
    )
    for k in range(10):
        y = s.hip_y - 0.02 - k * 0.05
        s.blobs.append(((s.torso_w * 0.9, y, s.hip_z + 0.05), (0.013, 0.013, 0.013), True))
    c, hw, hh = s.head_at(0.25)
    knob = Vector((0, c.y, c.z + hh * 0.95))

    def crisp(mb, s):
        mb.add(nh.ellipsoid(tuple(knob), (0.022, 0.03, 0.022), subdivisions=2), KNOB)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Majungasaurus")
