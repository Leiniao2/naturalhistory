"""
Procedural steppe bison (Bison priscus, Pleistocene of Eurasia and North
America) for map colonies.

The great wild cattle of the Ice Age mammoth steppe, about 3 m long and up to
2 m at the shoulder, the bison painted in the caves of Lascaux and Altamira: a
towering shoulder hump, a low rump, a massive head carried low with long,
upward-curving horns, a shaggy dark-brown mane and beard over the head, neck and
forelegs and a paler, shorter-haired body.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/bison_priscus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BisonPriscus.fbx
"""

import math  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402
import nh_neo_quad as q  # noqa: E402


def nose(mb, L, surf, size=0.022, col=(0.05, 0.04, 0.04)):
    """Dark nose pad at the tip of the muzzle."""
    p, _n = surf.hit(L.h(0.8, 0, 0.02), L.F)
    mb.add(nh.ellipsoid(tuple(p), (size, size * 0.72, size * 0.72), subdivisions=2), col)


SPEC = q.Spec(
    name="BisonPriscus",
    leg_f=0.55, leg_h=0.52, length=0.92, girth=(0.26, 0.33), belly=1.05,
    hump=0.75, hump_y=-0.38,
    leg_r=(0.07, 0.065), leg_taper=0.55, foot="hoof", stride=0.12,
    neck_len=0.20, neck_angle=-5, neck_r=(0.26, 0.22),
    head_len=0.40, head_r=(0.15, 0.15), snout_r=(0.085, 0.085), head_pitch=55, cranium=1.1,
    eye_t=0.30, eye_u=0.30,
    ears="point", ear_size=0.05, mane=0.10, beard=0.10,
    tail_len=0.30, tail_r=0.03, tail_tuft=0.04, tail_droop=0.95,
    horns=[dict(t=0.12, s=sx * 0.30, u=0.32, len=0.30, r=0.035, dir=(sx * 1, 0.0, 0.3),
                bend=(-sx * 0.9, -0.2, 1.4), color=(0.18, 0.15, 0.12), surface=False) for sx in (-1, 1)],
    coat=(0.50, 0.36, 0.22), dark=(0.24, 0.16, 0.10), pale=(0.62, 0.48, 0.32),
    mane_col=(0.22, 0.15, 0.09),
    pattern=q.collar((0.25, 0.17, 0.10), -0.95, -0.15, amount=0.8),
    shag=0.02, voxel=0.018,
)

if __name__ == "__main__":
    q.main(SPEC)
