"""
Procedural Metriorhynchus superciliosus (Middle-Late Jurassic metriorhynchid, Europe) for map colonies.

A fully marine relative of crocodiles about 3 m long, which had lost the bony armour of
its land cousins: smooth, streamlined body, a long, narrow snout full of conical teeth
for catching fish and cephalopods, small paddle-like forelimbs, larger hind paddles, and a
downturned tail tip carrying a shark-like fluke with the larger lobe below. Grey-green
back with a pale belly. Built with nh_jur_marine. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/metriorhynchus_superciliosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Metriorhynchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_marine as mr  # noqa: E402

PAINT = kit.paint(back=(0.26, 0.31, 0.27), flank=(0.44, 0.48, 0.42), belly=(0.86, 0.85, 0.78))

SPEC = mr.Spec(
    name="Metriorhynchus",
    rows=[(0, 1.02, -0.09, 0, 0), (0, 0.95, -0.06, 0.012, 0.016), (0, 0.8, -0.02, 0.03, 0.04), (0, 0.55, 0.0, 0.06, 0.07),
          (0, 0.3, 0.0, 0.1, 0.1), (0, 0.05, 0.0, 0.13, 0.12), (0, -0.2, 0.0, 0.12, 0.11), (0, -0.38, 0.01, 0.08, 0.075),
          (0, -0.5, 0.02, 0.07, 0.06), (0, -0.6, 0.02, 0.055, 0.045), (0, -0.7, 0.01, 0.03, 0.03),
          (0, -0.85, 0.0, 0.02, 0.02), (0, -0.98, -0.005, 0.014, 0.014), (0, -1.02, -0.006, 0, 0)],
    paint=PAINT,
    flippers=[((0.1, -0.22, -0.06), 0.22, 0.09, 40, 15), ((0.08, 0.3, -0.05), 0.34, 0.12, 50, 15)],
    tail_fin=[(0.82, -0.03), (0.98, 0.1), (1.0, 0.08), (1.02, -0.09), (1.0, -0.26), (0.95, -0.24), (0.88, -0.08)],
    teeth=[(-0.68, -0.97, 12, 0.015, 0.0, None, 0.011)],
    eye=(0.045, -0.58, 0.05), eye_r=0.013,
    jaw_line=(-0.6, -1.0, -0.004, 0.03),
)

if __name__ == "__main__":
    nh.run(lambda: mr.build(SPEC), "Metriorhynchus", **mr.PREVIEW)
