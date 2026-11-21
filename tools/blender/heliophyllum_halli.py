"""
Procedural Heliophyllum halli (Middle Devonian solitary rugose "horn coral", Hamilton Group
of New York and Ontario) for the map (Fixed style).

A large horn coral, often 5-15 cm long: a curved, cone-shaped skeleton lying on the sea floor
with its tip in the mud, the outer wall ringed by many fine growth lines grouped into bands
(counts of these daily and monthly lines showed that a Devonian year had about 400 days).
The wide, deep cup is lined with very many thin radial septa (sixty or more), whose sides
carry little ridges, so the calice looks like a sunburst ("helio-"). Built with the horn
generator of streptelasma_corniculum.py, re-parametrised: many more, finer septa, more
growth rings, warmer brown colours; one polyp has its tentacles out (soft parts speculative).

Usage:
  blender --background --python tools/blender/heliophyllum_halli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Heliophyllum.fbx (pivot at the base, z = 0)
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402
import streptelasma_corniculum as sc  # noqa: E402

# horns: apex (x, y), heading (deg), length, rim radius, major septa, wall rings, polyp extended
HORNS = [
    ((-0.72, -0.18), 12, 1.40, 0.34, 32, 24, False),
    ((0.66, 0.16), 160, 0.85, 0.22, 24, 17, True),
]
sc.EPITHECA = (0.70, 0.56, 0.40)
sc.RUGA = (0.42, 0.30, 0.20)
sc.APEX = (0.56, 0.44, 0.32)
sc.SEPTUM = (0.96, 0.90, 0.78)
sc.LIP = (0.86, 0.74, 0.58)
sc.GAP = (0.34, 0.24, 0.16)
sc.DEEP = (0.16, 0.11, 0.08)
sc.DISC = (0.70, 0.46, 0.30)
sc.TENTACLE = (0.80, 0.58, 0.40)
sc.TENTACLE_TIP = (0.98, 0.90, 0.72)
sc.TENTACLES = 24
sc.MINOR_REACH = 0.30
MUD = (0.58, 0.54, 0.46)


def build():
    rng = random.Random(11)
    mb = nh.MeshBuilder()
    mud = nh.uv_ellipsoid((0, 0, 0), (1.0, 0.82, 0.04), segments=24, rings=6,
                          deform=lambda n: 1.0 + 0.10 * noise.noise(n * 1.8 + sc.WARP))
    mb.add(mud, lambda co, n: tuple(x * (0.88 + 0.2 * noise.noise(co * 7 + sc.WARP)) for x in MUD))
    for apex, heading, length, rim_r, septa, rings, extended in HORNS:
        bm, frame = sc.horn(apex, heading, length, rim_r, septa, rings, rng)
        mb.add(bm)
        if extended:
            sc.polyp(mb, frame, rim_r, rng)
    nc.rubble(mb, rng, 0.85, 0.95, count=4, size=(0.04, 0.07))
    obj = mb.to_object("Heliophyllum", roughness=0.75)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Heliophyllum", ground=(0.72, 0.68, 0.56), views=((30, 25), (10, 70), (-100, 12)))
