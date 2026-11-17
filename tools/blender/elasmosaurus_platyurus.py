"""
Procedural Elasmosaurus platyurus (Late Cretaceous elasmosaurid plesiosaur, Kansas).

The classic long-necked plesiosaur, about 10-11 metres long, of which some 7 metres was neck
(72 vertebrae, more than any other known animal). A small head with long interlocking teeth
for snaring fish, a broad, flat, compact body, four long wing-like flippers and a short tail.
Brown-grey above with pale spots, cream below.
Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/elasmosaurus_platyurus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Elasmosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.30, 0.26, 0.22)
FLANK = (0.46, 0.41, 0.35)
BELLY = (0.86, 0.82, 0.72)


def extra(co, n, c):
    return nh.lerp(c, (0.78, 0.72, 0.60), 0.6 * cc.spots(co, 16.0, 0.16) * nh.smoothstep(0.2, 0.7, n.z))


def make():
    axis = [(0.62, -0.01, 0.0, 0.0), (0.55, 0.0, 0.02, 0.018), (0.42, 0.0, 0.06, 0.04),
            (0.28, 0.0, 0.13, 0.075), (0.10, 0.0, 0.16, 0.09), (-0.08, 0.0, 0.14, 0.085),
            (-0.20, 0.01, 0.07, 0.055), (-0.35, 0.03, 0.04, 0.036), (-0.60, 0.07, 0.03, 0.028),
            (-0.85, 0.10, 0.025, 0.024), (-1.05, 0.11, 0.022, 0.022), (-1.16, 0.11, 0.03, 0.028),
            (-1.22, 0.105, 0.022, 0.02), (-1.28, 0.10, 0.0, 0.0)]
    s = tp.Spec(name="Elasmosaurus", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY, extra=extra, mottle=0.08),
                pivot="centre", eye=(0.024, -1.17, 0.125, 0.008), eye_col=(0.7, 0.5, 0.2),
                disp=cc.scales_disp(0.0012, 50.0), voxel=0.009, max_tris=11000)
    s.limbs = [mr.flipper([(0.10, -0.06, -0.03), (0.30, -0.03, -0.06), (0.48, 0.05, -0.08), (0.58, 0.12, -0.08)],
                          [0.05, 0.05, 0.03, 0.008], flat=0.2),
               mr.flipper([(0.09, 0.26, -0.03), (0.26, 0.30, -0.05), (0.40, 0.37, -0.07), (0.48, 0.42, -0.07)],
                          [0.045, 0.042, 0.025, 0.007], flat=0.2)]

    def crisp(mb, s):
        teeth = [(sx * 0.014, -1.22 - 0.012 * k, 0.09) for k in range(4) for sx in (1, -1)]
        cc.teeth_row(mb, teeth, 0.018, 0.003, down=True)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Elasmosaurus")
