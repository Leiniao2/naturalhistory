"""
Procedural South Island giant moa (Dinornis robustus, Pleistocene - Holocene of
New Zealand) for map colonies.

The tallest bird known: big females reached about 2 m at the back and could
raise their heads to 3.6 m, though the neck was usually carried forward. A
bulky, rounded body with no wings at all (not even vestigial wing bones),
very thick, powerful legs, a long neck and a small head with a short, blunt,
slightly down-curved bill. Shaggy, hair-like reddish-brown feathers
(known from preserved plumage). Built with nh_neo_bigbird.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/dinornis_robustus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DinornisRobustus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_bigbird as q  # noqa: E402

SPEC = q.Spec(
    name="DinornisRobustus",
    hip=1.00, body=(0.34, 0.50, 0.40), body_tilt=5, leg_r=0.085,
    neck=((0, -0.40, 0.30), (0, -0.55, 0.70), (0, -0.66, 1.00)), neck_r=(0.15, 0.09, 0.065),
    head_r=0.07, beak_len=0.12, beak_h=0.07, hook=0.25, wing=0.0, tail=0.12,
    feather=(0.45, 0.30, 0.18), dark=(0.28, 0.18, 0.10), pale=(0.58, 0.44, 0.30),
    beak_col=(0.62, 0.56, 0.42), leg_col=(0.45, 0.40, 0.30), eye_col=(0.12, 0.08, 0.05), stride=0.28, shag=0.025,
)

if __name__ == "__main__":
    q.main(SPEC)
