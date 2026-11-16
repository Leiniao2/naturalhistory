"""
Procedural Cloudina riemkeae (terminal-Ediacaran tube animal, Nama Group) for the map: the
small, slender Cloudina - a dense tuft of many thin cone-in-cone tubes (only about 0.3-1.3 mm
wide, versus 2.5-6.5 mm in C. hartmannae), each a long stack of small, gently flared calcite
collars, crowding up out of a dark microbial mat and leaning every which way, with toppled tubes
lying among them. Much finer and more numerous than the hartmannae clump, so it reads as a
bristly white turf rather than a few stout tubes. Cream-white on the olive-grey mat.
Fixed style: pivot at the base (z = 0). Shared tube/cluster code lives in nh_cloudina.py.

Usage:
  blender --background --python tools/blender/cloudina_riemkeae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CloudinaRiemkeae.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_cloudina as cl  # noqa: E402

SEED = 23
STYLE = cl.TubeStyle(
    radius=0.013, growth=1.02, collars=(8, 13), height=2.4, flare=0.28, sink=0.2,
    ecc=0.14, curve=0.09, sides=5, mid_ring=False, bud_chance=0.25, bore_chance=0.0,
)


def build():
    return cl.cluster(STYLE, SEED, count=19, radius=0.30, tilt=(5, 45), lying=3, fragments=0,
                      name="CloudinaRiemkeae")


if __name__ == "__main__":
    nh.run(build, "CloudinaRiemkeae", ground=(0.30, 0.29, 0.22), background=(0.05, 0.14, 0.18),
           views=cl.VIEWS)
