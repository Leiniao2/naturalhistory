"""
Procedural Constellaria florida (Late Ordovician bryozoan, Cincinnati region) for map
colonies (Fixed style).

A colony of tiny filter-feeding zooids growing as flattened, branching fronds a few
centimetres tall. Its surface is dotted with regularly spaced, star-shaped patches
(maculae) where no feeding zooids grew: these "constellations", which gave the genus its
name, were vents where filtered water flowed out of the colony. Built as a cluster of
forking, ribbon-flat branches on a holdfast, painted with pale stars on a finely pitted
surface. Purple-brown with cream stars. Pivot on the sea floor (z = 0), facing -Y.

Usage:
  blender --background --python tools/blender/constellaria_florida.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ConstellariaFlorida.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector, noise  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "ConstellariaFlorida"
BASE = (0.58, 0.36, 0.44)
DARK = (0.42, 0.24, 0.32)
STAR = (0.96, 0.86, 0.62)


def col(co, n):
    pit = 0.5 + 0.5 * noise.noise(co * 70)
    c = nh.lerp(BASE, DARK, 0.5 * nh.smoothstep(0.55, 0.75, pit))
    s = kit.stars(co, n, cell=0.055, r=0.026, rays=6, seed=3.0)
    return nh.lerp(c, STAR, s)


def build():
    mb = nh.MeshBuilder()
    rnd = kit.seeded(11)

    def branch(p, d, L, w, level):
        steps = 5
        pts = [p]
        q = Vector(p)
        dd = Vector(d)
        for i in range(steps):
            dd = (dd + Vector((rnd.uniform(-0.05, 0.05), rnd.uniform(-0.03, 0.03), 0.08))).normalized()
            q = q + dd * (L / steps)
            pts.append(q.copy())
        radii = [w * (1.0 - 0.15 * i / steps) for i in range(steps + 1)]
        if level == 2:
            pts.append(q + dd * w * 0.6)
            radii.append(w * 0.35)
        mb.add(nh.tube(pts, radii, sides=12, scale_xy=(1.0, 0.28)), BASE)
        if level < 2:
            # fronds fork within one plane (x-z), like a fan
            for sg in (-1, 1):
                nd = (dd + Vector((sg * 0.55, rnd.uniform(-0.15, 0.15), 0))).normalized()
                branch(q - dd * 0.03, nd, L * 0.8, w * 0.82, level + 1)

    for k, (a, tilt, L) in enumerate(((0.0, 0.18, 0.42), (math.pi, 0.22, 0.36), (1.6, 0.35, 0.30))):
        d = Vector((math.cos(a) * tilt, math.sin(a) * tilt, 1.0)).normalized()
        branch(Vector((math.cos(a) * 0.05, math.sin(a) * 0.05, 0.02)), d, L, 0.13, 0 if k < 2 else 1)
    mb.add(nh.ellipsoid((0, 0, 0.03), (0.16, 0.16, 0.06), 2), BASE)
    fused = mb.fuse(voxel=0.016, smooth=4, max_tris=12000)
    out = nh.MeshBuilder()
    kit.mud(out, 0.6)
    out.add(fused, col)
    return kit.finish_fixed(out, NAME, roughness=0.7)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.VIEWS)
