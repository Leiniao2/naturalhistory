"""
Procedural Eurotamandua joresi (Messel, Germany, middle Eocene, ~47 Ma) for map colonies. Built with nh_pal_quad.py.

An anteater-like mammal about 90 cm long including its long, muscular, probably prehensile
tail. Long tubular snout with no teeth, small ears, short powerful forelimbs with a huge
curved digging claw on each hand for tearing open ant and termite nests, and no scales
(it is now thought to be a relative of pangolins, not of true anteaters). Coat: tamandua-like
buff with a darker saddle (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/eurotamandua_joresi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EurotamanduaJoresi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401
from mathutils import Vector  # noqa: E402,F401

CLAW = (0.25, 0.22, 0.18)

SPEC = q.Spec(
    name="EurotamanduaJoresi",
    length=0.6, shoulder=0.36, hip=0.38, width=0.1, depth=0.12, arch=0.02,
    fore_r=0.045, hind_r=0.05, shin=0.7, foot="paw", foot_r=0.04, toes=3, hock=0.2, stride=0.06,
    neck_len=0.14, neck_angle=10, neck_r=0.07,
    head_len=0.2, head_w=0.32, head_h=0.32, snout=1.7, snout_r=(0.2, 0.08), snout_tilt=12, jaw=0.0,
    ear=0.14, ear_shape="round", ear_angle=30, eye=0.06, eye_pos=(0.28, -0.22, 0.1), nose_col=(0.1, 0.08, 0.07),
    tail_len=0.75, tail_r=0.07, tail_angle=-15, tail_curl=-70,
    coat=(0.70, 0.60, 0.42), back=(0.22, 0.18, 0.15), pale=(0.80, 0.72, 0.56), pale_amt=0.5, dark_legs=0.2,
    voxel=0.009, max_tris=11000, ground=(0.32, 0.40, 0.24),
)


def claws(mb, L, surf):
    # one big hooked claw (and a smaller one) on each forefoot
    s = SPEC
    w = s.width * 0.78
    for x, st in ((-w, -s.stride), (w, s.stride)):
        foot = Vector((x * 1.02, L.sh.y - 0.02 + st, 0))
        for dx, size in ((0.0, 1.0), (0.018 * (1 if x > 0 else -1), 0.6)):
            p0 = foot + Vector((dx, -s.foot_r * 0.9, s.foot_r * 0.6))
            pts = [p0, p0 + Vector((0, -0.04 * size, -0.005)), p0 + Vector((0, -0.065 * size, -0.03 * size))]
            mb.add(nh.tube([tuple(p) for p in pts], [0.012 * size, 0.008 * size, 0.0], sides=6), CLAW)


if __name__ == "__main__":
    q.main(SPEC, more=claws)
