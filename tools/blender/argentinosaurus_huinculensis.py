"""
Procedural Argentinosaurus huinculensis (Late Cretaceous titanosaur, Patagonia).

A contender for the largest land animal ever, perhaps 30-35 metres long and 65-75 tonnes:
a vast barrel body on pillar-like legs, a long neck held forward and up, a small head and a
long tapering tail. Hind feet with stout claws, front feet as columns of fused toes.
Grey-brown above, lighter below, with faint darker blotches and rows of small osteoderm
bumps along the back, as in other titanosaurs.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/argentinosaurus_huinculensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Argentinosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_cre_dino as dn  # noqa: E402

BACK = (0.38, 0.35, 0.32)
FLANK = (0.52, 0.48, 0.42)
BELLY = (0.74, 0.70, 0.62)


def make():
    s = dn.DinoSpec(
        name="Argentinosaurus",
        paint=dn.make_paint(BACK, FLANK, BELLY, spot=(0.28, 0.25, 0.22), spot_scale=6.0, mottle=0.15),
        hip_y=0.30, hip_z=0.42, body_len=0.50, torso_w=0.16, torso_h=0.17, belly=0.03, chest_dz=0.02,
        tail_len=0.75, tail_r=0.55, tail_droop=-0.12,
        neck_len=0.72, neck_rise=0.36, neck_r=0.042, neck_s=-0.03,
        head_len=0.11, head_h=0.03, head_w=0.03, snout_h=0.7, snout_w=0.8, snout_drop=0.02,
        leg_r=0.065, leg_type="column", toes=3, toe_len=0.04, toe_r=0.02, claw=0.02, stride=0.03,
        fore="leg", fore_type="column", arm_r=0.055, fore_toes=0, shoulder_dy=0.05, fore_len_ratio=1.0,
        eye_r=0.007, eye_col=(0.3, 0.2, 0.1), scales=0.0015, voxel=0.01, max_tris=12000,
    )
    for k in range(10):
        y = s.hip_y + 0.05 - k * 0.07
        s.blobs.append(((0.05, y, s.hip_z + s.torso_h * 0.82), (0.012, 0.014, 0.01), True))
    return s


if __name__ == "__main__":
    dn.run(make, "Argentinosaurus")
