"""
Procedural Gnathorhiza serrata (Early Permian lungfish, ~40 cm) for map colonies.

A small, eel-shaped lungfish of the seasonal ponds and streams of Texas and Oklahoma,
one of the first animals known to survive droughts sealed in a burrow in the mud: a long,
rounded body, a blunt head, slender, whip-like paired fins and a continuous fin fringe
round the pointed tail. Muddy olive-brown with dark speckles and a yellowish belly.
Built with nh_car_fish. Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/gnathorhiza_serrata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Gnathorhiza.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

FIN = (0.36, 0.30, 0.18)


def whip_fins(sp, tree):
    out = []
    for root, d in (((0.035, -0.40, -0.03), (0.10, 0.14, -0.05)), ((0.025, 0.05, -0.035), (0.08, 0.13, -0.04))):
        for sx in (-1, 1):
            a = Vector((sx * root[0], root[1], root[2]))
            b = a + Vector((sx * d[0] * 0.5, d[1] * 0.5, d[2] * 0.6))
            c = a + Vector((sx * d[0], d[1], d[2]))
            out.append((nh.tube([a, b, c], [0.008, 0.005, 0.0], sides=6), FIN))
    return out


SPEC = cf.Spec(
    name="Gnathorhiza",
    mid=[(-0.6, 0.0), (0.6, 0.0)],
    height=[(-0.6, 0.0), (-0.58, 0.030), (-0.50, 0.048), (-0.35, 0.055), (0.0, 0.054), (0.30, 0.040),
            (0.50, 0.018), (0.6, 0.002)],
    width=[(-0.6, 0.0), (-0.58, 0.032), (-0.50, 0.050), (-0.35, 0.055), (0.0, 0.050), (0.30, 0.034),
           (0.50, 0.014), (0.6, 0.002)],
    fins=[
        ("mid", [(0.05, 0.05), (0.12, 0.075), (0.45, 0.045), (0.62, 0.004), (0.45, 0.012), (0.10, 0.05)]),
        ("mid", [(0.18, -0.038), (0.26, -0.065), (0.45, -0.045), (0.62, -0.004), (0.45, -0.012)]),
    ],
    fin_th=0.008,
    back=(0.28, 0.26, 0.16), flank=(0.46, 0.42, 0.26), belly=(0.82, 0.76, 0.48),
    fin_col=(0.34, 0.30, 0.18), pattern="spots", pattern_col=(0.16, 0.14, 0.08), pattern_scale=0.8,
    eye=(-0.52, 0.016, 0.010), iris=(0.70, 0.60, 0.30), gills=0,
    voxel=0.005, max_tris=6000,
    extra=[whip_fins],
)

if __name__ == "__main__":
    cf.run(SPEC)
