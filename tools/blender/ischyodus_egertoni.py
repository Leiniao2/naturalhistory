"""
Procedural Ischyodus egertoni (Middle-Late Jurassic chimaera, European seas) for the map
(Swim style).

A large ratfish relative, about 1.5 m long: a big blunt head with large eyes and a
beak-like mouth of tooth plates for crushing shellfish, broad wing-like pectoral fins,
a tall first dorsal fin fronted by a long, stout, serrated spine (in living chimaeras the
spine carries venom), a long low second dorsal fin and a body tapering into a long thin
whip tail. Painted silvery brown-grey with dark mottling on the back and a pale belly;
the spine ivory. Built with nh_car_fish (like Echinochimaera). Faces -Y, pivot at the body
centre.

Usage:
  blender --background --python tools/blender/ischyodus_egertoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ischyodus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

SPINE = (0.90, 0.86, 0.74)
PLATE = (0.80, 0.74, 0.60)


def fin_spine(sp):
    return [nh.tube([(0, -0.24, 0.11), (0, -0.235, 0.27), (0, -0.20, 0.40)], [0.018, 0.013, 0.003], sides=8)]


def details(sp, tree):
    out = []
    # serrations along the back edge of the spine
    for i in range(7):
        t = 0.2 + 0.1 * i
        p = Vector((0, -0.24 + 0.04 * t, 0.11 + 0.29 * t))
        out.append((nh.tube([p, p + Vector((0, 0.018, -0.01))], [0.004, 0.0], sides=4), SPINE))
    # beak-like tooth plates at the front of the mouth
    loc, nrm, _i, _d = tree.ray_cast(Vector((0, -1.0, -0.03)), Vector((0, 1, 0)))
    if loc is not None:
        for sx in (1, -1):
            out.append((nh.ellipsoid(loc + Vector((sx * 0.014, 0.004, -0.004)), (0.012, 0.008, 0.01), subdivisions=2), PLATE))
    return out


SPEC = cf.Spec(
    name="Ischyodus",
    mid=[(-0.6, 0.0), (0.0, 0.0), (0.6, 0.0)],
    height=[(-0.6, 0.0), (-0.585, 0.06), (-0.5, 0.12), (-0.32, 0.14), (-0.05, 0.1), (0.2, 0.05),
            (0.45, 0.014), (0.6, 0.002)],
    width=[(-0.6, 0.0), (-0.585, 0.055), (-0.5, 0.09), (-0.32, 0.095), (-0.05, 0.06), (0.2, 0.028),
           (0.45, 0.01), (0.6, 0.002)],
    fins=[
        ("mid", [(-0.23, 0.11), (-0.20, 0.38), (-0.12, 0.30), (-0.07, 0.09)]),
        ("mid", [(-0.02, 0.09), (0.02, 0.13), (0.36, 0.07), (0.42, 0.025)]),
        ("mid", [(0.1, -0.045), (0.3, -0.06), (0.45, -0.03), (0.45, -0.012)]),
        ("pair", (0.08, -0.36, -0.08), [(0, 0, 0), (0.0, 0.12, 0.0), (0.2, 0.32, -0.07), (0.27, 0.24, -0.07), (0.16, 0.05, -0.04)]),
        ("pair", (0.05, 0.0, -0.08), [(0, 0, 0), (0.0, 0.08, 0.0), (0.09, 0.11, -0.05), (0.08, 0.02, -0.05)]),
    ],
    fused_extra=[fin_spine],
    back=(0.36, 0.33, 0.28), flank=(0.60, 0.58, 0.54), belly=(0.90, 0.88, 0.82),
    fin_col=(0.30, 0.28, 0.25), pattern="mottle", pattern_col=(0.20, 0.18, 0.15), pattern_scale=1.0,
    eye=(-0.47, 0.04, 0.05), iris=(0.35, 0.60, 0.55), gills=0,
    extra=[details],
)

if __name__ == "__main__":
    cf.run(SPEC)
