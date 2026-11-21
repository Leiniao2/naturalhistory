"""
Procedural Asteriornis maastrichtensis (latest Cretaceous galloanseran bird, Maastricht
Formation, Belgium), the "Wonderchicken".

A small, quail-sized early modern bird standing on long, slender wading legs: a rounded
head with a chicken-like face and a broad, slightly duck-like bill, a short neck, a plump
body with folded wings, a short tail of feathers (no bony tail) and four-toed feet.
Speckled brown-and-buff plumage with a pale throat, darker wing coverts and a grey bill
(colours conjectural).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/asteriornis_maastrichtensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Asteriornis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, Matrix  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.38, 0.28, 0.18)
FLANK = (0.62, 0.50, 0.34)
BELLY = (0.90, 0.84, 0.70)
SPECK = (0.20, 0.14, 0.09)
WING = (0.30, 0.22, 0.14)
BILL = (0.45, 0.45, 0.42)
LEG = (0.55, 0.50, 0.38)


def make():
    s = dn.DinoSpec(
        name="Asteriornis",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=SPECK, spot_scale=110.0, mottle=0.1,
                            legs=LEG, leg_z=0.30),
        hip_y=0.10, hip_z=0.62, body_len=0.32, torso_w=0.15, torso_h=0.17, belly=0.04, chest_dz=0.06,
        tail_len=0.18, tail_r=0.6, tail_droop=0.04,
        neck_len=0.10, neck_rise=0.20, neck_r=0.06, neck_s=0.02,
        head_rows=[(0.0, 0.0, 0.07, 0.075), (-0.06, 0.005, 0.068, 0.07), (-0.11, -0.005, 0.045, 0.045),
                   (-0.14, -0.015, 0.03, 0.02), (-0.19, -0.025, 0.026, 0.012), (-0.20, -0.026, 0.0, 0.0)],
        head_len=0.20, head_h=0.075, head_w=0.07,
        leg_r=0.05, knee_fwd=0.06, ankle_back=0.12, toes=3, toe_len=0.10, toe_r=0.011, claw=0.01, stride=0.06,
        fore="none",
        eye_r=0.018, eye_pos=(-0.07, 0.02, 0.85), eye_col=(0.30, 0.18, 0.06),
        fuzz=0.004, scales=0.0, voxel=0.008, max_tris=9000,
    )
    hb = s.head_base

    def crisp(mb, s):
        # folded wings along the flanks
        for sx in (1, -1):
            mb.add(nh.ellipsoid((sx * s.torso_w * 0.88, s.chest_y + 0.17, s.hip_z + 0.05), (0.03, 0.17, 0.085),
                                rotation=Matrix.Rotation(0.25, 3, "X")), WING)
        # short tail fan
        c, r = dn.tail_point(s, 0.6)
        for k in range(5):
            a = (k - 2) * 0.3
            d = Vector((0.5 * a, 1.0, 0.35)).normalized()
            mb.add(cc.cone(c, c + d * 0.12, 0.02, sides=5), WING)
        # the bill
        mb.add(nh.ellipsoid((0, hb.y - 0.17, hb.z - 0.022), (0.03, 0.045, 0.014), subdivisions=2), BILL)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Asteriornis")
