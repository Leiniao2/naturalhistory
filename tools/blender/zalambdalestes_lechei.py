"""
Procedural Zalambdalestes lechei (Late Cretaceous eutherian, Djadokhta Formation, Mongolia).

A small, 20-centimetre, shrew-like early eutherian: a long, narrow, tapering snout with a
mobile nose tip, big eyes and rounded ears, short forelegs, long hind legs built for
hopping (like an elephant shrew), a hunched back and a long, thin tail. Sandy fawn fur
with a darker back stripe, white belly and eye ring (colours conjectural).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/zalambdalestes_lechei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Zalambdalestes.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_dino as dn  # noqa: E402

FUR = (0.46, 0.34, 0.22)
FUR_LIGHT = (0.70, 0.56, 0.38)
BELLY = (0.94, 0.90, 0.82)
NOSE = (0.30, 0.18, 0.16)
EAR = (0.58, 0.40, 0.32)


def make():
    s = dn.DinoSpec(
        name="Zalambdalestes",
        paint=dn.make_paint(FUR, FUR_LIGHT, BELLY, mottle=0.15),
        hip_y=0.22, hip_z=0.36, body_len=0.40, torso_w=0.10, torso_h=0.11, belly=0.0, chest_dz=-0.08,
        tail_len=0.85, tail_r=0.22, tail_droop=-0.25,
        neck_len=0.06, neck_rise=0.02, neck_r=0.06, neck_s=0.0,
        head_rows=[(0.0, 0.0, 0.055, 0.055), (-0.06, -0.01, 0.05, 0.045), (-0.13, -0.03, 0.025, 0.022),
                   (-0.20, -0.045, 0.014, 0.013), (-0.23, -0.05, 0.008, 0.008), (-0.24, -0.052, 0.0, 0.0)],
        head_len=0.24, head_h=0.055, head_w=0.055,
        leg_r=0.05, knee_fwd=0.13, ankle_back=0.10, toes=5, toe_len=0.06, toe_r=0.008, claw=0.008, stride=0.03,
        fore="leg", fore_type="bent", arm_r=0.022, fore_toes=5, shoulder_dy=0.04, fore_len_ratio=1.0,
        eye_r=0.014, eye_pos=(-0.05, 0.02, 0.8), eye_col=(0.04, 0.03, 0.03), eye_ring=(0.90, 0.86, 0.78),
        fuzz=0.004, scales=0.0, voxel=0.007, max_tris=10000,
    )
    hb = s.head_base

    def crisp(mb, s):
        for sx in (1, -1):
            mb.add(nh.ellipsoid((sx * 0.045, hb.y + 0.03, hb.z + 0.055), (0.012, 0.022, 0.03), subdivisions=2), EAR)
        mb.add(nh.ellipsoid((0, hb.y - 0.238, hb.z - 0.05), (0.009, 0.008, 0.008), subdivisions=2), NOSE)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    dn.run(make, "Zalambdalestes")
