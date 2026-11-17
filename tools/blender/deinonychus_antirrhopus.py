"""
Procedural Deinonychus antirrhopus (Early Cretaceous dromaeosaurid, western North America).

Bigger and heavier than Velociraptor: a deep, broad-snouted skull with a strong jaw full of
blade teeth, a thick S-neck, long feathered arms with big hand claws, a stiffened tail with a
feather fan, and the famous 'terrible claw' raised on the second toe. Slate grey with a pale
throat and belly, a rusty face and darker wing and tail quills.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/deinonychus_antirrhopus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Deinonychus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_cre_dino as dn  # noqa: E402

BACK = (0.20, 0.21, 0.23)
FLANK = (0.38, 0.38, 0.38)
BELLY = (0.86, 0.84, 0.78)
FACE = (0.60, 0.28, 0.14)
QUILL = (0.10, 0.10, 0.12)


def make():
    s = dn.DinoSpec(
        name="Deinonychus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=(0.10, 0.10, 0.11), freq=20.0, stripe_amt=0.35,
                            head=FACE, head_y=-0.62, y_range=(-0.6, 1.2)),
        hip_y=0.15, hip_z=0.52, body_len=0.45, torso_w=0.11, torso_h=0.14, belly=0.03,
        tail_len=0.95, tail_r=0.62, tail_droop=0.0,
        neck_len=0.20, neck_rise=0.17, neck_r=0.055, neck_s=0.03,
        head_len=0.30, head_h=0.065, head_w=0.055, snout_h=0.55, snout_w=0.55, snout_drop=0.01,
        jaw=True, jaw_open=14, teeth=7, tooth_len=0.016,
        leg_r=0.06, knee_fwd=0.11, toes=3, toe_len=0.08, toe_r=0.015, claw=0.02, sickle=0.08,
        arm_len=0.30, arm_r=0.022, fingers=3, finger_len=0.08, hand_claw=0.035,
        eye_r=0.015, eye_col=(0.90, 0.70, 0.20), fuzz=0.004, scales=0.0, voxel=0.009, max_tris=12000,
    )

    def crisp(mb, s):
        dn.arm_vanes(mb, s, lambda co, n: QUILL, length=0.14)
        dn.tail_fan(mb, s, lambda co, n: QUILL, u0=0.5, width=0.07)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Deinonychus")
