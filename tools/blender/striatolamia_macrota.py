"""
Procedural Striatolamia macrota (Paleocene-Eocene sand tiger shark, worldwide warm seas) for
map colonies. A lamniform shark of about 3 m, a relative of today's sand tiger: a bulky body
with a pointed, conical snout, a jaw bristling with long, slender, finely striated teeth that
stick out even when the mouth is shut, two dorsal fins of similar size set well back, and an
asymmetric tail with a long upper lobe and a short lower one. Grey-brown back with scattered
darker spots, pale belly.
Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/striatolamia_macrota.py -- [--render out.png]

Output: Assets/Resources/Models/Species/StriatolamiaMacrota.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.32, 0.29, 0.24)
FLANK = (0.50, 0.47, 0.41)
BELLY = (0.90, 0.88, 0.83)
FIN = (0.30, 0.27, 0.23)
SPOT = (0.20, 0.17, 0.14)


def paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.55, -0.1, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.2, 0.8, n.z))
    if n.z > -0.2 and co.y > -0.55 and cc.spots(co, 30.0, 0.3) > 0.5:
        c = nh.lerp(c, SPOT, 0.75)
    return cc.mottle(c, co, 0.05)


def make():
    # bulky, deep-bellied body with a conical snout
    axis = [(0.80, 0.02, 0.0, 0.0), (0.72, 0.02, 0.02, 0.026), (0.52, 0.01, 0.055, 0.07),
            (0.22, 0.0, 0.12, 0.14), (-0.08, -0.01, 0.15, 0.165), (-0.36, 0.0, 0.13, 0.14),
            (-0.58, 0.01, 0.085, 0.085), (-0.74, 0.02, 0.045, 0.04), (-0.86, 0.03, 0.0, 0.0)]
    jaw = [(-0.50, -0.075, 0.08, 0.022), (-0.62, -0.07, 0.06, 0.018), (-0.71, -0.06, 0.0, 0.0)]
    s = tp.Spec(name="StriatolamiaMacrota", axis=axis, paint=paint, power=2.0, jaw=jaw, hinge=(-0.50, -0.055),
                jaw_open=18, pivot="centre", eye=(0.056, -0.67, 0.035, 0.014), eye_col=(0.03, 0.03, 0.03),
                voxel=0.01, max_tris=10000)

    def crisp(mb, s):
        # long upper lobe, short lower lobe
        mr.tail_lobes(mb, 0.74, 0.02, (1.06, 0.24), (0.88, -0.13), FIN, thickness=0.018, chord=0.09)
        # two dorsals of similar size, the first set well back
        mr.fin(mb, [(0, -0.02, 0.15), (0, 0.16, 0.12)], [(0, 0.12, 0.33), (0, 0.18, 0.13)], FIN, thickness=0.018)
        mr.fin(mb, [(0, 0.34, 0.08), (0, 0.48, 0.055)], [(0, 0.44, 0.24), (0, 0.5, 0.06)], FIN, thickness=0.016)
        mr.fin(mb, [(0, 0.36, -0.08), (0, 0.48, -0.055)], [(0, 0.45, -0.2), (0, 0.5, -0.06)], FIN, thickness=0.016)
        for sx in (1, -1):
            mr.fin(mb, [(sx * 0.11, -0.32, -0.08), (sx * 0.11, -0.2, -0.09)],
                   [(sx * 0.33, -0.12, -0.21), (sx * 0.32, -0.08, -0.21)], FIN, thickness=0.015, side=1)
            mr.fin(mb, [(sx * 0.08, 0.14, -0.12), (sx * 0.07, 0.24, -0.1)],
                   [(sx * 0.15, 0.27, -0.2), (sx * 0.13, 0.3, -0.17)], FIN, thickness=0.012, side=1)
            for k in range(5):
                p = Vector((sx * (0.13 - 0.006 * k), -0.4 - 0.022 * k, 0.0))
                mb.add(nh.ellipsoid(p, (0.003, 0.004, 0.04), subdivisions=1), (0.18, 0.15, 0.12))
        # long, slender, ragged teeth sticking out at odd angles
        up = []
        for k in range(7):
            for sx in (1, -1):
                up.append((sx * 0.065 * (1 - 0.12 * k), -0.6 - 0.017 * k, -0.06))
        cc.teeth_row(mb, up, 0.038, 0.005, down=True)
        lo = [(sx * 0.055 * (1 - 0.12 * k), -0.56 - 0.018 * k, -0.06) for k in range(6) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.034, 0.005, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "StriatolamiaMacrota")
