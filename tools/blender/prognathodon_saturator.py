"""
Procedural Prognathodon saturator (latest Cretaceous mosasaur, the Netherlands).

A 12-metre heavy-jawed mosasaur: a massive, short, very deep skull with a blunt snout,
thick conical crushing teeth, a bulky body, four paddles and a downturned tail with a
shark-like upper fluke. Dark olive-grey back with darker blotches, pale belly, scarred
flanks.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/prognathodon_saturator.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Prognathodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.22, 0.25, 0.22)
FLANK = (0.38, 0.42, 0.38)
BELLY = (0.88, 0.86, 0.80)
SCAR = (0.66, 0.64, 0.58)


def extra(co, n, c):
    c = nh.lerp(c, (0.12, 0.14, 0.12), 0.55 * cc.spots(co, 8.0, 0.22) * nh.smoothstep(0.0, 0.5, n.z))
    scar = cc.stripes(co.__class__((co.x * 3.0, co.y + co.z * 0.6, co.z)), 34.0, sharp=(0.93, 0.98))
    return nh.lerp(c, SCAR, 0.6 * scar * nh.smoothstep(0.2, 0.4, co.y) * (1 - nh.smoothstep(0.5, 0.6, co.y)))


def make():
    axis = [(1.05, -0.05, 0.0, 0.0), (0.95, -0.03, 0.012, 0.03), (0.75, 0.0, 0.03, 0.06),
            (0.45, 0.0, 0.065, 0.09), (0.15, 0.0, 0.11, 0.115), (-0.15, 0.0, 0.12, 0.12),
            (-0.36, 0.01, 0.10, 0.10), (-0.46, 0.025, 0.09, 0.09), (-0.56, 0.03, 0.085, 0.08),
            (-0.68, 0.025, 0.07, 0.065), (-0.79, 0.015, 0.05, 0.05), (-0.85, 0.005, 0.03, 0.035),
            (-0.87, 0.0, 0.0, 0.0)]
    jaw = [(-0.47, -0.06, 0.08, 0.04), (-0.60, -0.06, 0.065, 0.034), (-0.74, -0.05, 0.048, 0.028),
           (-0.82, -0.045, 0.03, 0.02), (-0.85, -0.04, 0.0, 0.0)]
    s = tp.Spec(name="Prognathodon", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY, extra=extra, mottle=0.08),
                jaw=jaw, hinge=(-0.47, -0.03), jaw_open=16, pivot="centre",
                eye=(0.06, -0.58, 0.06, 0.014), eye_col=(0.85, 0.65, 0.2),
                disp=cc.scales_disp(0.0015, 50.0), voxel=0.011, max_tris=12000)
    s.limbs = [mr.flipper([(0.08, -0.26, -0.05), (0.21, -0.22, -0.09), (0.32, -0.14, -0.10)], [0.05, 0.045, 0.012]),
               mr.flipper([(0.07, 0.30, -0.05), (0.17, 0.35, -0.07), (0.25, 0.42, -0.08)], [0.04, 0.035, 0.01])]

    def crisp(mb, s):
        mr.tail_lobes(mb, 0.96, -0.03, (1.10, 0.10), (1.20, -0.22), FLANK, thickness=0.02, chord=0.1)
        up = [(sx * 0.06 * (1 - 0.05 * k), -0.55 - 0.045 * k, -0.045) for k in range(7) for sx in (1, -1)]
        cc.teeth_row(mb, up, 0.03, 0.011, down=True)
        lo = [(sx * 0.055 * (1 - 0.06 * k), -0.56 - 0.045 * k, -0.04) for k in range(6) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.028, 0.011, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Prognathodon")
