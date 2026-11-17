"""
Procedural low-poly Arborea arborea (Ediacaran arboreomorph frond, Ediacara, South Australia).

A leaf-shaped frond on a long, cylindrical stalk anchored by a bulbous,
partly buried holdfast disc: the broad, lanceolate petalodium has a stout
central stalk running up its face and many primary branches set side by side
like the leaflets of a fern, each slanting up and out from the midline and
finely ribbed. Unlike Charnia, the stem is long and bare. Sandy rose frond,
paler branches, darker stalk and a buff holdfast.
Pivot on the seabed (Fixed). The flat face of the frond faces -Y.

Output: Assets/Resources/Models/Species/Arborea.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

BRANCH = (0.86, 0.66, 0.56)
BRANCH_DARK = (0.62, 0.42, 0.36)
STALK = (0.56, 0.38, 0.30)
DISC = (0.72, 0.62, 0.46)

STEM_TOP = 0.45
FROND_LEN = 0.95
ROWS = 16


def half_width(t):
    return 0.2 * math.sin(math.pi * min(1.0, 0.12 + t * 0.95)) ** 0.8


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.frond_disc(0.17, 0.08, rings=3, segments=18),
           lambda co, n: nh.lerp(DISC, STALK, 0.4 * nh.smoothstep(0.6, 1.0, 0.5 + 0.5 * math.cos(math.hypot(co.x, co.y) * 60))))
    # bare stem, slightly curved, then the frond's central stalk
    top = STEM_TOP + FROND_LEN
    sway = lambda z: 0.04 * (z / top) ** 2
    pts = [(0, sway(z), z) for z in [0.03 + (top - 0.03) * i / 12 for i in range(13)]]
    radii = [0.035 - 0.022 * i / 12 for i in range(13)]
    radii[-1] = 0.0
    mb.add(nh.tube(pts, radii, sides=8), STALK)
    for k in range(ROWS):
        t = (k + 0.5) / ROWS
        z = STEM_TOP + FROND_LEN * t
        w = half_width(t)
        h = FROND_LEN / ROWS * 1.15
        for s in (-1, 1):
            br = nh.uv_ellipsoid((0, 0, 0), (w * 0.52, 0.02, h * 0.5), segments=10, rings=6)
            nh.transform(br, Matrix.Rotation(math.radians(-22) * s, 4, "Y"))
            c = Vector((s * w * 0.5, sway(z) - 0.005, z + 0.02))
            nh.transform(br, Matrix.Translation(c))

            def col(co, n, c=c):
                rib = 0.5 + 0.5 * math.cos((co.x - c.x) * math.tau / 0.03)
                return nh.lerp(BRANCH, BRANCH_DARK, 0.5 * nh.smoothstep(0.6, 1.0, rib))

            mb.add(br, col)
    return ec.ground(mb.to_object("Arborea", roughness=0.6))


if __name__ == "__main__":
    ec.export(build, "Arborea", fixed=True)
