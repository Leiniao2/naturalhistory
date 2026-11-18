"""
Procedural Stethacanthus altonensis (Early Carboniferous seas of North America,
a stethacanthid shark about 70 cm to 1 m long) for map colonies (Swim style).

The "ironing-board shark": a stout shark with a blunt snout, big eyes and a near-symmetrical
crescent tail, whose first dorsal fin is turned into a tall spine topped by a broad, flat,
forward-tilted brush; the flat top of the brush and the top of the head are studded with
enlarged tooth-like denticles. Blue-grey above, pale below, the brush darker.
Shares the denticle helper with akmonistion_zangerli.py; built with nh_car_fish.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/stethacanthus_altonensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Stethacanthus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
import akmonistion_zangerli as ak  # noqa: E402


def brush(sp):
    # a taller, broader board than Akmonistion's anvil, tilted forward
    parts = [nh.tube([(0, -0.10, 0.09), (0, -0.115, 0.22), (0, -0.13, 0.31)], [0.032, 0.03, 0.034], sides=10)]
    parts.append(nh.uv_ellipsoid((0, -0.16, 0.335), (0.05, 0.13, 0.035), 18, 10,
                                 deform=lambda v: 1.0 - 0.3 * max(0.0, v.z) ** 4))
    return parts


SPEC = cf.Spec(
    name="Stethacanthus",
    mid=[(-0.6, -0.01), (0.25, 0.0), (0.6, 0.05)],
    height=[(-0.6, 0.0), (-0.585, 0.045), (-0.5, 0.09), (-0.25, 0.12), (0.05, 0.10), (0.3, 0.045),
            (0.45, 0.03), (0.6, 0.006)],
    width=[(-0.6, 0.0), (-0.585, 0.04), (-0.5, 0.08), (-0.25, 0.10), (0.05, 0.08), (0.3, 0.035),
           (0.45, 0.022), (0.6, 0.004)],
    fins=[
        ("mid", [(0.40, 0.03), (0.55, 0.24), (0.63, 0.24), (0.57, 0.05), (0.63, -0.17), (0.56, -0.18), (0.40, -0.01)]),
        ("mid", [(0.20, 0.05), (0.26, 0.10), (0.30, 0.10), (0.31, 0.04)]),
        ("pair", (0.08, -0.30, -0.06), [(0, 0, 0), (0.0, 0.09, 0.0), (0.19, 0.14, -0.08), (0.20, 0.08, -0.09)]),
        ("pair", (0.04, 0.12, -0.06), [(0, 0, 0), (0.0, 0.07, 0.0), (0.07, 0.09, -0.04), (0.06, 0.03, -0.04)]),
    ],
    fused_extra=[brush],
    back=(0.24, 0.28, 0.33), flank=(0.40, 0.45, 0.50), belly=(0.86, 0.86, 0.82),
    fin_col=(0.20, 0.23, 0.27), pattern="none",
    eye=(-0.48, 0.03, 0.028), iris=(0.60, 0.62, 0.40), gills=5, gill_y=-0.37,
    extra=[ak.denticles],
)

if __name__ == "__main__":
    cf.run(SPEC)
