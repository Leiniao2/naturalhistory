"""
Procedural Rhabdoderma elegans (Late Carboniferous coal measures of Britain, Mazon Creek in
Illinois and Linton in Ohio, a small coelacanth about 25-40 cm long) for map colonies
(Swim style).

The coelacanth body plan: a deep, stocky body with a short blunt head and a large eye; a
fan-shaped first dorsal fin; fleshy lobed paired fins (pectoral, pelvic) and lobed second
dorsal and anal fins, each a muscular stalk ending in a fringe of fin rays; and the
diagnostic three-lobed (diphycercal) tail - matching upper and lower lobes with a small
tuft projecting from the middle. Dark blue-grey/brown back with faint pale flecks, paler
belly. Built with nh_car_fish. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/rhabdoderma_elegans.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Rhabdoderma.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
import nh_b2_carboniferous_fish as bf  # noqa: E402

FLECK = (0.70, 0.74, 0.78)


def lobes(sp):
    """Fleshy stalks of the lobed fins (fused with the body)."""
    out = []
    for sx in (-1, 1):
        # pectoral lobe: out, back and down from behind the head
        out.append(nh.tube([(sx * 0.07, -0.26, -0.06), (sx * 0.13, -0.21, -0.09), (sx * 0.18, -0.16, -0.11)],
                           [0.035, 0.028, 0.016], sides=10))
        # pelvic lobe
        out.append(nh.tube([(sx * 0.05, 0.02, -0.12), (sx * 0.09, 0.07, -0.16), (sx * 0.12, 0.11, -0.19)],
                           [0.03, 0.024, 0.013], sides=10))
    # second dorsal and anal lobes, on stalks
    out.append(nh.tube([(0, 0.17, 0.10), (0, 0.22, 0.16), (0, 0.27, 0.20)], [0.03, 0.026, 0.014], sides=10))
    out.append(nh.tube([(0, 0.17, -0.10), (0, 0.22, -0.16), (0, 0.27, -0.20)], [0.03, 0.026, 0.014], sides=10))
    # middle tail tuft stalk (the body continues through the tail)
    out.append(nh.tube([(0, 0.44, 0.0), (0, 0.56, 0.0), (0, 0.64, 0.0)], [0.022, 0.015, 0.008], sides=8))
    return out


def flecks(sp, tree):
    """Faint pale flecks over the flanks, and the mouth slit."""
    return (bf.dots(sp, tree, 48, FLECK, (-0.32, 0.36), (-0.45, 0.85), (0.005, 0.008))
            + bf.mouth_line(sp, tree, -0.598, -0.508, -0.035, -0.047))


SPEC = cf.Spec(
    name="Rhabdoderma",
    mid=[(-0.6, 0.0), (0.6, 0.0)],
    height=[(-0.6, 0.0), (-0.585, 0.06), (-0.5, 0.12), (-0.35, 0.18), (-0.15, 0.20), (0.05, 0.175),
            (0.25, 0.10), (0.42, 0.055), (0.55, 0.03), (0.66, 0.0)],
    width=[(-0.6, 0.0), (-0.585, 0.05), (-0.5, 0.085), (-0.35, 0.095), (-0.15, 0.09), (0.05, 0.075),
           (0.25, 0.05), (0.42, 0.03), (0.55, 0.018), (0.66, 0.0)],
    y1=0.66,
    fins=[
        # fan-like first dorsal (spiny rays)
        ("mid", [(-0.16, 0.15), (-0.12, 0.33), (-0.07, 0.34), (0.0, 0.29), (0.04, 0.15)]),
        # second dorsal and anal: fringe at the end of the stalk
        ("mid", [(0.22, 0.16), (0.22, 0.25), (0.27, 0.32), (0.33, 0.26), (0.30, 0.18)]),
        ("mid", [(0.22, -0.16), (0.22, -0.25), (0.27, -0.32), (0.33, -0.26), (0.30, -0.18)]),
        # diphycercal tail: upper and lower lobes
        ("mid", [(0.36, 0.05), (0.42, 0.20), (0.50, 0.25), (0.58, 0.20), (0.60, 0.07), (0.56, 0.02)]),
        ("mid", [(0.36, -0.05), (0.42, -0.20), (0.50, -0.25), (0.58, -0.20), (0.60, -0.07), (0.56, -0.02)]),
        # small middle tuft
        ("mid", [(0.62, 0.0), (0.65, 0.045), (0.71, 0.04), (0.73, 0.0), (0.71, -0.04), (0.65, -0.045)]),
        # pectoral fringe at the end of the lobe
        ("pair", (0.16, -0.18, -0.10), [(0, -0.03, 0.01), (0.07, 0.0, -0.03), (0.09, 0.07, -0.05),
                                         (0.03, 0.10, -0.03), (-0.02, 0.05, 0.0)]),
        ("pair", (0.11, 0.09, -0.18), [(0, -0.02, 0.01), (0.05, 0.01, -0.03), (0.06, 0.07, -0.05),
                                        (0.01, 0.09, -0.03), (-0.02, 0.04, 0.0)]),
    ],
    fin_th=0.014,
    fused_extra=[lobes],
    back=(0.20, 0.24, 0.30), flank=(0.38, 0.40, 0.44), belly=(0.74, 0.72, 0.66),
    fin_col=(0.22, 0.24, 0.28), pattern="mottle", pattern_col=(0.17, 0.17, 0.19), pattern_scale=1.2,
    eye=(-0.47, 0.035, 0.042), iris=(0.72, 0.68, 0.40), gills=0,
    mouth_z=-0.04,
    extra=[flecks],
)

if __name__ == "__main__":
    cf.run(SPEC)
