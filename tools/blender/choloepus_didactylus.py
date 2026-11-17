"""
Procedural Linnaeus's two-toed sloth (Choloepus didactylus) for map colonies.

A tree sloth of the rainforests of northern South America, larger and a little
more active than the three-toed sloths and not closely related to them (the two
groups evolved tree-hanging habits separately). Shown crawling on the ground the
way sloths move between trees: belly low, the long arms splayed and reaching forward
with two long hooked claws on each hand (three on the feet), the hind legs splayed
behind and the head held up. Built with the shared tree sloth recipe
(nh_tree_sloth.py) and set apart from the three-toed sloth by a longer, more
pointed muzzle with a big bare nose, a slightly larger head, no visible tail, two
claws on the forelimbs and arms only a little longer than the legs.

Long, shaggy buff-to-tan coat with darker brown limbs and paler, creamy fur on
the face, no eye stripe, bare dark nose. Crisp claws and eyes on top.

Usage:
  blender --background --python tools/blender/choloepus_didactylus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TwoToedSloth.fbx
Faces -Y, pivot on the ground. About 1.3 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tree_sloth as ts  # noqa: E402

SPEC = ts.TreeSlothSpec(
    name="TwoToedSloth",
    voxel=0.009, max_tris=3800,
    head_r=0.095, snout_len=0.065, snout_r=0.040, neck_len=0.10, arm_len=1.0,
    fore_claws=2, hind_claws=3, claw_len=0.11, tail=0.0, hair_len=0.028,
    coat=(0.60, 0.48, 0.33), coat_tip=(0.76, 0.66, 0.50), underfur=(0.33, 0.25, 0.16),
    algae_k=0.0, limbs=(0.42, 0.31, 0.20),
    face=(0.74, 0.64, 0.49), mask=None, throat=None,
)


def build():
    return ts.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "TwoToedSloth", ground=(0.36, 0.44, 0.26),
           views=((35, 20), (-90, 6), (0, 12), (20, 60)))
