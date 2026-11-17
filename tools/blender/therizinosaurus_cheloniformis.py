"""
Procedural Therizinosaurus cheloniformis (Late Cretaceous therizinosaur, Mongolia).

A huge, bizarre plant-eating theropod: a small beaked head on a long neck, a pot-bellied,
steeply tilted body on broad hips, short stout legs with four weight-bearing toes, a short
tail, and long arms ending in three enormous scythe-like claws up to about a metre long.
Probably covered in a coat of simple feathers. Shaggy grey-brown with a paler belly and a
dark face; the claws are horn-black.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/therizinosaurus_cheloniformis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Therizinosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.36, 0.30, 0.24)
FLANK = (0.50, 0.43, 0.34)
BELLY = (0.74, 0.68, 0.56)
FACE = (0.22, 0.18, 0.15)
BEAK = (0.70, 0.64, 0.50)


def make():
    s = dn.DinoSpec(
        name="Therizinosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, head=FACE, head_y=-0.62, mottle=0.15),
        hip_y=0.30, hip_z=0.55, body_len=0.48, torso_w=0.19, torso_h=0.22, belly=0.06, chest_dz=0.22,
        tail_len=0.45, tail_r=0.5, tail_droop=-0.05,
        neck_len=0.32, neck_rise=0.30, neck_r=0.05, neck_s=0.04,
        head_len=0.14, head_h=0.045, head_w=0.04, snout_h=0.5, snout_w=0.5, snout_drop=0.02,
        leg_r=0.085, knee_fwd=0.06, toes=4, toe_len=0.07, toe_r=0.022, claw=0.025, stride=0.03,
        arm_len=0.42, arm_r=0.045, arm_x=0.08, finger_r=0.02, fingers=3, finger_len=0.06, hand_claw=0.20,
        hand_dir=(0, -0.6, -0.6), arm_lift=0.05,
        eye_r=0.011, eye_col=(0.6, 0.45, 0.2), fuzz=0.006, scales=0.0, voxel=0.011, max_tris=13000,
    )
    hb = s.head_base

    def crisp(mb, s):
        mb.add(nh.ellipsoid((0, hb.y - 0.12, hb.z - 0.012), (0.02, 0.03, 0.022), subdivisions=2), BEAK)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Therizinosaurus")
