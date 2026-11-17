"""
Procedural Stupendemys geographicus (Middle-Late Miocene of northern South
America) for map colonies: a giant side-necked freshwater turtle (Podocnemididae)
with a shell up to about 2.4-2.9 m long, one of the largest turtles ever.

Shown swimming: a broad, low, oval carapace; in males its front corners
project forward as two stout horns, probably used in fights. A large, flat
head on a neck that folds sideways (pleurodire), webbed, paddle-like limbs and
a short tail. Dark brown-olive carapace, paler grey skin.
Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/stupendemys_geographicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/StupendemysGeographicus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.24, 0.22, 0.15)
SHELL_RIM = (0.36, 0.32, 0.22)
SKIN = (0.40, 0.39, 0.34)
BELLY = (0.62, 0.58, 0.46)
EYE = (0.10, 0.08, 0.04)


def build():
    b = nh.MeshBuilder()
    b.add(nh.ellipsoid((0, 0, 0.0), (0.50, 0.62, 0.16), subdivisions=4,
                       deform=lambda v: 1.0 + 0.12 * max(0.0, v.z) ** 2 - 0.25 * max(0.0, -v.z) ** 2), SHELL)
    b.add(nh.ellipsoid((0, 0, -0.06), (0.42, 0.54, 0.08)), BELLY)                       # plastron
    for sx in (-1, 1):                                                                    # anterior horns
        b.add(nh.tube([(sx * 0.30, -0.45, 0.03), (sx * 0.36, -0.70, 0.05), (sx * 0.40, -0.88, 0.07)],
                      [0.08, 0.06, 0.03], sides=10, scale_xy=(1.0, 0.7)), SHELL_RIM)
    # neck + flat head
    b.add(nh.tube([(0, -0.48, 0.0), (0.03, -0.66, 0.0), (0.06, -0.80, 0.0)], [0.08, 0.07, 0.065], sides=12), SKIN)
    b.add(nh.ellipsoid((0.07, -0.89, 0.0), (0.085, 0.11, 0.055)), SKIN)
    # paddles: front ones swept back mid-stroke, hind ones trailing
    for sx in (-1, 1):
        b.add(nh.tube([(sx * 0.38, -0.30, -0.03), (sx * 0.58, -0.22, -0.05), (sx * 0.72, -0.08, -0.06)],
                      [0.06, 0.05, 0.02], sides=8, scale_xy=(1.0, 0.3)), SKIN)
        b.add(nh.tube([(sx * 0.33, 0.42, -0.04), (sx * 0.46, 0.58, -0.05), (sx * 0.52, 0.70, -0.06)],
                      [0.06, 0.045, 0.02], sides=8, scale_xy=(1.0, 0.3)), SKIN)
    b.add(nh.tube([(0, 0.58, -0.02), (0, 0.72, -0.04)], [0.04, 0.0], sides=8), SKIN)
    fused = b.fuse(voxel=0.016, smooth=3, smooth_factor=0.5, max_tris=7000)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            c = (c[0], c[1], c[2])
            p = l.vert.co
            if l.vert.normal.z > 0.2 and (p.x / 0.5) ** 2 + (p.y / 0.62) ** 2 < 1.05 and p.y > -0.62:
                dist, _ = noise.voronoi(Vector((p.x * 5, p.y * 5, 0)), distance_metric="DISTANCE")
                c = nh.lerp((0.12, 0.11, 0.08), SHELL, nh.smoothstep(0.02, 0.1, dist[1] - dist[0]))
                c = nh.lerp(c, SHELL_RIM, nh.smoothstep(0.85, 1.0, (p.x / 0.5) ** 2 + (p.y / 0.62) ** 2))
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((0.07 + sx * 0.06, -0.95, 0.03), (0.015,) * 3, subdivisions=2), EYE)
    return mb.to_object("StupendemysGeographicus")


if __name__ == "__main__":
    nh.run(build, "StupendemysGeographicus", background=(0.04, 0.10, 0.13), views=((35, 35), (-90, 5), (0, 80)))
