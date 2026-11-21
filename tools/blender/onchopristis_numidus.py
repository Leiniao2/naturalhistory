"""
Procedural Onchopristis numidus (mid-Cretaceous sclerorhynchid ray, Kem Kem beds / Bahariya,
North Africa).

A giant sawfish-like ray: a long, flat, blade-like rostrum (about a quarter of the length)
studded along each edge with widely spaced, barbed, harpoon-shaped teeth; a flattened,
shark-like body with broad triangular pectoral fins merging into the head, small pelvic
fins, two dorsal fins and a long tail with a low, asymmetric caudal fin. Brownish-olive
above, cream below (colours conjectural).
Swim style: faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/onchopristis_numidus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Onchopristis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.36, 0.32, 0.22)
FLANK = (0.50, 0.45, 0.33)
BELLY = (0.90, 0.86, 0.76)
FIN = (0.30, 0.27, 0.19)
SAW = (0.42, 0.38, 0.28)
TOOTH = (0.92, 0.88, 0.76)


def make():
    # flattened body: hw > hh, a long tail, the head tapering into the rostrum
    axis = [(0.95, 0.03, 0.0, 0.0), (0.88, 0.03, 0.012, 0.014), (0.70, 0.02, 0.025, 0.028),
            (0.45, 0.01, 0.045, 0.045), (0.20, 0.0, 0.075, 0.06), (-0.05, 0.0, 0.10, 0.065),
            (-0.25, 0.0, 0.10, 0.055), (-0.38, -0.005, 0.07, 0.035), (-0.46, -0.01, 0.035, 0.016),
            (-0.55, -0.01, 0.026, 0.009), (-0.90, -0.01, 0.018, 0.006), (-0.96, -0.01, 0.0, 0.0)]
    s = tp.Spec(name="Onchopristis", axis=axis, paint=mr.fish_paint(BACK, FLANK, BELLY, mottle=0.1), power=2.2,
                pivot="centre", eye=(0.045, -0.36, 0.03, 0.012), eye_col=(0.75, 0.65, 0.30), voxel=0.008,
                max_tris=9000)

    def crisp(mb, s):
        # broad pectoral fins merging into the head
        for sx in (1, -1):
            mr.fin(mb, [(sx * 0.07, -0.36, -0.01), (sx * 0.09, -0.10, -0.01)],
                   [(sx * 0.12, -0.38, -0.02), (sx * 0.30, -0.02, -0.03)], FIN, thickness=0.012, side=1)
            mr.fin(mb, [(sx * 0.05, 0.22, -0.02), (sx * 0.04, 0.32, -0.02)],
                   [(sx * 0.14, 0.30, -0.03), (sx * 0.10, 0.38, -0.03)], FIN, thickness=0.01, side=1)
        mr.fin(mb, [(0, 0.05, 0.06), (0, 0.16, 0.05)], [(0, 0.12, 0.17), (0, 0.20, 0.06)], FIN)
        mr.fin(mb, [(0, 0.48, 0.04), (0, 0.58, 0.035)], [(0, 0.55, 0.13), (0, 0.62, 0.04)], FIN)
        mr.tail_lobes(mb, 0.90, 0.03, (1.06, 0.14), (1.02, -0.03), FIN, thickness=0.01, chord=0.06)
        # the barbed rostral teeth: widely spaced, pointing outwards and slightly back
        for k in range(8):
            y = -0.58 - 0.045 * k
            for sx in (1, -1):
                p = Vector((sx * 0.02, y, -0.01))
                mb.add(cc.curved_cone(p, p + Vector((sx * 0.02, 0.0, 0)), p + Vector((sx * 0.035, 0.012, 0)), 0.006,
                                      sides=5), TOOTH)
        for sx in (1, -1):
            mb.add(nh.ellipsoid((sx * 0.03, -0.42, -0.05), (0.008, 0.005, 0.003), subdivisions=1), (0.1, 0.08, 0.06))
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "Onchopristis")
