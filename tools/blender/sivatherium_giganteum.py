"""
Procedural Sivatherium giganteum (Pliocene - Early Pleistocene of the Indian
subcontinent) for map colonies.

A massive, okapi-like giraffid, among the heaviest ruminants ever: a deep,
heavy body with strong shoulders, a short thick neck, and on the broad skull
two pairs of ossicones - a pair of large, palmate, branching ones at the back
of the head and a pair of small cones over the eyes. Plain brown coat with a
pale belly and paler lower legs. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/sivatherium_giganteum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SivatheriumGiganteum.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="SivatheriumGiganteum",
    leg_f=0.88, leg_h=0.80, length=0.80, girth=(0.25, 0.30),
    leg_r=(0.075, 0.08), leg_taper=0.55, foot="hoof", stride=0.12,
    neck_len=0.40, neck_angle=40, neck_r=(0.20, 0.14),
    head_len=0.48, head_r=(0.13, 0.13), snout_r=(0.07, 0.08), head_pitch=60,
    ears="point", ear_size=0.09,
    tail_len=0.40, tail_r=0.025, tail_tuft=0.04, tail_droop=0.95,
    horns=[dict(t=0.18, s=sx * 0.13, u=0.30, len=0.22, r=0.04, dir=(sx * 0.9, 0.3, 0.8), bend=(sx * 0.1, 0.3, 0.3), tip=0.03,
                color=(0.42, 0.33, 0.24)) for sx in (-1, 1)]
         + [dict(t=0.42, s=sx * 0.10, u=0.25, len=0.08, r=0.025, dir=(sx * 0.5, 0, 1), tip=0.012, color=(0.42, 0.33, 0.24))
            for sx in (-1, 1)],
    extra_details=lambda mb, L, surf: q.palmate_ossicones(mb, L),
    coat=(0.48, 0.35, 0.24), dark=(0.30, 0.21, 0.14), pale=(0.80, 0.72, 0.60),
    pattern=q.lower_legs((0.78, 0.70, 0.58), z1=0.35, amount=0.7), shag=0.004, voxel=0.018,
)

if __name__ == "__main__":
    q.main(SPEC)
