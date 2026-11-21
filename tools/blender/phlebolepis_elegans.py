"""
Procedural Phlebolepis elegans (a thelodont, a jawless fish about 7 cm long from the Late
Silurian of Saaremaa, Estonia) for map colonies.

A small, deep-bodied thelodont: a short, rounded head with a terminal mouth, small eyes far
forward, a row of gill openings, broad flap-like pectoral folds, a tall triangular dorsal
fin and an anal fin, and a hypocercal tail with a big upper web. Covered in fine
tooth-like scales (shagreen). Warm brown back with darker blotches.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/phlebolepis_elegans.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PhlebolepisElegans.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="PhlebolepisElegans",
    rows=[(-0.78, 0.02, 0.02, 0.02, 0.0), (-0.72, 0.09, 0.08, 0.06, 0.0), (-0.58, 0.14, 0.13, 0.09, 0.0),
          (-0.36, 0.14, 0.17, 0.11, 0.0), (-0.10, 0.11, 0.16, 0.11, -0.01), (0.15, 0.07, 0.11, 0.08, -0.02),
          (0.38, 0.04, 0.06, 0.05, -0.04), (0.60, 0.02, 0.03, 0.026, -0.08), (0.80, 0.004, 0.006, 0.006, -0.13)],
    power=2.3, skin="shagreen", head_back=-0.52,
    tail="hypo", tail_y0=0.40, tail_main=0.24, tail_minor=0.06,
    median=[(-0.10, 0.18, 0.15, 1, 0.9), (0.18, 0.34, 0.07, -1, 0.8)],
    paired=[(-0.50, -0.20, -0.3, 0.14, 1.0, 0.2, 0.7)],
    gills=(-0.52, -0.36, 8, -0.5, 0.011),
    eye_y=-0.66, eye_a=0.30, eye_r=0.026, mouth=(-0.78, -0.72, 0.0),
    back=(0.34, 0.24, 0.15), flank=(0.60, 0.46, 0.32), belly=(0.86, 0.78, 0.64), blotch=(0.20, 0.13, 0.08),
    blotch_amount=0.55, fin=(0.42, 0.32, 0.22), fin_edge=(0.70, 0.58, 0.44), ray=(0.24, 0.17, 0.11),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
