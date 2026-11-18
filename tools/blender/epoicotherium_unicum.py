"""
Procedural Epoicotherium unicum (North America, early Oligocene, ~33-30 Ma) for map colonies. Built with nh_pal_quad.py.

A palaeanodont, a small (about 20 cm) burrowing mammal from the stem of the
pangolins, built like a golden mole: a low, cylindrical body, a pointed,
shovel-like snout, tiny eyes, no external ears, short powerful forelimbs with
huge digging claws, and a short tail. It tunnelled through loose sand and ate
ants, termites and grubs. Coat: sandy grey-brown, velvety (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/epoicotherium_unicum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EpoicotheriumUnicum.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_pal_quad as q  # noqa: E402
from mathutils import Vector  # noqa: E402

CLAW = (0.82, 0.76, 0.62)

SPEC = q.Spec(
    name="EpoicotheriumUnicum",
    length=0.72, shoulder=0.42, hip=0.42, width=0.19, depth=0.18, belly=1.05,
    fore_r=0.07, hind_r=0.06, shin=0.75, foot="hand", foot_r=0.06, toes=3, hock=0.0, stride=0.05,
    neck_len=0.1, neck_angle=0, neck_r=0.15,
    head_len=0.3, head_w=0.48, head_h=0.38, snout=0.9, snout_r=(0.3, 0.1), snout_tilt=12,
    jaw=0.6, jaw_r=0.12, ear=0.0, eye=0.03, eye_pos=(0.34, -0.25, 0.12), nose_col=(0.55, 0.38, 0.33),
    tail_len=0.18, tail_r=0.04, tail_angle=-25,
    coat=(0.60, 0.53, 0.42), back=(0.48, 0.42, 0.33), pale=(0.74, 0.68, 0.56), pale_amt=0.6,
    voxel=0.01, max_tris=9000, ground=(0.62, 0.55, 0.40),
)


def claws(mb, L, surf):
    """Big curved digging claws on the forefeet, small ones on the hind feet."""
    s = L.s
    for x, front, st in ((-s.width * 0.78, True, -s.stride), (s.width * 0.78, True, s.stride),
                         (-s.width * 0.82, False, s.stride), (s.width * 0.82, False, -s.stride)):
        y = (L.sh.y - 0.02 + st) if front else (L.hp.y + 0.03 + st)
        fr = s.foot_r
        n, size = (3, 1.0) if front else (3, 0.45)
        for i in range(n):
            a = (i / (n - 1) - 0.5) * 0.9
            root = Vector((x * 1.02 + math.sin(a) * fr * 0.8, y - fr * 1.3, fr * 0.45))
            d = Vector((math.sin(a) * 0.3, -1, -0.35)).normalized()
            tip = root + d * 0.09 * size + Vector((0, 0, -0.03 * size))
            mid = root.lerp(tip, 0.5) + Vector((0, -0.01, 0.015 * size))
            mb.add(nh.tube([tuple(root), tuple(mid), tuple(tip)], [0.018 * size, 0.012 * size, 0.0], sides=6), CLAW)


if __name__ == "__main__":
    q.main(SPEC, more=claws)
