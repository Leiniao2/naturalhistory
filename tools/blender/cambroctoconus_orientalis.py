"""
Procedural Cambroctoconus orientalis (middle Cambrian, Drumian, Shandong Province, China) for the
map: a small, crudely lobed cluster of octagonal, cone-shaped calcareous cups budding from one
another, each with eight-fold septa in its calyx, on a little patch of reef rubble.

Park et al. (2011, Nature Communications) described it from coralomorph-sponge-microbial reefs
of the Zhangxia (Changhia) Formation and proposed it as a stem-group cnidarian whose eight-fold
symmetry recalls octocorals. Their description, followed here:
  * each cup is eight-sided (octagonal in plan) and steeply conical, about 11-13 mm tall and
    8-11 mm wide at the rim, narrowing to 1.5-3 mm at the base, which expands into a solid
    holdfast;
  * a pair of longitudinal lamellar septa projects inward from each of the eight corners of the
    cup (16 thin plates here, from the rim down to the floor of the calyx, so from above they
    read as eight radial partitions);
  * the wall is perforate (hinted by darker mottling) with transverse growth lines;
  * new cups (offsets) bud mostly from the outer wall of a parent, some from the rim, and most
    point the same way as the parent, so cups stack into lobed clusters.
Here: a parent cup on a holdfast, three daughters budding from its flanks, one from its rim and
one granddaughter budding from a daughter's rim. Cups are a single ring-stack each (outer wall,
rounded rim, calyx) from nh_cambroctoconus. Soft parts are unknown and not shown; colours are a
guess (pale grey-cream calcite, darker calyx).
Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/cambroctoconus_orientalis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CambroctoconusOrientalis.fbx
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

SEED = 11
RINGS = 6            # outer-wall rings per cup
PARENT = dict(height=1.0, base=0.07, rim=0.40)
# buds: (parent index, azimuth deg, bud position on parent 0..1 (1 = rim), reach, rise, rim radius)
BUDS = [
    (0, 20, 0.40, 0.55, 0.58, 0.30),
    (0, 145, 0.30, 0.58, 0.50, 0.28),
    (0, 260, 0.50, 0.50, 0.55, 0.26),
    (0, 330, 0.97, 0.22, 0.34, 0.21),   # from the parent's rim
    (2, 200, 0.96, 0.16, 0.40, 0.19),   # granddaughter from a daughter's rim
]

PAL = dict(
    WALL=(0.84, 0.81, 0.72),       # pale grey-cream calcite
    WALL_DARK=(0.62, 0.59, 0.52),  # growth lines, lower cup
    RIM=(0.93, 0.91, 0.84),
    CALYX=(0.34, 0.29, 0.24),      # deep, shadowed calyx floor
    SEPTUM=(0.92, 0.90, 0.83),
    PORE=(0.56, 0.54, 0.49),
    HOLDFAST=(0.74, 0.71, 0.63),
)


def build():
    rng = random.Random(SEED)
    mb = nh.MeshBuilder()
    h = PARENT["height"]
    ppts = cc.bezier(Vector((0, 0, 0.02)), Vector((0.0, 0.02, h * 0.5)), Vector((-0.04, 0.03, h)), RINGS)
    pr = [PARENT["base"] + (PARENT["rim"] - PARENT["base"]) * (i / (RINGS - 1)) ** 0.95 for i in range(RINGS)]
    cups = [(ppts, pr)]
    for parent, az, bud, reach, rise, r_rim in BUDS:
        pts0, r0 = cups[parent]
        out = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0))
        c, r_par = cc.axis_point(pts0, r0, bud)
        pdir = ((pts0[-1] - pts0[0]).normalized() + cc.UP).normalized()   # roughly the parent's way
        p0 = c + out * r_par * 0.55
        p1 = p0 + out * reach * 0.6 + pdir * rise * 0.35
        p2 = p0 + out * reach + pdir * rise
        pts = cc.bezier(p0, p1, p2, RINGS - 1)
        radii = [0.035 + (r_rim - 0.035) * (i / (RINGS - 2)) ** 0.95 for i in range(RINGS - 1)]
        cups.append((pts, radii))
    for i, (pts, radii) in enumerate(cups):
        bm, _top, _rt = cc.cup(pts, radii, PAL, concave=0.015, rib=0.0, wall=0.12, depth=0.5,
                               septa="paired", septum_len=0.52, rot=rng.uniform(0, 0.8), seed=i * 3.1)
        mb.add(bm)
    mb.add(*cc.holdfast((0.0, 0.0, 0.0), 0.17, PAL, height=0.05, seed=2.0))
    # low microbial crust the colony is cemented to, then reef rubble
    crust = nh.ellipsoid((0.02, 0.0, -0.02), (0.34, 0.30, 0.06), subdivisions=2,
                         deform=lambda n: 1.0 + 0.2 * noise.noise(n * 2.5 + Vector((4, 1, 7))))
    mb.add(crust, lambda co, n: nh.lerp((0.46, 0.42, 0.36), (0.58, 0.54, 0.46),
                                        0.5 + 0.5 * noise.noise(co * 9)))
    nc.rubble(mb, rng, 0.32, 0.55, count=6, size=(0.04, 0.07))
    obj = mb.to_object("CambroctoconusOrientalis", roughness=0.8)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "CambroctoconusOrientalis", ground=(0.62, 0.58, 0.48),
           views=((20, 25), (110, 35), (10, 75)))
