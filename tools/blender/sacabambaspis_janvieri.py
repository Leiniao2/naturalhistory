"""
Procedural Sacabambaspis janvieri (Middle Ordovician arandaspid, Anzaldo Formation,
Bolivia; about 25-35 cm long) for map colonies (Swim style).

A jawless armoured fish: a deep, rounded head armour of a big oval dorsal and ventral
shield joined at the sides by a row of many small, narrow branchial plates; tiny eyes
set at the very front of the head and facing forward like headlights, with a pair of
pineal openings between them; a small terminal mouth; a slender body covered in long,
narrow scales; and a tail of an upper and a lower web with a long median lobe between
them. No paired fins. Built with nh_ord_agnathan.py (colour conjectural).

Usage:
  blender --background --python tools/blender/sacabambaspis_janvieri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SacabambaspisJanvieri.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_agnathan as ag  # noqa: E402

SPEC = ag.Spec(
    name="SacabambaspisJanvieri",
    rows=((-0.80, 0.02, 0.02, 0.02, 0.0), (-0.76, 0.10, 0.08, 0.06, 0.0), (-0.64, 0.16, 0.13, 0.10, 0.0),
          (-0.42, 0.18, 0.155, 0.12, 0.0), (-0.16, 0.16, 0.14, 0.11, 0.0), (0.08, 0.11, 0.10, 0.08, 0.0),
          (0.36, 0.065, 0.065, 0.05, 0.0), (0.56, 0.032, 0.035, 0.028, 0.0), (0.72, 0.012, 0.014, 0.012, 0.0)),
    shield_end=-0.05, suture_z=-0.02, trunk_end=0.62, tail="arandaspid", tail_len=0.42, tail_h=0.13,
    eye_y=-0.765, eye_a=0.35, eye_r=0.018, eye_look=(0.35, -1.0, 0.15), pineal=True,
    gills=16, gill_y=(-0.40, -0.08), gill_a=-0.12, branchial_plates=True, tubercles="dots",
    shield=(0.56, 0.50, 0.42), shield_dark=(0.30, 0.26, 0.21), tubercle=(0.82, 0.78, 0.68),
    back=(0.34, 0.30, 0.25), flank=(0.50, 0.45, 0.37), belly=(0.74, 0.70, 0.60),
)

if __name__ == "__main__":
    nh.run(lambda: ag.build_ostracoderm(SPEC), SPEC.name, **ag.PREVIEW)
