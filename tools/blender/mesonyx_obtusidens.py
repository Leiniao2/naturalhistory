"""
Procedural Mesonyx obtusidens (Wyoming and Utah, middle Eocene, ~49-43 Ma) for map colonies. Built with nh_pal_quad.py.

A mesonychid, one of an extinct group of wolf-like, meat-eating hoofed mammals: about
1.5 m long, with a large head and long jaws whose blunt, heavy cheek teeth crushed bone and
meat, a slim, long-legged body built for running, a long tail, and toes ending in small
blunt hoof-like nails instead of claws. It hunted and scavenged on the open woodland floor.
Coat: grey-brown with faint dark bands (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/mesonyx_obtusidens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MesonyxObtusidens.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401
from mathutils import Vector  # noqa: E402,F401

SPEC = q.Spec(
    name="MesonyxObtusidens",
    length=0.78, shoulder=0.62, hip=0.62, width=0.13, depth=0.165,
    fore_r=0.055, hind_r=0.066, shin=0.6, foot="paw", foot_r=0.035, toes=4, hock=0.7, stride=0.1,
    neck_len=0.22, neck_angle=28, neck_r=0.085,
    head_len=0.32, head_w=0.36, head_h=0.36, snout=1.0, snout_r=(0.24, 0.15), snout_tilt=10, jaw=0.9, jaw_r=0.16,
    ear=0.24, ear_angle=15, eye=0.06, eye_pos=(0.3, -0.25, 0.14), nose_col=(0.1, 0.08, 0.07),
    tail_len=0.65, tail_r=0.05, tail_angle=-30, tail_curl=10,
    horns=[Horn(base=(0.09, -1.05, -0.24), direction=(0, -0.1, -1), length=0.1, radius=0.025, color=(0.9, 0.86, 0.75))],
    coat=(0.48, 0.42, 0.34), back=(0.32, 0.28, 0.23), pale=(0.75, 0.70, 0.60), pale_amt=0.7,
    stripes=7, stripe_col=(0.26, 0.22, 0.18), stripe_amt=0.35, dark_legs=0.4,
    voxel=0.011, max_tris=12000, ground=(0.45, 0.45, 0.32),
)


def nails(mb, L, surf):
    # small blunt hoof-like nails at the toe tips
    s = SPEC
    w = s.width * 0.78
    for x, st, front in ((-w, -s.stride, True), (w, s.stride, True), (-w * 1.05, s.stride, False), (w * 1.05, -s.stride, False)):
        foot = Vector((x * 1.02, (L.sh.y - 0.02 if front else L.hp.y + 0.03) + st, 0))
        fr = s.foot_r * (1.0 if front else 1.05)
        for i in range(4):
            a = (i / 3 - 0.5) * 1.5
            import math
            t = foot + Vector((math.sin(a) * fr * 0.85, -fr * 1.15 * 0.95 - math.cos(a) * fr * 0.25 - fr * 0.25, fr * 0.22))
            mb.add(nh.ellipsoid(tuple(t), (fr * 0.22, fr * 0.2, fr * 0.2), subdivisions=1), q.HOOF)


if __name__ == "__main__":
    q.main(SPEC, more=nails)
