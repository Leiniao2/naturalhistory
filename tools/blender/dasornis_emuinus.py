"""
Procedural Dasornis emuinus (southern England, early Eocene, ~54-50 Ma) for map colonies:
a giant pelagornithid ("bony-toothed bird"), with a wingspan of perhaps 4-5 m.

A long-winged ocean glider like a huge albatross: very long, narrow wings, a
short tail and a long, stout bill lined with sharp bony spikes (pseudo-teeth)
for gripping slippery fish and squid. Shown with a dark grey-brown back and
wings, a pale head and underside and a yellowish bill (a reconstruction choice).
Built with nh_neo_soar.py. Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/dasornis_emuinus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DasornisEmuinus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_soar as q  # noqa: E402

SPEC = q.Spec(
    name="DasornisEmuinus",
    span=3.8, chord=0.36, tip_chord=0.15, fingers=0, finger_len=0.0,
    body=(0.14, 0.40, 0.13), neck_len=0.2, head_r=0.07, beak_len=0.40, beak_r=0.042, hook=0.4, teeth=11,
    tail=0.15, tail_w=0.12,
    plumage=(0.82, 0.80, 0.76), under=(0.90, 0.89, 0.86), wing_top=(0.28, 0.25, 0.22),
    head_col=(0.88, 0.87, 0.84), beak_col=(0.80, 0.66, 0.38),
)

if __name__ == "__main__":
    q.main(SPEC)
