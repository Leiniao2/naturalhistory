"""
Procedural Hesperornis regalis (Late Cretaceous hesperornithine bird, Western Interior
Seaway), swimming.

A flightless, loon-like diving bird up to about 1.8 metres long: a long neck, a long beak
with small teeth set in grooves, wings reduced to tiny stubs, and powerful legs set far back
on the body ending in big lobed toes for foot-propelled dives after fish. Dark grey-brown
back, white underside and throat. Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/hesperornis_regalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hesperornis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.20, 0.20, 0.21)
FLANK = (0.36, 0.34, 0.32)
WHITE = (0.92, 0.91, 0.88)
BEAK = (0.78, 0.62, 0.30)
FOOT = (0.30, 0.28, 0.22)


def paint(co, n):
    c = cc.countershade(n, WHITE, FLANK, BACK, lo=-0.4, mid=0.0, hi=0.6)
    if co.y < -0.45:
        c = nh.lerp(c, BEAK, nh.smoothstep(-0.48, -0.55, co.y))
    return cc.mottle(c, co, 0.06)


def make():
    axis = [(0.48, 0.02, 0.0, 0.0), (0.44, 0.02, 0.03, 0.02), (0.32, 0.0, 0.09, 0.07),
            (0.12, 0.0, 0.13, 0.10), (-0.08, 0.01, 0.11, 0.09), (-0.20, 0.04, 0.05, 0.05),
            (-0.32, 0.08, 0.035, 0.035), (-0.42, 0.10, 0.035, 0.035), (-0.48, 0.10, 0.028, 0.026),
            (-0.60, 0.09, 0.012, 0.011), (-0.72, 0.08, 0.0, 0.0)]
    s = tp.Spec(name="Hesperornis", axis=axis, paint=paint, pivot="centre",
                eye=(0.026, -0.455, 0.112, 0.009), eye_col=(0.75, 0.15, 0.1),
                disp=cc.fuzz_disp(0.002, 60.0), voxel=0.009, max_tris=9000)
    # legs splayed out sideways and back from the rear of the body
    s.tubes.append(([(0.07, 0.25, -0.02), (0.16, 0.32, -0.04), (0.24, 0.40, -0.04), (0.28, 0.48, -0.04)],
                    [0.04, 0.025, 0.015, 0.01], True))

    def crisp(mb, s):
        for sx in (1, -1):
            base = Vector((sx * 0.28, 0.48, -0.04))
            for k, ang in enumerate((-0.35, 0.0, 0.35)):
                d = Vector((sx * (0.25 + ang), 1.0, 0.0)).normalized()
                tip = base + d * 0.12
                mb.add(cc.ribbon([(base, base + Vector((0, 0, 0.0))), (tip - Vector((sx * 0.02, 0, 0)), tip + Vector((sx * 0.02, 0, 0)))],
                                 0.008), FOOT)
            mb.add(nh.ellipsoid((sx * 0.12, -0.02, 0.02), (0.012, 0.04, 0.008), subdivisions=1), FLANK)   # wing stub
        teeth = [(sx * 0.012, -0.52 - 0.03 * k, 0.083) for k in range(4) for sx in (1, -1)]
        cc.teeth_row(mb, teeth, 0.007, 0.0025, down=True)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Hesperornis")
