"""
Procedural Squalicorax falcatus (Late Cretaceous anacoracid 'crow shark').

A 2.5-metre lamniform shark: a slim, torpedo body with a short, rounded snout, a tall
triangular first dorsal fin, long pectorals, a crescent tail with a longer upper lobe and
a mouth full of curved, saw-edged teeth. Dusky brown-grey back, a paler grey flank and a
white belly, dark fin tips.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/squalicorax_falcatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Squalicorax.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.26, 0.24, 0.22)
FLANK = (0.44, 0.43, 0.42)
BELLY = (0.94, 0.93, 0.90)
TIP = (0.10, 0.09, 0.09)


def paint(co, n):
    c = FLANK if n.z > -0.25 else BELLY
    c = nh.lerp(c, BACK, nh.smoothstep(0.2, 0.8, n.z))
    return cc.mottle(c, co, 0.05)


def fin_col(co, n):
    return TIP if abs(co.z) > 0.22 or abs(co.x) > 0.30 or co.y > 0.95 else BACK


def make():
    axis = [(0.80, 0.0, 0.0, 0.0), (0.72, 0.0, 0.016, 0.022), (0.52, 0.0, 0.04, 0.055),
            (0.25, 0.0, 0.09, 0.105), (-0.05, 0.0, 0.11, 0.12), (-0.35, 0.0, 0.10, 0.10),
            (-0.58, 0.0, 0.07, 0.07), (-0.72, 0.005, 0.045, 0.04), (-0.79, 0.01, 0.0, 0.0)]
    jaw = [(-0.52, -0.06, 0.06, 0.02), (-0.63, -0.055, 0.045, 0.016), (-0.70, -0.05, 0.0, 0.0)]
    s = tp.Spec(name="Squalicorax", axis=axis, paint=paint, power=2.0, jaw=jaw, hinge=(-0.52, -0.045),
                jaw_open=14, pivot="centre", eye=(0.05, -0.63, 0.025, 0.011), eye_col=(0.03, 0.03, 0.04),
                voxel=0.009, max_tris=9000)

    def crisp(mb, s):
        mr.tail_lobes(mb, 0.74, 0.0, (1.02, 0.30), (0.92, -0.16), fin_col, thickness=0.016, chord=0.08)
        mr.fin(mb, [(0, -0.16, 0.11), (0, 0.06, 0.09)], [(0, -0.02, 0.36), (0, 0.08, 0.10)], fin_col, thickness=0.016)
        mr.fin(mb, [(0, 0.50, 0.04), (0, 0.55, 0.035)], [(0, 0.54, 0.08), (0, 0.57, 0.035)], BACK)
        mr.fin(mb, [(0, 0.40, -0.05), (0, 0.46, -0.045)], [(0, 0.45, -0.10), (0, 0.48, -0.045)], BACK)
        for sx in (1, -1):
            mr.fin(mb, [(sx * 0.08, -0.32, -0.06), (sx * 0.08, -0.20, -0.07)],
                   [(sx * 0.34, -0.08, -0.17), (sx * 0.32, -0.05, -0.17)], fin_col, thickness=0.014, side=1)
            for k in range(5):
                p = (sx * (0.095 - 0.004 * k), -0.38 - 0.014 * k, 0.015)
                mb.add(nh.ellipsoid(p, (0.003, 0.004, 0.028), subdivisions=1), (0.18, 0.17, 0.16))
        up = [(sx * 0.05 * (1 - 0.1 * k), -0.62 - 0.016 * k, -0.05) for k in range(5) for sx in (1, -1)]
        cc.teeth_row(mb, up, 0.016, 0.007, down=True)
        lo = [(sx * 0.04 * (1 - 0.1 * k), -0.58 - 0.016 * k, -0.05) for k in range(4) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.014, 0.006, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Squalicorax")
