"""
Procedural Eriptychius americanus Denison, 1967 (Late Ordovician jawless armoured fish from the
Harding Sandstone of Colorado) for map colonies (Swim style).

One of the oldest armoured vertebrates, about 15-20 cm long. Its head was covered by a solid
shield built of many small bony plates (tesserae) each carved with fine, elongate ridges, and
under it lay one of the oldest known cartilage braincases. Known from the front of the head
shield and scattered tesserae, so the body follows Astraspis and Arandaspis: a deep, rounded,
heavily armoured head, a row of gill openings, small side eyes, a scaly trunk and a hypocercal
tail, no paired fins. Dark bronze-brown armour with pale ridges (colour conjectural).
Built with nh_ord_agnathan.py.

Usage:
  blender --background --python tools/blender/eriptychius_americanus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EriptychiusAmericanus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_agnathan as ag  # noqa: E402

SPEC = ag.Spec(
    name="EriptychiusAmericanus",
    rows=((-0.80, 0.03, 0.025, 0.02, 0.0), (-0.74, 0.11, 0.09, 0.06, 0.0), (-0.58, 0.17, 0.16, 0.09, 0.0),
          (-0.34, 0.185, 0.175, 0.105, 0.0), (-0.08, 0.15, 0.15, 0.09, 0.0), (0.16, 0.10, 0.10, 0.07, 0.0),
          (0.40, 0.06, 0.06, 0.045, 0.0), (0.58, 0.03, 0.032, 0.025, 0.0), (0.72, 0.012, 0.014, 0.012, 0.0)),
    power=2.0, shield_end=-0.06, suture_z=-0.035, trunk_end=0.60, tail="hypocercal", tail_len=0.40, tail_h=0.15,
    eye_y=-0.62, eye_a=0.20, eye_r=0.024, eye_look=(1.0, -0.4, 0.2), pineal=True,
    gills=9, gill_y=(-0.40, -0.12), gill_a=-0.08, branchial_plates=False, tubercles="ridges",
    shield=(0.42, 0.30, 0.18), shield_dark=(0.20, 0.13, 0.08), tubercle=(0.86, 0.72, 0.50),
    back=(0.26, 0.19, 0.12), flank=(0.40, 0.30, 0.20), belly=(0.70, 0.60, 0.46),
    fin=(0.36, 0.28, 0.20), fin_edge=(0.58, 0.48, 0.36), ray=(0.20, 0.14, 0.10),
)

if __name__ == "__main__":
    nh.run(lambda: ag.build_ostracoderm(SPEC), SPEC.name, **ag.PREVIEW)
