"""
Procedural giant beaver (Castoroides ohioensis, Pleistocene of North America)
for map colonies.

A beaver the size of a black bear, about 2 m long and up to 100 kg, one of the
largest rodents ever. It lived in lakes and swamps but probably did not fell
trees: its huge, ridged incisors (up to 15 cm) suited chewing tough water
plants. A heavy, low body, short legs, a small-eared head and a long, narrower
tail than a modern beaver's. Dense dark-brown fur, orange incisors.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/castoroides_ohioensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CastoroidesOhioensis.fbx
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


def flat_tail(b, L):
    s = L.s
    root = Vector((0, L.yh + s.girth[0] * 0.7, L.zh - s.girth[1] * 0.25))
    b.add(nh.tube([tuple(root), tuple(root + Vector((0, 0.28, -0.08))), tuple(root + Vector((0, 0.52, -0.14)))],
                  [0.07, 0.075, 0.03], sides=12, scale_xy=(1.5, 0.35)), (0.22, 0.17, 0.13))


SPEC = q.Spec(
    name="CastoroidesOhioensis",
    leg_f=0.18, leg_h=0.22, length=0.80, girth=(0.25, 0.27), belly=1.12,
    hump=0.15, hump_y=0.2,
    leg_r=(0.06, 0.08), leg_taper=0.75, foot="paw", foot_r=1.3, stride=0.08,
    neck_len=0.10, neck_angle=10, neck_r=(0.22, 0.19),
    head_len=0.34, head_r=(0.14, 0.14), snout_r=(0.085, 0.085), head_pitch=20, cranium=1.0,
    eye_t=0.40, eye_u=0.50,
    ears="round", ear_size=0.045,
    tail_len=0.0,
    tusks=[dict(t=1.0, s=sx * 0.04, u=-0.12, dir=(0, -0.4, -1), len=0.11, r=0.025, tip=0.018, bend=(0, 0.6, 0),
                flat=0.55, color=(0.85, 0.45, 0.12)) for sx in (-1, 1)],
    coat=(0.36, 0.24, 0.15), dark=(0.22, 0.14, 0.08), pale=(0.52, 0.40, 0.28),
    extra=flat_tail, extra_details=lambda mb, L, surf: nose(mb, L, surf, 0.026, (0.10, 0.07, 0.06)),
    shag=0.008, voxel=0.016,
)

if __name__ == "__main__":
    q.main(SPEC)
