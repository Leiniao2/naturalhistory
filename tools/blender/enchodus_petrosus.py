"""
Procedural Enchodus petrosus (Late Cretaceous aulopiform, Western Interior Seaway), the
"sabre-toothed herring".

A slender, 1.5-metre predatory fish: a long torpedo body, a large head with big eyes and a
long jaw, a pair of huge, curved fangs at the front of each jaw (the palatine and dentary
fangs) plus rows of smaller teeth, a tall first dorsal fin, a small adipose fin, low
pectoral and pelvic fins and a deeply forked tail. Dark blue-green back, bright silvery
flanks, white belly.
Swim style: faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/enchodus_petrosus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Enchodus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.10, 0.22, 0.26)
FLANK = (0.72, 0.76, 0.78)
BELLY = (0.95, 0.95, 0.93)
FIN = (0.32, 0.40, 0.42)


def make():
    axis = [(0.86, 0.0, 0.0, 0.0), (0.80, 0.0, 0.012, 0.03), (0.66, 0.0, 0.03, 0.05),
            (0.40, 0.0, 0.06, 0.09), (0.10, 0.0, 0.08, 0.12), (-0.20, 0.01, 0.08, 0.12),
            (-0.42, 0.02, 0.07, 0.10), (-0.58, 0.02, 0.05, 0.075), (-0.70, 0.015, 0.03, 0.045),
            (-0.76, 0.01, 0.0, 0.0)]
    jaw = [(-0.42, -0.06, 0.05, 0.022), (-0.58, -0.05, 0.04, 0.02), (-0.72, -0.03, 0.022, 0.014),
           (-0.79, -0.015, 0.0, 0.0)]
    s = tp.Spec(name="Enchodus", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY), power=2.0,
                jaw=jaw, hinge=(-0.42, -0.03), jaw_open=18, pivot="centre",
                eye=(0.05, -0.56, 0.035, 0.03), eye_col=(0.90, 0.85, 0.55), voxel=0.009, max_tris=9000)

    def crisp(mb, s):
        mr.tail_lobes(mb, 0.82, 0.0, (1.06, 0.24), (1.06, -0.24), FIN, thickness=0.012, chord=0.07)
        mr.fin(mb, [(0, -0.12, 0.11), (0, 0.02, 0.11)], [(0, -0.04, 0.30), (0, 0.06, 0.13)], FIN)      # tall dorsal
        mr.fin(mb, [(0, 0.48, 0.07), (0, 0.54, 0.055)], [(0, 0.52, 0.11), (0, 0.56, 0.06)], FIN)       # adipose
        mr.fin(mb, [(0, 0.42, -0.07), (0, 0.56, -0.05)], [(0, 0.50, -0.14), (0, 0.60, -0.06)], FIN)    # anal
        for sx in (1, -1):
            mr.fin(mb, [(sx * 0.05, -0.38, -0.07), (sx * 0.05, -0.34, -0.08)],
                   [(sx * 0.16, -0.24, -0.13), (sx * 0.14, -0.22, -0.13)], FIN, side=1)
            mr.fin(mb, [(sx * 0.04, 0.12, -0.10), (sx * 0.04, 0.16, -0.10)],
                   [(sx * 0.10, 0.24, -0.15), (sx * 0.09, 0.26, -0.14)], FIN, side=1)
        # the sabre fangs: one big pair at the front of the upper jaw, one in the lower
        for sx in (1, -1):
            p = Vector((sx * 0.018, -0.72, -0.01))
            mb.add(cc.curved_cone(p, p + Vector((0, -0.01, -0.04)), p + Vector((0, 0.01, -0.075)), 0.009), cc.TOOTH)
        lo = [(sx * 0.016, -0.74, -0.03) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.06, 0.008, down=False, rot=s._jaw_rot)
        small = [(sx * 0.035, -0.66 + 0.04 * k, -0.02) for k in range(4) for sx in (1, -1)]
        cc.teeth_row(mb, small, 0.015, 0.004, down=True)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Enchodus")
