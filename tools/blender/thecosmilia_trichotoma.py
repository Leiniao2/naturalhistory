"""
Procedural Thecosmilia trichotoma (Late Jurassic stony coral, Europe) for map colonies.

A reef-building scleractinian coral of the warm Jurassic seas: a bushy (phaceloid) colony
up to about 50 cm across made of separate, ribbed tubular branches that fork again and
again, each ending in a large round cup (corallite) 1-2 cm wide with radiating septa. In
life each cup held one big fleshy polyp with a ring of tentacles that caught plankton, and
algae in its tissues fed it with sunlight. Painted cream skeleton with olive-brown polyps
and pale-tipped tentacles. Fixed style: pivot on the sea floor, faces -Y.

Usage:
  blender --background --python tools/blender/thecosmilia_trichotoma.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Thecosmilia.fbx
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_coral as coral  # noqa: E402
from mathutils import Vector  # noqa: E402

SKEL = (0.86, 0.80, 0.66)
RIB = (0.66, 0.60, 0.48)
POLYP = (0.44, 0.40, 0.20)
DISC = (0.62, 0.54, 0.26)
TIP = (0.86, 0.86, 0.66)


def branch(mb, rng, base, d, length, r, depth):
    tip = base + d * length
    mid = base.lerp(tip, 0.5) + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * length * 0.05

    def ribbed(co, n):
        a = math.atan2(n.y, n.x)
        return RIB if math.sin(a * 12) > 0.4 else SKEL
    mb.add(nh.tube([base, mid, tip], [r * 0.9, r, r * 1.08], sides=14), ribbed)
    if depth > 0 and length > 0.12:
        k = 2 if depth > 1 else rng.choice((2, 3))
        for i in range(k):
            a = rng.uniform(0, math.tau) + i * math.tau / k
            nd = (d + Vector((math.cos(a), math.sin(a), 0)) * rng.uniform(0.35, 0.6)).normalized()
            branch(mb, rng, tip - d * r * 0.5, nd, length * rng.uniform(0.75, 0.95), r * 0.95, depth - 1)
        return
    # the cup and its polyp: a rim, a disc of septa, and a ring of short tentacles
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(d).normalized()
    R = r * 1.15
    rim = nh.tube([tip - d * 0.004, tip + d * 0.01], [R, R], sides=16)
    mb.add(rim, SKEL)
    mb.add(nh.ellipsoid(tuple(tip + d * 0.012), (R * 0.95, R * 0.95, R * 0.35), subdivisions=2,
                        rotation=Vector((0, 0, 1)).rotation_difference(d).to_matrix()), DISC)
    for k in range(14):
        a = k / 14 * math.tau
        o = (side * math.cos(a) + up * math.sin(a))
        b = tip + d * 0.012 + o * R * 0.75
        t = b + (o * 0.6 + d).normalized() * R * 0.9
        mb.add(nh.tube([b, t], [R * 0.13, R * 0.05], sides=4), POLYP)
        mb.add(nh.ellipsoid(tuple(t), (R * 0.07,) * 3, subdivisions=1), TIP)


def build():
    rng = random.Random(11)
    mb = nh.MeshBuilder()
    coral.rubble(mb, rng, 0.05, 0.55, count=10)
    for i in range(3):
        a = i / 3 * math.tau + 0.4
        d = Vector((math.cos(a) * 0.35, math.sin(a) * 0.35, 1.0)).normalized()
        branch(mb, rng, Vector((math.cos(a) * 0.04, math.sin(a) * 0.04, 0.0)), d, 0.3, 0.05, 2)
    obj = mb.to_object("Thecosmilia", roughness=0.6)
    nh.ground_to_zero(obj)
    return obj


if __name__ == "__main__":
    nh.run(build, "Thecosmilia", background=(0.05, 0.15, 0.18), views=((35, 25), (-90, 5), (30, 70)))
