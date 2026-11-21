"""
Procedural Leptodus americanus (Middle Permian lyttoniid brachiopod, ~10 cm) for map colonies.

One of the strangest brachiopods, common on Permian reefs: instead of a neat two-valved
shell, the lower valve is a flat, leaf-shaped, oyster-like plate cemented to the reef,
divided inside by a median ridge and rows of comb-like side ridges, and the thin upper
valve is a lobed, fishbone-like lid that fits down between them. The lid lifted a little
to filter water. Grey-cream shell with darker gaps, three shells on a reef patch.
Faces -Y, pivot on the sea floor (Fixed style).

Usage:
  blender --background --python tools/blender/leptodus_americanus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Leptodus.fbx
"""

import math
import random
import sys
from pathlib import Path

import bmesh
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, Matrix, noise  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_coral as nc  # noqa: E402
import nh_ord_echino as oe  # noqa: E402

SHELL = (0.80, 0.76, 0.66)
SHELL_DARK = (0.56, 0.52, 0.44)
GAP = (0.42, 0.30, 0.24)
LID = (0.90, 0.86, 0.76)
MANTLE = (0.86, 0.58, 0.46)
MUD = ((0.62, 0.58, 0.50), (0.72, 0.68, 0.58))


def outline_w(t):
    """Half-width of the leaf at t in 0 (beak) .. 1 (front)."""
    return 0.24 * math.sin(math.pi * min(1.0, t * 0.92 + 0.04)) ** 0.7 * (0.55 + 0.45 * t)


def shell(L, gape):
    """Ventral plate (dish) + comb septa + lobed lid, local frame: beak at origin, long axis +Y."""
    parts = []
    nt, ns = 26, 18
    bm = bmesh.new()
    grid = []
    for i in range(nt + 1):
        t = i / nt
        w = outline_w(t) * L
        row = []
        for j in range(ns + 1):
            u = -1 + 2 * j / ns
            z = 0.025 * L + 0.02 * L * (1 - u * u)
            row.append(bm.verts.new((u * w, t * L, z)))
        grid.append(row)
    for i in range(nt):
        for j in range(ns):
            bm.faces.new([grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]])
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.03 * L)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    parts.append((bm, lambda co, n: nh.lerp(SHELL, SHELL_DARK, 0.5 + 0.5 * math.sin(co.y * 90))))
    # rim wall
    rim = [(outline_w(t) * L * s, t * L) for s in (1,) for t in [k / 30 for k in range(31)]]
    rim += [(-outline_w(t) * L, t * L) for t in [k / 30 for k in range(30, -1, -1)]]
    pts = [Vector((x, y, 0.06 * L)) for x, y in rim]
    parts.append((nh.tube(pts, [0.018 * L] * len(pts), sides=6), SHELL))
    # mantle tissue visible in the gaps
    parts.append((nh.ellipsoid((0, L * 0.5, 0.055 * L), (0.2 * L, 0.46 * L, 0.012 * L), subdivisions=3), GAP))
    # lid: median bar + lobes, tilted up by `gape` about the beak
    lid = []
    lid.append(nh.tube([(0, 0.06 * L, 0.09 * L), (0, 0.9 * L, 0.09 * L)], [0.025 * L, 0.02 * L], sides=6))
    n_lobes = 9
    for k in range(n_lobes):
        t = 0.15 + 0.78 * k / (n_lobes - 1)
        w = outline_w(t) * L * 0.85
        for s in (1, -1):
            lid.append(nh.tube([(0, t * L, 0.09 * L), (s * w * 0.5, t * L + 0.02 * L, 0.095 * L),
                                (s * w, t * L + 0.06 * L, 0.09 * L)], [0.022 * L, 0.02 * L, 0.012 * L], sides=6))
    rot = Matrix.Rotation(gape, 4, "X")
    for b in lid:
        nh.transform(b, rot)
        parts.append((b, LID))
    if gape > 0.05:
        parts.append((nh.ellipsoid((0, 0.85 * L, 0.10 * L), (0.14 * L, 0.04 * L, 0.03 * L), subdivisions=2), MANTLE))
    return parts


def place(mb, parts, at, yaw, L):
    """Centre the shell (beak at -L/2) on `at`, turned by yaw."""
    m = (Matrix.Translation(Vector(at)) @ Matrix.Rotation(yaw, 4, "Z")
         @ Matrix.Translation(Vector((0, -L / 2, 0))))
    for bm, col in parts:
        nh.transform(bm, m)
        mb.add(bm, col)


def build():
    rng = random.Random(8)
    mb = nh.MeshBuilder()
    oe.mud_patch(mb, 0.95, MUD, seed=2)
    nc.rubble(mb, rng, 0.6, 0.9, count=6, size=(0.05, 0.09))
    place(mb, shell(0.95, math.radians(7)), (-0.30, 0.0, 0.0), math.radians(185), 0.95)
    place(mb, shell(0.60, math.radians(3)), (0.30, -0.30, 0.0), math.radians(30), 0.60)
    place(mb, shell(0.55, math.radians(10)), (0.32, 0.38, 0.0), math.radians(-150), 0.55)
    return oe._finish(mb, "Leptodus", roughness=0.6)


if __name__ == "__main__":
    nh.run(build, "Leptodus", ground=(0.62, 0.58, 0.48), views=((30, 35), (10, 75), (-100, 12)))
