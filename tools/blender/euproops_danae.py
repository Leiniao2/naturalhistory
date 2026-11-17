"""
Procedural Euproops danae (Late Carboniferous of Mazon Creek, Illinois, a small horseshoe
crab about 3-5 cm long) for map colonies (Swim style).

A little xiphosurid: a broad, crescent-shaped head shield whose rear corners are drawn out
into long, backswept genal spines, a raised central ridge with a pair of eye ridges, a fused,
roughly hexagonal hind shield (thoracetron) fringed with short marginal spines, and a long
straight tail spine. Dark olive-brown with paler ridges. Built with nh_car_arthropod.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/euproops_danae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Euproops.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_arthropod as ar  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

NAME = "Euproops"
SHELL = (0.26, 0.22, 0.13)
RIDGE = (0.46, 0.40, 0.25)
HIND = (0.30, 0.25, 0.15)
SPINE = (0.22, 0.18, 0.11)
EYE = (0.06, 0.05, 0.04)

Y0 = -0.1     # back edge of the head shield
R = 0.36


def head_outline():
    """Convex crescent-free half disc; the genal spines are added as separate flattened tubes."""
    pts = [(R * 0.9, Y0 + 0.03), (0.0, Y0 + 0.03), (-R * 0.9, Y0 + 0.03)]
    for k in range(0, 17):
        a = math.pi - k / 16 * math.pi
        pts.append((R * 1.02 * math.cos(a), Y0 - R * 1.05 * math.sin(a)))
    return list(reversed(pts))


def genal_spines():
    out = []
    for sx in (-1, 1):
        out.append(nh.tube([(sx * R * 0.88, Y0 - 0.06, 0.03), (sx * R * 0.97, Y0 + 0.12, 0.028),
                            (sx * R * 1.0, Y0 + 0.36, 0.026)], [0.05, 0.03, 0.0], sides=10, scale_xy=(1.0, 0.3)))
    return out


HIND_OUT = [(0.23, -0.09), (0.25, 0.04), (0.17, 0.19), (0.07, 0.25), (-0.07, 0.25), (-0.17, 0.19), (-0.25, 0.04),
            (-0.23, -0.09), (0, -0.08)]


def build():
    parts = []
    parts.append((ar.plate(head_outline(), 0.03, 0.022, dome=0.03, rings=3), SHELL))
    parts += [(bm, SHELL) for bm in genal_spines()]
    # central ridge and the two eye ridges
    parts.append((nh.uv_ellipsoid((0, Y0 - 0.12, 0.07), (0.05, 0.14, 0.03), 14, 8), RIDGE))
    for sx in (-1, 1):
        parts.append((nh.tube([(sx * 0.10, Y0 - 0.30, 0.05), (sx * 0.17, Y0 - 0.17, 0.065), (sx * 0.15, Y0 - 0.02, 0.06)],
                              [0.016, 0.02, 0.014], sides=8), RIDGE))
    parts.append((ar.plate(list(reversed(HIND_OUT)), 0.035, 0.022, dome=0.03, rings=3), HIND))
    parts.append((nh.uv_ellipsoid((0, 0.08, 0.06), (0.04, 0.13, 0.022), 12, 8), RIDGE))
    parts.append((nh.tube([(0, 0.21, 0.04), (0, 0.43, 0.035), (0, 0.66, 0.03)], [0.022, 0.014, 0.0], sides=8), SPINE))
    fused = ar.fuse_parts(parts, voxel=0.006, max_tris=5000)
    tree = BVHTree.FromBMesh(fused)
    details = []
    # marginal spines on the hind shield
    for sx in (-1, 1):
        for k in range(5):
            t = k / 4
            p = Vector((sx * (0.245 - 0.15 * t), 0.02 + 0.18 * t, 0.035))
            d = Vector((sx * 1.0, 0.6, 0)).normalized()
            details.append((nh.tube([p - d * 0.01, p + d * 0.06], [0.009, 0.0], sides=4), SPINE))
        loc, nrm = ar.ray_down(tree, sx * 0.17, Y0 - 0.16)
        if loc is not None:
            details.append(ar.eye(loc + nrm * 0.002, 0.016, (sx, 0, 0.5), iris=EYE))
    return ar.finish(fused, details, NAME, ground=False)


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.10, 0.20, 0.20), views=((35, 35), (-90, 8), (0, 85)))
