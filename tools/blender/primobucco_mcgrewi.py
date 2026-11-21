"""
Procedural Primobucco mcgrewi (early Eocene, ~52 Ma, Green River lakes of Wyoming) for map
colonies. Built with nh_neo_soar.py.

An early roller (Coraciiformes), a small bird about 15-20 cm long with a stout, slightly
hooked bill, a large head, broad rounded wings and a fairly long square tail, shown in
flight. Pollen in the stomach of one fossil shows it hunted among flowering trees.
Colours (unknown) after living rollers: turquoise-blue wings,
a green-tinged head, buff-lilac breast.
Faces -Y, pivot at the body centre (flier).

Usage:
  blender --background --python tools/blender/primobucco_mcgrewi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PrimobuccoMcgrewi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_soar as ns  # noqa: E402

SPEC = ns.Spec(
    name="PrimobuccoMcgrewi",
    span=1.3, chord=0.30, tip_chord=0.22, fingers=0,
    body=(0.10, 0.24, 0.10), neck_len=0.05, head_r=0.085,
    beak_len=0.10, beak_r=0.032, hook=0.5,
    tail=0.30, tail_w=0.09,
    plumage=(0.74, 0.55, 0.52), under=(0.78, 0.66, 0.62),
    wing_top=(0.10, 0.48, 0.62), head_col=(0.38, 0.58, 0.46), beak_col=(0.12, 0.11, 0.10),
    voxel=0.008, max_tris=5000,
)

if __name__ == "__main__":
    ns.main(SPEC)
