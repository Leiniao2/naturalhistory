"""
Procedural Acanthodes bronni (Early Permian acanthodian, ~30 cm) for map colonies.

One of the last 'spiny sharks': a slim, streamlined fish with a big eye, a wide, toothless
mouth, a single small dorsal fin set far back, a strongly upturned (heterocercal) tail and
a stout spine in front of every fin - pectoral, pelvic, anal and dorsal. Covered in tiny
square scales: dark olive above, silvery-pale below.
Built with nh_car_fish. Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/acanthodes_bronni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Acanthodes.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

SPINE = (0.78, 0.74, 0.62)


def spines(sp, tree):
    out = []
    # (root, tip) for the right side / midline
    mids = [((0, 0.14, 0.050), (0, 0.24, 0.115)),      # dorsal
            ((0, 0.12, -0.040), (0, 0.22, -0.100))]    # anal
    for a, b in mids:
        out.append((nh.tube([Vector(a), Vector(b)], [0.0065, 0.0], sides=6), SPINE))
    pairs = [((0.040, -0.36, -0.030), (0.150, -0.18, -0.075)),   # pectoral
             ((0.020, -0.05, -0.045), (0.070, 0.05, -0.085))]    # pelvic
    for a, b in pairs:
        for sx in (-1, 1):
            out.append((nh.tube([Vector((sx * a[0], a[1], a[2])), Vector((sx * b[0], b[1], b[2]))],
                                [0.006, 0.0], sides=6), SPINE))
    return out


SPEC = cf.Spec(
    name="Acanthodes",
    mid=[(-0.6, 0.0), (0.2, 0.0), (0.45, 0.03), (0.6, 0.07)],
    height=[(-0.6, 0.0), (-0.58, 0.035), (-0.50, 0.055), (-0.30, 0.065), (0.00, 0.060), (0.25, 0.038),
            (0.45, 0.016), (0.6, 0.003)],
    width=[(-0.6, 0.0), (-0.58, 0.030), (-0.50, 0.048), (-0.30, 0.050), (0.00, 0.042), (0.25, 0.024),
           (0.45, 0.010), (0.6, 0.002)],
    fins=[
        ("mid", [(0.16, 0.05), (0.23, 0.105), (0.30, 0.040)]),                         # dorsal behind spine
        ("mid", [(0.14, -0.04), (0.21, -0.095), (0.28, -0.035)]),                      # anal
        ("mid", [(0.38, -0.005), (0.50, -0.07), (0.56, -0.05), (0.60, 0.065), (0.45, 0.035)]),  # hypochordal lobe
        ("pair", (0.04, -0.36, -0.03), [(0, 0, 0), (0.11, 0.18, -0.045), (0.06, 0.20, -0.03), (0.0, 0.07, 0.0)]),
        ("pair", (0.02, -0.05, -0.045), [(0, 0, 0), (0.05, 0.10, -0.04), (0.02, 0.10, -0.03)]),
    ],
    fin_th=0.008,
    back=(0.24, 0.28, 0.24), flank=(0.55, 0.58, 0.55), belly=(0.86, 0.87, 0.84),
    fin_col=(0.30, 0.33, 0.28), pattern="none",
    eye=(-0.50, 0.018, 0.022), iris=(0.82, 0.78, 0.55), gills=5, gill_y=-0.45,
    voxel=0.005, max_tris=6000,
    extra=[spines],
)

if __name__ == "__main__":
    cf.run(SPEC)
