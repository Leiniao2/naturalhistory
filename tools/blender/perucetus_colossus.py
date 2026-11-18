"""
Procedural Perucetus colossus (Peru, middle Eocene, ~39 Ma) for map colonies:
a gigantic basilosaurid whale about 17-20 m long, maybe the heaviest animal ever.

Its bones were hugely thickened and dense (pachyostosis), ballast for a slow life
in shallow coastal water. Shown as a fat, bloated, manatee-like whale with a
small head, short flippers, tiny hind legs and a tail fluke (its skull is unknown,
so the head is a guess from its relatives). Grey-brown back, paler belly.
Built with nh_pal_whale.py. Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/perucetus_colossus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PerucetusColossus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_whale as w  # noqa: E402

SPEC = w.Spec(
    name="PerucetusColossus",
    length=2.2, flat=1.05, head_end=0.12, teeth=6, tooth_len=0.018,
    profile=((0.0, 0.02), (0.05, 0.06), (0.11, 0.11), (0.2, 0.22), (0.38, 0.3), (0.58, 0.27), (0.78, 0.15),
             (0.92, 0.06), (1.0, 0.03)),
    flipper=(0.22, 0.2, 0.07), hind=(0.66, 0.05, 0.015), fluke=0.26, sag=0.02,
    back=(0.30, 0.28, 0.26), belly=(0.68, 0.64, 0.58), mid=(0.46, 0.43, 0.39), pattern=0.25, eye_r=0.014,
    voxel=0.013, max_tris=13000,
)

if __name__ == "__main__":
    w.main(SPEC)
