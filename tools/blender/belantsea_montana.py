"""
Procedural Belantsea montana (Early Carboniferous Bear Gulch Limestone of Montana, a
petalodont holocephalan about 25 cm long) for map colonies (Swim style).

A deep, laterally compressed, almost round leaf-shaped disc of a body (about as tall as it
is long) with a small blunt head and a small mouth set with petal-shaped teeth, huge
wing-like pectoral fins, a long high dorsal fin running along most of the back (rounding
off the top of the disc), a deep ventral keel with small pelvic fins, and a short thin
tail. Brown-purple with darker spots, pale belly. Built with nh_car_fish.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/belantsea_montana.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Belantsea.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
import nh_b2_carboniferous_fish as bf  # noqa: E402
from mathutils import Vector  # noqa: E402

PETAL = (0.93, 0.88, 0.76)
MOUTH = (0.12, 0.07, 0.08)


def mouth(sp, tree):
    """Small terminal mouth with a row of petal-shaped teeth."""
    out = []
    loc, nrm, _i, _d = tree.ray_cast(Vector((0, -1.0, -0.06)), Vector((0, 1, 0)))
    if loc is None:
        return out
    out.append((nh.ellipsoid(loc + Vector((0, 0.004, 0)), (0.03, 0.012, 0.009), subdivisions=2), MOUTH))
    for k in range(5):
        x = -0.02 + 0.01 * k
        b = loc + Vector((x, -0.002, 0.004))
        # flattened petal: a squashed ellipsoid standing up
        out.append((nh.ellipsoid(b, (0.0055, 0.003, 0.009), subdivisions=1), PETAL))
        b2 = loc + Vector((x * 0.9, -0.0, -0.006))
        out.append((nh.ellipsoid(b2, (0.005, 0.003, 0.007), subdivisions=1), PETAL))
    return out


def spots(sp, tree):
    return bf.dots(sp, tree, 46, (0.22, 0.12, 0.15), (-0.30, 0.25), (-0.2, 0.9), (0.016, 0.026), flat=0.5)


SPEC = cf.Spec(
    name="Belantsea",
    y0=-0.45, y1=0.62,
    mid=[(-0.45, -0.02), (-0.2, 0.02), (0.1, 0.0), (0.62, 0.0)],
    height=[(-0.45, 0.0), (-0.435, 0.07), (-0.36, 0.17), (-0.22, 0.27), (-0.05, 0.30), (0.10, 0.26),
            (0.22, 0.15), (0.30, 0.05), (0.45, 0.022), (0.62, 0.004)],
    width=[(-0.45, 0.0), (-0.435, 0.04), (-0.36, 0.06), (-0.2, 0.07), (0.0, 0.065), (0.15, 0.05),
           (0.28, 0.025), (0.45, 0.012), (0.62, 0.003)],
    fins=[
        # long high dorsal fin along most of the back, rounding the disc
        ("mid", [(-0.24, 0.25), (-0.18, 0.37), (-0.06, 0.43), (0.08, 0.42), (0.20, 0.35), (0.28, 0.20),
                 (0.30, 0.06), (0.20, 0.12), (0.05, 0.25)]),
        # deep ventral keel / anal fin
        ("mid", [(0.05, -0.22), (0.14, -0.32), (0.24, -0.27), (0.30, -0.10), (0.24, -0.08)]),
        # small tail fin
        ("mid", [(0.50, 0.01), (0.56, 0.045), (0.63, 0.01), (0.63, -0.01), (0.56, -0.04), (0.50, -0.01)]),
        # huge wing-like pectorals
        ("pair", (0.05, -0.27, -0.10), [(0, -0.02, 0.02), (0.22, -0.01, 0.0), (0.40, 0.08, -0.08),
                                         (0.42, 0.22, -0.16), (0.26, 0.30, -0.14), (0.08, 0.24, -0.06),
                                         (0.0, 0.16, -0.02)], 0.016),
        # small pelvics
        ("pair", (0.04, 0.02, -0.25), [(0, 0, 0), (0.0, 0.07, 0.0), (0.07, 0.10, -0.04), (0.06, 0.03, -0.04)]),
    ],
    fin_th=0.014,
    back=(0.30, 0.18, 0.22), flank=(0.45, 0.31, 0.32), belly=(0.86, 0.78, 0.72),
    fin_col=(0.34, 0.21, 0.24), pattern="spots", pattern_col=(0.14, 0.07, 0.10), pattern_scale=0.6,
    eye=(-0.34, 0.07, 0.04), iris=(0.75, 0.62, 0.35), gills=0,
    extra=[mouth, spots],
)

if __name__ == "__main__":
    cf.run(SPEC)
