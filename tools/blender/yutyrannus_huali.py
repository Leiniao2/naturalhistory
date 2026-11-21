"""
Procedural Yutyrannus huali (Early Cretaceous tyrannosauroid, Yixian Formation, China).

A 9-metre early tyrannosaur covered in long shaggy filaments: a long, deep skull with a
tall, thin, wavy crest along the top of the snout, a sturdy neck, three-fingered arms
much longer than those of later tyrannosaurs, powerful legs and a long tail. The coat is
shaggy and tawny brown with a darker back, pale throat and belly and darker tail rings
(colours conjectural); a rusty crest.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/yutyrannus_huali.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Yutyrannus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.30, 0.22, 0.14)
FLANK = (0.56, 0.42, 0.26)
BELLY = (0.88, 0.82, 0.68)
BAND = (0.20, 0.14, 0.09)
FACE = (0.48, 0.38, 0.28)
CREST = (0.62, 0.24, 0.12)
SHAG = (0.40, 0.29, 0.18)


def make():
    s = dn.DinoSpec(
        name="Yutyrannus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAND, freq=14.0, stripe_amt=0.55,
                            head=FACE, head_y=-0.66, y_range=(0.25, 1.4), mottle=0.18),
        hip_y=0.22, hip_z=0.58, body_len=0.52, torso_w=0.15, torso_h=0.19, belly=0.05,
        tail_len=0.95, tail_r=0.64, tail_droop=-0.04,
        neck_len=0.18, neck_rise=0.15, neck_r=0.085, neck_s=0.03,
        head_len=0.34, head_h=0.09, head_w=0.065, snout_h=0.6, snout_w=0.55, snout_drop=0.02,
        jaw=True, jaw_open=14, jaw_h=0.45, teeth=8, tooth_len=0.026,
        leg_r=0.085, knee_fwd=0.12, toes=3, toe_len=0.10, toe_r=0.022, claw=0.026, stride=0.07,
        arm_len=0.20, arm_r=0.022, fingers=3, finger_len=0.05, hand_claw=0.03,
        eye_r=0.014, eye_col=(0.85, 0.60, 0.15), fuzz=0.012, scales=0.0, voxel=0.01, max_tris=14000,
    )
    hb = s.head_base

    def crisp(mb, s):
        # the thin, wavy nasal crest along the snout midline
        pairs = []
        for k in range(9):
            f = 0.28 + 0.5 * k / 8
            c, hw, hh = s.head_at(f)
            h = 0.035 * (0.4 + 0.6 * (1 - abs(k - 4) / 4)) * (1.0 + 0.25 * ((k % 2) - 0.5))
            pairs.append(((0, c.y, c.z + hh * 0.85), (0, c.y + 0.01, c.z + hh * 0.85 + h)))
        mb.add(cc.ribbon(pairs, 0.008, normal_hint=Vector((1, 0, 0))), CREST)
        # shaggy filament tufts on the arms
        for sx in (1, -1):
            sh, el, wr, tip = dn.arm_points(s, sx)
            for p in (el, el.lerp(wr, 0.5)):
                mb.add(cc.curved_cone(p, p + Vector((sx * 0.01, 0.03, -0.01)), p + Vector((sx * 0.01, 0.06, -0.04)),
                                      0.01, sides=5), SHAG)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Yutyrannus")
