"""
Procedural Entelognathus primordialis (late Silurian placoderm about 20 cm long from the
Kuanti Formation of Qujing, Yunnan, China, about 423 million years old) for map colonies.

A box-like armoured head and trunk shield of large bony plates, flat underneath, but
with the marginal jaw bones (maxilla, premaxilla, dentary) of a bony fish, so the gape
runs along the side of the head; small eyes high on the head, a pectoral fin emerging
from the shield; behind the armour a scaled body, a dorsal fin and a heterocercal tail.
Grey-brown bone with darker sutures.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/entelognathus_primordialis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EntelognathusPrimordialis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="EntelognathusPrimordialis",
    rows=[(-0.80, 0.03, 0.03, 0.02, -0.02), (-0.74, 0.12, 0.08, 0.06, -0.01), (-0.60, 0.19, 0.12, 0.09, 0.0),
          (-0.40, 0.21, 0.15, 0.10, 0.01), (-0.18, 0.18, 0.15, 0.10, 0.01), (0.05, 0.11, 0.11, 0.08, 0.02),
          (0.30, 0.06, 0.07, 0.05, 0.04), (0.55, 0.03, 0.035, 0.03, 0.08), (0.80, 0.004, 0.006, 0.005, 0.15)],
    power=3.0, skin="scales", stations=32, around=18,
    armour=(-0.12, [(-0.76, 0.0), (-0.68, 0.35), (-0.58, 0.0), (-0.50, 0.40), (-0.40, 0.0), (-0.66, 1.0),
                    (-0.50, 1.1), (-0.30, 0.45), (-0.24, 0.0), (-0.30, 1.2), (-0.60, 2.2), (-0.30, 2.5), (-0.62, 1.6)]),
    tail="hetero", tail_y0=0.40, tail_main=0.22, tail_minor=0.04,
    median=[(0.00, 0.18, 0.12, 1, 0.6), (0.25, 0.38, 0.06, -1, 0.7)],
    paired=[(-0.30, -0.18, -0.6, 0.14, 1.0, 0.3, 0.8), (0.12, 0.20, -1.2, 0.06, 0.6, 0.6, 0.9)],
    eye_y=-0.64, eye_a=0.75, eye_r=0.025, eye_look=(0.7, -0.3, 0.6), mouth=(-0.79, -0.58, 0.3),
    back=(0.30, 0.28, 0.22), flank=(0.50, 0.46, 0.36), belly=(0.80, 0.76, 0.64), blotch=(0.22, 0.20, 0.15),
    bone=(0.56, 0.52, 0.42), suture=(0.18, 0.15, 0.11),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
