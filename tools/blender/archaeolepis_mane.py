"""
Procedural Archaeolepis mane (Early Jurassic moth, Dorset, England) for map swarms.

The oldest known member of the moths and butterflies, about 190 million years old, known
from wings covered in the overlapping scales that give the group its name ("scale wings").
Like the living mandibulate moths it was probably a tiny, day-flying insect about 1 cm
across with chewing jaws, which fed on pollen and spores long before flowers existed:
narrow, pointed fore- and hindwings fringed with long scales, a slim, hairy body, long
antennae. Painted bronze-gold wings crossed by violet-purple bands, like the metallic
micropterigid moths of today (the fossil's colours are unknown). Wings spread in flight.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/archaeolepis_mane.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Archaeolepis.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_jur_kit as kit  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

GOLD = (0.80, 0.62, 0.26)
VIOLET = (0.36, 0.20, 0.40)
FRINGE = (0.50, 0.42, 0.30)
BODY = (0.30, 0.24, 0.18)
HAIR = (0.70, 0.56, 0.30)


def wing_outline(length, width, n=14):
    """Narrow, lanceolate wing in wing space: x outward from the root, y backward."""
    lead, trail = [], []
    for i in range(n + 1):
        t = i / n
        x = length * t
        lead.append((x, -width * 0.25 * math.sin(math.pi * t) ** 0.6 - width * 0.05 * (1 - t)))
        trail.append((x, width * 0.75 * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.8 + width * 0.1 * (1 - t)))
    return lead + list(reversed(trail[1:-1]))


def wing(mb, root, length, width, sweep, lift, sx, fringe):
    out = wing_outline(length, width)
    m = Matrix.Translation(Vector(root)) @ Matrix.Rotation(math.radians(lift * sx), 4, "Y") @ Matrix.Rotation(math.radians(-sweep * sx), 4, "Z")
    if sx < 0:
        m = m @ Matrix.Scale(-1, 4, Vector((1, 0, 0)))
    pts = [(x, y, 0.0) for x, y in out]
    bm = nh.flat_panel(pts, 0.006)
    import bmesh
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    inv = m.inverted()

    def col(co, n):
        p = inv @ co
        t = p.x / length
        band = 0.5 + 0.5 * math.sin(t * math.pi * 5.0 + 0.6)
        c = nh.lerp(GOLD, VIOLET, nh.smoothstep(0.55, 0.85, band))
        return c
    nh.transform(bm, m)
    mb.add(bm, col, smooth=False)
    # fringe of long scales along the trailing edge
    for i in range(3, 14):
        t = i / 14
        x = length * t
        y = width * 0.75 * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.8 + width * 0.1 * (1 - t)
        b = m @ Vector((x, y, 0))
        e = m @ Vector((x + length * 0.03, y + fringe, 0))
        mb.add(nh.tube([b, e], [0.006, 0.001], sides=3), FRINGE, smooth=False)


def build():
    mb = nh.MeshBuilder()
    fused = [nh.ellipsoid((0, -0.2, 0.0), (0.05, 0.05, 0.05), subdivisions=2),     # head
             nh.ellipsoid((0, -0.08, 0.0), (0.06, 0.1, 0.06), subdivisions=2),      # thorax
             kit.limb([(0, 0.0, 0.0), (0, 0.18, -0.01), (0, 0.38, -0.03)], [0.05, 0.045, 0.015], sides=10)]
    body = kit.fuse_parts(fused, 0.008, 2500)
    mb.add(body, lambda co, n: nh.lerp(BODY, HAIR, 0.5 + 0.5 * math.sin(co.y * 70)) if co.y > 0.02 else BODY)
    for sx in (1, -1):
        wing(mb, (sx * 0.04, -0.1, 0.02), 0.62, 0.17, 18, 12, sx, 0.05)
        wing(mb, (sx * 0.04, -0.03, 0.0), 0.5, 0.13, 42, 6, sx, 0.06)
        # antennae and jaws
        mb.add(kit.limb([(sx * 0.02, -0.23, 0.03), (sx * 0.1, -0.4, 0.08), (sx * 0.2, -0.55, 0.08)], [0.007, 0.005, 0.003], sides=4), BODY)
        mb.add(nh.tube([(sx * 0.012, -0.24, -0.02), (sx * 0.004, -0.27, -0.04)], [0.008, 0.002], sides=4), BODY)
        kit.eyes(mb, (0.035, -0.22, 0.01), 0.02, sx_list=(sx,), iris=(0.12, 0.10, 0.08))
        # legs tucked under
        for y in (-0.12, -0.07, -0.02):
            b = Vector((sx * 0.03, y, -0.04))
            mb.add(kit.limb([b, b + Vector((sx * 0.06, 0.0, -0.04)), b + Vector((sx * 0.08, 0.04, -0.09))], [0.007, 0.005, 0.003], sides=4), BODY)
    return kit.finish(mb, "Archaeolepis", pivot="center", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "Archaeolepis", background=(0.20, 0.28, 0.18), views=((35, 35), (0, 80), (-90, 5)))
