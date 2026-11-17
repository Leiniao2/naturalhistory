"""
Procedural marsupial lion (Thylacoleo carnifex, Pleistocene of Australia) for
map colonies.

A leopard-sized but very heavily built predator, pound for pound one of the
strongest-biting mammals known: a short, deep, cat-like head with blade-like
cheek teeth, extremely powerful forelimbs (with a huge thumb claw), a long,
thick tail and plantigrade-ish hind feet. Tawny coat; the dark stripes across
the back follow an Aboriginal rock painting thought to show it.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/thylacoleo_carnifex.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ThylacoleoCarnifex.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="ThylacoleoCarnifex",
    leg_f=0.40, leg_h=0.40, length=0.72, girth=(0.18, 0.21),
    leg_r=(0.068, 0.06), leg_taper=0.65, foot="paw", foot_r=1.15, stride=0.12,
    neck_len=0.20, neck_angle=20, neck_r=(0.15, 0.12),
    head_len=0.30, head_r=(0.11, 0.11), snout_r=(0.07, 0.07), head_pitch=10,
    ears="round", ear_size=0.07,
    tail_len=0.60, tail_r=0.05, tail_droop=0.55,
    coat=(0.68, 0.52, 0.32), dark=(0.40, 0.29, 0.17), pale=(0.86, 0.78, 0.64),
    pattern=q.back_stripes((0.18, 0.12, 0.08), freq=9.0, amount=0.85, y0=0.0, y1=1.0),
    shag=0.004, voxel=0.015,
)

if __name__ == "__main__":
    q.main(SPEC)
