"""
Procedural Cryptoclidus eurymerus (Middle Jurassic Oxford Clay plesiosaur, England) for map colonies.

A long-necked plesiosaur about 4 m long: a small, flat head on a neck as long as the body,
jaws lined with many long, thin, interlocking teeth that formed a trap for small fish and
squid, a broad, flattened body with four long, pointed flippers (the hind pair slightly
larger), and a short tail. Dark slate-blue back fading to a pale belly, with faint
spots. Built with nh_jur_marine. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/cryptoclidus_eurymerus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cryptoclidus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_marine as mr  # noqa: E402

PAINT = kit.paint(back=(0.20, 0.25, 0.30), flank=(0.36, 0.42, 0.46), belly=(0.82, 0.82, 0.78),
                  spots=(0.12, 0.15, 0.18), spot_scale=14.0, spot_amt=0.4)

SPEC = mr.Spec(
    name="Cryptoclidus",
    rows=[(0, 0.75, 0.0, 0, 0), (0, 0.62, 0.0, 0.03, 0.025), (0, 0.45, 0.0, 0.09, 0.07), (0, 0.25, 0.0, 0.17, 0.11),
          (0, 0.0, 0.0, 0.2, 0.13), (0, -0.25, 0.0, 0.17, 0.11), (0, -0.42, 0.01, 0.09, 0.075),
          (0, -0.65, 0.03, 0.06, 0.055), (0, -0.9, 0.05, 0.045, 0.045), (0, -1.12, 0.06, 0.04, 0.038),
          (0, -1.2, 0.06, 0.045, 0.035), (0, -1.27, 0.055, 0.035, 0.025), (0, -1.33, 0.05, 0.02, 0.015), (0, -1.36, 0.048, 0, 0)],
    paint=PAINT,
    flippers=[((0.16, -0.2, -0.04), 0.5, 0.15, 30, 10), ((0.15, 0.24, -0.04), 0.52, 0.16, 38, 10)],
    flipper_thick=0.014,
    teeth=[(-1.24, -1.34, 8, 0.024, 0.045, None, 0.03)],
    eye=(0.03, -1.21, 0.075), eye_r=0.011,
    jaw_line=(-1.18, -1.35, 0.045, 0.036),
    voxel=0.012,
)

if __name__ == "__main__":
    nh.run(lambda: mr.build(SPEC), "Cryptoclidus", **mr.PREVIEW)
