"""
Procedural giant squid (Architeuthis dux, Pleistocene to today, deep oceans
worldwide) for map colonies.

One of the largest invertebrates, females up to about 12-13 m long including the
two long feeding tentacles (the mantle alone about 2 m): a long, muscular,
torpedo-shaped mantle with a pair of small, rounded fins at the rear, a head
with the largest eyes in the animal kingdom (up to 27 cm across), eight thick
sucker-lined arms and two whip-like tentacles ending in toothed sucker clubs.
It hunts in the dark at 300-1,000 m and is the favourite prey of sperm whales.
Deep reddish-purple chromatophores over a paler body.

Reuses the squid mantle, head and arm helpers of wyoteuthis.py. Pivot at the
body centre, arms forward (-Y), back up (+Z).

Usage:
  blender --background --python tools/blender/architeuthis_dux.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArchiteuthisDux.fbx
"""

import math
import sys
from pathlib import Path

from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import wyoteuthis as wy  # noqa: E402

wy.PALE = (0.86, 0.62, 0.56)
wy.DORSAL = (0.58, 0.16, 0.16)
wy.SPOT = (0.40, 0.08, 0.10)
wy.FIN = (0.78, 0.40, 0.36)
wy.FIN_EDGE = (0.55, 0.18, 0.18)
wy.ARM = (0.72, 0.32, 0.28)
wy.HOOK = (0.95, 0.88, 0.82)

# long, slender mantle tapering to a point at the rear
wy.MANTLE_R = [(-0.38, 0.115), (-0.30, 0.125), (-0.10, 0.128), (0.15, 0.118), (0.40, 0.098),
               (0.62, 0.075), (0.78, 0.055), (0.88, 0.040), (0.95, 0.022), (0.985, 0.006)]


def fin(sign):
    """Small, rounded fin pair at the very rear of the mantle."""
    pts = []
    outline = [(0.0, 0.98), (0.05, 0.95), (0.09, 0.88), (0.10, 0.82), (0.08, 0.76), (0.04, 0.72), (0.0, 0.70)]
    for u, y in outline:
        pts.append((sign * (wy.mr(y) * 0.8 + u), y, 0.0))
    if sign < 0:
        pts.reverse()
    return nh.flat_panel(pts, thickness=0.012)


def arm_path(k, n_arms=8):
    """Eight thick arms in a ring, spreading and curling a little."""
    a = k / n_arms * math.tau + math.pi / n_arms
    ring = 0.07
    length = 0.55 + 0.05 * math.cos(a * 2.0)
    pts, radii = [], []
    n = 14
    for i in range(n):
        t = i / (n - 1)
        spread = ring * (1.0 + 1.6 * math.sin(t * math.pi * 0.8)) * (1.0 - 0.2 * t)
        curl = 0.08 * t * t
        x = math.cos(a) * spread + curl * math.cos(a + 1.2)
        z = math.sin(a) * spread * 0.9 + curl * math.sin(a + 1.2)
        pts.append((x, wy.ARM_BASE_Y + 0.06 - length * t, z))
        radii.append(0.030 * (1.0 - 0.85 * t) + 0.002)
    radii[-1] = 0.0
    return pts, radii, a


def tentacle(sx):
    """Long whip-like feeding tentacle ending in a broadened club."""
    pts, radii = [], []
    n = 24
    for i in range(n):
        t = i / (n - 1)
        x = sx * (0.03 + 0.10 * math.sin(t * math.pi * 1.5))
        z = -0.02 + 0.06 * math.sin(t * math.pi * 2.0 + sx)
        pts.append((x, wy.ARM_BASE_Y - 1.10 * t, z))
        club = math.exp(-((t - 0.9) / 0.06) ** 2)
        radii.append(0.010 + 0.022 * club)
    radii[-1] = 0.0
    return pts, radii


def build():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    parts.add(wy.mantle(), grey)
    parts.add(nh.ellipsoid(center=(0, -0.47, 0.0), radii=(0.11, 0.16, 0.10), subdivisions=3), grey)
    for s in (-1, 1):
        parts.add(nh.ellipsoid(center=(s * 0.085, -0.47, 0.01), radii=(0.07, 0.09, 0.08), subdivisions=3), grey)
    parts.add(nh.ellipsoid(center=(0, -0.385, 0.0), radii=(0.11, 0.06, 0.10), subdivisions=3), grey)
    parts.add(nh.tube([(0, -0.30, -0.08), (0, -0.42, -0.10), (0, -0.50, -0.09)], [0.035, 0.03, 0.02], sides=10), grey)
    parts.add(nh.ellipsoid(center=(0, -0.60, 0.0), radii=(0.085, 0.08, 0.08), subdivisions=3), grey)
    fused = parts.fuse(voxel=0.025, smooth=4, smooth_factor=0.5)

    mb = nh.MeshBuilder()
    mb.add(fused, color=wy.body_color)
    for s in (-1, 1):
        mb.add(fin(s), color=wy.fin_color, smooth=False)
        c = Vector((s * 0.145, -0.47, 0.02))
        # the giant eye: a big black pupil in a pale silvery-blue iris
        mb.add(nh.ellipsoid(center=c, radii=(0.03, 0.075, 0.07), subdivisions=3),
               color=lambda co, n, s=s: (0.02, 0.02, 0.04) if n.x * s > 0.75 else (0.70, 0.74, 0.80))
    for k in range(8):
        pts, radii, a = arm_path(k)
        mb.add(nh.tube(pts, radii, sides=6, cap_start=False), color=wy.arm_color(a))
    for sx in (-1, 1):
        pts, radii = tentacle(sx)
        mb.add(nh.tube(pts, radii, sides=6, cap_start=False), color=wy.arm_color(math.pi / 2 * sx))
    return mb.to_object("ArchiteuthisDux", roughness=0.35)


if __name__ == "__main__":
    nh.run(build, "ArchiteuthisDux", background=(0.05, 0.16, 0.22), views=((35, 25), (-90, 8), (0, 90)))
