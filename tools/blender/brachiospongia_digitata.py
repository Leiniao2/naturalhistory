"""
Procedural Brachiospongia digitata (Late Ordovician glass sponge, Kentucky and Tennessee)
for map colonies (Fixed style).

A large, strange hexactinellid sponge up to about 30 cm across, shaped like an upturned
glove or a crown: a broad, flat-topped central body with a wide opening (osculum) on top,
and around its lower edge eight or so big, hollow, finger-like lobes that spread out and
curve down to rest on the sea floor, holding the body up off the mud. Its thin wall was a
lattice of fused glassy spicules. Fused body painted with a square spicule lattice. Pale
straw-grey. Pivot on the sea floor (z = 0), facing -Y.

Usage:
  blender --background --python tools/blender/brachiospongia_digitata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BrachiospongiaDigitata.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "BrachiospongiaDigitata"
WALL = (0.80, 0.76, 0.62)
RIB = (0.95, 0.93, 0.84)
WINDOW = (0.52, 0.48, 0.38)
INSIDE = (0.26, 0.22, 0.16)

N_ARMS = 8


def lattice(co, n):
    k = 26.0
    a = abs(math.sin(co.x * k)) if abs(n.x) < 0.8 else 1.0
    b = abs(math.sin(co.y * k)) if abs(n.y) < 0.8 else 1.0
    c = abs(math.sin(co.z * k)) if abs(n.z) < 0.8 else 1.0
    m = min(a, b, c)
    col = nh.lerp(WINDOW, WALL, nh.smoothstep(0.05, 0.4, m))
    col = nh.lerp(RIB, col, nh.smoothstep(0.0, 0.18, m))
    col = tuple(x * (0.92 + 0.08 * noise.noise(co * 4)) for x in col)
    return col


def build():
    mb = nh.MeshBuilder()
    zc = 0.34
    # central body: a squat drum, rounded at the shoulders
    mb.add(nh.uv_ellipsoid((0, 0, zc + 0.04), (0.36, 0.36, 0.20), 28, 14), WALL)
    mb.add(nh.tube([(0, 0, zc - 0.06), (0, 0, zc + 0.16)], [0.34, 0.33], sides=28), WALL)
    # finger-like lobes, out and down to the mud
    for k in range(N_ARMS):
        a = k / N_ARMS * math.tau + 0.2
        d = Vector((math.cos(a), math.sin(a), 0))
        L = 0.62 + 0.06 * math.sin(k * 2.3)
        pts = [d * 0.12 + Vector((0, 0, zc)), d * 0.32 + Vector((0, 0, zc - 0.02)),
               d * (L * 0.80) + Vector((0, 0, zc - 0.10)), d * L + Vector((0, 0, 0.15)),
               d * (L + 0.04) + Vector((0, 0, 0.06))]
        mb.add(nh.tube(pts, [0.15, 0.14, 0.12, 0.10, 0.08], sides=12), WALL)
    fused = mb.fuse(voxel=0.02, smooth=6, max_tris=9000)
    out = nh.MeshBuilder()
    kit.mud(out, 1.0)
    out.add(fused, lattice)
    # osculum: a dark, recessed opening with a pale rim on the flat top
    top = zc + 0.20
    out.add(nh.ellipsoid((0, 0, top + 0.012), (0.22, 0.22, 0.03), 3), INSIDE)
    out.add(nh.tube([(0.24 * math.cos(t / 40 * math.tau), 0.24 * math.sin(t / 40 * math.tau), top + 0.02)
                     for t in range(41)], [0.025] * 41, sides=6, cap_start=False, cap_end=False), RIB)
    return kit.finish_fixed(out, NAME, roughness=0.75)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
