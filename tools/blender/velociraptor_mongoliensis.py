"""
Procedural Velociraptor mongoliensis (Late Cretaceous dromaeosaurid, Mongolia) for the map.

A turkey-sized, fully feathered raptor: long low skull with a slightly concave snout,
S-necked, stiff straight tail ending in a fan of feathers, folded feathered arms with
three clawed fingers, and the raised sickle claw on the second toe of each foot.
Sandy tan with dark brown back bars, pale belly, dark wing quills with pale tips.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/velociraptor_mongoliensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Velociraptor.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.42, 0.30, 0.17)
FLANK = (0.66, 0.52, 0.33)
BELLY = (0.90, 0.84, 0.70)
BAR = (0.20, 0.13, 0.07)
QUILL = (0.22, 0.16, 0.10)
QUILL_TIP = (0.86, 0.80, 0.66)


def quill(co, n):
    return QUILL


def make():
    s = dn.DinoSpec(
        name="Velociraptor",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAR, freq=34.0, stripe_amt=0.6,
                            head=(0.52, 0.40, 0.26), head_y=-0.55, y_range=(-0.5, 1.2)),
        hip_y=0.15, hip_z=0.48, body_len=0.42, torso_w=0.095, torso_h=0.12, belly=0.02,
        tail_len=0.95, tail_r=0.62, tail_droop=0.02,
        neck_len=0.20, neck_rise=0.18, neck_r=0.045, neck_s=0.03,
        head_len=0.30, head_h=0.045, head_w=0.04, snout_h=0.45, snout_w=0.45, snout_drop=0.0,
        jaw=True, jaw_open=8, teeth=7, tooth_len=0.012,
        leg_r=0.05, knee_fwd=0.10, toes=3, toe_len=0.07, toe_r=0.012, claw=0.018, sickle=0.06,
        arm_len=0.24, arm_r=0.018, fingers=3, finger_len=0.06, hand_claw=0.025,
        eye_r=0.014, eye_col=(0.85, 0.62, 0.15), fuzz=0.004, scales=0.0, voxel=0.009, max_tris=11000,
    )

    def crisp(mb, s):
        dn.arm_vanes(mb, s, quill, length=0.12)
        dn.tail_fan(mb, s, lambda co, n: QUILL, u0=0.45, width=0.06)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Velociraptor")
