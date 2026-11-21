"""
Procedural Epicyon haydeni (Late Miocene of North America) for map colonies:
the largest bone-crushing "hyena-dog" (Borophaginae).

A wolf-shaped canid the size of a big lion, with a short, very deep, domed
muzzle and massive jaws for cracking bones, a thick neck, long legs and a
bushy tail. Grizzled tawny-grey coat. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/epicyon_haydeni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EpicyonHaydeni.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="EpicyonHaydeni",
    leg_f=0.50, leg_h=0.48, length=0.78, girth=(0.17, 0.22),
    leg_r=(0.060, 0.066), leg_taper=0.55, foot="paw", stride=0.14,
    neck_len=0.26, neck_angle=24, neck_r=(0.15, 0.12),
    head_len=0.42, head_r=(0.13, 0.13), snout_r=(0.07, 0.07), head_pitch=8,
    cranium=1.2, jaw=1.3, eye_t=0.40,
    ears="point", ear_size=0.12,
    tail_len=0.48, tail_r=0.05, tail_tuft=0.06, tail_droop=0.65,
    tusks=[dict(t=0.88, s=sx * 0.08, u=-0.16, dir=(0, -0.15, -1), len=0.09, r=0.016, tip=0.003,
                color=(0.92, 0.88, 0.76)) for sx in (-1, 1)],
    coat=(0.60, 0.50, 0.36), dark=(0.32, 0.26, 0.19), pale=(0.84, 0.78, 0.66),
    pattern=q.back_stripes((0.36, 0.29, 0.21), freq=7.0, amount=0.35, y0=-0.4, y1=1.0),
    shag=0.009, voxel=0.016,
)

if __name__ == "__main__":
    q.main(SPEC)
