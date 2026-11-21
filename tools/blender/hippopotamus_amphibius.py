"""
Procedural common hippopotamus (Hippopotamus amphibius, Pleistocene to today;
Africa, and during warm Ice Age spells as far north as Britain) for map colonies.

A barrel-bodied, short-legged giant about 3.5-5 m long and 1.5-3 tonnes, the
closest living relative of whales: a vast, wide muzzle with big tusk-like canines,
eyes, ears and nostrils set high on the head so they stay above the water, and a
short flat tail. Almost hairless grey-brown skin flushed pink around the eyes,
ears, face and belly.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/hippopotamus_amphibius.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HippopotamusAmphibius.fbx
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


def hippo_extra(b, L):
    """Bulbous upper-lip pads and raised eye turrets on the top of the head."""
    s = L.s
    HL = s.head_len
    for sx in (-1, 1):
        b.add(nh.ellipsoid(L.h(0.85, sx * 0.20, -0.03), (0.09, 0.09, 0.09)), s.coat)
        b.add(nh.ellipsoid(L.h(0.36, sx * s.head_r[0] / HL * 0.55, s.head_r[1] / HL * 0.75), (0.05, 0.05, 0.04)), s.coat)
        b.add(nh.ellipsoid(L.h(0.98, sx * 0.08, 0.13), (0.03, 0.025, 0.025)), s.coat)   # nostril bumps


def hippo_details(mb, L, surf):
    for sx in (-1, 1):
        root = Vector(L.h(0.86, sx * 0.13, -0.16))
        mb.add(q.bent_tube(root, (sx * 0.15, -0.3, 1), 0.10, 0.022, bend=(0, -0.4, 0), tip_r=0.006), q.IVORY)


def pink(co, n, c, s):
    L = q.Layout(s)
    d = Vector(co) - L.hb
    t = d.dot(L.F) / s.head_len
    k = 0.0
    if t > 0.25 and (d - L.F * d.dot(L.F)).length < s.head_r[1] * 2.2:
        k = 0.22 * nh.smoothstep(0.25, 0.9, t)
    k = max(k, 0.55 * nh.smoothstep(-0.3, -0.8, n.z))
    return nh.lerp(c, (0.78, 0.50, 0.45), k)


SPEC = q.Spec(
    name="HippopotamusAmphibius",
    leg_f=0.22, leg_h=0.22, length=1.00, girth=(0.36, 0.36), belly=1.15,
    leg_r=(0.10, 0.11), leg_taper=0.85, foot="pillar", foot_r=1.0, stride=0.07,
    neck_len=0.12, neck_angle=8, neck_r=(0.32, 0.28),
    head_len=0.50, head_r=(0.22, 0.20), snout_r=(0.20, 0.15), head_pitch=18, cranium=1.0, jaw=1.3,
    eye_t=0.36, eye_u=0.95,
    ears="round", ear_size=0.05,
    tail_len=0.14, tail_r=0.04, tail_droop=0.8,
    coat=(0.44, 0.38, 0.38), dark=(0.30, 0.26, 0.27), pale=(0.70, 0.55, 0.50), countershade=0.5,
    pattern=pink, extra=hippo_extra, extra_details=hippo_details,
    shag=0.0, voxel=0.022,
)

if __name__ == "__main__":
    q.main(SPEC)
