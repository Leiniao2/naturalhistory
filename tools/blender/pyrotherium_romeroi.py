"""
Procedural Pyrotherium romeroi (Patagonia and Bolivia, late Oligocene, ~29-24 Ma) for map colonies. Built with nh_pal_quad.py.

A large South American hoofed mammal about 3 m long, an elephant look-alike from an
unrelated, now extinct lineage (the pyrotheres). Heavy barrel body on pillar-like legs, a
short trunk, and two pairs of forward-pointing, flattened incisor tusks (two above, two
below) used to strip and cut tough plants; its cheek teeth had sharp cross-crests. Skin:
grey (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pyrotherium_romeroi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PyrotheriumRomeroi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401
from mathutils import Vector  # noqa: E402,F401

IVORY = (0.86, 0.82, 0.70)

SPEC = q.Spec(
    name="PyrotheriumRomeroi",
    length=1.05, shoulder=0.9, hip=0.86, width=0.27, depth=0.29, belly=1.12,
    fore_r=0.09, hind_r=0.1, shin=0.85, foot="pad", foot_r=0.09, hock=0.0, stride=0.07,
    neck_len=0.14, neck_angle=12, neck_r=0.18,
    head_len=0.42, head_w=0.4, head_h=0.42, snout=0.45, snout_r=(0.3, 0.22), snout_tilt=22, jaw=1.0, jaw_r=0.18,
    ear=0.14, ear_shape="round", ear_angle=40, eye=0.05, eye_pos=(0.34, -0.2, 0.14),
    tail_len=0.25, tail_r=0.035, tail_angle=-65, tail_tuft=0.03,
    horns=[
        Horn(base=(0.08, -0.72, -0.3), direction=(0.04, -1, -0.25), length=0.34, radius=0.045, flat=1.4, color=IVORY),
        Horn(base=(0.06, -0.72, -0.5), direction=(0.04, -1, 0.2), length=0.28, radius=0.04, flat=1.4, color=IVORY),
    ],
    coat=(0.48, 0.46, 0.43), back=(0.38, 0.36, 0.34), pale=(0.58, 0.55, 0.51), pale_amt=0.6, skin=0.7, fur=0.3,
    voxel=0.015, max_tris=15000, ground=(0.50, 0.47, 0.32),
)


def trunk(b, L):
    k = SPEC.head_len
    p0 = L.h(*Vector(L.snout_pt(0.7)))
    tip = Vector(L.snout_pt(1.0))
    pts = [p0, L.h(tip.x, tip.y - 0.1, tip.z + 0.02), L.h(tip.x, tip.y - 0.16, tip.z - 0.15)]
    b.add(nh.tube(pts, [0.17 * k, 0.13 * k, 0.1 * k], sides=12), SPEC.coat)


if __name__ == "__main__":
    q.main(SPEC, extra=trunk)
