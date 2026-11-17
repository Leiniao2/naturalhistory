"""
Procedural Haliestes dasos (mid-Silurian sea spider from the Herefordshire Lagerstaette,
England, about 430 million years old; body a few mm long) for map colonies (Swim style).

The oldest well-preserved pycnogonid: a slender trunk of four segments, each with a pair
of lateral processes carrying a long, many-jointed leg ending in a hooked claw; a long,
barrel-shaped proboscis in front; a pair of big, chelate "great appendages"
(chelifores) beside it; a small eye tubercle on the head; and, unusually, a long
segmented tail (abdomen) behind. Pale yellowish-tan. Reuses the jointed legs and pincers
of nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/haliestes_dasos.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HaliestesDasos.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

NAME = "HaliestesDasos"
COL = eu.Spec(name=NAME, shell=(0.72, 0.58, 0.36), shell_dark=(0.46, 0.34, 0.20), rim=(0.86, 0.76, 0.56),
              under=(0.80, 0.68, 0.48), leg=(0.70, 0.56, 0.34), leg_dark=(0.52, 0.40, 0.22), spine=(0.40, 0.30, 0.18))
TRUNK = [-0.18, -0.06, 0.06, 0.18]


def build():
    s = COL
    mb = nh.MeshBuilder()
    # trunk segments with lateral processes
    for i, y in enumerate(TRUNK):
        mb.add(nh.uv_ellipsoid((0, y, 0), (0.05, 0.075, 0.04), 10, 6), s.shell)
        for sx in (-1, 1):
            a = math.radians(-45 + 30 * i)
            d = Vector((sx * math.cos(a), math.sin(a), 0.0))
            base = Vector((0, y, 0))
            proc = base + d * 0.11
            mb.add(nh.tube([base, proc], [0.035, 0.028], sides=8), s.shell)
            knee = proc + d * 0.22 + Vector((0, 0, 0.12))
            mid = proc + d * 0.45 + Vector((0, 0, 0.05))
            tip = proc + d * 0.66 + Vector((0, 0, -0.08))
            claw = tip + d * 0.05 + Vector((0, 0, -0.04))
            eu.jointed(mb, s, [proc, proc + d * 0.08, knee, mid, tip, claw], [0.024, 0.022, 0.018, 0.014, 0.010, 0.0],
                       spines=0)
    # head with eye tubercle, proboscis, chelifores
    mb.add(nh.uv_ellipsoid((0, -0.29, 0.005), (0.055, 0.07, 0.045), 10, 6), s.shell)
    mb.add(nh.tube([(0, -0.30, 0.04), (0, -0.30, 0.09)], [0.02, 0.012], sides=6), s.shell_dark)
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.01, -0.305, 0.09), (0.008,) * 3, 1), (0.08, 0.06, 0.05))
    mb.add(nh.tube([(0, -0.33, -0.01), (0, -0.42, -0.02), (0, -0.55, -0.03), (0, -0.62, -0.035)],
                   [0.035, 0.042, 0.03, 0.0], sides=10), s.rim)
    for sx in (-1, 1):
        base = Vector((sx * 0.04, -0.33, 0.02))
        j1 = base + Vector((sx * 0.08, -0.06, 0.05))
        j2 = j1 + Vector((-sx * 0.01, -0.12, 0.0))
        eu.pincer(mb, s, sx, base, j1, j2, 0.55, 0.12, 3)
    # segmented tail
    pts = [Vector((0, 0.24 + 0.06 * k, 0.01 * k)) for k in range(6)]
    for a, b in zip(pts, pts[1:]):
        mb.add(nh.tube([a, a.lerp(b, 0.5), b], [0.022, 0.024, 0.018], sides=7), s.shell)
    mb.add(nh.tube([pts[-1], pts[-1] + Vector((0, 0.06, 0.0))], [0.016, 0.0], sides=6), s.shell_dark)
    obj = mb.to_object(NAME, roughness=0.5)
    vs = obj.data.vertices
    zs, ys = [v.co.z for v in vs], [v.co.y for v in vs]
    off = Vector((0, -(min(ys) + max(ys)) / 2, -(min(zs) + max(zs)) / 2))
    for v in vs:
        v.co += off
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, **eu.VIEWS)
