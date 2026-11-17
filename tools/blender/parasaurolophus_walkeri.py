"""
Procedural Parasaurolophus walkeri (Late Cretaceous lambeosaurine hadrosaur, Alberta).

A duck-billed dinosaur famous for its long, hollow, backward-curving head crest - a tube of
bone up to a metre long containing the nasal passages, which probably worked as a resonating
horn for low calls. Bulky body, deep tail, standing on all fours; broad flat beak.
Rusty-brown back with pale vertical bars, a cream belly and a crest banded red and cream.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/parasaurolophus_walkeri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Parasaurolophus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.45, 0.25, 0.14)
FLANK = (0.62, 0.42, 0.26)
BELLY = (0.88, 0.80, 0.62)
BAR = (0.85, 0.76, 0.56)
CREST = (0.70, 0.18, 0.10)
CREST2 = (0.90, 0.82, 0.62)
BILL = (0.35, 0.30, 0.25)


def make():
    s = dn.DinoSpec(
        name="Parasaurolophus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAR, freq=26.0, stripe_amt=0.45, y_range=(-0.4, 0.6)),
        hip_y=0.2, hip_z=0.58, body_len=0.60, torso_w=0.16, torso_h=0.2, belly=0.05, chest_dz=-0.07,
        tail_len=0.80, tail_r=0.6, tail_droop=-0.05, tail_flat=0.65,
        neck_len=0.22, neck_rise=0.14, neck_r=0.06, neck_s=0.03,
        head_len=0.24, head_h=0.06, head_w=0.048, snout_h=0.5, snout_w=0.85, snout_drop=0.06,
        leg_r=0.09, knee_fwd=0.10, toes=3, toe_len=0.07, toe_r=0.025, claw=0.01, stride=0.05,
        fore="leg", fore_type="bent", arm_r=0.042, fore_toes=3, shoulder_dy=0.06,
        eye_r=0.012, eye_col=(0.75, 0.5, 0.15), scales=0.002, voxel=0.011, max_tris=13000,
    )
    hb = s.head_base

    def crisp(mb, s):
        # crest: tube from the snout roof sweeping back well past the skull
        pts = cc.bezier_pts((0, hb.y - 0.08, hb.z + 0.04), (0, hb.y + 0.05, hb.z + 0.16),
                            (0, hb.y + 0.30, hb.z + 0.17), 12)
        radii = [0.022 + 0.008 * math.sin(math.pi * i / 11) for i in range(12)]
        radii[-1] = 0.012

        def col(co, n):
            t = (co.y - (hb.y - 0.08)) / 0.38
            return CREST if math.sin(t * 18.0) > -0.3 else CREST2
        mb.add(nh.tube(pts, radii, sides=10), col)
        mb.add(nh.ellipsoid((0, hb.y - 0.235, hb.z - 0.05), (0.04, 0.03, 0.012), subdivisions=2), BILL)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Parasaurolophus")
