"""
Procedural Halszkaraptor escuilliei (Late Cretaceous halszkaraptorine dromaeosaur, Mongolia).

A duck-sized amphibious raptor: a very long, swan-like neck, a flat, spoon-shaped snout full of
small teeth, short flattened flipper-like arms, an upright stance on longish legs with a small
sickle claw, and a modest tail. Dark glossy brown above, white below and on the throat, like a
merganser, with a reddish crown and pale eye stripe.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/halszkaraptor_escuilliei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Halszkaraptor.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.18, 0.15, 0.13)
FLANK = (0.34, 0.28, 0.24)
BELLY = (0.94, 0.92, 0.88)
CROWN = (0.55, 0.22, 0.12)
QUILL = (0.10, 0.09, 0.08)


def make():
    s = dn.DinoSpec(
        name="Halszkaraptor",
        paint=dn.make_paint(BACK, FLANK, BELLY, head=CROWN, head_y=-0.80, mottle=0.06),
        hip_y=0.18, hip_z=0.50, body_len=0.36, torso_w=0.12, torso_h=0.13, belly=0.03, chest_dz=0.03,
        tail_len=0.60, tail_r=0.55, tail_droop=-0.05,
        neck_len=0.40, neck_rise=0.30, neck_r=0.03, neck_s=0.07,
        head_rows=[(0.0, 0.0, 0.032, 0.032), (-0.04, -0.005, 0.028, 0.026), (-0.09, -0.015, 0.024, 0.014),
                   (-0.14, -0.02, 0.028, 0.011), (-0.165, -0.022, 0.018, 0.008), (-0.175, -0.022, 0.0, 0.0)],
        head_len=0.175, head_h=0.032, head_w=0.032,
        leg_r=0.05, knee_fwd=0.10, toes=3, toe_len=0.07, toe_r=0.013, claw=0.014, sickle=0.035, stride=0.05,
        arm_len=0.16, arm_r=0.018, fingers=3, finger_len=0.025, hand_claw=0.008, finger_r=0.01,
        hand_dir=(0, 0.3, -1.0),
        eye_r=0.011, eye_pos=(-0.03, 0.012, 0.85), eye_col=(0.85, 0.65, 0.15), fuzz=0.003, scales=0.0,
        voxel=0.007, max_tris=10000,
    )

    def crisp(mb, s):
        dn.arm_vanes(mb, s, lambda co, n: QUILL, length=0.05, n=4, droop=0.3)
        dn.tail_fan(mb, s, lambda co, n: QUILL, u0=0.6, width=0.04)
        hb = s.head_base
        teeth = [(sx * 0.022, hb.y - 0.10 - 0.012 * k, hb.z - 0.03) for k in range(5) for sx in (1, -1)]
        import nh_cre_core as cc
        cc.teeth_row(mb, teeth, 0.008, 0.0025, down=True)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Halszkaraptor")
