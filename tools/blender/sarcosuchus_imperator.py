"""
Procedural Sarcosuchus imperator (Early Cretaceous pholidosaurid crocodyliform, Niger and
Brazil), 'SuperCroc'.

One of the largest crocodile-like reptiles, about 9-9.5 metres long and 8 tonnes. Its long,
fairly narrow snout ends in a bulbous expansion (the bulla) over the nostrils and an
overbite of big teeth; a broad continuous shield of osteoderms covered its back and tail.
Sprawling legs and a flattened tail. Brown-grey with darker banding, yellowish belly.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/sarcosuchus_imperator.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sarcosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

BACK = (0.33, 0.29, 0.22)
FLANK = (0.50, 0.44, 0.32)
BELLY = (0.86, 0.80, 0.56)
BAND = (0.18, 0.15, 0.11)
BULLA = (0.26, 0.22, 0.18)


def make():
    s = dn.DinoSpec(
        name="Sarcosuchus",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=BAND, freq=16.0, stripe_amt=0.6, mottle=0.12,
                            extra=lambda co, n, c: nh.lerp(c, BAND, 0.5 * cc.spots(co, 30.0, 0.3) * nh.smoothstep(0.5, 0.9, n.z))),
        hip_y=0.25, hip_z=0.14, body_len=0.52, torso_w=0.15, torso_h=0.09, belly=0.0,
        tail_len=0.85, tail_r=0.85, tail_droop=-0.03, tail_flat=0.45,
        neck_len=0.08, neck_rise=0.01, neck_r=0.06, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.085, 0.05), (-0.08, -0.004, 0.065, 0.04), (-0.18, -0.008, 0.035, 0.024),
                   (-0.34, -0.012, 0.028, 0.02), (-0.46, -0.012, 0.03, 0.02), (-0.52, -0.008, 0.042, 0.032),
                   (-0.56, -0.01, 0.03, 0.025), (-0.58, -0.014, 0.0, 0.0)],
        head_len=0.58, head_h=0.05, head_w=0.085, jaw=True, jaw_open=7, jaw_h=0.45, teeth=12, tooth_len=0.018,
        leg_type="sprawl", leg_r=0.04, toes=4, toe_len=0.055, toe_r=0.012, claw=0.014, stride=-0.05,
        fore="leg", fore_type="sprawl", arm_r=0.032, fore_toes=5, shoulder_dy=0.05,
        eye_r=0.014, eye_pos=(-0.03, 0.04, 0.5), eye_col=(0.75, 0.62, 0.2), scales=0.003, voxel=0.0095,
        max_tris=13000,
    )
    for k in range(18):
        y = s.chest_y + k * 0.045
        for x in (0.03, 0.08):
            s.blobs.append(((x, y, s.hip_z + 0.075 - x * 0.3), (0.022, 0.02, 0.012), True))
    return s


if __name__ == "__main__":
    dn.run(make, "Sarcosuchus")
