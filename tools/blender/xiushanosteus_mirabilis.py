"""
Procedural Xiushanosteus mirabilis (a tiny placoderm, about 3 cm long, from the early
Silurian (Telychian, about 436 million years ago) Huixingshao Formation of Chongqing,
China, described in 2023) for map colonies.

One of the oldest complete jawed fishes: a short, broad head shield and a long trunk
shield of bony plates boxing in the front half of the body, a short blunt snout with the
eyes set high on the sides, a stout pectoral spine at the corner of the trunk shield,
and a scaly trunk behind with a single dorsal fin and an upturned (heterocercal) tail.
Painted grey-brown armour with dark plate sutures. Built with nh_sil_fish.py.
Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/xiushanosteus_mirabilis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/XiushanosteusMirabilis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="XiushanosteusMirabilis",
    rows=[(-0.78, 0.04, 0.03, 0.025, -0.01), (-0.72, 0.13, 0.08, 0.06, -0.01), (-0.58, 0.21, 0.12, 0.09, 0.0),
          (-0.38, 0.23, 0.14, 0.10, 0.01), (-0.14, 0.19, 0.13, 0.09, 0.01), (0.06, 0.11, 0.10, 0.07, 0.02),
          (0.30, 0.06, 0.065, 0.05, 0.04), (0.55, 0.03, 0.035, 0.028, 0.08), (0.80, 0.004, 0.006, 0.005, 0.15)],
    power=3.4, skin="scales", stations=30, around=16,
    armour=(-0.04, [(-0.72, 0.0), (-0.62, 0.45), (-0.52, 0.0), (-0.40, 0.5), (-0.30, 0.0), (-0.62, 1.1),
                    (-0.42, 1.25), (-0.18, 0.5), (-0.12, 0.0), (-0.18, 1.3), (-0.40, 2.3), (-0.16, 2.6),
                    (-0.55, 1.7), (-0.25, 1.9)]),
    spines=[(-0.14, -0.1, (0.17, 0.12, -0.04), 0.016)],
    tail="hetero", tail_y0=0.38, tail_main=0.20, tail_minor=0.04,
    median=[(0.04, 0.22, 0.10, 1, 0.7)],
    paired=[(0.14, 0.22, -1.2, 0.05, 0.6, 0.6, 0.9)],
    eye_y=-0.62, eye_a=0.55, eye_r=0.028, eye_look=(0.8, -0.3, 0.4), mouth=(-0.77, -0.62, 0.35),
    back=(0.30, 0.26, 0.22), flank=(0.52, 0.46, 0.38), belly=(0.82, 0.78, 0.68), blotch=(0.20, 0.17, 0.14),
    bone=(0.62, 0.56, 0.46), suture=(0.16, 0.12, 0.09),
    fin=(0.40, 0.35, 0.28), fin_edge=(0.70, 0.64, 0.52), ray=(0.22, 0.18, 0.14),
)

if __name__ == "__main__":
    nh.run(lambda: sf.build(SPEC), SPEC.name, **sf.PREVIEW)
