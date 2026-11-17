"""
Procedural Echinochimaera meltoni (Early Carboniferous Bear Gulch Limestone of Montana, a
small chimaeroid fish, males up to about 15 cm long) for map colonies (Swim style).

A ratfish-like holocephalan: a big, deep, blunt head with huge eyes, a body tapering to a
thin tail that ends in a small paddle, broad wing-like pectoral fins, a tall first dorsal fin
behind a stout spine and a long low second dorsal. As in males of the species, rows of
short spines run over the head and along the back. Warm brown with dark spots, pale belly.
Built with nh_car_fish. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/echinochimaera_meltoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Echinochimaera.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

SPINE = (0.86, 0.80, 0.66)


def fin_spine(sp):
    return [nh.tube([(0, -0.26, 0.12), (0, -0.25, 0.26), (0, -0.21, 0.36)], [0.016, 0.012, 0.003], sides=8)]


def spines(sp, tree):
    out = []
    for i in range(14):
        y = -0.50 + i * 0.05
        for x in ((0.0,) if i > 4 else (-0.035, 0.035)):
            loc, nrm, _i, _d = tree.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
            if loc is None or (i > 4 and -0.3 < y < -0.12):
                continue
            L = 0.03 if i < 5 else 0.02
            out.append((nh.tube([loc - nrm * 0.003, loc + (nrm + Vector((0, 0.6, 0))).normalized() * L],
                                [0.006, 0.0], sides=4), SPINE))
    return out


SPEC = cf.Spec(
    name="Echinochimaera",
    mid=[(-0.6, 0.0), (0.0, 0.0), (0.6, 0.0)],
    height=[(-0.6, 0.0), (-0.58, 0.07), (-0.48, 0.135), (-0.3, 0.15), (-0.05, 0.1), (0.2, 0.05),
            (0.45, 0.018), (0.6, 0.004)],
    width=[(-0.6, 0.0), (-0.58, 0.06), (-0.48, 0.1), (-0.3, 0.1), (-0.05, 0.065), (0.2, 0.03),
           (0.45, 0.012), (0.6, 0.003)],
    fins=[
        ("mid", [(-0.25, 0.12), (-0.21, 0.34), (-0.15, 0.30), (-0.10, 0.10)]),
        ("mid", [(-0.04, 0.09), (0.0, 0.14), (0.3, 0.09), (0.36, 0.04)]),
        ("mid", [(0.42, 0.012), (0.50, 0.06), (0.60, 0.012), (0.60, -0.012), (0.50, -0.06), (0.42, -0.012)]),
        ("pair", (0.08, -0.36, -0.09), [(0, 0, 0), (0.0, 0.15, 0.0), (0.24, 0.2, -0.05), (0.26, 0.08, -0.04)]),
        ("pair", (0.05, 0.0, -0.08), [(0, 0, 0), (0.0, 0.08, 0.0), (0.08, 0.1, -0.05), (0.07, 0.02, -0.05)]),
    ],
    fused_extra=[fin_spine],
    back=(0.34, 0.25, 0.16), flank=(0.50, 0.38, 0.25), belly=(0.86, 0.80, 0.68),
    fin_col=(0.30, 0.22, 0.15), pattern="spots", pattern_col=(0.17, 0.12, 0.08), pattern_scale=0.8,
    eye=(-0.47, 0.04, 0.05), iris=(0.40, 0.65, 0.55), gills=0,
    extra=[spines],
)

if __name__ == "__main__":
    cf.run(SPEC)
