"""
Procedural Argentavis magnificens (Late Miocene of Argentina) for map colonies:
a teratorn, one of the largest flying birds ever, with a wingspan estimated at
about 6-7 m and a weight of some 70 kg.

Shown soaring with broad, plank-like wings spread flat, the long primaries
splayed into "fingers" at the tips like a condor's, a short wedge tail, a
stout neck and a large head with a strong, hooked bill. Dark brown-black
plumage with paler underwing coverts and a bare greyish head (plumage is a
reconstruction choice). Built with nh_neo_soar.py.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/argentavis_magnificens.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArgentavisMagnificens.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_soar as q  # noqa: E402

SPEC = q.Spec(
    name="ArgentavisMagnificens",
    span=3.4, chord=0.62, tip_chord=0.42, fingers=7, finger_len=0.34,
    body=(0.16, 0.42, 0.15), neck_len=0.16, head_r=0.075, beak_len=0.15, beak_r=0.04, hook=0.8,
    tail=0.26, tail_w=0.2,
    plumage=(0.13, 0.10, 0.08), under=(0.36, 0.32, 0.27), head_col=(0.55, 0.50, 0.46), beak_col=(0.75, 0.70, 0.58),
)

if __name__ == "__main__":
    q.main(SPEC)
