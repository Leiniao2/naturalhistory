"""
Procedural Pelagornis chilensis (Late Miocene of Chile) for map colonies: a
pelagornithid or "bony-toothed" bird, a giant seabird with a wingspan of
about 5.2 m.

Shown gliding on very long, narrow, albatross-like wings, with a short tail, a
slender neck and a long, straight bill lined with sharp bony spikes
(pseudo-teeth, outgrowths of the jaw bones rather than true teeth) for
gripping slippery fish and squid. White body and head, grey-black upper wings
(an albatross-like reconstruction choice). Built with nh_neo_soar.py.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/pelagornis_chilensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PelagornisChilensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_soar as q  # noqa: E402

SPEC = q.Spec(
    name="PelagornisChilensis",
    span=4.0, chord=0.34, tip_chord=0.16, fingers=0, finger_len=0.0,
    body=(0.13, 0.40, 0.12), neck_len=0.18, head_r=0.065, beak_len=0.36, beak_r=0.035, hook=0.35, teeth=9,
    tail=0.16, tail_w=0.12,
    plumage=(0.86, 0.86, 0.84), under=(0.92, 0.92, 0.90), wing_top=(0.22, 0.22, 0.24),
    beak_col=(0.82, 0.74, 0.55),
)

if __name__ == "__main__":
    q.main(SPEC)
