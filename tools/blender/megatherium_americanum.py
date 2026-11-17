"""
Procedural Megatherium americanum (giant ground sloth, Pleistocene South America)
for map colonies.

The largest of the ground sloths, about 6 m long and as heavy as an elephant, from
the Pleistocene pampas and open country of South America. Built with the shared
Megatherium recipe (nh_megatherium.py): a small, narrow, long-snouted head on a short
neck, a pear-shaped body swelling into an enormous pelvis and short, massive hind
legs, a thick muscular tail, and long forelimbs walking on the outer edges of the
hands with the big curved claws folded in under them; the hind feet also stand on
their outer edges with the great middle claw curled inward. This species gets the
bulkiest barrel, broadest hips and thickest tail of the two. Shaggy brown coat with
paler tips (hair colour and length are a guess), bare grey skin on the lips, nose
and soles; horn-coloured claws, small dark eyes and nostrils as crisp details.

Usage:
  blender --background --python tools/blender/megatherium_americanum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MegatheriumAmericanum.fbx
Faces -Y, pivot on the ground. About 2 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_megatherium as meg  # noqa: E402

SPEC = meg.MegatheriumSpec(
    name="MegatheriumAmericanum",
    voxel=0.012, max_tris=20000,
    bulk=1.0, hip_w=1.06, fore_len=1.0, hind_thick=1.05,
    head_k=0.88, snout_len=1.25, tail_k=1.05, hair_len=1.0, claw_k=1.0,
    coat=(0.33, 0.23, 0.14), coat_tip=(0.50, 0.38, 0.24), underfur=(0.17, 0.11, 0.07),
    face=(0.24, 0.18, 0.12),
)


def build():
    return meg.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "MegatheriumAmericanum", ground=(0.52, 0.48, 0.30),
           views=((35, 20), (-90, 6), (0, 8), (20, 60)))
