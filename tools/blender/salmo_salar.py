"""
Procedural Atlantic salmon (Salmo salar, Pleistocene to today; North Atlantic
and its rivers) for map colonies.

A migratory trout-family fish usually 70-80 cm long (up to 1.5 m): it hatches in
cold gravel rivers, grows at sea for one to four years, then leaps its way back
upstream to spawn in the river where it was born. A streamlined, slightly
compressed body, a small fleshy adipose fin behind the dorsal fin, a nearly
square tail and, in spawning males, a hooked lower jaw (kype). Steel-blue back,
silver flanks with scattered black x-shaped spots above the lateral line, and a
white belly. Built with the swimmer helpers (nh_cre_tetrapod / nh_cre_marine).
Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/salmo_salar.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SalmoSalar.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_cre_core as cc  # noqa: E402
import nh_cre_tetrapod as tp  # noqa: E402
import nh_cre_marine as mr  # noqa: E402

BACK = (0.20, 0.28, 0.36)
FLANK = (0.72, 0.75, 0.78)
BELLY = (0.95, 0.95, 0.94)
FIN = (0.36, 0.40, 0.44)
SPOT = (0.04, 0.04, 0.05)


def spots(co, n, c):
    if n.z < -0.05 or co.y > 0.55:
        return c
    dist, _p = noise.voronoi(Vector((co.x * 0.3, co.y * 24.0, co.z * 24.0)), distance_metric="DISTANCE")
    return nh.lerp(c, SPOT, 0.9 * (1.0 - nh.smoothstep(0.13, 0.19, dist[0])))


paint = mr.fish_paint(BACK, FLANK, BELLY, extra=spots, mottle=0.03)


def make():
    # rows (y, z, half-width, half-height)
    axis = [(0.70, 0.0, 0.0, 0.0), (0.64, 0.0, 0.020, 0.045), (0.52, 0.0, 0.030, 0.060),
            (0.30, 0.0, 0.060, 0.120), (0.00, 0.0, 0.085, 0.165), (-0.30, 0.0, 0.080, 0.150),
            (-0.52, 0.0, 0.062, 0.105), (-0.66, -0.005, 0.040, 0.060), (-0.74, -0.01, 0.0, 0.0)]
    jaw = [(-0.52, -0.05, 0.045, 0.02), (-0.64, -0.045, 0.03, 0.015), (-0.76, -0.03, 0.0, 0.0)]
    s = tp.Spec(name="SalmoSalar", axis=axis, paint=paint, power=2.0, jaw=jaw, hinge=(-0.52, -0.04),
                jaw_open=4, pivot="centre", eye=(0.042, -0.62, 0.025, 0.020), eye_col=(0.75, 0.70, 0.55),
                voxel=0.009, max_tris=9000)

    def crisp(mb, s):
        mr.tail_lobes(mb, 0.66, 0.0, (0.82, 0.14), (0.82, -0.14), FIN, thickness=0.014, chord=0.17)
        mr.fin(mb, [(0, -0.12, 0.15), (0, 0.10, 0.14)], [(0, -0.06, 0.30), (0, 0.10, 0.17)], FIN)       # dorsal
        mr.fin(mb, [(0, 0.40, 0.08), (0, 0.47, 0.07)], [(0, 0.45, 0.13), (0, 0.48, 0.08)], FIN)         # adipose
        mr.fin(mb, [(0, 0.34, -0.09), (0, 0.46, -0.07)], [(0, 0.42, -0.18), (0, 0.48, -0.09)], FIN)     # anal
        for sx in (1, -1):
            mr.fin(mb, [(sx * 0.06, -0.44, -0.08), (sx * 0.06, -0.38, -0.09)],
                   [(sx * 0.16, -0.30, -0.16), (sx * 0.14, -0.30, -0.14)], FIN, thickness=0.01, side=1)
            mr.fin(mb, [(sx * 0.05, 0.08, -0.14), (sx * 0.05, 0.16, -0.13)],
                   [(sx * 0.10, 0.20, -0.21), (sx * 0.09, 0.22, -0.17)], FIN, thickness=0.01, side=1)
            # gill cover edge
            mb.add(nh.ellipsoid((sx * 0.058, -0.47, 0.0), (0.004, 0.008, 0.07), subdivisions=1), (0.55, 0.58, 0.62))
    s.crisp = crisp
    return s


if __name__ == "__main__":
    mr.run(make, "SalmoSalar")
