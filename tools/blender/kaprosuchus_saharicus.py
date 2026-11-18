"""
Procedural Kaprosuchus saharicus (mid-Cretaceous mahajangasuchid crocodyliform, Niger).

'BoarCroc': a 6-metre land-running crocodyliform with long, fairly upright legs holding the
body well off the ground, a deep, short, high snout with three pairs of tusk-like fangs
jutting above and below the jaws, forward-facing eyes and a pair of bony horns sweeping
back from the rear of the skull; a back armoured with rows of scutes and a long tail.
Dusty sand-brown with dark cross-bands, a pale belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kaprosuchus_saharicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kaprosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402
import nh_cre_armour as ar  # noqa: E402

BACK = (0.36, 0.30, 0.20)
FLANK = (0.56, 0.48, 0.34)
BELLY = (0.86, 0.80, 0.66)
BAND = (0.18, 0.14, 0.10)
SCUTE = (0.26, 0.22, 0.16)
HORN = (0.40, 0.34, 0.26)


def make():
    s = dn.DinoSpec(
        name="Kaprosuchus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAND, freq=20.0, stripe_amt=0.55, mottle=0.12),
        hip_y=0.25, hip_z=0.30, body_len=0.52, torso_w=0.13, torso_h=0.10, belly=0.0,
        tail_len=0.85, tail_r=0.85, tail_droop=-0.10, tail_flat=0.5,
        neck_len=0.08, neck_rise=0.03, neck_r=0.07, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.08, 0.065), (-0.08, -0.005, 0.07, 0.06), (-0.17, -0.015, 0.048, 0.048),
                   (-0.25, -0.025, 0.036, 0.040), (-0.30, -0.03, 0.03, 0.032), (-0.33, -0.035, 0.0, 0.0)],
        head_len=0.33, head_h=0.065, head_w=0.08, jaw=True, jaw_open=12, jaw_h=0.45, teeth=7, tooth_len=0.016,
        leg_type="column", leg_r=0.05, leg_x=0.03, toes=4, toe_len=0.06, toe_r=0.013, claw=0.015, stride=0.07,
        fore="leg", fore_type="bent", arm_r=0.04, fore_toes=5, shoulder_dy=0.05, fore_len_ratio=1.0,
        eye_r=0.014, eye_pos=(-0.06, 0.05, 0.6), eye_col=(0.85, 0.65, 0.2), scales=0.003, voxel=0.009,
        max_tris=13000,
    )
    hb = s.head_base

    def crisp(mb, s):
        ar.scutes(mb, s, [s.chest_y + 0.02 + 0.05 * k for k in range(12)], [-25, -8, 8, 25], 0.016, SCUTE,
                  height=0.5)
        ar.scutes(mb, s, [s.hip_y + 0.05 + 0.06 * k for k in range(9)], [-12, 12], 0.012, SCUTE, height=0.6)
        # tusks: big caniniform fangs jutting up from the lower jaw and down from the upper
        for sx in (1, -1):
            for dy in (0.20, 0.26):
                p = Vector((sx * 0.04, hb.y - dy, hb.z - 0.04))
                mb.add(cc.curved_cone(p, p + Vector((sx * 0.01, -0.005, 0.04)), p + Vector((sx * 0.015, 0.0, 0.07)),
                                      0.009, sides=6), cc.TOOTH)
            p = Vector((sx * 0.04, hb.y - 0.15, hb.z - 0.03))
            mb.add(cc.curved_cone(p, p + Vector((sx * 0.008, 0, -0.04)), p + Vector((sx * 0.01, 0.005, -0.07)),
                                  0.009, sides=6), cc.TOOTH)
            # horn-like bosses at the back of the skull
            q = Vector((sx * 0.06, hb.y + 0.01, hb.z + 0.05))
            mb.add(cc.curved_cone(q, q + Vector((sx * 0.02, 0.03, 0.02)), q + Vector((sx * 0.03, 0.07, 0.01)),
                                  0.016, sides=6), HORN)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Kaprosuchus")
