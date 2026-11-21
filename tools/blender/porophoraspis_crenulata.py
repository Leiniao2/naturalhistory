"""
Procedural Porophoraspis crenulata (Middle Ordovician arandaspid, central Australia) for
map colonies (Swim style).

One of the oldest well-known armoured jawless fishes: a small, finless fish with a head
and chest enclosed in a broad, flattened box of bony plates, a dorsal and a ventral shield
ornamented with crenulated ridges and pierced by pores (hence the name), a long row of
little branchial plates along each flank, tiny eyes at the very front, and a scaly,
tapering tail ending in an arandaspid fin with a long middle lobe. Olive-grey shield,
paler belly. Built with nh_ord_agnathan.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/porophoraspis_crenulata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PorophoraspisCrenulata.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_agnathan as ag  # noqa: E402

SPEC = ag.Spec(
    name="PorophoraspisCrenulata",
    rows=((-0.80, 0.03, 0.015, 0.012, 0.0), (-0.75, 0.12, 0.05, 0.04, 0.0), (-0.60, 0.18, 0.085, 0.065, 0.0),
          (-0.34, 0.195, 0.10, 0.07, 0.0), (-0.08, 0.16, 0.09, 0.065, 0.0), (0.16, 0.10, 0.075, 0.055, 0.0),
          (0.40, 0.06, 0.05, 0.04, 0.0), (0.58, 0.03, 0.03, 0.025, 0.0), (0.72, 0.012, 0.012, 0.01, 0.0)),
    power=2.4, shield_end=-0.04, suture_z=-0.015, trunk_end=0.62, tail="arandaspid", tail_len=0.40, tail_h=0.14,
    eye_y=-0.75, eye_a=0.45, eye_r=0.017, eye_look=(0.45, -0.9, 0.3), pineal=True,
    gills=14, gill_y=(-0.46, -0.08), gill_a=-0.10, branchial_plates=True, tubercles="ridges",
    shield=(0.44, 0.46, 0.34), shield_dark=(0.22, 0.24, 0.17), tubercle=(0.74, 0.74, 0.58),
    back=(0.27, 0.29, 0.22), flank=(0.42, 0.44, 0.34), belly=(0.70, 0.70, 0.58),
    fin=(0.38, 0.40, 0.30), fin_edge=(0.60, 0.60, 0.48),
)

if __name__ == "__main__":
    nh.run(lambda: ag.build_ostracoderm(SPEC), SPEC.name, **ag.PREVIEW)
