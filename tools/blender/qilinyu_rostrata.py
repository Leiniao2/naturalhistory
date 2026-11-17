"""
Procedural Qilinyu rostrata (late Silurian placoderm about 20 cm long from the Kuanti
Formation of Qujing, Yunnan, China, about 423 million years old) for map colonies.

Like its neighbour Entelognathus it combined a box-like placoderm head and trunk shield
with bony-fish-like marginal jaw bones, but its snout was drawn out into a short,
pointed rostrum overhanging the mouth (rostrata = "beaked"). Small high eyes, a flat
underside, pectoral fins, a dorsal fin behind the armour, a scaled body and a
heterocercal tail. Warm tan with dark sutures.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/qilinyu_rostrata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/QilinyuRostrata.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="QilinyuRostrata",
    rows=[(-0.72, 0.03, 0.03, 0.02, -0.01), (-0.66, 0.11, 0.07, 0.05, -0.01), (-0.54, 0.17, 0.11, 0.08, 0.0),
          (-0.36, 0.20, 0.14, 0.09, 0.01), (-0.16, 0.17, 0.14, 0.09, 0.01), (0.05, 0.11, 0.11, 0.08, 0.02),
          (0.30, 0.06, 0.07, 0.05, 0.04), (0.55, 0.03, 0.035, 0.03, 0.08), (0.80, 0.004, 0.006, 0.005, 0.15)],
    power=3.2, skin="scales", stations=32, around=18,
    armour=(-0.10, [(-0.68, 0.0), (-0.60, 0.35), (-0.50, 0.0), (-0.44, 0.40), (-0.34, 0.0), (-0.58, 1.0),
                    (-0.44, 1.1), (-0.26, 0.45), (-0.20, 0.0), (-0.26, 1.2), (-0.54, 2.2), (-0.26, 2.5)]),
    rostrum=0.09,
    tail="hetero", tail_y0=0.40, tail_main=0.22, tail_minor=0.04,
    median=[(0.02, 0.20, 0.11, 1, 0.6), (0.26, 0.38, 0.06, -1, 0.7)],
    paired=[(-0.28, -0.16, -0.6, 0.15, 1.0, 0.3, 0.8), (0.12, 0.20, -1.2, 0.06, 0.6, 0.6, 0.9)],
    eye_y=-0.56, eye_a=0.8, eye_r=0.024, eye_look=(0.7, -0.3, 0.6), mouth=(-0.70, -0.52, 0.4),
    back=(0.38, 0.30, 0.20), flank=(0.60, 0.50, 0.36), belly=(0.84, 0.78, 0.64), blotch=(0.26, 0.20, 0.13),
    bone=(0.66, 0.56, 0.40), suture=(0.22, 0.15, 0.09),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
