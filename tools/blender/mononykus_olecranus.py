"""
Procedural Mononykus olecranus (Late Cretaceous alvarezsaurid, Nemegt Formation, Mongolia).

A small, lightly built, feathered theropod about a metre long: a small slender head with a
narrow snout and big eyes, a long thin neck, a compact body, very short but stout arms
each ending in a single big thumb claw, long slender running legs and a long tail.
Sandy buff feathering with a darker back, pale belly and a dark eye mask (colours
conjectural).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/mononykus_olecranus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mononykus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.48, 0.36, 0.22)
FLANK = (0.74, 0.62, 0.44)
BELLY = (0.94, 0.90, 0.80)
MASK = (0.18, 0.13, 0.09)
TAIL = (0.30, 0.22, 0.14)


def make():
    s = dn.DinoSpec(
        name="Mononykus",
        paint=None,
        hip_y=0.12, hip_z=0.62, body_len=0.32, torso_w=0.085, torso_h=0.10, belly=0.02, chest_dz=0.01,
        tail_len=0.85, tail_r=0.5, tail_droop=-0.02,
        neck_len=0.26, neck_rise=0.24, neck_r=0.028, neck_s=0.04,
        head_len=0.14, head_h=0.032, head_w=0.03, snout_h=0.35, snout_w=0.4, snout_drop=0.012,
        leg_r=0.045, knee_fwd=0.11, ankle_back=0.05, toes=3, toe_len=0.07, toe_r=0.011, claw=0.012, stride=0.12,
        arm_len=0.08, arm_r=0.022, fingers=1, finger_len=0.03, hand_claw=0.04, finger_r=0.012,
        hand_dir=(0, -1.0, -0.4),
        eye_r=0.012, eye_pos=(-0.04, 0.008, 0.9), eye_col=(0.85, 0.65, 0.20), fuzz=0.004, scales=0.0,
        voxel=0.007, max_tris=10000,
    )
    hb = s.head_base

    def extra(co, n, c):
        if co.y < hb.y + 0.01 and co.y > hb.y - 0.08 and abs(n.x) > 0.5 and abs(co.z - (hb.z + 0.008)) < 0.012:
            return nh.lerp(c, MASK, 0.85)
        return c
    s.paint = dn.make_paint(BACK, FLANK, BELLY, mottle=0.1, extra=extra)
    # stout forearm muscles: a big breastbone keel and chunky forearms
    s.blobs.append(((0, s.chest_y + 0.03, s.chest_z - s.torso_h * 0.6), (0.03, 0.05, 0.04), False))

    def crisp(mb, s):
        dn.tail_fan(mb, s, lambda co, n: TAIL, u0=0.75, width=0.03)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Mononykus")
