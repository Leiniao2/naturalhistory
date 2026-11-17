"""
Procedural Birkenia elegans (mid-Silurian anaspid, a small jawless fish about 10 cm long from
Lesmahagow and Hagshaw Hills, Scotland) for map colonies.

A deep, laterally flattened little fish covered in rows of narrow, tall scales; a crest
of hooked ridge scales along the back (pointing forward in front, backward behind);
a row of eight small gill openings behind the eye; a terminal mouth; no paired fins
but a spine in front of the anal region; and a hypocercal tail whose scaled body axis
bends down into the lower lobe, with the fin web above it. Dark olive above.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/birkenia_elegans.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BirkeniaElegans.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="BirkeniaElegans",
    rows=[(-0.80, 0.010, 0.015, 0.015, 0.00), (-0.74, 0.045, 0.07, 0.06, 0.0), (-0.62, 0.07, 0.12, 0.10, 0.0),
          (-0.40, 0.08, 0.16, 0.13, 0.0), (-0.10, 0.075, 0.16, 0.13, -0.01), (0.20, 0.06, 0.12, 0.10, -0.03),
          (0.40, 0.045, 0.08, 0.07, -0.06), (0.60, 0.025, 0.045, 0.04, -0.11), (0.80, 0.004, 0.006, 0.006, -0.19)],
    power=2.0, skin="scales", stations=40, around=18, head_back=-0.60,
    tail="hypo", tail_y0=0.36, tail_main=0.20, tail_minor=0.05,
    spines=[(0.10, -1.4, (0.02, 0.10, -0.06), 0.010)],
    scutes=(-0.45, 0.34, 11, 0.04), gills=(-0.56, -0.38, 8, -0.15, 0.012),
    eye_y=-0.68, eye_a=0.2, eye_r=0.028, mouth=(-0.80, -0.74, 0.0),
    back=(0.20, 0.22, 0.17), flank=(0.40, 0.42, 0.33), belly=(0.74, 0.72, 0.60), blotch=(0.14, 0.15, 0.11),
    fin=(0.36, 0.38, 0.30), fin_edge=(0.62, 0.62, 0.52), ray=(0.20, 0.20, 0.15),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
