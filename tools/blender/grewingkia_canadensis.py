"""
Procedural Grewingkia canadensis (Billings, 1862) (Late Ordovician solitary rugose "horn coral",
the only large Ordovician horn coral, common in the Richmondian beds of Kentucky, Indiana, Ohio and
Ontario) for the map (Fixed style).

A big, heavy horn coral, usually 4-8 cm and up to 13 cm long: a curved, thick-walled cone with
strong growth wrinkles, lying on the soft sea floor with its tip in the mud. Its deep cup is
lined with many crowded septa (more than Streptelasma), whose inner ends twist together into a
raised axial structure in the middle of the floor. Old shells are often encrusted by bryozoans.
Built with the horn generator of streptelasma_corniculum.py (re-parametrised: more septa, larger,
thicker, greyer, with an axial boss and pale bryozoan crusts); one polyp has its tentacles out
(soft parts speculative).

Usage:
  blender --background --python tools/blender/grewingkia_canadensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GrewingkiaCanadensis.fbx (pivot at the base, z = 0)
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402
import streptelasma_corniculum as sc  # noqa: E402

# horns: apex (x, y), heading (deg), length, rim radius, major septa, wall rings, polyp extended
HORNS = [
    ((-0.70, -0.30), 10, 1.30, 0.30, 22, 15, True),
    ((0.62, 0.10), 150, 1.00, 0.24, 18, 13, False),
]
sc.EPITHECA = (0.66, 0.62, 0.54)
sc.RUGA = (0.42, 0.38, 0.32)
sc.APEX = (0.50, 0.46, 0.40)
sc.SEPTUM = (0.92, 0.90, 0.84)
sc.LIP = (0.80, 0.76, 0.68)
sc.GAP = (0.30, 0.26, 0.22)
sc.DEEP = (0.14, 0.12, 0.10)
sc.DISC = (0.62, 0.52, 0.36)
sc.TENTACLE = (0.74, 0.66, 0.44)
sc.TENTACLE_TIP = (0.95, 0.92, 0.76)
sc.TENTACLES = 20
sc.MINOR_REACH = 0.42
CRUST = (0.86, 0.80, 0.66)
MUD = (0.60, 0.56, 0.48)


def axial_boss(mb, frame, rim_r):
    p, fwd, side, up = frame
    c = p - fwd * rim_r * (sc.FLOOR - 0.12)
    mb.add(nh.ellipsoid(tuple(c), (rim_r * 0.16, rim_r * 0.16, rim_r * 0.16), subdivisions=2),
           lambda co, n: nh.lerp(sc.SEPTUM, sc.GAP, 0.5 + 0.5 * math.sin(math.atan2(co.y - c.y, co.x - c.x) * 7)))


def crusts(mb, rng, horns):
    """Pale, low bryozoan patches stuck on the outer walls."""
    for apex, heading, length, rim_r, *_ in horns:
        h = Vector((math.cos(math.radians(heading)), math.sin(math.radians(heading)), 0))
        for k in range(3):
            t = rng.uniform(0.35, 0.7)
            at = Vector((apex[0], apex[1], 0)) + h * length * t * 0.75 + Vector((0, 0, length * t * t * 0.45 + rim_r * 0.55))
            side = h.cross(Vector((0, 0, 1))).normalized() * rng.choice((-1, 1)) * rim_r * 0.4
            mb.add(nh.ellipsoid(tuple(at + side), (rim_r * 0.35, rim_r * 0.3, rim_r * 0.12), subdivisions=2),
                   lambda co, n: tuple(x * (0.9 + 0.15 * noise.noise(co * 40)) for x in CRUST))


def build():
    rng = random.Random(5)
    mb = nh.MeshBuilder()
    mud = nh.uv_ellipsoid((0, 0, 0), (0.95, 0.80, 0.04), segments=24, rings=6,
                          deform=lambda n: 1.0 + 0.10 * noise.noise(n * 1.8 + sc.WARP))
    mb.add(mud, lambda co, n: tuple(x * (0.88 + 0.2 * noise.noise(co * 7 + sc.WARP)) for x in MUD))
    for apex, heading, length, rim_r, septa, rings, extended in HORNS:
        bm, frame = sc.horn(apex, heading, length, rim_r, septa, rings, rng)
        mb.add(bm)
        axial_boss(mb, frame, rim_r)
        if extended:
            sc.polyp(mb, frame, rim_r, rng)
    crusts(mb, rng, HORNS)
    nc.rubble(mb, rng, 0.80, 0.95, count=4, size=(0.04, 0.07))
    obj = mb.to_object("GrewingkiaCanadensis", roughness=0.75)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "GrewingkiaCanadensis", ground=(0.72, 0.68, 0.56), views=((30, 25), (10, 70), (-100, 12)))
