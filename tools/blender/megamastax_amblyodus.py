"""
Procedural Megamastax amblyodus (late Silurian bony fish from the Kuanti Formation of
Qujing, Yunnan, China, about 423 million years old, estimated about 1 m long) for map
colonies (Swim style).

Megamastax ("big mouth") is known only from large lower jaws and a jaw bone carrying
blunt, crushing teeth, so its body is reconstructed after its close relative Guiyu:
this script reuses guiyu_oneiros.py (median dorsal plates and spines, rhombic scales,
heterocercal tail) with a larger, deeper and broader head and a darker, greenish-grey
colouring, to read as a heavier predator.

Usage:
  blender --background --python tools/blender/megamastax_amblyodus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MegamastaxAmblyodus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import guiyu_oneiros as gy  # noqa: E402

gy.NAME = "MegamastaxAmblyodus"
gy.BACK = (0.17, 0.20, 0.17)
gy.FLANK = (0.36, 0.40, 0.34)
gy.BELLY = (0.72, 0.72, 0.62)
gy.BLOTCH = (0.10, 0.12, 0.10)
gy.BONE = (0.40, 0.40, 0.33)
gy.BONE_DARK = (0.22, 0.23, 0.19)
gy.FIN = (0.30, 0.32, 0.27)
gy.FIN_EDGE = (0.50, 0.52, 0.45)
gy.PROF = ef.Profile([
    (-0.80, 0.014, 0.014, 0.016, -0.014),
    (-0.775, 0.065, 0.065, 0.060, -0.004),
    (-0.72, 0.115, 0.115, 0.095, 0.006),
    (-0.62, 0.150, 0.150, 0.130, 0.012),
    (-0.48, 0.160, 0.170, 0.145, 0.018),
    (-0.30, 0.145, 0.168, 0.142, 0.020),
    (-0.10, 0.122, 0.142, 0.120, 0.022),
    (0.10, 0.092, 0.110, 0.095, 0.030),
    (0.30, 0.058, 0.072, 0.062, 0.048),
    (0.42, 0.042, 0.052, 0.044, 0.070),
    (0.60, 0.024, 0.030, 0.024, 0.128),
    (0.80, 0.004, 0.006, 0.005, 0.215),
], power=lambda y: 2.5 if y < -0.5 else 2.15)

if __name__ == "__main__":
    nh.run(gy.build, gy.NAME, **ef.PREVIEW)
