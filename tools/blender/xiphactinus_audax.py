"""
Procedural Xiphactinus audax (Late Cretaceous ichthyodectiform fish, Western Interior Seaway).

A giant predatory bony fish about 5-6 metres long, shaped like an enormous tarpon: a deep,
muscular body, a blunt head with an upturned, bulldog-like lower jaw armed with long fangs,
long sickle-shaped pectoral fins and a deeply forked tail. A famous Kansas fossil has a
2-metre Gillicus swallowed whole inside it. Steel-blue back, silver flanks, white belly.
Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/xiphactinus_audax.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Xiphactinus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.16, 0.24, 0.34)
FLANK = (0.70, 0.74, 0.78)
BELLY = (0.95, 0.95, 0.94)
FIN = (0.30, 0.36, 0.44)


def make():
    # tall, laterally compressed body: hw < hh
    axis = [(0.80, 0.0, 0.0, 0.0), (0.75, 0.0, 0.012, 0.035), (0.62, 0.0, 0.03, 0.06),
            (0.40, 0.0, 0.06, 0.12), (0.10, 0.0, 0.085, 0.17), (-0.20, 0.0, 0.09, 0.18),
            (-0.45, 0.0, 0.08, 0.15), (-0.62, 0.0, 0.065, 0.11), (-0.74, 0.01, 0.045, 0.07),
            (-0.80, 0.03, 0.0, 0.0)]
    jaw = [(-0.56, -0.07, 0.055, 0.03), (-0.68, -0.05, 0.045, 0.025), (-0.78, -0.02, 0.025, 0.018),
           (-0.83, 0.01, 0.0, 0.0)]
    s = tp.Spec(name="Xiphactinus", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY), power=2.0,
                jaw=jaw, hinge=(-0.56, -0.04), jaw_open=10, pivot="centre",
                eye=(0.05, -0.68, 0.04, 0.022), eye_col=(0.85, 0.80, 0.50), voxel=0.01, max_tris=10000)

    def crisp(mb, s):
        mr.tail_lobes(mb, 0.76, 0.0, (0.98, 0.26), (0.98, -0.26), FIN, thickness=0.014, chord=0.08)
        mr.fin(mb, [(0, 0.22, 0.15), (0, 0.34, 0.11)], [(0, 0.30, 0.28), (0, 0.38, 0.13)], FIN)     # dorsal
        mr.fin(mb, [(0, 0.30, -0.13), (0, 0.42, -0.09)], [(0, 0.38, -0.22), (0, 0.46, -0.10)], FIN)  # anal
        for sx in (1, -1):
            mr.fin(mb, [(sx * 0.07, -0.45, -0.08), (sx * 0.07, -0.40, -0.10)],
                   [(sx * 0.22, -0.25, -0.18), (sx * 0.20, -0.22, -0.19)], FIN, side=1)
        fangs = [(sx * 0.035, -0.74 + 0.04 * k, -0.04) for k in range(4) for sx in (1, -1)]
        cc.teeth_row(mb, fangs, 0.045, 0.008, down=False, rot=s._jaw_rot)
        up = [(sx * 0.04, -0.74 + 0.04 * k, -0.01) for k in range(4) for sx in (1, -1)]
        cc.teeth_row(mb, up, 0.025, 0.006, down=True)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Xiphactinus")
