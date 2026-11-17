"""
Procedural Arandaspis prionotolepis (Early-Middle Ordovician arandaspid, Stairway
Sandstone, Northern Territory, Australia; about 15 cm long), one of the oldest known
vertebrates with a bony armour, for map colonies (Swim style).

A small, flattened jawless fish: a dorsal and a ventral head shield with fine ridged
ornament, joined at the sides by a row of narrow branchial plates; tiny eyes at the
front of the head with a pair of pineal openings between them; no paired fins; a body of
long, narrow, ridged scales (its name means "saw-edged scales") and a simple tail.
Grey-brown (colour conjectural). Built with nh_ord_agnathan.py.

Usage:
  blender --background --python tools/blender/arandaspis_prionotolepis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArandaspisPrionotolepis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_agnathan as ag  # noqa: E402

SPEC = ag.Spec(
    name="ArandaspisPrionotolepis",
    rows=((-0.80, 0.02, 0.012, 0.012, 0.0), (-0.75, 0.10, 0.045, 0.035, 0.0), (-0.60, 0.16, 0.075, 0.055, 0.0),
          (-0.36, 0.175, 0.085, 0.06, 0.0), (-0.12, 0.15, 0.08, 0.055, 0.0), (0.12, 0.10, 0.07, 0.05, 0.0),
          (0.38, 0.06, 0.05, 0.04, 0.0), (0.58, 0.03, 0.03, 0.025, 0.0), (0.74, 0.01, 0.012, 0.01, 0.0)),
    power=2.6, shield_end=-0.10, suture_z=-0.012, trunk_end=0.64, tail="hypocercal", tail_len=0.36, tail_h=0.12,
    eye_y=-0.73, eye_a=0.55, eye_r=0.016, eye_look=(0.5, -0.8, 0.4), pineal=True,
    gills=12, gill_y=(-0.44, -0.14), gill_a=-0.08, branchial_plates=True, tubercles="ridges",
    shield=(0.46, 0.42, 0.38), shield_dark=(0.24, 0.22, 0.20), tubercle=(0.70, 0.66, 0.60),
    back=(0.28, 0.26, 0.24), flank=(0.44, 0.41, 0.37), belly=(0.68, 0.65, 0.58),
)

if __name__ == "__main__":
    nh.run(lambda: ag.build_ostracoderm(SPEC), SPEC.name, **ag.PREVIEW)
