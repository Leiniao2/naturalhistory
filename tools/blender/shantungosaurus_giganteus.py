"""
Procedural Shantungosaurus giganteus (Late Cretaceous saurolophine hadrosaur, Shandong, China).

The biggest duck-billed dinosaur, about 15 metres long: a long, low, crestless head with a
broad duck-bill, a deep heavy body walking on all fours (hind legs much bigger), a tall
neural-spine ridge over the hips and a deep, flattened tail. Grey-blue back with darker
stripes, pale belly, dark bill.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/shantungosaurus_giganteus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Shantungosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.30, 0.34, 0.38)
FLANK = (0.50, 0.52, 0.52)
BELLY = (0.86, 0.84, 0.78)
STRIPE = (0.18, 0.20, 0.24)
BILL = (0.22, 0.20, 0.18)


def make():
    s = dn.DinoSpec(
        name="Shantungosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=STRIPE, freq=16.0, stripe_amt=0.55, y_range=(-0.5, 1.2)),
        hip_y=0.20, hip_z=0.60, body_len=0.66, torso_w=0.18, torso_h=0.23, belly=0.05, chest_dz=-0.10,
        tail_len=0.90, tail_r=0.62, tail_droop=-0.06, tail_flat=0.55,
        neck_len=0.22, neck_rise=0.08, neck_r=0.065, neck_s=0.03,
        head_len=0.36, head_h=0.06, head_w=0.055, snout_h=0.45, snout_w=1.05, snout_drop=0.045,
        leg_r=0.10, knee_fwd=0.10, toes=3, toe_len=0.07, toe_r=0.028, claw=0.01, stride=0.05,
        fore="leg", fore_type="bent", arm_r=0.045, fore_toes=3, shoulder_dy=0.06,
        eye_r=0.012, eye_col=(0.75, 0.5, 0.15), scales=0.002, voxel=0.011, max_tris=13000,
    )
    # tall spines over the hips
    for k in range(7):
        y = s.hip_y - 0.18 + 0.07 * k
        s.blobs.append(((0, y, s.hip_z + s.torso_h * 0.55), (0.035, 0.07, 0.07 - 0.006 * abs(k - 3)), False))
    hb = s.head_base

    def crisp(mb, s):
        mb.add(nh.ellipsoid((0, hb.y - 0.35, hb.z - 0.075), (0.062, 0.04, 0.013), subdivisions=2), BILL)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Shantungosaurus")
