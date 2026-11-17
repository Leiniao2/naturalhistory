"""
Procedural Tylosaurus proriger (Late Cretaceous mosasaur, Western Interior Seaway, Kansas).

A huge, slender mosasaur about 13 metres long, recognisable by the long, toothless, bony
rostrum that projects ahead of its teeth like a battering ram. Long low skull, a slender body,
paddle limbs and a downturned tail fluke. Stomach contents show it ate fish, sharks, sea
birds, plesiosaurs and other mosasaurs. Blue-grey above with faint darker mottling, white
below. Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/tylosaurus_proriger.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Tylosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.22, 0.28, 0.36)
FLANK = (0.40, 0.46, 0.52)
BELLY = (0.90, 0.90, 0.88)


def extra(co, n, c):
    return nh.lerp(c, (0.14, 0.18, 0.24), 0.5 * cc.spots(co, 9.0, 0.2) * nh.smoothstep(0.0, 0.5, n.z))


def make():
    axis = [(1.10, -0.04, 0.0, 0.0), (1.0, -0.02, 0.01, 0.025), (0.80, 0.0, 0.025, 0.05),
            (0.50, 0.0, 0.05, 0.075), (0.20, 0.0, 0.085, 0.095), (-0.10, 0.0, 0.10, 0.10),
            (-0.35, 0.01, 0.08, 0.08), (-0.47, 0.02, 0.065, 0.065), (-0.57, 0.025, 0.06, 0.055),
            (-0.72, 0.02, 0.045, 0.042), (-0.86, 0.012, 0.03, 0.03), (-0.97, 0.005, 0.02, 0.02),
            (-1.02, 0.0, 0.0, 0.0)]
    jaw = [(-0.51, -0.035, 0.055, 0.022), (-0.66, -0.035, 0.042, 0.018), (-0.82, -0.03, 0.028, 0.014),
           (-0.90, -0.028, 0.0, 0.0)]
    s = tp.Spec(name="Tylosaurus", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY, extra=extra, mottle=0.08),
                jaw=jaw, hinge=(-0.51, -0.015), jaw_open=9, pivot="centre",
                eye=(0.045, -0.64, 0.04, 0.012), eye_col=(0.8, 0.6, 0.2),
                disp=cc.scales_disp(0.0015, 50.0), voxel=0.01, max_tris=12000)
    s.limbs = [mr.flipper([(0.06, -0.24, -0.04), (0.18, -0.20, -0.07), (0.28, -0.13, -0.08)], [0.04, 0.036, 0.01]),
               mr.flipper([(0.05, 0.28, -0.04), (0.14, 0.33, -0.06), (0.22, 0.40, -0.07)], [0.032, 0.028, 0.008])]

    def crisp(mb, s):
        mr.tail_lobes(mb, 1.0, -0.02, (1.16, 0.08), (1.24, -0.20), FLANK, thickness=0.018, chord=0.09)
        up = [(sx * 0.04, -0.58 - 0.04 * k, -0.02) for k in range(7) for sx in (1, -1)]
        cc.teeth_row(mb, up, 0.022, 0.006, down=True)
        lo = [(sx * 0.035, -0.60 - 0.038 * k, -0.018) for k in range(6) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.02, 0.006, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Tylosaurus")
