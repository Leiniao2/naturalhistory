"""
Procedural Cloudina hartmannae (terminal-Ediacaran tube animal, Nama Group) for the map: a
small reef-like clump of the classic cone-in-cone tubes - each a stack of nested, moderately
flared calcite collars set slightly off-centre on one another, so the tube is wavy-walled and
gently curved - leaning every which way out of a dark microbial mat, with a few toppled tubes
and broken collar stacks lying around. Some tubes bud a daughter tube from inside a collar,
and a few carry a dark drill hole (the bore holes read as possible early predation).
Tubes several times longer than wide, cream-white on the olive-grey mat.
Fixed style: pivot at the base (z = 0). Shared tube/cluster code lives in nh_cloudina.py.

Usage:
  blender --background --python tools/blender/cloudina_hartmannae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CloudinaHartmannae.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_cloudina as cl  # noqa: E402

SEED = 11
STYLE = cl.TubeStyle(
    radius=0.036, growth=1.04, collars=(5, 9), height=1.3, flare=0.32, sink=0.25,
    ecc=0.14, curve=0.10, sides=8, mid_ring=True, bud_chance=0.35, bore_chance=0.35,
)


def build():
    return cl.cluster(STYLE, SEED, count=9, radius=0.34, tilt=(5, 50), lying=1, fragments=2,
                      name="CloudinaHartmannae")


if __name__ == "__main__":
    nh.run(build, "CloudinaHartmannae", ground=(0.30, 0.29, 0.22), background=(0.05, 0.14, 0.18),
           views=cl.VIEWS)
