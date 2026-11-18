"""
Procedural Tarbosaurus bataar (Late Cretaceous tyrannosaurid, Mongolia).

A 10-metre tyrannosaur: a massive, deep skull (narrower than T. rex's) with banana teeth and
rough bosses over the eyes, a thick S-neck, minute two-fingered arms, a deep barrel chest on
long pillar legs and a heavy tail. Dusty olive-brown with darker transverse bands, a pale
cream throat and belly and a rusty face.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/tarbosaurus_bataar.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tarbosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_cre_dino as dn  # noqa: E402

BACK = (0.30, 0.29, 0.20)
FLANK = (0.50, 0.46, 0.32)
BELLY = (0.86, 0.80, 0.64)
BAND = (0.16, 0.14, 0.10)
FACE = (0.40, 0.30, 0.20)


def make():
    s = dn.DinoSpec(
        name="Tarbosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAND, freq=16.0, stripe_amt=0.6,
                            head=FACE, head_y=-0.62, y_range=(-0.70, 1.3)),
        hip_y=0.22, hip_z=0.60, body_len=0.52, torso_w=0.16, torso_h=0.20, belly=0.05,
        tail_len=0.92, tail_r=0.66, tail_droop=-0.03,
        neck_len=0.14, neck_rise=0.14, neck_r=0.095, neck_s=0.03,
        head_len=0.36, head_h=0.11, head_w=0.08, snout_h=0.68, snout_w=0.6, snout_drop=0.02,
        jaw=True, jaw_open=16, jaw_h=0.5, teeth=8, tooth_len=0.03,
        leg_r=0.09, knee_fwd=0.12, toes=3, toe_len=0.10, toe_r=0.024, claw=0.028, stride=0.06,
        arm_len=0.07, arm_r=0.016, fingers=2, finger_len=0.02, hand_claw=0.012,
        eye_r=0.014, eye_col=(0.85, 0.55, 0.10), scales=0.002, voxel=0.01, max_tris=14000,
    )
    # brow bosses and a rugose ridge along the snout
    c, hw, hh = s.head_at(0.24)
    s.blobs.append(((hw * 0.65, c.y, c.z + hh * 0.85), (0.024, 0.035, 0.02), True))
    for k in range(4):
        c, hw, hh = s.head_at(0.45 + 0.11 * k)
        s.blobs.append(((hw * 0.3, c.y, c.z + hh * 0.9), (0.012, 0.02, 0.012), True))
    return s


if __name__ == "__main__":
    dn.run(make, "Tarbosaurus")
