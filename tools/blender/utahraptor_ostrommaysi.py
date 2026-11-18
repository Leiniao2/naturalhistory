"""
Procedural Utahraptor ostrommaysi (Early Cretaceous dromaeosaurid, Utah).

The giant of the raptors, about 6 metres long and heavily built: a deep, broad skull with
blade teeth, a thick neck, long feathered arms with big hand claws, stocky legs carrying a
huge raised sickle claw, and a long feathered tail. Rusty brown with dark bars across the
back, a pale cream belly, a black-and-white banded face and dark quills.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/utahraptor_ostrommaysi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Utahraptor.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.36, 0.20, 0.11)
FLANK = (0.58, 0.38, 0.22)
BELLY = (0.88, 0.82, 0.70)
BAR = (0.16, 0.09, 0.05)
QUILL = (0.12, 0.08, 0.06)
TIP = (0.90, 0.88, 0.82)


def make():
    s = dn.DinoSpec(
        name="Utahraptor",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAR, freq=20.0, stripe_amt=0.6,
                            head=(0.20, 0.16, 0.14), head_y=-0.60, y_range=(-0.60, 1.3)),
        hip_y=0.15, hip_z=0.50, body_len=0.47, torso_w=0.13, torso_h=0.16, belly=0.04,
        tail_len=0.92, tail_r=0.62, tail_droop=0.0,
        neck_len=0.19, neck_rise=0.16, neck_r=0.065, neck_s=0.03,
        head_len=0.30, head_h=0.075, head_w=0.06, snout_h=0.6, snout_w=0.6, snout_drop=0.01,
        jaw=True, jaw_open=16, teeth=7, tooth_len=0.018,
        leg_r=0.07, knee_fwd=0.11, toes=3, toe_len=0.08, toe_r=0.018, claw=0.022, sickle=0.12,
        arm_len=0.30, arm_r=0.026, fingers=3, finger_len=0.08, hand_claw=0.04,
        eye_r=0.015, eye_col=(0.95, 0.75, 0.20), fuzz=0.004, scales=0.0, voxel=0.009, max_tris=13000,
    )

    def crisp(mb, s):
        quill = lambda co, n: nh.lerp(QUILL, TIP, 0.8) if co.y > s.hip_y + s.tail_len * 0.93 else QUILL
        dn.arm_vanes(mb, s, lambda co, n: QUILL, length=0.15)
        dn.tail_fan(mb, s, quill, u0=0.45, width=0.08)
    s.crisp = crisp
    # pale stripe behind the eye
    hb = s.head_base
    s.paint = dn.make_paint(BACK, FLANK, BELLY, stripe=BAR, freq=20.0, stripe_amt=0.6,
                            head=(0.20, 0.16, 0.14), head_y=-0.60, y_range=(-0.60, 1.3),
                            extra=lambda co, n, c: TIP if (hb.y - 0.08 < co.y < hb.y + 0.04 and abs(co.z - hb.z) < 0.012) else c)
    return s


if __name__ == "__main__":
    dn.run(make, "Utahraptor")
