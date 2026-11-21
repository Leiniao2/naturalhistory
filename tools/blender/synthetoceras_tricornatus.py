"""
Procedural Synthetoceras tricornatus (Late Miocene of North America) for map
colonies: the largest protoceratid, a deer-like relative of camels.

A long-legged, deer-sized browser. Males bore a pair of horns curving up behind
the eyes and one long nose horn that forked into a Y at the tip. Sandy brown
coat, pale belly.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/synthetoceras_tricornatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SynthetocerasTricornatus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

def fork(mb, L, surf):
    # the Y at the top of the nose horn
    p, _n = surf.near(q.Vector(L.h(0.62, 0, 0.12)))
    base = p + q.Vector((0, -0.35, 1)).normalized() * 0.27
    for sx in (-1, 1):
        mb.add(q.bent_tube(base, (sx * 0.8, -0.2, 0.7), 0.13, 0.016, tip_r=0.005), (0.30, 0.25, 0.20))


SPEC = q.Spec(
    name="SynthetocerasTricornatus",
    leg_f=0.78, leg_h=0.78, length=0.72, girth=(0.16, 0.20),
    leg_r=(0.050, 0.058), leg_taper=0.5, foot="hoof", stride=0.13,
    neck_len=0.40, neck_angle=45, neck_r=(0.12, 0.08),
    head_len=0.44, head_r=(0.08, 0.09), snout_r=(0.045, 0.05), head_pitch=50,
    ears="point", ear_size=0.08,
    tail_len=0.18, tail_r=0.025, tail_droop=0.9,
    horns=[dict(t=0.25, s=sx * 0.08, u=0.25, len=0.14, r=0.022, dir=(sx * 0.3, 0.3, 1), bend=(sx * 0.2, 0, 0), tip=0.008,
                color=(0.30, 0.25, 0.20)) for sx in (-1, 1)]
          + [dict(t=0.62, s=0, u=0.12, len=0.30, r=0.03, dir=(0, -0.35, 1), tip=0.018, color=(0.30, 0.25, 0.20))],
    coat=(0.62, 0.46, 0.30), dark=(0.40, 0.29, 0.18), pale=(0.86, 0.80, 0.68),
    extra_details=fork,
    shag=0.003, voxel=0.015,
)

if __name__ == "__main__":
    q.main(SPEC)
