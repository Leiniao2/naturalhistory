"""
Procedural Repenomamus giganticus (Early Cretaceous gobiconodontid mammal, Yixian Formation,
China).

A badger-sized mammal about 1 metre long and 12-14 kg, among the largest mammals of the age
of dinosaurs. A sister species was found with a baby Psittacosaurus in its stomach, and a
fossil locks a Repenomamus in a fight with an adult one, so it preyed on small dinosaurs.
Stocky sprawling-to-upright body on short strong legs, a broad head with stout jaws and
small ears, and a fairly long tail. Grizzled dark brown fur with a pale chest.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/repenomamus_giganticus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Repenomamus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

FUR = (0.25, 0.18, 0.12)
FUR_LIGHT = (0.45, 0.36, 0.26)
CHEST = (0.78, 0.70, 0.56)
NOSE = (0.08, 0.06, 0.05)


def make():
    s = dn.DinoSpec(
        name="Repenomamus",
        paint=dn.make_paint(FUR, FUR_LIGHT, CHEST, mottle=0.25, head=(0.32, 0.25, 0.18), head_y=-0.5),
        hip_y=0.30, hip_z=0.25, body_len=0.65, torso_w=0.15, torso_h=0.14, belly=0.01, chest_dz=-0.01,
        tail_len=0.55, tail_r=0.35, tail_droop=-0.12,
        neck_len=0.08, neck_rise=0.03, neck_r=0.09, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.10, 0.09), (-0.08, -0.01, 0.10, 0.085), (-0.16, -0.025, 0.07, 0.06),
                   (-0.23, -0.04, 0.04, 0.035), (-0.26, -0.045, 0.0, 0.0)],
        head_len=0.26, head_h=0.09, head_w=0.10,
        leg_type="column", leg_r=0.06, leg_x=0.03, toes=5, toe_len=0.04, toe_r=0.012, claw=0.02, stride=0.05,
        fore="leg", fore_type="bent", arm_r=0.05, fore_toes=5, shoulder_dy=0.08,
        eye_r=0.013, eye_pos=(-0.13, 0.03, 0.78), eye_col=(0.05, 0.04, 0.03),
        fuzz=0.008, scales=0.0, voxel=0.01, max_tris=11000,
    )
    hb = s.head_base

    def crisp(mb, s):
        for sx in (1, -1):
            mb.add(nh.ellipsoid((sx * 0.07, hb.y + 0.02, hb.z + 0.08), (0.025, 0.01, 0.03), subdivisions=2), FUR)
        mb.add(nh.ellipsoid((0, hb.y - 0.255, hb.z - 0.035), (0.02, 0.012, 0.015), subdivisions=2), NOSE)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Repenomamus")
