"""
Procedural Glyptocrinus decadactylus (Late Ordovician camerate crinoid, Cincinnati region)
for map colonies (Fixed style).

A sea lily on a long, round stem: a rigid, cone-shaped cup of thick, star-ridged plates
and ten arms (two from each of the five rays, hence the name) that branch again as they
rise into a feathery feeding fan. Pale grey-violet. Built with nh_ord_echino.crinoid.
Pivot on the sea floor (z = 0), facing -Y.

Usage:
  blender --background --python tools/blender/glyptocrinus_decadactylus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GlyptocrinusDecadactylus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

if __name__ == "__main__":
    nh.run(lambda: ec.crinoid("GlyptocrinusDecadactylus", forks=2, stem_h=1.3, stem_r=0.03, arm_len=0.62,
                              spread=0.45, cup_h=0.24, body=(0.62, 0.58, 0.66), dark=(0.38, 0.34, 0.44),
                              arm=(0.76, 0.72, 0.80), sway=0.05),
           "GlyptocrinusDecadactylus", **ec.VIEWS)
