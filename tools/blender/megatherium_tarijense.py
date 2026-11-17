"""
Procedural Megatherium tarijense (Pleistocene ground sloth of Tarija, Bolivia) for
map colonies.

A smaller relative of M. americanum, described from the Pleistocene deposits of the
Tarija valley in southern Bolivia; remains referred to it come from the Andean
region. It is known from far less material than M. americanum, so this is a
deliberately conservative variation on the same recipe (nh_megatherium.py) rather
than a reconstruction of its own: the same small, narrow, long-snouted head, pear-
shaped body, short massive hind legs, thick tail and long forelimbs walking on the
outer edges of the hands with the big curved claws folded in. What differs (and is
partly guesswork) is the build: a slimmer, less barrel-shaped trunk, narrower
hips, slimmer hind legs and tail, slightly longer forelimbs and a proportionally
smaller head, so it reads as the lighter animal next to M. americanum; the much
smaller body size itself comes from species.json sizeCm. The coat is drawn a little
longer and a cooler, greyer brown for the highland setting; hair colour and length
are not known from fossils.

Usage:
  blender --background --python tools/blender/megatherium_tarijense.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MegatheriumTarijense.fbx
Faces -Y, pivot on the ground. About 2 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_megatherium as meg  # noqa: E402

SPEC = meg.MegatheriumSpec(
    name="MegatheriumTarijense",
    voxel=0.012, max_tris=18000,
    bulk=0.86, hip_w=0.97, fore_len=1.06, hind_thick=0.9,
    head_k=0.84, snout_len=1.25, tail_k=0.85, hair_len=1.15, claw_k=0.95,
    coat=(0.34, 0.27, 0.19), coat_tip=(0.54, 0.46, 0.34), underfur=(0.18, 0.14, 0.10),
    face=(0.26, 0.21, 0.16),
)


def build():
    return meg.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "MegatheriumTarijense", ground=(0.50, 0.48, 0.34),
           views=((35, 20), (-90, 6), (0, 8), (20, 60)))
