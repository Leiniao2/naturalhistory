"""
Procedural Pharyngolepis oblongus (Late Silurian anaspid, a jawless fish from Ringerike,
Norway, about 15 cm long) for map colonies (Swim style).

A long, slender, torpedo-shaped jawless fish built for speed: a small terminal mouth, a
long row of up to fifteen small gill openings behind each eye, a body clad in narrow,
oblique rows of scales, a crest of hooked scutes along the back, long ventrolateral fin
folds along the belly, a stout spine behind the gills and a large hypocercal tail (the
body axis turns down into the lower lobe). Dark grey-brown back, silvery flanks.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/pharyngolepis_oblongus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PharyngolepisOblongus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="PharyngolepisOblongus",
    rows=[(-0.85, 0.010, 0.012, 0.012, 0.00), (-0.80, 0.035, 0.05, 0.045, 0.0), (-0.68, 0.055, 0.085, 0.075, 0.0),
          (-0.45, 0.065, 0.105, 0.090, 0.0), (-0.15, 0.062, 0.105, 0.090, -0.005), (0.15, 0.052, 0.085, 0.075, -0.015),
          (0.38, 0.038, 0.060, 0.052, -0.035), (0.58, 0.022, 0.035, 0.030, -0.07), (0.82, 0.004, 0.006, 0.006, -0.15)],
    power=2.1, skin="scales", stations=46, around=18, head_back=-0.66,
    tail="hypo", tail_y0=0.40, tail_main=0.26, tail_minor=0.07,
    spines=[(-0.40, -1.3, (0.03, 0.06, -0.05), 0.008)],
    scutes=(-0.55, 0.38, 14, 0.035), gills=(-0.64, -0.34, 14, -0.15, 0.009),
    folds=(-0.30, 0.30, 0.05),
    eye_y=-0.73, eye_a=0.25, eye_r=0.024, mouth=(-0.85, -0.80, 0.0),
    back=(0.18, 0.18, 0.16), flank=(0.56, 0.58, 0.56), belly=(0.86, 0.86, 0.80), blotch=(0.12, 0.12, 0.11),
    fin=(0.30, 0.31, 0.29), fin_edge=(0.64, 0.66, 0.62), ray=(0.16, 0.16, 0.15),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
