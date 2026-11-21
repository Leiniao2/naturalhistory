"""
Procedural giant Pacific octopus (Enteroctopus dofleini, Pleistocene to today,
North Pacific from California to Japan) for map colonies.

The largest octopus, usually 3-5 m across the arms and 15-50 kg: a big, baggy,
wrinkled mantle, a head with prominent eyes, and eight long arms, each with up
to 280 suckers, webbed together at the base. It hunts crabs, clams and fish on
rocky sea floors, crushes shells with its beak, changes colour in a moment and
can solve puzzles and recognise individual people. Reddish-brown skin with
pale wrinkles and papillae, cream suckers.

Shown crawling with its arms spread and curling. Pivot at the body centre,
faces -Y (the eyes and the leading arms), mantle up and back.

Usage:
  blender --background --python tools/blender/enteroctopus_dofleini.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EnteroctopusDofleini.fbx
"""

import math
import sys
from pathlib import Path

from mathutils import Vector, noise

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

SKIN = (0.66, 0.24, 0.14)
DARK = (0.42, 0.12, 0.08)
PALE = (0.90, 0.62, 0.48)
SUCKER = (0.95, 0.86, 0.72)


def arm_points(k):
    """Arm k of 8: leaves the arm crown, spreads over the sea floor and curls at the tip."""
    a = (k + 0.5) / 8 * math.tau          # 0 = +X; arms all round, the front pair reaching forward (-Y)
    d = Vector((math.cos(a), math.sin(a), 0))
    side = Vector((-d.y, d.x, 0))
    curl = 1 if k % 2 else -1
    length = 0.95 if d.y < 0 else 0.80
    pts, radii = [], []
    n = 22
    for i in range(n):
        t = i / (n - 1)
        r = 0.10 + length * t
        bend = side * curl * 0.18 * t * t + side * 0.05 * math.sin(t * 5 + k)
        z = -0.06 - 0.04 * math.sin(t * math.pi * 0.6) + 0.10 * nh.smoothstep(0.75, 1.0, t)
        p = d * r + bend + Vector((0, -0.05, z))
        if t > 0.8:   # tip curls up and over
            u = (t - 0.8) / 0.2
            p += -d * 0.06 * u * u + Vector((0, 0, 0.05 * u))
        pts.append(tuple(p))
        radii.append(0.055 * (1 - t) ** 1.2 + 0.003)
    radii[-1] = 0.0
    return pts, radii


def skin_color(co, n):
    c = nh.lerp(SKIN, DARK, 0.6 * nh.smoothstep(0.1, 0.7, n.z) * nh.smoothstep(0.0, 0.3, co.z))
    w = noise.noise(co * 22.0)
    c = nh.lerp(c, PALE, 0.55 * nh.smoothstep(0.25, 0.5, w))
    if n.z < -0.4 and co.z < 0.0:     # pale undersides of the arms with sucker rows
        s = 0.5 + 0.5 * math.sin((co.x * co.x + co.y * co.y) ** 0.5 * 140.0)
        c = nh.lerp(PALE, SUCKER, nh.smoothstep(0.4, 0.8, s))
    return c


def build():
    parts = nh.MeshBuilder()
    grey = (0.5, 0.5, 0.5)
    # baggy mantle rising behind the head, tilted back
    parts.add(nh.ellipsoid((0, 0.18, 0.18), (0.20, 0.27, 0.21), subdivisions=4,
                           deform=lambda v: 1.0 + 0.06 * noise.noise(v * 4.0)), grey)
    parts.add(nh.ellipsoid((0, -0.02, 0.03), (0.17, 0.15, 0.12), subdivisions=3), grey)          # head
    for sx in (-1, 1):
        parts.add(nh.ellipsoid((sx * 0.10, -0.05, 0.10), (0.06, 0.06, 0.06), subdivisions=3), grey)  # eye bulges
    # web between the arm roots
    parts.add(nh.ellipsoid((0, -0.05, -0.06), (0.30, 0.30, 0.05), subdivisions=3), grey)
    for k in range(8):
        pts, radii = arm_points(k)
        parts.add(nh.tube(pts, radii, sides=8, cap_start=False), grey)
    fused = parts.fuse(voxel=0.014, smooth=5, smooth_factor=0.5, max_tris=14000)
    mb = nh.MeshBuilder()
    mb.add(fused, color=skin_color)
    for sx in (-1, 1):
        at = Vector((sx * 0.135, -0.08, 0.12))
        nh.eye(mb, at, (sx * 0.8, -0.4, 0.4), 0.026, SKIN, iris=(0.80, 0.68, 0.30))
    obj = mb.to_object("EnteroctopusDofleini", roughness=0.4)
    vs = obj.data.vertices
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (lo + hi) / 2
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "EnteroctopusDofleini", background=(0.05, 0.16, 0.22), views=((35, 30), (-90, 8), (0, 85)))
