"""
Procedural Pliosaurus funkei (Late Jurassic pliosaurid, Svalbard, Norway; "Predator X")
for the map (Swim style).

One of the largest pliosaurs, perhaps 10-12 m long: a huge, broad-backed triangular skull
about 2 m long tapering to a narrower snout, jaws lined with big, ridged conical teeth
(the longest at the front), a short, thick neck, a heavy teardrop body, four very large
hydrofoil flippers (the hind pair slightly larger) and a short tail. Dark blue-grey back
with pale speckles, grey flanks and a pale belly (colour unknown). Built with
nh_cre_tetrapod / nh_cre_marine like Kronosaurus. Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/pliosaurus_funkei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pliosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.15, 0.19, 0.24)
FLANK = (0.32, 0.36, 0.40)
BELLY = (0.84, 0.83, 0.78)
SPECK = (0.62, 0.66, 0.68)


def extra(co, n, c):
    return nh.lerp(c, SPECK, 0.35 * cc.spots(co, 30.0, 0.06) * nh.smoothstep(0.1, 0.6, n.z))


def make():
    axis = [(0.80, 0.0, 0.0, 0.0), (0.72, 0.0, 0.025, 0.022), (0.55, 0.0, 0.08, 0.07),
            (0.32, 0.0, 0.18, 0.14), (0.08, 0.0, 0.22, 0.165), (-0.16, 0.0, 0.2, 0.155),
            (-0.34, 0.01, 0.15, 0.115), (-0.44, 0.02, 0.135, 0.1), (-0.54, 0.03, 0.13, 0.085),
            (-0.72, 0.03, 0.1, 0.065), (-0.9, 0.02, 0.065, 0.045), (-1.04, 0.01, 0.04, 0.03),
            (-1.1, 0.005, 0.025, 0.02), (-1.13, 0.0, 0.0, 0.0)]
    jaw = [(-0.42, -0.065, 0.125, 0.045), (-0.62, -0.06, 0.1, 0.036), (-0.84, -0.05, 0.065, 0.028),
           (-1.0, -0.04, 0.04, 0.018), (-1.09, -0.035, 0.0, 0.0)]
    s = tp.Spec(name="Pliosaurus", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY, extra=extra, mottle=0.08),
                jaw=jaw, hinge=(-0.42, -0.03), jaw_open=16, pivot="centre",
                eye=(0.07, -0.55, 0.085, 0.017), eye_col=(0.85, 0.65, 0.2),
                disp=cc.scales_disp(0.0012, 45.0), voxel=0.011, max_tris=13000)
    s.limbs = [mr.flipper([(0.16, -0.14, -0.06), (0.4, -0.1, -0.11), (0.62, 0.0, -0.13), (0.74, 0.07, -0.13)],
                          [0.08, 0.075, 0.045, 0.01], flat=0.2),
               mr.flipper([(0.15, 0.34, -0.05), (0.38, 0.39, -0.09), (0.6, 0.48, -0.11), (0.7, 0.54, -0.11)],
                          [0.078, 0.075, 0.042, 0.01], flat=0.2)]

    def crisp(mb, s):
        up = [(sx * (0.085 - 0.05 * k / 9), -0.6 - 0.052 * k, -0.035) for k in range(10) for sx in (1, -1)]
        cc.teeth_row(mb, up, 0.045, 0.012, down=True)
        lo = [(sx * (0.08 - 0.05 * k / 8), -0.62 - 0.05 * k, -0.03) for k in range(9) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.04, 0.011, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Pliosaurus")
