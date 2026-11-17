"""
Procedural Astraspis desiderata (Late Ordovician astraspid, Harding Sandstone, Colorado;
about 13-15 cm long) for map colonies (Swim style).

A jawless armoured fish whose head armour is a mosaic of small polygonal plates, each
capped with shiny, star-shaped tubercles of enameloid (the name means "star shield");
eyes set at the sides of the head; eight separate gill openings in a row on each side
behind them; no paired fins; a body of thick rhombic scales and a tail whose axis bends
down. Dark armour with pale tubercles (colour conjectural). Built with nh_ord_agnathan.py.

Usage:
  blender --background --python tools/blender/astraspis_desiderata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AstraspisDesiderata.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_agnathan as ag  # noqa: E402

SPEC = ag.Spec(
    name="AstraspisDesiderata",
    rows=((-0.80, 0.02, 0.02, 0.02, 0.0), (-0.74, 0.08, 0.07, 0.05, 0.0), (-0.58, 0.14, 0.13, 0.085, 0.0),
          (-0.36, 0.16, 0.15, 0.10, 0.0), (-0.10, 0.14, 0.13, 0.09, 0.0), (0.16, 0.10, 0.10, 0.07, 0.0),
          (0.40, 0.06, 0.06, 0.045, 0.0), (0.58, 0.03, 0.032, 0.025, 0.0), (0.72, 0.012, 0.014, 0.012, 0.0)),
    shield_end=-0.12, suture_z=-0.03, trunk_end=0.60, tail="hypocercal", tail_len=0.42, tail_h=0.17,
    eye_y=-0.60, eye_a=0.25, eye_r=0.026, eye_look=(1.0, -0.3, 0.2), pineal=False,
    gills=8, gill_y=(-0.42, -0.17), gill_a=-0.05, branchial_plates=False, tubercles="stars",
    shield=(0.30, 0.30, 0.32), shield_dark=(0.16, 0.16, 0.18), tubercle=(0.88, 0.86, 0.78),
    back=(0.22, 0.22, 0.24), flank=(0.36, 0.35, 0.36), belly=(0.62, 0.60, 0.56),
    fin=(0.32, 0.31, 0.32), fin_edge=(0.52, 0.50, 0.48), ray=(0.18, 0.18, 0.19),
)

if __name__ == "__main__":
    nh.run(lambda: ag.build_ostracoderm(SPEC), SPEC.name, **ag.PREVIEW)
