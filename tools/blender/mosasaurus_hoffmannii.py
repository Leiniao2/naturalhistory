"""
Procedural Mosasaurus hoffmannii (Late Cretaceous mosasaur, Maastricht and worldwide seas).

The largest mosasaur, a marine lizard up to about 12-17 metres long: a massive, deep skull
with a slightly open mouth of thick conical teeth, a long barrel body, four paddle limbs and
a tail ending in a shark-like downturned fluke. Dark charcoal-green above, pale below.
Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/mosasaurus_hoffmannii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mosasaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.13, 0.16, 0.14)
FLANK = (0.30, 0.34, 0.30)
BELLY = (0.85, 0.84, 0.78)


def make():
    axis = [(1.05, -0.05, 0.0, 0.0), (0.95, -0.03, 0.012, 0.03), (0.75, 0.0, 0.03, 0.06),
            (0.45, 0.0, 0.06, 0.09), (0.15, 0.0, 0.11, 0.12), (-0.15, 0.0, 0.13, 0.13),
            (-0.40, 0.01, 0.10, 0.10), (-0.52, 0.02, 0.085, 0.085), (-0.62, 0.03, 0.08, 0.075),
            (-0.75, 0.025, 0.065, 0.06), (-0.88, 0.015, 0.045, 0.045), (-0.97, 0.005, 0.025, 0.028),
            (-1.00, 0.0, 0.0, 0.0)]
    jaw = [(-0.56, -0.04, 0.07, 0.03), (-0.70, -0.04, 0.055, 0.025), (-0.85, -0.035, 0.04, 0.02),
           (-0.95, -0.03, 0.02, 0.012), (-0.98, -0.03, 0.0, 0.0)]
    s = tp.Spec(name="Mosasaurus", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY, mottle=0.1),
                jaw=jaw, hinge=(-0.56, -0.02), jaw_open=10, pivot="centre",
                eye=(0.055, -0.70, 0.05, 0.014), eye_col=(0.75, 0.55, 0.15),
                disp=cc.scales_disp(0.0015, 50.0), voxel=0.011, max_tris=12000)
    s.limbs = [mr.flipper([(0.08, -0.28, -0.05), (0.22, -0.24, -0.08), (0.34, -0.16, -0.1)], [0.05, 0.045, 0.012]),
               mr.flipper([(0.07, 0.30, -0.05), (0.18, 0.36, -0.08), (0.27, 0.44, -0.09)], [0.04, 0.035, 0.01])]

    def crisp(mb, s):
        mr.tail_lobes(mb, 0.95, -0.03, (1.12, 0.10), (1.20, -0.22), FLANK, thickness=0.02, chord=0.1)
        up = [(sx * 0.055, -0.62 - 0.045 * k, -0.025) for k in range(8) for sx in (1, -1)]
        cc.teeth_row(mb, up, 0.03, 0.008, down=True)
        lo = [(sx * 0.045, -0.64 - 0.04 * k, -0.02) for k in range(7) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.025, 0.007, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Mosasaurus")
