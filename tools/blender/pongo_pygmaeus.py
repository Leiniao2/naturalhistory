"""
Procedural Bornean orangutan (Pongo pygmaeus, Pleistocene to today; orangutans
once ranged across mainland Southeast Asia and southern China) for map colonies.

The largest tree-living animal, adult males about 1.4 m tall and 80-100 kg:
extremely long arms (spanning over 2 m), short bowed legs, no tail, a bulging
belly and long, shaggy orange-red hair. Shown on all fours with fists curled,
and the grey face of a flanged male framed by broad cheek pads and a throat sac.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pongo_pygmaeus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PongoPygmaeus.fbx
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


def flanges(b, L):
    s = L.s
    HL = s.head_len
    for sx in (-1, 1):
        b.add(nh.ellipsoid(L.h(0.40, sx * 0.52, 0.0), (0.022, 0.045, 0.065)), s.skin)
    b.add(nh.ellipsoid(L.h(0.50, 0, -0.50), (0.08, 0.07, 0.06)), s.coat)  # throat sac


SPEC = q.Spec(
    name="PongoPygmaeus",
    leg_f=0.62, leg_h=0.34, length=0.40, girth=(0.20, 0.22), belly=1.2,
    leg_r=(0.055, 0.06), leg_taper=0.65, foot="knuckle", stride=0.12,
    neck_len=0.08, neck_angle=30, neck_r=(0.14, 0.12),
    head_len=0.22, head_r=(0.11, 0.11), snout_r=(0.075, 0.07), head_pitch=0, cranium=1.1, eye_t=0.48, eye_u=0.30,
    ears="none",
    tail_len=0.0,
    coat=(0.70, 0.32, 0.10), dark=(0.50, 0.20, 0.06), pale=(0.78, 0.42, 0.16), skin=(0.36, 0.32, 0.30),
    pattern=q.face((0.36, 0.32, 0.30), 0.45),
    extra=flanges,
    shag=0.02, voxel=0.012, max_tris=9000,
)

if __name__ == "__main__":
    q.main(SPEC)
