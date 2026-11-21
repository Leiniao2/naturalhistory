"""
Procedural great white shark (Carcharodon carcharias, Pliocene/Pleistocene to
today, temperate and subtropical seas worldwide) for map colonies.

The largest predatory fish alive, females up to about 6 m and 2 tonnes: a
heavy, spindle-shaped body, a conical snout, black eyes, big triangular
saw-edged teeth, long pectoral fins with black tips, a tall triangular first
dorsal fin and a crescent tail with nearly equal lobes. It ambushes seals from
below. Slate grey above, sharply white below.
Built like carcharodon_hastalis.py with the Cretaceous swimmer helpers
(nh_cre_tetrapod / nh_cre_marine). Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/carcharodon_carcharias.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CarcharodonCarcharias.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.30, 0.32, 0.35)     # slate grey
FLANK = (0.45, 0.47, 0.50)
BELLY = (0.95, 0.95, 0.93)
FIN = (0.32, 0.34, 0.37)
TIP = (0.05, 0.05, 0.06)


def paint(co, n):
    # sharp, irregular line between the grey back and the white belly
    edge = -0.12 + 0.12 * __import__('mathutils').noise.noise(Vector((0, co.y * 6.0, 0.3)))
    c = FLANK if n.z > edge else BELLY
    if co.x ** 2 > 0.03 and co.z < -0.12 and co.y < 0.1:   # black pectoral tips
        return TIP
    c = nh.lerp(c, BACK, nh.smoothstep(0.1, 0.7, n.z))
    if co.y < -0.70 and n.z > -0.4:                  # darker pointed snout tip
        c = nh.lerp(c, BACK, 0.4)
    return cc.mottle(c, co, 0.04)


def make():
    # rows (y, z, half-width, half-height): stout, heavy body and a conical, blunter snout
    axis = [(0.84, 0.0, 0.0, 0.0), (0.76, 0.0, 0.02, 0.03), (0.56, 0.0, 0.055, 0.07),
            (0.25, 0.0, 0.13, 0.15), (-0.05, 0.0, 0.16, 0.175), (-0.35, 0.0, 0.14, 0.15),
            (-0.58, 0.0, 0.095, 0.095), (-0.72, 0.01, 0.055, 0.05), (-0.82, 0.02, 0.0, 0.0)]
    jaw = [(-0.50, -0.075, 0.075, 0.022), (-0.62, -0.07, 0.055, 0.018), (-0.70, -0.065, 0.0, 0.0)]
    s = tp.Spec(name="CarcharodonCarcharias", axis=axis, paint=paint, power=2.0, jaw=jaw, hinge=(-0.50, -0.055),
                jaw_open=16, pivot="centre", eye=(0.072, -0.62, 0.035, 0.018), eye_col=(0.02, 0.02, 0.03),
                voxel=0.01, max_tris=10000)
    s.blobs.append(((0.045, 0.72, 0.0), (0.025, 0.085, 0.014), True))   # strong caudal keels

    def crisp(mb, s):
        mr.tail_lobes(mb, 0.78, 0.0, (1.01, 0.30), (0.99, -0.27), FIN, thickness=0.02, chord=0.085)
        mr.fin(mb, [(0, -0.16, 0.13), (0, 0.08, 0.11)], [(0, 0.00, 0.38), (0, 0.08, 0.13)], FIN, thickness=0.02)
        mr.fin(mb, [(0, 0.54, 0.05), (0, 0.60, 0.04)], [(0, 0.58, 0.10), (0, 0.62, 0.04)], FIN)
        mr.fin(mb, [(0, 0.54, -0.05), (0, 0.60, -0.04)], [(0, 0.58, -0.09), (0, 0.62, -0.04)], FIN)   # anal fin
        for sx in (1, -1):
            # long sickle-shaped pectorals
            mr.fin(mb, [(sx * 0.10, -0.32, -0.07), (sx * 0.10, -0.19, -0.08)],
                   [(sx * 0.44, -0.02, -0.22), (sx * 0.43, 0.01, -0.22)], FIN, thickness=0.016, side=1)
            mr.fin(mb, [(sx * 0.06, 0.30, -0.08), (sx * 0.05, 0.38, -0.07)],
                   [(sx * 0.13, 0.42, -0.13), (sx * 0.12, 0.44, -0.12)], FIN, thickness=0.012, side=1)
            for k in range(5):     # long gill slits
                p = Vector((sx * (0.118 - 0.006 * k), -0.38 - 0.022 * k, 0.0 + 0.003 * k))
                mb.add(nh.ellipsoid(p, (0.003, 0.004, 0.045), subdivisions=1), (0.10, 0.14, 0.22))
        # big triangular serrated upper teeth
        for k in range(6):
            for sx in (1, -1):
                p = Vector((sx * 0.066 * (1 - 0.11 * k), -0.60 - 0.02 * k, -0.058))
                mb.add(nh.ellipsoid(p + Vector((0, 0, -0.012)), (0.011, 0.003, 0.016), subdivisions=1,
                                    deform=lambda v: 1.0 - 0.6 * max(0.0, -v.z) * (abs(v.x))), cc.TOOTH, smooth=False)
        lo = [(sx * 0.05 * (1 - 0.1 * k), -0.57 - 0.02 * k, -0.058) for k in range(5) for sx in (1, -1)]
        cc.teeth_row(mb, lo, 0.022, 0.007, down=False, rot=s._jaw_rot)
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "CarcharodonCarcharias")
