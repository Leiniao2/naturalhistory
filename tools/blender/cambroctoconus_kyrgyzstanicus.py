"""
Procedural Cambroctoconus kyrgyzstanicus (middle Cambrian, Stage 5 / Amgan, Sauk Tanga, Alay
Range, Kyrgyzstan) for the map: a little group of slender, horn-shaped octagonal cups with
strongly ribbed corners and deep calyces, standing on a patch of shelly sediment.

Described by Peel (in Geyer et al. 2014) from bituminous coquinoid limestones at Sauk Tanga.
The diagnosis, as summarised later (Peel 2017), is a trochoidal (horn-shaped) corallum about
7 mm tall, octagonal in cross-section, with broad longitudinal angulations separated by flat to
shallowly concave fields, and a deep calyx without septa or with only isolated septa or short,
broad septal spines. Modelled here, using the shared octagonal cup from nh_cambroctoconus:
  * cups are more slender than C. orientalis (rim radius about a quarter of the height instead
    of about 0.4) and gently curved like horns;
  * the faces between the eight corners are shallowly dished and the corners stand a little
    proud and paler, so the angulations read as eight longitudinal ribs (C. orientalis is
    modelled with flat faces);
  * the calyx is deep (two thirds of the axis) with only eight short, broad septal spines high
    on the corners instead of full paired septa;
  * the wall is porous (darker mottling) and a touch warmer, darker grey than C. orientalis.
No budding is reported for this species, so the cups here are solitary individuals, each on
its own small holdfast, rather than a budding cluster; that, the exact proportions, the
curvature and all colours are reconstruction choices to keep the two species distinct.
Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/cambroctoconus_kyrgyzstanicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CambroctoconusKyrgyzstanicus.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402
import nh_cambroctoconus as cc  # noqa: E402

SEED = 4
RINGS = 7            # outer-wall rings per cup
# individuals: (x, y, height, rim radius, lean azimuth deg (away from the group), lean deg, curl)
CUPS = [
    (0.00, 0.00, 1.00, 0.25, 150, 14, 0.10),
    (0.30, -0.12, 0.78, 0.20, 338, 22, 0.12),
    (-0.22, -0.24, 0.66, 0.18, 227, 26, 0.10),
    (0.12, 0.30, 0.52, 0.15, 68, 18, 0.08),
]

PAL = dict(
    WALL=(0.78, 0.75, 0.67),       # grey-cream, a shade darker and warmer than C. orientalis
    WALL_DARK=(0.55, 0.52, 0.45),
    RIM=(0.90, 0.87, 0.79),
    CALYX=(0.30, 0.26, 0.22),
    SEPTUM=(0.86, 0.83, 0.75),
    PORE=(0.50, 0.47, 0.41),
    HOLDFAST=(0.68, 0.64, 0.56),
)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    for i, (x, y, h, r_rim, az, lean, curl) in enumerate(CUPS):
        d = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0))
        base = Vector((x, y, 0.01))
        top = base + Vector((0, 0, h)) + d * h * math.sin(math.radians(lean))
        # horn curve: the lower part leans further, the rim swings back upright
        mid = base + Vector((0, 0, h * 0.5)) + d * h * (math.sin(math.radians(lean)) * 0.5 + curl)
        pts = cc.bezier(base, mid, top, RINGS)
        radii = [0.03 + (r_rim - 0.03) * (k / (RINGS - 1)) ** 0.85 for k in range(RINGS)]
        bm, _top, _rt = cc.cup(pts, radii, PAL, concave=0.03, rib=0.02, wall=0.13, depth=0.66,
                               septa="spines", septum_len=0.30, rot=rng.uniform(0, 0.8), seed=i * 2.3)
        mb.add(bm)
        mb.add(*cc.holdfast((x, y, 0.0), 0.06 + 0.25 * r_rim, PAL, height=0.035, seed=i * 1.9))
    # shelly, bituminous lime-mud patch
    patch = nh.ellipsoid((0.04, 0.0, -0.03), (0.52, 0.50, 0.05), subdivisions=2,
                         deform=lambda n: 1.0 + 0.15 * noise.noise(n * 2.0 + Vector((2, 9, 4))))
    mb.add(patch, lambda co, n: nh.lerp((0.36, 0.33, 0.29), (0.48, 0.44, 0.38),
                                        0.5 + 0.5 * noise.noise(co * 11)))
    nc.rubble(mb, rng, 0.25, 0.55, count=7, size=(0.03, 0.06))
    obj = mb.to_object("CambroctoconusKyrgyzstanicus", roughness=0.8)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "CambroctoconusKyrgyzstanicus", ground=(0.55, 0.52, 0.45),
           views=((20, 25), (110, 35), (10, 75)))
