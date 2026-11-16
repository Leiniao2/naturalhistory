"""
Procedural low-poly Trichonympha collaris for colony instancing: a termite-gut
flagellate, slimmer than T. campanula, named for the collar behind its rostrum.

A narrow, elongate cell: a longer rostrum with a glassy cap, then a distinct
collar-like constriction and flared lip before the body widens into a slender
bell with a rounded rear. Rows of flagella spring from the rostrum and the front
half of the cell and trail backwards (a separate tuft on the rostrum, then the
sheath over the bell, with a gap at the collar); the bare rear end is greyer and
packed with angular brown wood splinters engulfed from the termite's gut, and a
faint nucleus shows through. Pale grey-blue, glassy colours.

Drift style: pivot at the body centre, faces -Y (rostrum first).

Usage:
  blender --background --python tools/blender/trichonympha_collaris.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TrichonymphaCollaris.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Matrix, Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_trichonympha as tr  # noqa: E402

SEED = 8
LENGTH = 1.8
# (t, radius): t = 0 rostrum tip, 1 rear end. Long rostrum, pinched collar, slender bell.
PROFILE = [
    (0.00, 0.000), (0.012, 0.050), (0.035, 0.074), (0.06, 0.064),   # rostral cap
    (0.10, 0.080), (0.14, 0.100), (0.175, 0.082),                   # rostrum, then the collar groove
    (0.205, 0.150), (0.235, 0.165), (0.265, 0.150),                 # flared collar lip
    (0.33, 0.185), (0.45, 0.255), (0.60, 0.300), (0.74, 0.300),
    (0.86, 0.260), (0.95, 0.180), (0.99, 0.080), (1.00, 0.000),
]


def build():
    rng = random.Random(SEED)
    cell = tr.Cell(PROFILE, length=LENGTH, flatten=0.95, seed=SEED)
    mb = nh.MeshBuilder()
    # extra rings around the collar keep the pinch crisp
    ts = sorted(set([0.5 - 0.5 * math.cos(math.pi * k / 30) for k in range(31)]
                    + [0.16, 0.175, 0.19, 0.205, 0.22, 0.235, 0.25, 0.265, 0.28]))
    mb.add(cell.mesh(segments=22, ts=ts), tr.body_color(cell, nucleus_t=0.45, rostrum_t=0.16))
    # rostral tuft (stops at the collar groove) and the main sheath behind the collar
    mb.add(*tr.flagella(cell, rng, rows=20, per_row=4, t_range=(0.03, 0.14), length=(0.11, 0.09),
                        t_max=0.19, twist=0.3, lift=0.03, radius=0.006))
    mb.add(*tr.flagella(cell, rng, rows=28, per_row=8, t_range=(0.22, 0.52), length=(0.24, 0.22),
                        t_max=0.70, twist=0.35, lift=0.05, radius=0.0065))
    tr.wood_particles(cell, rng, mb, count=34, t_range=(0.68, 0.99), size=(0.045, 0.08))
    obj = mb.to_object("TrichonymphaCollaris", roughness=0.35)
    corners = [Vector(c) for c in obj.bound_box]
    mid = sum(corners, Vector()) / 8
    obj.data.transform(Matrix.Translation(-mid))
    return obj


if __name__ == "__main__":
    nh.run(build, "TrichonymphaCollaris", views=((35, 35), (-90, 10), (180, 60)))
