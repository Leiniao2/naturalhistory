"""
Procedural Jamoytius kerwoodi (early Silurian jawless fish about 17 cm long from
Lesmahagow, Scotland) for map colonies.

A slender, eel-like, lightly built fish with a soft, almost scaleless body marked by
W-shaped muscle bands (myomeres); a long fin fold along each flank, a low dorsal fold,
a ring-shaped mouth at the front of the head, round eyes, a row of gill openings and a
hypocercal tail. Possibly an anaspid relative, possibly closer to lampreys. Pale
greenish-grey.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/jamoytius_kerwoodi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/JamoytiusKerwoodi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="JamoytiusKerwoodi",
    rows=[(-0.80, 0.010, 0.012, 0.012, 0.0), (-0.76, 0.045, 0.045, 0.045, 0.0), (-0.66, 0.065, 0.07, 0.065, 0.0),
          (-0.40, 0.065, 0.08, 0.07, 0.0), (0.00, 0.060, 0.075, 0.065, -0.005), (0.30, 0.045, 0.06, 0.05, -0.015),
          (0.55, 0.028, 0.04, 0.035, -0.04), (0.80, 0.004, 0.006, 0.006, -0.09)],
    power=2.0, skin="smooth", head_back=-0.60, myomeres=22,
    tail="hypo", tail_y0=0.45, tail_main=0.14, tail_minor=0.04,
    median=[(-0.05, 0.40, 0.03, 1, 0.3)], folds=(-0.50, 0.30, 0.05),
    gills=(-0.58, -0.40, 8, -0.1, 0.010),
    eye_y=-0.70, eye_a=0.25, eye_r=0.028, mouth=(-0.80, -0.77, 0.0),
    back=(0.36, 0.40, 0.34), flank=(0.56, 0.60, 0.52), belly=(0.82, 0.82, 0.74), blotch=(0.28, 0.30, 0.25),
    blotch_amount=0.2, fin=(0.55, 0.58, 0.50), fin_edge=(0.75, 0.76, 0.68), ray=(0.40, 0.42, 0.36),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
