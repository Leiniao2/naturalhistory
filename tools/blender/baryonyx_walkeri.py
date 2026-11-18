"""
Procedural Baryonyx walkeri (Early Cretaceous spinosaurid, England).

A 9-metre fish-eating theropod: a long, low, narrow crocodile-like snout with a rosette of
teeth at the tip and a small crest over the nose, a long straight neck, strong arms carrying a
huge hooked thumb claw, a low ridge along the back and a long tail. Muddy green-brown with
darker blotches, a pale belly and a reddish snout.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/baryonyx_walkeri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Baryonyx.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.26, 0.28, 0.20)
FLANK = (0.45, 0.45, 0.33)
BELLY = (0.84, 0.80, 0.66)
BLOTCH = (0.16, 0.17, 0.12)
SNOUT = (0.55, 0.30, 0.20)


def make():
    s = dn.DinoSpec(
        name="Baryonyx",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=BLOTCH, spot_scale=10.0, head=SNOUT, head_y=-0.78),
        hip_y=0.18, hip_z=0.55, body_len=0.50, torso_w=0.12, torso_h=0.16, belly=0.03, chest_dz=-0.03,
        tail_len=0.95, tail_r=0.62, tail_droop=-0.04,
        neck_len=0.24, neck_rise=0.12, neck_r=0.06, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.055, 0.06), (-0.08, -0.01, 0.045, 0.05), (-0.18, -0.03, 0.03, 0.035),
                   (-0.30, -0.05, 0.022, 0.026), (-0.38, -0.06, 0.03, 0.026), (-0.43, -0.07, 0.02, 0.016),
                   (-0.45, -0.072, 0.0, 0.0)],
        head_len=0.45, head_h=0.06, head_w=0.055,
        jaw=True, jaw_open=12, jaw_h=0.45, teeth=12, tooth_len=0.016,
        leg_r=0.07, knee_fwd=0.12, toes=3, toe_len=0.09, toe_r=0.02, claw=0.025, stride=0.05,
        arm_len=0.24, arm_r=0.028, fingers=3, finger_len=0.05, hand_claw=0.03, hand_dir=(0, -0.8, -0.6),
        eye_r=0.012, eye_pos=(-0.06, 0.03, 0.8), eye_col=(0.85, 0.60, 0.15), scales=0.002, voxel=0.009,
        max_tris=13000,
    )
    # low ridge of neural spines along the back
    for k in range(9):
        y = s.hip_y + 0.12 - k * 0.07
        s.blobs.append(((0, y, s.hip_z + s.torso_h * 0.62), (0.02, 0.06, 0.05 - 0.004 * abs(k - 4)), False))
    hb = s.head_base
    s.blobs.append(((0, hb.y - 0.10, hb.z + 0.045), (0.01, 0.05, 0.02), False))   # nasal crest

    def crisp(mb, s):
        for sx in (1, -1):
            sh, el, wr, tip = dn.arm_points(s, sx)
            base = wr + Vector((sx * -0.012, -0.02, -0.01))
            mb.add(cc.curved_cone(base, base + Vector((0, -0.04, -0.01)), base + Vector((0, -0.07, -0.05)),
                                  0.014, sides=7), cc.CLAW)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Baryonyx")
