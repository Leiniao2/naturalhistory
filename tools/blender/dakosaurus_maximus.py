"""
Procedural Dakosaurus maximus (Late Jurassic metriorhynchid, Europe) for map colonies.

A big marine crocodyliform, about 4-5 m long, nicknamed "Godzilla": unlike its slender-
snouted relatives it had a short, deep, broad-based snout armed with large, serrated,
blade-like teeth, making it a top predator that could cut up large prey. Smooth,
armourless streamlined body, paddle limbs and a downturned tail with a fluke. Dark
brown-grey back with darker blotches and a pale belly. Built with nh_jur_marine. Faces -Y,
pivot at the body centre.

Usage:
  blender --background --python tools/blender/dakosaurus_maximus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dakosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
import nh_jur_marine as mr  # noqa: E402

PAINT = kit.paint(back=(0.24, 0.21, 0.18), flank=(0.42, 0.37, 0.31), belly=(0.84, 0.80, 0.72),
                  spots=(0.14, 0.12, 0.10), spot_scale=7.0, spot_amt=0.5)

SPEC = mr.Spec(
    name="Dakosaurus",
    rows=[(0, 1.0, -0.09, 0, 0), (0, 0.93, -0.06, 0.014, 0.018), (0, 0.78, -0.02, 0.035, 0.045), (0, 0.55, 0.0, 0.07, 0.08),
          (0, 0.3, 0.0, 0.12, 0.12), (0, 0.05, 0.0, 0.15, 0.14), (0, -0.2, 0.0, 0.14, 0.13), (0, -0.38, 0.01, 0.1, 0.095),
          (0, -0.5, 0.025, 0.09, 0.09), (0, -0.6, 0.025, 0.08, 0.08), (0, -0.7, 0.015, 0.065, 0.065),
          (0, -0.78, 0.005, 0.048, 0.05), (0, -0.83, 0.0, 0.025, 0.03), (0, -0.85, 0.0, 0, 0)],
    paint=PAINT,
    flippers=[((0.12, -0.22, -0.07), 0.24, 0.1, 40, 15), ((0.1, 0.3, -0.06), 0.36, 0.13, 50, 15)],
    tail_fin=[(0.8, -0.03), (0.96, 0.1), (0.99, 0.08), (1.0, -0.09), (0.98, -0.27), (0.93, -0.25), (0.86, -0.08)],
    teeth=[(-0.62, -0.81, 7, lambda t: 0.05 - 0.025 * t, -0.01, 0.005, 0.035)],
    eye=(0.06, -0.58, 0.075), eye_r=0.016,
    jaw_line=(-0.55, -0.84, -0.01, 0.06),
)

if __name__ == "__main__":
    nh.run(lambda: mr.build(SPEC), "Dakosaurus", **mr.PREVIEW)
