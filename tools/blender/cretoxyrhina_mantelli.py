"""
Procedural Cretoxyrhina mantelli (Late Cretaceous lamniform shark, worldwide seas), the
'Ginsu shark'.

A big, fast mackerel shark about 7-8 metres long, built like a stocky great white: a conical
snout, rows of smooth-edged blade teeth, a tall triangular first dorsal fin, broad pectoral
fins and a crescent-shaped tail with a keeled base. Bite marks show it attacked mosasaurs,
plesiosaurs and big fish. Grey above, sharply white below.
Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/cretoxyrhina_mantelli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cretoxyrhina.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.30, 0.33, 0.36)
FLANK = (0.42, 0.45, 0.48)
BELLY = (0.94, 0.94, 0.92)


def paint(co, n):
    c = FLANK if n.z > -0.25 else BELLY
    c = nh.lerp(c, BACK, nh.smoothstep(0.2, 0.8, n.z))
    return cc.mottle(c, co, 0.05)


def make():
    axis = [(0.82, 0.0, 0.0, 0.0), (0.74, 0.0, 0.02, 0.03), (0.55, 0.0, 0.05, 0.07),
            (0.25, 0.0, 0.12, 0.14), (-0.05, 0.0, 0.15, 0.16), (-0.35, 0.0, 0.13, 0.14),
            (-0.60, 0.0, 0.09, 0.09), (-0.75, 0.01, 0.055, 0.05), (-0.84, 0.02, 0.0, 0.0)]
    jaw = [(-0.52, -0.08, 0.08, 0.025), (-0.64, -0.075, 0.06, 0.02), (-0.72, -0.07, 0.0, 0.0)]
    s = tp.Spec(name="Cretoxyrhina", axis=axis, paint=paint, power=2.0, jaw=jaw, hinge=(-0.52, -0.06),
                jaw_open=12, pivot="centre", eye=(0.065, -0.66, 0.035, 0.012), eye_col=(0.03, 0.03, 0.04),
                voxel=0.01, max_tris=10000)
    s.blobs.append(((0.05, 0.72, 0.0), (0.02, 0.08, 0.015), True))   # caudal keels

    def crisp(mb, s):
        mr.tail_lobes(mb, 0.76, 0.0, (1.00, 0.30), (0.96, -0.26), FLANK, thickness=0.02, chord=0.09)
        mr.fin(mb, [(0, -0.15, 0.15), (0, 0.10, 0.12)], [(0, 0.02, 0.40), (0, 0.10, 0.14)], BACK, thickness=0.02)
        mr.fin(mb, [(0, 0.52, 0.06), (0, 0.58, 0.05)], [(0, 0.56, 0.11), (0, 0.60, 0.05)], BACK)
        for sx in (1, -1):
            mr.fin(mb, [(sx * 0.11, -0.32, -0.08), (sx * 0.11, -0.18, -0.09)],
                   [(sx * 0.42, -0.05, -0.20), (sx * 0.40, -0.02, -0.20)], FLANK, thickness=0.018, side=1)
            for k in range(7):
                p = Vector((sx * (0.13 - 0.005 * k), -0.36 - 0.015 * k, 0.02 + 0.004 * k))
                mb.add(nh.ellipsoid(p, (0.003, 0.004, 0.035), subdivisions=1), (0.18, 0.2, 0.22))
        up = [(sx * 0.07 * (1 - 0.1 * k), -0.62 - 0.02 * k, -0.06) for k in range(6) for sx in (1, -1)]
        cc.teeth_row(mb, up, 0.025, 0.009, down=True)
        lo = [(sx * 0.055 * (1 - 0.1 * k), -0.58 - 0.02 * k, -0.06) for k in range(5) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.02, 0.008, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Cretoxyrhina")
