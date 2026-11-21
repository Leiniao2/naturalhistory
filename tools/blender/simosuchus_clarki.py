"""
Procedural Simosuchus clarki (Late Cretaceous notosuchian crocodyliform, Maevarano Formation,
Madagascar).

A small, 75-centimetre land crocodile with a short, deep, blunt "pug" face, leaf-shaped
cusped teeth for plants, a compact, broad body armoured with rows of bony scutes from neck
to tail, upright legs held under the body and a short, thick tail. Earthy olive-brown
with darker scutes, a mottled flank and a pale throat and belly (colours conjectural).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/simosuchus_clarki.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Simosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402
import nh_cre_armour as ar  # noqa: E402

BACK = (0.33, 0.31, 0.20)
FLANK = (0.52, 0.47, 0.32)
BELLY = (0.86, 0.82, 0.68)
SCUTE = (0.24, 0.22, 0.15)


def make():
    s = dn.DinoSpec(
        name="Simosuchus",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=SCUTE, spot_scale=18.0, mottle=0.14),
        hip_y=0.22, hip_z=0.30, body_len=0.50, torso_w=0.16, torso_h=0.12, belly=0.01,
        tail_len=0.55, tail_r=0.8, tail_droop=-0.14, tail_flat=0.8,
        neck_len=0.06, neck_rise=0.02, neck_r=0.08, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.09, 0.075), (-0.06, -0.005, 0.09, 0.075), (-0.12, -0.02, 0.075, 0.065),
                   (-0.165, -0.035, 0.055, 0.05), (-0.185, -0.045, 0.03, 0.03), (-0.19, -0.05, 0.0, 0.0)],
        head_len=0.19, head_h=0.075, head_w=0.09,
        leg_type="column", leg_r=0.05, leg_x=0.02, toes=4, toe_len=0.05, toe_r=0.013, claw=0.014, stride=0.06,
        fore="leg", fore_type="column", arm_r=0.042, fore_toes=4, shoulder_dy=0.05, fore_len_ratio=1.0,
        eye_r=0.016, eye_pos=(-0.07, 0.04, 0.8), eye_col=(0.80, 0.62, 0.18), scales=0.003, voxel=0.009,
        max_tris=12000,
    )
    hb = s.head_base

    def crisp(mb, s):
        ar.scutes(mb, s, [s.chest_y - 0.02 + 0.045 * k for k in range(13)], [-50, -30, -10, 10, 30, 50], 0.015,
                  SCUTE, height=0.45)
        ar.scutes(mb, s, [s.hip_y + 0.05 + 0.05 * k for k in range(8)], [-15, 15], 0.013, SCUTE, height=0.5)
        # leaf-shaped teeth peeking from the blunt jaw
        teeth = [(sx * (0.045 - 0.006 * k), hb.y - 0.12 - 0.017 * k, hb.z - 0.065) for k in range(4) for sx in (1, -1)]
        cc.teeth_row(mb, teeth, 0.014, 0.006, down=True)
        for sx in (1, -1):
            mb.add(nh.ellipsoid((sx * 0.018, hb.y - 0.188, hb.z - 0.03), (0.006, 0.004, 0.005), subdivisions=1),
                   (0.08, 0.06, 0.05))
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Simosuchus")
