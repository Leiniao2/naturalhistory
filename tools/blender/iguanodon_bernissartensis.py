"""
Procedural Iguanodon bernissartensis (Early Cretaceous iguanodontian, Europe).

A big, bulky plant-eater about 10 metres long that could walk on two legs or four: a long,
horse-like head ending in a toothless beak, a heavy body with a deep tail, stout hind legs
with three hoofed toes and strong arms whose hands carried hoof-like middle fingers and a
conical thumb spike. Olive-green above with darker stripes, pale yellowish belly.
Shown on all fours. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/iguanodon_bernissartensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Iguanodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.30, 0.34, 0.20)
FLANK = (0.48, 0.50, 0.32)
BELLY = (0.84, 0.80, 0.58)
STRIPE = (0.18, 0.21, 0.12)
SPIKE = (0.80, 0.76, 0.62)


def make():
    s = dn.DinoSpec(
        name="Iguanodon",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=STRIPE, freq=22.0, stripe_amt=0.5),
        hip_y=0.2, hip_z=0.58, body_len=0.62, torso_w=0.16, torso_h=0.2, belly=0.05, chest_dz=-0.08,
        tail_len=0.85, tail_r=0.6, tail_droop=-0.05, tail_flat=0.7,
        neck_len=0.20, neck_rise=0.10, neck_r=0.065, neck_s=0.02,
        head_len=0.28, head_h=0.07, head_w=0.05, snout_h=0.55, snout_w=0.6, snout_drop=0.05,
        leg_r=0.09, knee_fwd=0.10, toes=3, toe_len=0.07, toe_r=0.025, claw=0.012, stride=0.05,
        fore="leg", fore_type="bent", arm_r=0.045, fore_toes=3, shoulder_dy=0.06,
        eye_r=0.013, eye_col=(0.7, 0.45, 0.15), scales=0.002, voxel=0.011, max_tris=13000,
    )

    def crisp(mb, s):
        # thumb spikes pointing inward-forward-up from the wrists
        x = s.torso_w * 0.7
        for sx in (1, -1):
            base = Vector((sx * (x + 0.035), s.chest_y + s.shoulder_dy - 0.05, 0.12))
            mb.add(cc.cone(base, base + Vector((-sx * 0.02, -0.07, 0.04)), 0.02, sides=8), SPIKE)
        hb = s.head_base
        mb.add(nh.ellipsoid((0, hb.y - 0.27, hb.z - 0.06), (0.025, 0.02, 0.025), subdivisions=2), (0.3, 0.28, 0.22))
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Iguanodon")
