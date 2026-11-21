"""
Procedural grey wolf (Canis lupus, Pleistocene to today across the northern
hemisphere) for map colonies.

The largest wild dog, about 1.0-1.5 m long plus the tail: long legs, a deep,
narrow chest, a long muzzle, tall pointed ears and a bushy, hanging tail.
Grizzled grey coat, darker along the back with a dark saddle, paler buff legs
and a cream throat and belly. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/canis_lupus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CanisLupus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402
import nh_model as nh  # noqa: E402


def nose(mb, L, surf):
    """Black nose pad at the tip of the muzzle."""
    p, _n = surf.hit(L.h(0.8, 0, 0.02), L.F)
    mb.add(nh.ellipsoid(tuple(p), (0.022, 0.016, 0.016), subdivisions=2), (0.05, 0.04, 0.04))

SPEC = q.Spec(
    name="CanisLupus",
    leg_f=0.52, leg_h=0.54, length=0.62, girth=(0.13, 0.19), belly=0.85,
    hump=0.12, hump_y=-0.40,
    leg_r=(0.045, 0.05), leg_taper=0.6, foot="paw", stride=0.14,
    neck_len=0.18, neck_angle=28, neck_r=(0.13, 0.13),
    head_len=0.27, head_r=(0.105, 0.095), snout_r=(0.03, 0.034), head_pitch=10, cranium=1.2, eye_t=0.40, eye_u=0.40,
    ears="point", ear_size=0.12, mane=0.04,
    tail_len=0.42, tail_r=0.065, tail_tuft=0.07, tail_droop=0.8,
    coat=(0.52, 0.49, 0.44), dark=(0.22, 0.20, 0.18), pale=(0.86, 0.82, 0.74),
    mane_col=(0.30, 0.28, 0.25),
    pattern=q.combine(q.lower_legs((0.72, 0.62, 0.48), z1=0.6, amount=0.7),
                      q.face((0.80, 0.76, 0.68), t0=0.75, amount=0.5)),
    extra_details=nose,
    shag=0.008, voxel=0.014,
)

if __name__ == "__main__":
    q.main(SPEC)
