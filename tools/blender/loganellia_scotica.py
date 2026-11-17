"""
Procedural Loganellia scotica (early-mid Silurian thelodont, a jawless fish about 12 cm long
known from complete specimens from Lesmahagow, Scotland) for map colonies.

A broad, flattened head and forebody with wide paired pectoral flaps; the body tapers
to a deeply forked, hypocercal tail; a single dorsal and an anal fin. The whole body is
covered in tiny, tooth-like scales (shagreen), a slit-like row of gill openings
underneath and a wide terminal mouth. Dark brownish-grey above, paler below.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/loganellia_scotica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LoganelliaScotica.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="LoganelliaScotica",
    rows=[(-0.80, 0.02, 0.012, 0.012, 0.0), (-0.74, 0.10, 0.045, 0.035, 0.0), (-0.60, 0.16, 0.07, 0.05, 0.0),
          (-0.42, 0.17, 0.09, 0.06, 0.0), (-0.20, 0.12, 0.10, 0.07, 0.0), (0.10, 0.07, 0.09, 0.07, -0.01),
          (0.35, 0.045, 0.06, 0.05, -0.03), (0.60, 0.022, 0.03, 0.028, -0.06), (0.80, 0.004, 0.006, 0.006, -0.10)],
    power=2.4, skin="shagreen", head_back=-0.50,
    tail="fork", tail_y0=0.48, tail_main=0.20, tail_minor=0.0,
    median=[(0.05, 0.25, 0.09, 1, 0.8), (0.18, 0.34, 0.06, -1, 0.8)],
    paired=[(-0.50, -0.26, -0.2, 0.12, 1.0, 0.15, 0.6)],
    gills=(-0.50, -0.34, 7, -0.6, 0.012),
    eye_y=-0.66, eye_a=0.35, eye_r=0.026, mouth=(-0.80, -0.70, 0.2),
    back=(0.40, 0.36, 0.30), flank=(0.58, 0.53, 0.46), belly=(0.78, 0.74, 0.66), blotch=(0.18, 0.17, 0.15),
    fin=(0.36, 0.33, 0.30), fin_edge=(0.60, 0.56, 0.50), ray=(0.20, 0.18, 0.16),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
