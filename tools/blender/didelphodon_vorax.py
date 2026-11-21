"""
Procedural Didelphodon vorax (Late Cretaceous stagodontid metatherian, Hell Creek / Lance,
North America).

A badger-sized relative of the marsupials: a short, very broad and deep skull with bulging
jaw muscles, a blunt muzzle and big crushing canines, a long low body, short sturdy legs
with five-toed feet, and a thick, tapering otter-like tail for a life along streams. Dense
dark-brown fur with a grizzled back, a paler face mask and throat (colours conjectural).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/didelphodon_vorax.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Didelphodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

FUR = (0.20, 0.14, 0.10)
FUR_LIGHT = (0.40, 0.31, 0.22)
CHEST = (0.70, 0.62, 0.50)
FACE = (0.60, 0.52, 0.42)
NOSE = (0.07, 0.05, 0.05)


def make():
    s = dn.DinoSpec(
        name="Didelphodon",
        paint=dn.make_paint(FUR, FUR_LIGHT, CHEST, mottle=0.25, head=FACE, head_y=None),
        hip_y=0.28, hip_z=0.20, body_len=0.62, torso_w=0.13, torso_h=0.12, belly=0.0, chest_dz=-0.01,
        tail_len=0.70, tail_r=0.55, tail_droop=-0.10, tail_flat=1.1,
        neck_len=0.06, neck_rise=0.03, neck_r=0.09, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.11, 0.09), (-0.07, -0.005, 0.11, 0.085), (-0.15, -0.02, 0.07, 0.06),
                   (-0.21, -0.035, 0.045, 0.04), (-0.235, -0.04, 0.0, 0.0)],
        head_len=0.235, head_h=0.09, head_w=0.11,
        jaw=True, jaw_open=10, jaw_h=0.35,
        leg_type="column", leg_r=0.05, leg_x=0.04, toes=5, toe_len=0.035, toe_r=0.010, claw=0.014, stride=0.05,
        fore="leg", fore_type="bent", arm_r=0.045, fore_toes=5, shoulder_dy=0.07,
        eye_r=0.012, eye_pos=(-0.12, 0.03, 0.75), eye_col=(0.05, 0.04, 0.03),
        fuzz=0.008, scales=0.0, voxel=0.009, max_tris=11000,
    )
    hb = s.head_base
    s.paint = dn.make_paint(FUR, FUR_LIGHT, CHEST, mottle=0.25, head=FACE, head_y=hb.y - 0.12)

    def crisp(mb, s):
        for sx in (1, -1):
            mb.add(nh.ellipsoid((sx * 0.075, hb.y + 0.02, hb.z + 0.075), (0.022, 0.01, 0.026), subdivisions=2), FUR)
            # big blunt canines
            p = Vector((sx * 0.028, hb.y - 0.20, hb.z - 0.05))
            mb.add(cc.curved_cone(p, p + Vector((0, -0.004, -0.02)), p + Vector((0, 0.0, -0.035)), 0.008), cc.TOOTH)
        mb.add(nh.ellipsoid((0, hb.y - 0.232, hb.z - 0.035), (0.022, 0.012, 0.016), subdivisions=2), NOSE)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Didelphodon")
