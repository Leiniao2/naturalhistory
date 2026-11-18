"""
Procedural Carbonemys cofrinii (Cerrejon, Colombia, middle-late Paleocene, ~60-58 Ma) for map
colonies: a giant side-necked freshwater turtle (Podocnemididae) with a shell about 1.7 m
long, living alongside Titanoboa in a hot tropical swamp forest.

Shown swimming: a broad, smooth, rounded carapace without horns, a very large,
broad head with powerful, heavy jaws (big enough to tackle crocodile-sized prey),
a neck that folds sideways (pleurodire), webbed paddle-like limbs and a short tail.
Dark olive-brown shell with paler rims, olive-grey skin.
Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/carbonemys_cofrinii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CarbonemysCofrinii.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

SHELL = (0.22, 0.24, 0.16)
SHELL_RIM = (0.38, 0.36, 0.24)
SEAM = (0.10, 0.11, 0.07)
SKIN = (0.36, 0.38, 0.30)
BELLY = (0.66, 0.62, 0.48)
JAW = (0.50, 0.48, 0.38)
EYE = (0.10, 0.08, 0.04)


def build():
    b = nh.MeshBuilder()
    b.add(nh.ellipsoid((0, 0, 0.0), (0.50, 0.58, 0.18), subdivisions=4,
                       deform=lambda v: 1.0 + 0.10 * max(0.0, v.z) ** 2 - 0.3 * max(0.0, -v.z) ** 2), SHELL)
    b.add(nh.ellipsoid((0, 0, -0.06), (0.42, 0.50, 0.08)), BELLY)                       # plastron
    # neck folded a little to one side and a big, broad, heavy-jawed head
    b.add(nh.tube([(0, -0.46, 0.0), (0.04, -0.62, 0.0), (0.07, -0.76, 0.0)], [0.10, 0.095, 0.09], sides=12), SKIN)
    b.add(nh.ellipsoid((0.08, -0.88, 0.01), (0.13, 0.15, 0.08)), SKIN)                  # broad skull
    b.add(nh.ellipsoid((0.08, -0.97, -0.035), (0.115, 0.10, 0.045)), JAW)               # deep lower jaw
    b.add(nh.ellipsoid((0.08, -1.0, 0.0), (0.09, 0.07, 0.055)), SKIN)                   # blunt snout
    for sx in (-1, 1):
        b.add(nh.tube([(sx * 0.38, -0.30, -0.03), (sx * 0.60, -0.22, -0.05), (sx * 0.76, -0.06, -0.06)],
                      [0.065, 0.055, 0.02], sides=8, scale_xy=(1.0, 0.3)), SKIN)
        b.add(nh.tube([(sx * 0.33, 0.40, -0.04), (sx * 0.47, 0.56, -0.05), (sx * 0.53, 0.68, -0.06)],
                      [0.065, 0.05, 0.02], sides=8, scale_xy=(1.0, 0.3)), SKIN)
    b.add(nh.tube([(0, 0.54, -0.02), (0, 0.68, -0.04)], [0.045, 0.0], sides=8), SKIN)
    fused = b.fuse(voxel=0.016, smooth=3, smooth_factor=0.5, max_tris=7000)
    fused.normal_update()
    col = fused.loops.layers.color.get("Col")
    for f in fused.faces:
        for l in f.loops:
            c = l[col]
            c = (c[0], c[1], c[2])
            p = l.vert.co
            e = (p.x / 0.5) ** 2 + (p.y / 0.58) ** 2
            if l.vert.normal.z > 0.2 and e < 1.05:
                dist, _ = noise.voronoi(Vector((p.x * 4.5, p.y * 4.5, 0)), distance_metric="DISTANCE")
                c = nh.lerp(SEAM, SHELL, nh.smoothstep(0.02, 0.1, dist[1] - dist[0]))
                c = nh.lerp(c, SHELL_RIM, nh.smoothstep(0.82, 1.0, e))
                c = nh.lerp(c, SEAM, 0.25 * max(0.0, noise.noise(p * 12)))
            l[col] = (c[0], c[1], c[2], 1.0)
    mb = nh.MeshBuilder()
    mb.add(fused)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((0.08 + sx * 0.085, -0.96, 0.04), (0.018,) * 3, subdivisions=2), EYE)
    obj = mb.to_object("CarbonemysCofrinii")
    vs = obj.data.vertices
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (lo + hi) / 2
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "CarbonemysCofrinii", background=(0.04, 0.10, 0.13), views=((35, 35), (-90, 5), (0, 80)))
