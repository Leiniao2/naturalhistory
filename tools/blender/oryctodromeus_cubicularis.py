"""
Procedural Oryctodromeus cubicularis (mid-Cretaceous burrowing orodromine, Montana).

A small digging plant-eater about 2 metres long: a short, deep, wedge-shaped snout with a
horny beak, a thick neck, robust forearms with broad, blunt digging claws and heavy shoulders,
strong legs and a flexible tail. Fuzzy filaments; earthy brown with paler speckles, a cream
belly and a dark dusting of soil on the legs and snout.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/oryctodromeus_cubicularis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Oryctodromeus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.36, 0.26, 0.17)
FLANK = (0.56, 0.44, 0.30)
BELLY = (0.86, 0.80, 0.66)
SPECK = (0.74, 0.64, 0.48)
SOIL = (0.24, 0.18, 0.13)
BEAK = (0.22, 0.18, 0.14)


def make():
    s = dn.DinoSpec(
        name="Oryctodromeus",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=SPECK, spot_scale=60.0, legs=SOIL, leg_z=0.16, mottle=0.1),
        hip_y=0.12, hip_z=0.42, body_len=0.40, torso_w=0.11, torso_h=0.12, belly=0.03, chest_dz=-0.02,
        tail_len=0.85, tail_r=0.55, tail_droop=-0.03,
        neck_len=0.10, neck_rise=0.08, neck_r=0.05, neck_s=0.01,
        head_rows=[(0.0, 0.0, 0.045, 0.05), (-0.05, -0.008, 0.042, 0.048), (-0.10, -0.025, 0.03, 0.035),
                   (-0.14, -0.04, 0.016, 0.018), (-0.15, -0.045, 0.0, 0.0)],
        head_len=0.15, head_h=0.05, head_w=0.045,
        leg_r=0.055, knee_fwd=0.09, toes=3, toe_len=0.06, toe_r=0.014, claw=0.014, stride=0.05,
        arm_len=0.20, arm_r=0.024, fingers=3, finger_len=0.035, hand_claw=0.025, finger_r=0.012,
        hand_dir=(0, -0.6, -1.0),
        eye_r=0.012, eye_pos=(-0.04, 0.012, 0.85), eye_col=(0.55, 0.35, 0.10), fuzz=0.004, scales=0.0,
        voxel=0.008, max_tris=10000,
    )
    # heavy digging shoulders
    s.blobs.append(((s.torso_w * 0.75, s.chest_y + 0.05, s.chest_z - 0.01), (0.045, 0.06, 0.06), True))
    hb = s.head_base

    def crisp(mb, s):
        mb.add(nh.ellipsoid((0, hb.y - 0.145, hb.z - 0.045), (0.014, 0.018, 0.016), subdivisions=2), BEAK)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Oryctodromeus")
