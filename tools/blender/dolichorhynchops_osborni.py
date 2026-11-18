"""
Procedural Dolichorhynchops osborni (Late Cretaceous polycotylid plesiosaur, Western Interior Seaway).

A 4.5-metre short-necked plesiosaur built for speed: a long, slender, gharial-like snout full
of needle teeth on a short neck, a compact teardrop body, four long, narrow, wing-like
flippers and a short tail with a small fin. Dark blue-grey above, a pale belly and light
speckles on the back.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/dolichorhynchops_osborni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dolichorhynchops.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.18, 0.24, 0.32)
FLANK = (0.36, 0.42, 0.50)
BELLY = (0.90, 0.90, 0.88)


def extra(co, n, c):
    return nh.lerp(c, (0.70, 0.74, 0.78), 0.35 * cc.spots(co, 45.0, 0.08) * nh.smoothstep(0.3, 0.8, n.z))


def make():
    axis = [(0.62, 0.0, 0.0, 0.0), (0.56, 0.0, 0.015, 0.02), (0.44, 0.0, 0.05, 0.05),
            (0.25, 0.0, 0.12, 0.09), (0.05, 0.0, 0.15, 0.11), (-0.15, 0.0, 0.13, 0.10),
            (-0.30, 0.01, 0.08, 0.07), (-0.40, 0.02, 0.055, 0.05), (-0.48, 0.025, 0.045, 0.042),
            (-0.56, 0.02, 0.03, 0.028), (-0.68, 0.012, 0.016, 0.016), (-0.82, 0.005, 0.011, 0.011),
            (-0.86, 0.004, 0.0, 0.0)]
    jaw = [(-0.52, -0.012, 0.03, 0.012), (-0.64, -0.008, 0.014, 0.007), (-0.80, -0.003, 0.009, 0.005),
           (-0.84, -0.002, 0.0, 0.0)]
    s = tp.Spec(name="Dolichorhynchops", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY, extra=extra, mottle=0.06),
                jaw=jaw, hinge=(-0.51, 0.0), jaw_open=10, pivot="centre",
                eye=(0.035, -0.53, 0.04, 0.012), eye_col=(0.8, 0.6, 0.2),
                disp=cc.scales_disp(0.001, 50.0), voxel=0.008, max_tris=11000)
    s.limbs = [mr.flipper([(0.11, -0.12, -0.04), (0.32, -0.10, -0.07), (0.52, -0.02, -0.08), (0.64, 0.06, -0.08)],
                          [0.05, 0.045, 0.025, 0.006], flat=0.18),
               mr.flipper([(0.10, 0.20, -0.04), (0.28, 0.24, -0.06), (0.46, 0.32, -0.07), (0.56, 0.38, -0.07)],
                          [0.045, 0.042, 0.022, 0.006], flat=0.18)]

    def crisp(mb, s):
        mr.fin(mb, [(0, 0.52, 0.01), (0, 0.62, 0.0)], [(0, 0.58, 0.07), (0, 0.66, 0.0)], BACK)
        up = [(sx * 0.012, -0.58 - 0.025 * k, -0.005) for k in range(10) for sx in (1, -1)]
        cc.teeth_row(mb, up, 0.014, 0.0025, down=True)
        lo = [(sx * 0.010, -0.59 - 0.025 * k, -0.006) for k in range(9) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.012, 0.0025, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Dolichorhynchops")
