"""
Procedural Patagotitan mayorum (mid-Cretaceous titanosaur, Patagonia).

One of the largest land animals, about 37 metres long: a vast, deep barrel body on massive
pillar legs, a very long, thick neck held forward and up, a small blunt head and a long
tapering tail, and a broad, wide-gauge stance. Slate grey with a warm brown back, faint
darker bands and a paler belly and throat.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/patagotitan_mayorum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Patagotitan.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_cre_dino as dn  # noqa: E402

BACK = (0.36, 0.30, 0.26)
FLANK = (0.46, 0.45, 0.44)
BELLY = (0.72, 0.70, 0.66)


def make():
    s = dn.DinoSpec(
        name="Patagotitan",
        paint=dn.make_paint(BACK, FLANK, BELLY, stripe=(0.26, 0.24, 0.22), freq=10.0, stripe_amt=0.35,
                            mottle=0.12),
        hip_y=0.30, hip_z=0.44, body_len=0.52, torso_w=0.19, torso_h=0.19, belly=0.04, chest_dz=0.03,
        tail_len=0.85, tail_r=0.5, tail_droop=-0.14,
        neck_len=0.80, neck_rise=0.42, neck_r=0.05, neck_s=-0.04,
        head_len=0.12, head_h=0.035, head_w=0.034, snout_h=0.75, snout_w=0.85, snout_drop=0.025,
        leg_r=0.075, leg_type="column", leg_x=0.02, toes=3, toe_len=0.04, toe_r=0.022, claw=0.02, stride=0.04,
        fore="leg", fore_type="column", arm_r=0.065, fore_toes=0, shoulder_dy=0.05, fore_len_ratio=1.0,
        eye_r=0.007, eye_col=(0.3, 0.2, 0.1), scales=0.0015, voxel=0.01, max_tris=13000,
    )
    return s


if __name__ == "__main__":
    dn.run(make, "Patagotitan")
