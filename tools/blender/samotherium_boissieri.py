"""
Procedural Samotherium boissieri (Late Miocene of Samos, Greece) for map
colonies: a giraffid with a neck intermediate between the okapi and giraffe.

Long legs, a moderately long, slanting neck, a long head with a pair of long,
backward-sweeping ossicones above the eyes. Reddish-brown coat with a pale
belly and pale lower legs barred with brown (an okapi-like reconstruction
choice). Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/samotherium_boissieri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SamotheriumBoissieri.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="SamotheriumBoissieri",
    leg_f=0.92, leg_h=0.84, length=0.72, girth=(0.20, 0.25),
    leg_r=(0.060, 0.068), leg_taper=0.5, foot="hoof", stride=0.13,
    neck_len=0.72, neck_angle=55, neck_r=(0.15, 0.09),
    head_len=0.46, head_r=(0.09, 0.10), snout_r=(0.05, 0.06), head_pitch=60,
    ears="point", ear_size=0.09,
    tail_len=0.42, tail_r=0.025, tail_tuft=0.04, tail_droop=0.95,
    horns=[dict(t=0.30, s=sx * 0.08, u=0.28, len=0.20, r=0.028, dir=(sx * 0.25, 0.9, 0.7), bend=(0, 0.2, -0.3), tip=0.012,
                color=(0.35, 0.26, 0.18)) for sx in (-1, 1)],
    coat=(0.55, 0.33, 0.20), dark=(0.33, 0.19, 0.11), pale=(0.85, 0.78, 0.66),
    pattern=q.combine(q.lower_legs((0.86, 0.80, 0.70), z1=0.5, amount=0.85),
                      q.leg_bands((0.35, 0.22, 0.14), freq=26, amount=0.6, z1=0.5)),
    shag=0.003, voxel=0.017,
)

if __name__ == "__main__":
    q.main(SPEC)
