"""
Procedural Odontochelys semitestacea (Late Triassic stem turtle, ~40 cm) for map colonies
(Swim style).

The "toothed turtle with a half shell" from the coastal waters of Guizhou, China, about
220 million years ago. Its belly was already covered by a complete bony plastron, but
its back had no shell yet: only broad, flattened ribs and a row of small bony plates
along the spine. It still had teeth along the edges of its pointed snout, a fairly long
neck and a long tail, and paddled through shallow water. Built with the shared Triassic
tetrapod recipe (nh_tri_tetrapod.py): a wide, flat body with the broad ribs painted and
slightly raised on the back, a crisp pale plastron plate under the belly, small teeth and
paddle-like feet. Painted olive-green with darker rib grooves (speculative). Faces -Y,
pivot at the body centre.

Usage:
  blender --background --python tools/blender/odontochelys_semitestacea.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Odontochelys.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tri_tetrapod as tt  # noqa: E402
from mathutils import Vector  # noqa: E402

PLASTRON = (0.86, 0.80, 0.58)
PLASTRON_SEAM = (0.55, 0.48, 0.32)
RIB = (0.12, 0.14, 0.07)


def sway(y):
    s = max(0.0, (y - 0.3) / 0.7)
    return 0.08 * s * s


AXIS = [
    (-1.00, 0.010, 0.010, 0.010),
    (-0.96, 0.014, 0.030, 0.026),
    (-0.90, 0.018, 0.044, 0.036),
    (-0.84, 0.020, 0.050, 0.040),
    (-0.78, 0.018, 0.036, 0.032),
    (-0.66, 0.012, 0.040, 0.034),
    (-0.54, 0.008, 0.120, 0.050),
    (-0.40, 0.006, 0.240, 0.060),
    (-0.15, 0.006, 0.260, 0.060),
    (0.08, 0.004, 0.220, 0.056),
    (0.22, 0.000, 0.110, 0.044),
    (0.40, -0.004, 0.050, 0.030, sway(0.40)),
    (0.62, -0.008, 0.026, 0.018, sway(0.62)),
    (0.85, -0.010, 0.010, 0.008, sway(0.85)),
    (1.00, -0.010, 0.002, 0.002, sway(1.00)),
]

FORE = tt.Limb(pts=[(0.20, -0.42, -0.01), (0.31, -0.44, -0.025), (0.37, -0.46, -0.03)],
               radii=[0.030, 0.024, 0.020], paddle=(0.065, 0.040, 110, 0))
HIND = tt.Limb(pts=[(0.18, 0.12, -0.01), (0.28, 0.17, -0.025), (0.33, 0.20, -0.03)],
               radii=[0.030, 0.024, 0.020], paddle=(0.060, 0.038, 140, 0))


def ribs(co, n, c, spec):
    if -0.52 < co.y < 0.16 and n.z > 0.3:
        k = abs(math.sin((co.y + 0.52) * 38.0))
        c = nh.lerp(c, RIB, 0.85 * (1.0 - nh.smoothstep(0.0, 0.45, k)) * nh.smoothstep(0.02, 0.06, abs(co.x)))
    return c


def plastron_col(co, n):
    k = abs(math.sin((co.y + 0.5) * 22.0)) if abs(co.x) > 0.008 else 0.0
    seam = (1.0 - nh.smoothstep(0.0, 0.12, k)) + (1.0 - nh.smoothstep(0.003, 0.006, abs(co.x)))
    return nh.lerp(PLASTRON, PLASTRON_SEAM, min(1.0, seam) * 0.7)


def post(mb, surf, spec):
    # plastron: a flat plate just under the belly
    outline = []
    for i in range(24):
        a = i / 24 * math.tau
        x = 0.20 * math.copysign(abs(math.cos(a)) ** 0.7, math.cos(a))
        y = -0.18 + 0.34 * math.copysign(abs(math.sin(a)) ** 0.8, math.sin(a))
        outline.append((x, y, -0.055))
    plate = tt.panel(outline, 0.008)
    import bmesh
    bmesh.ops.subdivide_edges(plate, edges=plate.edges[:], cuts=3, use_grid_fill=True)
    mb.add(plate, plastron_col, smooth=False)
    # neural plates along the spine
    y = -0.50
    while y < 0.20:
        loc, nrm = surf.hit((0, y, 1.0), (0, 0, -1))
        if loc is not None:
            mb.add(nh.ellipsoid(loc, (0.012, 0.018, 0.006), subdivisions=2), (0.30, 0.32, 0.18))
        y += 0.045


SPEC = tt.TetrapodSpec(
    name="Odontochelys",
    axis=AXIS, power=2.6,
    limbs=[FORE, HIND],
    voxel=0.008, max_tris=8000,
    pivot="centre",
    mouth=(-1.0, -0.84, 0.010, 0.016, 0.004),
    teeth=(8, 0.010, 0.003, -0.98, -0.86),
    eyes=(-0.86, 0.040, 0.012, (0.80, 0.62, 0.15)),
    nostrils=(-0.985, 0.016),
    back=(0.34, 0.40, 0.22), flank=(0.50, 0.52, 0.32), belly=(0.78, 0.74, 0.56),
    pattern=("spots", (0.18, 0.22, 0.12), 18.0, 0.45),
    paint_extra=ribs,
    post=post,
)

if __name__ == "__main__":
    tt.run(SPEC)
