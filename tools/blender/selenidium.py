"""
Procedural low-poly Selenidium pendula, an archigregarine (a sporozoan) from the gut of marine
worms.

A long, worm-like single cell, round in section and tapering to both ends, bent in a gentle S as
it sways and coils in its host's gut. The front end carries a small pointed mucron that it holds
on with; the surface is drawn into a dozen low lengthwise pleats, shown as fine pale and dark
stripes, and the round nucleus shows through in the middle. Pale golden, translucent-looking.
Colour is in vertex colours (see nh_model).

Usage:
  blender --background --python tools/blender/selenidium.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Selenidium.fbx
Faces -Y (front), long axis along Y, ~1.6 units long. Pivot at the body centre (Drift).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402

LENGTH = 1.5
RADIUS = 0.11
PLEATS = 12
BEND = 0.12           # sideways S-bend

BODY = (0.86, 0.76, 0.50)
BODY_DEEP = (0.70, 0.58, 0.34)
PLEAT_LIGHT = (0.94, 0.88, 0.66)
NUCLEUS = (0.56, 0.44, 0.26)
NUCLEOLUS = (0.36, 0.26, 0.14)
MUCRON = (0.76, 0.64, 0.40)


def axis(t):
    """Point on the body axis, t from 0 (front) to 1 (rear)."""
    y = -LENGTH / 2 + LENGTH * t
    return Vector((BEND * math.sin(t * math.tau * 0.9), y, 0.04 * math.sin(t * math.pi * 2.0 + 0.5)))


def build():
    mb = nh.MeshBuilder()
    n = 18
    pts, radii = [], []
    for k in range(n + 1):
        t = k / n
        pts.append(axis(t))
        # blunt-pointed front, widest a third of the way back, tapering to a fine rear
        r = RADIUS * (math.sin(math.pi * min(1.0, t * 1.08)) ** 0.55) * (1.0 - 0.35 * t)
        radii.append(max(r, 0.035) if k < n else 0.0)  # blunt front (the mucron sits on it), fine rear

    def body_col(co, nrm):
        t = (co.y + LENGTH / 2) / LENGTH
        c = nh.lerp(BODY, BODY_DEEP, nh.smoothstep(0.55, 1.0, t) * 0.6)
        # lengthwise pleats: stripes round the body
        a = math.atan2(nrm.z, nrm.x)
        stripe = 0.5 + 0.5 * math.cos(a * PLEATS)
        c = nh.lerp(c, PLEAT_LIGHT, nh.smoothstep(0.35, 0.9, stripe) * 0.8)
        c = nh.lerp(c, BODY_DEEP, nh.smoothstep(0.35, 0.0, stripe) * 0.5)
        # the round nucleus showing through, a third of the way back, its nucleolus darker
        d = abs(t - 0.36) * LENGTH
        c = nh.lerp(c, NUCLEUS, (1 - nh.smoothstep(0.05, 0.09, d)) * 0.8)
        return nh.lerp(c, NUCLEOLUS, (1 - nh.smoothstep(0.015, 0.03, d)) * 0.7)

    mb.add(nh.tube(pts, radii, sides=PLEATS * 2), body_col)
    # the mucron: a short pointed cap at the front
    front, nxt = axis(0.0), axis(0.03)
    d = (front - nxt).normalized()
    mb.add(nh.tube([front - d * 0.03, front + d * 0.06], [0.04, 0.0], sides=8), MUCRON)
    return mb.to_object("Selenidium", roughness=0.45)


if __name__ == "__main__":
    nh.run(build, "Selenidium", views=((35, 30), (90, 10), (0, 80)))
