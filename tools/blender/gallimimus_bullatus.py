"""
Procedural Gallimimus bullatus (Late Cretaceous ornithomimid, Mongolia).

An ostrich-like dinosaur about 6 metres long: a small, toothless, beaked head with big
eyes on a long slender neck, a compact feathered body, slender arms with three long
fingers, and very long running legs; a long stiff tail. Grey-brown feathering with a pale
belly and throat, darker wing fringes and a slate beak.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/gallimimus_bullatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gallimimus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.38, 0.34, 0.30)
FLANK = (0.58, 0.53, 0.46)
BELLY = (0.92, 0.90, 0.84)
WING = (0.20, 0.18, 0.17)
BEAK = (0.25, 0.25, 0.27)


def make():
    s = dn.DinoSpec(
        name="Gallimimus",
        paint=dn.make_paint(BACK, FLANK, BELLY, mottle=0.08),
        hip_y=0.12, hip_z=0.66, body_len=0.36, torso_w=0.10, torso_h=0.12, belly=0.03, chest_dz=0.02,
        tail_len=0.80, tail_r=0.55, tail_droop=-0.02,
        neck_len=0.36, neck_rise=0.36, neck_r=0.032, neck_s=0.05,
        head_len=0.14, head_h=0.035, head_w=0.03, snout_h=0.4, snout_w=0.45, snout_drop=0.02,
        leg_r=0.06, knee_fwd=0.12, ankle_back=0.05, toes=3, toe_len=0.07, toe_r=0.014, claw=0.015, stride=0.10,
        arm_len=0.24, arm_r=0.016, fingers=3, finger_len=0.07, hand_claw=0.02,
        eye_r=0.012, eye_pos=(-0.035, 0.012, 0.9), eye_col=(0.30, 0.20, 0.08), fuzz=0.004, scales=0.0,
        voxel=0.008, max_tris=11000,
    )
    hb = s.head_base

    def crisp(mb, s):
        dn.arm_vanes(mb, s, lambda co, n: WING, length=0.10, n=5)
        dn.tail_fan(mb, s, lambda co, n: WING, u0=0.7, width=0.04)
        mb.add(nh.ellipsoid((0, hb.y - 0.125, hb.z - 0.012), (0.014, 0.03, 0.012), subdivisions=2), BEAK)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Gallimimus")
