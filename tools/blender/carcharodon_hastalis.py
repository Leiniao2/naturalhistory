"""
Procedural Carcharodon hastalis (the broad-toothed mako, Miocene to Pliocene seas
worldwide), the probable ancestor of the great white shark.

A big, fast lamniform shark about 6-7 metres long, built like an enlarged mako: a slim,
torpedo-shaped body with a long, sharply pointed conical snout, big black eyes, long
sickle-shaped pectoral fins, a tall first dorsal, a crescent-shaped tail with almost equal
lobes and a strong keel on each side of the tail base. Its upper teeth were broad, flat,
smooth-edged triangles (hence the name), shown here in rows below the snout. Metallic
blue-grey above, sharply white below.
Built with the Cretaceous swimmer helpers (nh_cre_tetrapod / nh_cre_marine), like
cretoxyrhina_mantelli.py. Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/carcharodon_hastalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CarcharodonHastalis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.13, 0.22, 0.38)     # metallic blue
FLANK = (0.30, 0.40, 0.55)
BELLY = (0.95, 0.95, 0.93)
FIN = (0.16, 0.24, 0.40)


def paint(co, n):
    # sharp mako line between the blue back and the white belly
    c = FLANK if n.z > -0.15 else BELLY
    c = nh.lerp(c, BACK, nh.smoothstep(0.1, 0.7, n.z))
    if co.y < -0.70 and n.z > -0.4:                  # darker pointed snout tip
        c = nh.lerp(c, BACK, 0.4)
    return cc.mottle(c, co, 0.04)


def make():
    # rows (y, z, half-width, half-height): slimmer and longer-snouted than Cretoxyrhina
    axis = [(0.84, 0.0, 0.0, 0.0), (0.76, 0.0, 0.018, 0.026), (0.56, 0.0, 0.045, 0.06),
            (0.25, 0.0, 0.105, 0.125), (-0.05, 0.0, 0.13, 0.145), (-0.35, 0.0, 0.115, 0.125),
            (-0.60, 0.0, 0.075, 0.075), (-0.76, 0.01, 0.04, 0.038), (-0.88, 0.025, 0.0, 0.0)]
    jaw = [(-0.50, -0.075, 0.075, 0.022), (-0.62, -0.07, 0.055, 0.018), (-0.70, -0.065, 0.0, 0.0)]
    s = tp.Spec(name="CarcharodonHastalis", axis=axis, paint=paint, power=2.0, jaw=jaw, hinge=(-0.50, -0.055),
                jaw_open=16, pivot="centre", eye=(0.058, -0.665, 0.03, 0.017), eye_col=(0.02, 0.02, 0.03),
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
        # broad, flat triangular upper teeth: wide-based, short cones squashed fore-aft
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
    mr.run(make, "CarcharodonHastalis")
