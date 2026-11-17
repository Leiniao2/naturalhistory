"""
Procedural Giganotosaurus carolinii (Late Cretaceous carcharodontosaurid, Patagonia).

One of the largest theropods: long, comparatively low and narrow skull with blade-like
teeth and a low ridge of bumps along the snout, a thick neck, three-fingered arms (longer
than a tyrannosaur's), deep chest and a long heavy tail. Grey-tan with dark chocolate
cross-bands over the back and tail, a pale throat and belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/giganotosaurus_carolinii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Giganotosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_cre_dino as dn  # noqa: E402

BACK = (0.36, 0.33, 0.28)
FLANK = (0.56, 0.50, 0.40)
BELLY = (0.86, 0.80, 0.66)
BAND = (0.17, 0.12, 0.09)


def make():
    s = dn.DinoSpec(
        name="Giganotosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAND, freq=18.0, stripe_amt=0.75,
                            head=(0.42, 0.32, 0.26), head_y=-0.75, y_range=(-0.75, 1.3)),
        hip_y=0.2, hip_z=0.56, body_len=0.55, torso_w=0.15, torso_h=0.19, belly=0.04,
        tail_len=0.95, tail_r=0.65, tail_droop=-0.03,
        neck_len=0.16, neck_rise=0.13, neck_r=0.085, neck_s=0.02,
        head_len=0.38, head_h=0.085, head_w=0.065, snout_h=0.62, snout_w=0.55, snout_drop=0.02,
        jaw=True, jaw_open=13, teeth=9, tooth_len=0.022,
        leg_r=0.085, knee_fwd=0.13, toes=3, toe_len=0.10, toe_r=0.022, claw=0.028, stride=0.06,
        arm_len=0.14, arm_r=0.022, fingers=3, finger_len=0.035, hand_claw=0.022,
        eye_r=0.014, eye_col=(0.80, 0.50, 0.10), scales=0.002, voxel=0.01, max_tris=14000,
    )
    # low bumpy ridges along the top of the snout and a brow boss
    for k in range(5):
        c, hw, hh = s.head_at(0.45 + 0.1 * k)
        s.blobs.append(((hw * 0.35, c.y, c.z + hh * 0.9), (0.012, 0.018, 0.012), True))
    c, hw, hh = s.head_at(0.22)
    s.blobs.append(((hw * 0.6, c.y, c.z + hh * 0.75), (0.02, 0.03, 0.015), True))
    return s


if __name__ == "__main__":
    dn.run(make, "Giganotosaurus")
