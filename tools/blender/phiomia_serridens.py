"""
Procedural Phiomia serridens (North Africa, late Eocene - early Oligocene, ~37-30 Ma) for map
colonies. Built with nh_pal_quad.py.

An early proboscidean about 2.5 m long and 1.3 m at the shoulder, between Moeritherium and the
later gomphotheres: a tapir-like head with a short trunk, a pair of short upper tusks pointing
down and forward, and a long lower jaw ending in two flat, shovel-like lower tusks. Long body on
fairly long, pillar-like legs; small ears. Skin: grey-brown (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/phiomia_serridens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PhiomiaSerridens.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402

IVORY = (0.88, 0.84, 0.72)

SPEC = q.Spec(
    name="PhiomiaSerridens",
    length=1.0, shoulder=0.88, hip=0.82, width=0.22, depth=0.25, belly=1.05,
    fore_r=0.075, hind_r=0.085, shin=0.8, foot="pad", foot_r=0.075, hock=0.0, stride=0.08,
    neck_len=0.16, neck_angle=15, neck_r=0.16,
    head_len=0.4, head_w=0.4, head_h=0.42, snout=0.55, snout_r=(0.3, 0.2), snout_tilt=25, jaw=1.3, jaw_r=0.16,
    ear=0.2, ear_shape="round", ear_angle=40, eye=0.055, eye_pos=(0.33, -0.22, 0.12),
    tail_len=0.3, tail_r=0.035, tail_angle=-65, tail_tuft=0.03,
    horns=[
        # upper tusks: short, down and forward
        Horn(base=(0.17, -0.62, -0.3), direction=(0.1, -0.5, -1), length=0.3, radius=0.045, bend=0.4,
             bend_dir=(0, -1, 0), color=IVORY),
        # lower shovel tusks at the jaw tip
        Horn(base=(0.06, -0.88, -0.5), direction=(0.05, -1, 0.05), length=0.2, radius=0.05, flat=1.8,
             color=IVORY),
    ],
    coat=(0.42, 0.38, 0.34), back=(0.33, 0.30, 0.27), pale=(0.55, 0.50, 0.45), pale_amt=0.6, skin=0.6, fur=0.3,
    voxel=0.014, max_tris=14000, ground=(0.40, 0.42, 0.28),
)


def trunk(b, L):
    # a short trunk drooping from the snout tip, over the lower jaw
    p0 = L.h(*q.Vector(L.snout_pt(0.8)))
    tip = q.Vector(L.snout_pt(1.0))
    pts = [p0, L.h(tip.x, tip.y - 0.12, tip.z - 0.12), L.h(tip.x, tip.y - 0.16, tip.z - 0.42)]
    b.add(nh.tube(pts, [0.15 * SPEC.head_len, 0.12 * SPEC.head_len, 0.09 * SPEC.head_len], sides=12), SPEC.coat)


if __name__ == "__main__":
    q.main(SPEC, extra=trunk)
