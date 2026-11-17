"""
Procedural Carnotaurus sastrei (Late Cretaceous abelisaurid, Patagonia) for the map.

A lightly built, long-legged big theropod with a short, deep, blunt skull crowned by two
thick horns over the eyes, a muscular neck, stumpy vestigial arms and a long tail with a
broad base. The skin is known from impressions: small pebbly scales with rows of larger
conical bumps along the flanks. Brick-red head and back fading to tan flanks and a pale belly,
with darker rosettes on the sides.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/carnotaurus_sastrei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Carnotaurus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.45, 0.17, 0.10)
FLANK = (0.66, 0.46, 0.30)
BELLY = (0.88, 0.80, 0.64)
SPOT = (0.28, 0.12, 0.08)
HORN = (0.30, 0.22, 0.16)


def make():
    s = dn.DinoSpec(
        name="Carnotaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=SPOT, spot_scale=14.0,
                            head=(0.55, 0.15, 0.10), head_y=-0.62),
        hip_y=0.18, hip_z=0.62, body_len=0.50, torso_w=0.13, torso_h=0.16, belly=0.03,
        tail_len=0.95, tail_r=0.68, tail_droop=-0.02,
        neck_len=0.16, neck_rise=0.14, neck_r=0.075, neck_s=0.02,
        head_len=0.24, head_h=0.085, head_w=0.07, snout_h=0.65, snout_w=0.7, snout_drop=0.02,
        jaw=True, jaw_open=12, teeth=6, tooth_len=0.02,
        leg_r=0.075, knee_fwd=0.13, toes=3, toe_len=0.09, toe_r=0.02, claw=0.025,
        arm_len=0.07, arm_r=0.018, fingers=2, finger_len=0.02, hand_claw=0.0,
        eye_r=0.014, eye_col=(0.85, 0.55, 0.10), scales=0.002, voxel=0.01, max_tris=13000,
    )
    # rows of larger feature scales along the flanks (fused bumps)
    for k in range(9):
        y = s.hip_y - 0.05 - k * 0.055
        s.blobs.append(((s.torso_w * 0.92, y, s.hip_z + 0.04), (0.012, 0.012, 0.012), True))
    c, hw, hh = s.head_at(0.25)

    def crisp(mb, s):
        for sx in (1, -1):
            base = Vector((sx * hw * 0.55, c.y + 0.01, c.z + hh * 0.75))
            mid = base + Vector((sx * 0.05, 0.0, 0.04))
            tip = base + Vector((sx * 0.09, 0.02, 0.045))
            mb.add(cc.curved_cone(base, mid, tip, 0.03, sides=8), HORN)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Carnotaurus")
