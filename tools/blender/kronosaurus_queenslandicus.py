"""
Procedural Kronosaurus queenslandicus (Early Cretaceous pliosaur, Queensland, Australia).

A giant short-necked plesiosaur about 9-10 metres long with a skull over 2 metres long:
enormous jaws lined with big conical teeth, a short thick neck, a teardrop body driven by
four powerful flippers and a short tail. Stomach contents include turtles and other
plesiosaurs. Dark brown-grey above with darker blotches, a pale belly.
Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/kronosaurus_queenslandicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Kronosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.24, 0.22, 0.21)
FLANK = (0.38, 0.36, 0.33)
BELLY = (0.82, 0.80, 0.74)


def extra(co, n, c):
    return nh.lerp(c, (0.12, 0.11, 0.10), 0.5 * cc.spots(co, 8.0, 0.22) * nh.smoothstep(0.0, 0.5, n.z))


def make():
    axis = [(0.85, 0.0, 0.0, 0.0), (0.78, 0.0, 0.02, 0.02), (0.62, 0.0, 0.07, 0.06),
            (0.40, 0.0, 0.16, 0.12), (0.15, 0.0, 0.20, 0.15), (-0.10, 0.0, 0.18, 0.14),
            (-0.30, 0.01, 0.13, 0.10), (-0.42, 0.02, 0.11, 0.09), (-0.55, 0.03, 0.10, 0.075),
            (-0.75, 0.025, 0.075, 0.055), (-0.92, 0.015, 0.05, 0.04), (-1.02, 0.005, 0.03, 0.025),
            (-1.06, 0.0, 0.0, 0.0)]
    jaw = [(-0.45, -0.06, 0.10, 0.04), (-0.65, -0.055, 0.075, 0.032), (-0.85, -0.045, 0.05, 0.025),
           (-0.98, -0.035, 0.03, 0.016), (-1.03, -0.03, 0.0, 0.0)]
    s = tp.Spec(name="Kronosaurus", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY, extra=extra, mottle=0.1),
                jaw=jaw, hinge=(-0.45, -0.03), jaw_open=14, pivot="centre",
                eye=(0.065, -0.56, 0.08, 0.016), eye_col=(0.8, 0.6, 0.15),
                disp=cc.scales_disp(0.0012, 45.0), voxel=0.011, max_tris=12000)
    s.limbs = [mr.flipper([(0.14, -0.12, -0.06), (0.35, -0.08, -0.10), (0.55, 0.02, -0.12), (0.65, 0.08, -0.12)],
                          [0.07, 0.07, 0.04, 0.01], flat=0.2),
               mr.flipper([(0.13, 0.38, -0.05), (0.32, 0.42, -0.08), (0.50, 0.50, -0.10), (0.58, 0.55, -0.10)],
                          [0.065, 0.065, 0.035, 0.01], flat=0.2)]

    def crisp(mb, s):
        up = [(sx * 0.06, -0.62 - 0.05 * k, -0.035) for k in range(8) for sx in (1, -1)]
        cc.teeth_row(mb, up, 0.04, 0.011, down=True)
        lo = [(sx * 0.055, -0.64 - 0.045 * k, -0.03) for k in range(7) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.035, 0.01, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Kronosaurus")
