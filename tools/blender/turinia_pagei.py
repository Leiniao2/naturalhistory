"""
Procedural Turinia pagei for the map: a thelodont, a jawless fish covered in tiny
tooth-like scales, from the Early Devonian (about 410 million years ago) of Scotland and
the Welsh Borderland; up to about 20-35 cm long, one of the largest thelodonts.

A broad, flattened head and forebody with very wide, flap-like pectoral fins, a wide
terminal mouth, small eyes set at the front edge of the head, a row of gill slits under
the head, a body tapering to a hypocercal tail (the body axis turning down into the lower
lobe) and small dorsal and anal fins. The whole skin is a fine shagreen of minute scales.
Colours unknown: sandy grey-brown above with dark mottling, pale below.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/turinia_pagei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Turinia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="Turinia",
    rows=[(-0.80, 0.03, 0.010, 0.010, 0.0), (-0.74, 0.14, 0.035, 0.028, 0.0), (-0.60, 0.21, 0.055, 0.040, 0.0),
          (-0.42, 0.22, 0.070, 0.048, 0.0), (-0.22, 0.15, 0.080, 0.056, 0.0), (0.08, 0.08, 0.075, 0.058, -0.01),
          (0.35, 0.045, 0.050, 0.044, -0.03), (0.60, 0.022, 0.028, 0.026, -0.06), (0.80, 0.004, 0.006, 0.006, -0.11)],
    power=2.6, skin="shagreen", head_back=-0.46,
    tail="hypo", tail_y0=0.44, tail_main=0.22, tail_minor=0.07,
    median=[(0.08, 0.24, 0.07, 1, 0.8), (0.20, 0.34, 0.05, -1, 0.8)],
    paired=[(-0.48, -0.20, -0.1, 0.18, 1.0, 0.10, 0.75)],
    gills=(-0.48, -0.32, 8, -0.7, 0.011),
    eye_y=-0.70, eye_a=0.45, eye_r=0.022, mouth=(-0.80, -0.72, 0.2),
    back=(0.50, 0.44, 0.34), flank=(0.64, 0.58, 0.46), belly=(0.86, 0.82, 0.72), blotch=(0.20, 0.17, 0.12),
    blotch_amount=0.6, fin=(0.46, 0.40, 0.32), fin_edge=(0.70, 0.64, 0.52), ray=(0.26, 0.22, 0.17),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
