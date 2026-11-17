"""
Procedural pale-throated three-toed sloth (Bradypus tridactylus) for map colonies.

A small, slow tree sloth of the rainforests of northern Amazonia and the Guianas,
shown crawling on the ground the way sloths move between trees: belly low, the long
arms splayed out and reaching forward with three long hooked claws on each hand, the
shorter hind legs (also three-clawed) behind, and the small round head held up on
its neck. Built with the shared tree sloth recipe (nh_tree_sloth.py) and set apart
from the two-toed sloth by a short, blunt muzzle on a round, flat face, a stubby
tail, three claws on the forelimbs and arms clearly longer than the legs.

Shaggy coarse greyish-brown coat with a greenish algal tinge along the back, darker
brown limbs, a pale cream face with the dark stripe running back from each eye, a
pale yellowish throat (the feature that tells this species from the brown-throated
sloth), bare dark nose. Males also carry an orange-and-black patch between the
shoulders (the speculum); this model shows a generic adult without it. Crisp claws,
eyes on top.

Usage:
  blender --background --python tools/blender/bradypus_tridactylus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ThreeToedSloth.fbx
Faces -Y, pivot on the ground. About 1.3 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tree_sloth as ts  # noqa: E402

SPEC = ts.TreeSlothSpec(
    name="ThreeToedSloth",
    voxel=0.009, max_tris=3800,
    head_r=0.09, snout_len=0.012, snout_r=0.040, neck_len=0.12, arm_len=1.12,
    fore_claws=3, hind_claws=3, claw_len=0.11, tail=0.06, hair_len=0.024,
    coat=(0.47, 0.42, 0.35), coat_tip=(0.64, 0.60, 0.52), underfur=(0.24, 0.21, 0.17),
    algae=(0.42, 0.47, 0.32), algae_k=0.55, limbs=(0.38, 0.33, 0.27),
    face=(0.78, 0.74, 0.62), mask=(0.12, 0.09, 0.07), throat=(0.86, 0.80, 0.60),
)


def build():
    return ts.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "ThreeToedSloth", ground=(0.36, 0.44, 0.26),
           views=((35, 20), (-90, 6), (0, 12), (20, 60)))
