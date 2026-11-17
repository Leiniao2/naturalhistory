"""
Procedural Iocrinus subcrassus (Late Ordovician disparid crinoid of the Cincinnati region)
for the map. A stalked sea lily: a root-like holdfast, a long column of pentagonal,
ridged columnals, a small cup, and five robust arms that fork repeatedly into a fan for
catching food particles from the current. Pale mauve-grey (colour conjectural).
Built with nh_ord_echino.py.

Usage:
  blender --background --python tools/blender/iocrinus_subcrassus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/IocrinusSubcrassus.fbx (Fixed style: pivot on the sea floor, z = 0)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

if __name__ == "__main__":
    nh.run(lambda: ec.crinoid("IocrinusSubcrassus", forks=2, stem_h=0.9, stem_r=0.045, arm_len=0.85, spread=0.75, cup_h=0.15), "IocrinusSubcrassus", **ec.VIEWS)
