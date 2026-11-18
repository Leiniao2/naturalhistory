"""
Procedural Monograptus priodon (Silurian monograptid graptolite, planktonic worldwide
from the Llandovery to the Wenlock) for map colonies (Drift style).

A planktonic colony of a single, long, gently curved branch (stipe), often 10 cm or more
long, carried by a fine thread (nema) and started from a small conical sicula at one
end. Along one side runs a row of close-set cups (thecae), each housing a filter-feeding
zooid, whose mouths are curled back into little hooks - the "saw-tooth" (priodon) edge.
Amber-brown, translucent-looking organic skeleton. Pivot at the colony centre.

Usage:
  blender --background --python tools/blender/monograptus_priodon.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MonograptusPriodon.fbx
"""

import math
import sys
from pathlib import Path

from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402

NAME = "MonograptusPriodon"
AMBER = (0.80, 0.56, 0.26)
AMBER_PALE = (0.95, 0.80, 0.50)
AMBER_DARK = (0.42, 0.24, 0.10)
THREAD = (0.90, 0.82, 0.64)

LEN = 1.7
THECAE = 22
BEND = 0.18


def fusellar(co, n):
    band = 0.5 + 0.5 * math.sin((co.x + co.z) * 150.0)
    return nh.lerp(AMBER, AMBER_PALE, 0.2 + 0.45 * band)


def axis(t):
    """Point along the gently curved stipe (t 0 = sicula end .. 1), and its downward normal."""
    x = -LEN / 2 + LEN * t
    z = BEND * (1 - (2 * t - 1) ** 2)
    dz = BEND * (-4 * (2 * t - 1)) / LEN
    tan = Vector((1.0, 0.0, dz)).normalized()
    down = Vector((tan.z, 0.0, -tan.x))
    return Vector((x, 0.0, z)), tan, down


def build():
    mb = nh.MeshBuilder()
    pts = [axis(i / 20)[0] for i in range(21)]
    mb.add(nh.tube(pts, [0.016 + 0.012 * i / 20 for i in range(21)], sides=6), fusellar)
    # sicula at the proximal end and the nema thread running on beyond it
    p0, tan0, down0 = axis(0.0)
    mb.add(nh.tube([p0 + tan0 * 0.02, p0 - tan0 * 0.05 + down0 * 0.03, p0 - tan0 * 0.10 + down0 * 0.08],
                   [0.016, 0.026, 0.034], sides=8), fusellar)
    p1, tan1, _ = axis(1.0)
    mb.add(nh.tube([p1, p1 + tan1 * 0.15 + Vector((0, 0, 0.03)), p1 + tan1 * 0.35 + Vector((0, 0, 0.02))],
                   [0.006, 0.005, 0.0], sides=4, cap_start=False), THREAD)
    # hooked thecae along the lower side, growing a little larger distally
    for k in range(THECAE):
        t = (k + 0.6) / (THECAE + 0.2)
        base, tan, down = axis(t)
        g = 0.75 + 0.4 * t
        a = base + down * 0.015
        b = a + tan * 0.035 * g + down * 0.045 * g
        c = b + tan * 0.035 * g + down * 0.02 * g
        h = c - tan * 0.02 * g + Vector((0, 0, 0)) - down * 0.022 * g   # hook curling back
        mb.add(nh.tube([a, b, c, h], [0.022 * g, 0.026 * g, 0.022 * g, 0.012 * g], sides=6,
                       cap_start=False), fusellar)
        mb.add(nh.ellipsoid(tuple(h), (0.013 * g,) * 3, 1), AMBER_DARK)
    obj = mb.to_object(NAME, roughness=0.35)
    corners = [Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, views=((30, 25), (0, 85), (90, 5)))
