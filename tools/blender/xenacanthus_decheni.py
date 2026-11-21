"""
Procedural Xenacanthus decheni (Early Permian xenacanth shark, ~70 cm) for map colonies.

A small freshwater shark of European lakes and rivers: an eel-like body with a long,
low ribbon of a dorsal fin running back into a pointed, symmetrical tail, two small anal
fins, broad paddle-like paired fins and a long, straight spine sticking up and back from
the back of the head. Olive-grey with dark mottling and a pale belly.
Built with nh_car_fish. Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/xenacanthus_decheni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Xenacanthus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

SPINE = (0.80, 0.74, 0.58)


def head_spine(sp, tree):
    a, b = Vector((0, -0.38, 0.040)), Vector((0, -0.14, 0.105))
    return [(nh.tube([a, a.lerp(b, 0.5), b], [0.009, 0.006, 0.0], sides=6), SPINE)]


SPEC = cf.Spec(
    name="Xenacanthus",
    mid=[(-0.6, 0.0), (0.6, 0.0)],
    height=[(-0.6, 0.0), (-0.59, 0.022), (-0.52, 0.040), (-0.35, 0.052), (-0.05, 0.050), (0.25, 0.035),
            (0.48, 0.015), (0.6, 0.002)],
    width=[(-0.6, 0.0), (-0.59, 0.030), (-0.52, 0.050), (-0.35, 0.052), (-0.05, 0.042), (0.25, 0.026),
           (0.48, 0.010), (0.6, 0.002)],
    fins=[
        ("mid", [(-0.20, 0.045), (-0.16, 0.085), (0.30, 0.075), (0.55, 0.022), (0.60, 0.004), (0.40, 0.016),
                 (0.0, 0.045)]),
        ("mid", [(0.36, -0.016), (0.42, -0.050), (0.58, -0.016), (0.60, -0.003)]),
        ("mid", [(0.20, -0.030), (0.24, -0.058), (0.30, -0.030)]),
        ("pair", (0.045, -0.36, -0.035), [(0, 0, 0), (0.0, 0.08, 0.0), (0.13, 0.14, -0.03), (0.14, 0.06, -0.03)]),
        ("pair", (0.03, 0.08, -0.035), [(0, 0, 0), (0.0, 0.08, 0.0), (0.07, 0.11, -0.025), (0.07, 0.04, -0.025)]),
    ],
    fin_th=0.011,
    back=(0.34, 0.34, 0.26), flank=(0.50, 0.50, 0.40), belly=(0.86, 0.84, 0.74),
    fin_col=(0.30, 0.30, 0.22), pattern="mottle", pattern_col=(0.20, 0.20, 0.14), pattern_scale=0.6,
    eye=(-0.53, 0.020, 0.014), iris=(0.70, 0.66, 0.35), gills=6, gill_y=-0.46,
    teeth=6, tooth_len=0.010, mouth_y=(-0.595, -0.53), mouth_z=-0.016,
    voxel=0.0055, max_tris=7000,
    extra=[head_spine],
)

if __name__ == "__main__":
    cf.run(SPEC)
