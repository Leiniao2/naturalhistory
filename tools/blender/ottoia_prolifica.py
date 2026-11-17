"""
Procedural low-poly Ottoia prolifica (Burgess Shale priapulid worm).

A plump, finely annulated worm in a gentle U/S curve (as if half out of its
burrow) with the barrel-shaped introvert everted at the front: a swollen
proboscis covered in rows of small backward-pointing hooks, ending in a ring
of larger teeth around the mouth. The trunk tapers a little to a rear end
with a few small hooks. Fleshy pink with paler rings, dark tan hooks.
Faces -Y, pivot at the body centre (Swim; a burrowing seafloor predator).

Output: Assets/Resources/Models/Species/Ottoia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.86, 0.56, 0.52)
RING = (0.70, 0.40, 0.38)
PROB = (0.92, 0.70, 0.58)
HOOK = (0.44, 0.28, 0.16)
MOUTH = (0.30, 0.12, 0.12)

N = 40


def axis(t):
    """t 0 (mouth) .. 1 (tail): curls down at the back like a worm half in its burrow."""
    y = -0.6 + 1.2 * t
    z = 0.12 * math.sin(t * math.pi * 1.2) - 0.25 * max(0.0, t - 0.7) ** 1.5
    x = 0.08 * math.sin(t * math.pi * 2.0)
    return Vector((x, y, z))


def radius(t):
    if t < 0.22:  # proboscis
        return 0.05 + 0.03 * math.sin(t / 0.22 * math.pi * 0.9)
    return 0.065 - 0.02 * nh.smoothstep(0.7, 1.0, t)


def build():
    mb = nh.MeshBuilder()
    pts = [axis(i / N) for i in range(N + 1)]
    rr = [radius(i / N) for i in range(N + 1)]
    rr[0], rr[-1] = 0.035, 0.02
    mb.add(nh.tube(pts, rr, sides=12),
           lambda co, n: PROB if co.y < -0.33 else nh.lerp(BODY, RING, 0.6 * nh.smoothstep(0.7, 1.0,
                                                              0.5 + 0.5 * math.cos(co.y * math.tau / 0.028))))
    # hooks on the proboscis
    for i in range(1, 9):
        t = i / 40
        c = axis(t)
        d = (axis(t + 0.01) - c).normalized()
        side = d.cross(Vector((0, 0, 1))).normalized()
        up = side.cross(d).normalized()
        for k in range(8):
            a = k / 8 * math.tau + i * 0.4
            nrm = side * math.cos(a) + up * math.sin(a)
            p = c + nrm * radius(t) * 0.95
            mb.add(ec.spike(p, p + nrm * 0.02 + d * 0.02, r=0.006, sides=3), HOOK, smooth=False)
    # ring of mouth teeth
    c = axis(0.0)
    for k in range(10):
        a = k / 10 * math.tau
        nrm = Vector((math.cos(a), 0, math.sin(a)))
        p = c + nrm * 0.03
        mb.add(ec.spike(p, p + nrm * 0.01 + Vector((0, -0.03, 0)), r=0.007, sides=3), HOOK, smooth=False)
    mb.add(nh.ellipsoid(c + Vector((0, -0.005, 0)), (0.022, 0.01, 0.022), subdivisions=1), MOUTH)
    # posterior hooks
    c = axis(1.0)
    for k in range(5):
        a = k / 5 * math.tau
        p = c + Vector((math.cos(a) * 0.02, 0, math.sin(a) * 0.02))
        mb.add(ec.spike(p, p + Vector((math.cos(a) * 0.02, 0.01, math.sin(a) * 0.02 - 0.01)), r=0.006, sides=3),
               HOOK, smooth=False)
    return ec.centre(mb.to_object("Ottoia", roughness=0.4))


if __name__ == "__main__":
    ec.export(build, "Ottoia")
