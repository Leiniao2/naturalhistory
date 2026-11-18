"""
Procedural Leaellynasaura amicagraphica (Early Cretaceous small ornithopod, polar Australia).

A small, lightly built, fast plant-eater: a short head with big eyes and a horny beak, short
arms, long slender running legs and an extraordinarily long tail, about three times the
length of the body. Covered in short, fluffy filaments for warmth; dark grey-brown back,
pale buff flanks and belly, a white eye-ring and faint tail bands.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/leaellynasaura_amicagraphica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Leaellynasaura.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.26, 0.22, 0.19)
FLANK = (0.54, 0.46, 0.36)
BELLY = (0.88, 0.84, 0.74)
BAND = (0.16, 0.13, 0.11)
BEAK = (0.30, 0.26, 0.20)


def make():
    s = dn.DinoSpec(
        name="Leaellynasaura",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAND, freq=22.0, stripe_amt=0.6, y_range=(0.4, 2.0),
                            mottle=0.08),
        hip_y=-0.10, hip_z=0.42, body_len=0.30, torso_w=0.08, torso_h=0.095, belly=0.02,
        tail_len=1.35, tail_r=0.55, tail_droop=-0.02,
        neck_len=0.12, neck_rise=0.11, neck_r=0.03, neck_s=0.02,
        head_len=0.10, head_h=0.035, head_w=0.03, snout_h=0.45, snout_w=0.45, snout_drop=0.02,
        leg_r=0.045, knee_fwd=0.09, toes=3, toe_len=0.06, toe_r=0.011, claw=0.012, stride=0.08,
        arm_len=0.10, arm_r=0.012, fingers=4, finger_len=0.02, hand_claw=0.006,
        eye_r=0.014, eye_pos=(-0.035, 0.008, 0.9), eye_col=(0.25, 0.15, 0.06), eye_ring=(0.92, 0.90, 0.84),
        fuzz=0.004, scales=0.0, voxel=0.007, max_tris=10000,
    )
    hb = s.head_base

    def crisp(mb, s):
        mb.add(nh.ellipsoid((0, hb.y - 0.095, hb.z - 0.01), (0.012, 0.018, 0.012), subdivisions=2), BEAK)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Leaellynasaura")
