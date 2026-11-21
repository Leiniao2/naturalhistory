"""
Procedural Euphanerops longaevus for the map: a late anaspid, a jawless fish from the Late
Devonian (Frasnian, about 380 million years ago) of Miguasha, Quebec; about 10-15 cm long.

Slender and eel-like, almost scaleless, with a small terminal mouth, small eyes, a
remarkably long row of about 30 gill openings stretching back along the body, a long
low fin fold along the belly (anal fin fold), a low dorsal fold and a hypocercal tail
whose body axis turns down into the lower lobe. Specimens with tiny fish inside are among
the earliest records of vertebrates eating other vertebrates.
Colours unknown: olive-brown back with faint muscle-block bands, pale belly.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/euphanerops_longaevus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Euphanerops.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="Euphanerops",
    rows=[(-0.80, 0.008, 0.010, 0.010, 0.0), (-0.76, 0.034, 0.038, 0.036, 0.0), (-0.66, 0.048, 0.056, 0.052, 0.0),
          (-0.40, 0.050, 0.062, 0.058, 0.0), (0.00, 0.046, 0.060, 0.056, -0.005), (0.30, 0.036, 0.048, 0.044, -0.015),
          (0.55, 0.022, 0.032, 0.030, -0.040), (0.80, 0.004, 0.006, 0.006, -0.095)],
    power=2.0, skin="smooth", head_back=-0.66, myomeres=26,
    tail="hypo", tail_y0=0.46, tail_main=0.15, tail_minor=0.04,
    median=[(0.00, 0.42, 0.025, 1, 0.3), (-0.10, 0.44, 0.045, -1, 0.3)],
    gills=(-0.62, -0.05, 30, -0.35, 0.007),
    eye_y=-0.71, eye_a=0.35, eye_r=0.024, mouth=(-0.80, -0.775, 0.0),
    back=(0.34, 0.30, 0.18), flank=(0.56, 0.50, 0.34), belly=(0.86, 0.82, 0.68), blotch=(0.20, 0.17, 0.10),
    blotch_amount=0.25, fin=(0.50, 0.45, 0.32), fin_edge=(0.74, 0.70, 0.56), ray=(0.34, 0.30, 0.20),
    iris=(0.70, 0.58, 0.28),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
