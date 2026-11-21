"""
Procedural Furca mauritanica (Early Ordovician marrellomorph arthropod of the Fezouata
biota, Morocco) for map colonies (Swim style).

A small, delicate arthropod a few centimetres across, a late relative of the Cambrian
Marrella: a flat, rounded head shield from which three pairs of long, slender spines
spread out sideways and backwards, each forking and bearing short side branches (furca
is Latin for fork), so the animal looked like a lacy, many-pointed star. Under the shield
a short body of many small segments carried feathery limbs, with long antennae in front.
It probably lived and fed just above the sea floor. Pale amber shield, translucent spines.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/furca_mauritanica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/FurcaMauritanica.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_b2_ordovician_kit as kit  # noqa: E402

NAME = "FurcaMauritanica"
SHIELD = (0.84, 0.62, 0.34)
SHIELD_DARK = (0.56, 0.36, 0.18)
SPINE = (0.92, 0.78, 0.52)
BODY = (0.70, 0.48, 0.30)
LIMB = (0.90, 0.72, 0.52)
EYE = (0.06, 0.05, 0.04)


def spine(mb, base, d, L, r):
    d = d.normalized()
    up = Vector((0, 0, 1))
    side = d.cross(up).normalized()
    tip = base + d * L + up * 0.03
    mb.add(nh.tube([base, base + d * L * 0.5 + up * 0.02, tip], [r, r * 0.7, 0.0], sides=6), SPINE)
    # fork at the tip and short side branches along it
    fork = base + d * L * 0.72 + up * 0.025
    for sg in (-1, 1):
        dd = (d + side * sg * 0.6).normalized()
        mb.add(nh.tube([fork, fork + dd * L * 0.30], [r * 0.6, 0.0], sides=5), SPINE)
    for k in range(1, 4):
        b = base + d * L * (0.18 + 0.15 * k)
        for sg in (-1, 1):
            dd = (d * 0.6 + side * sg).normalized()
            mb.add(nh.tube([b, b + dd * L * 0.08], [r * 0.45, 0.0], sides=4), SPINE)


def build():
    mb = nh.MeshBuilder()
    # rounded, gently domed head shield
    mb.add(nh.uv_ellipsoid((0, -0.05, 0.0), (0.30, 0.28, 0.06), 28, 10),
           lambda co, n: nh.lerp(SHIELD, SHIELD_DARK, 0.5 * nh.smoothstep(0.15, 0.30, math.hypot(co.x, co.y + 0.05))
                                 + 0.3 * nh.smoothstep(0.0, 0.03, -n.z)))
    mb.add(nh.uv_ellipsoid((0, -0.05, 0.04), (0.08, 0.20, 0.035), 14, 8), SHIELD_DARK)
    # three pairs of long forked spines
    for sx in (-1, 1):
        for (ang, L) in ((-20, 0.62), (25, 0.70), (65, 0.62)):
            a = math.radians(ang)
            d = Vector((sx * math.cos(a), math.sin(a), 0.0))
            spine(mb, Vector((sx * 0.22 * math.cos(a), -0.05 + 0.20 * math.sin(a), 0.0)), d, L, 0.028)
    # segmented body behind, under the shield
    y = 0.12
    w = 0.12
    for i in range(10):
        mb.add(nh.uv_ellipsoid((0, y, -0.04), (w, 0.035, 0.03), 12, 6), BODY if i % 2 else LIMB)
        for sx in (-1, 1):
            b = Vector((sx * w * 0.9, y, -0.05))
            mb.add(nh.tube([b, b + Vector((sx * 0.08, 0.03, -0.01))], [0.012, 0.0], sides=4), LIMB)
        y += 0.045
        w *= 0.90
    # antennae and eyes
    for sx in (-1, 1):
        mb.add(nh.ellipsoid((sx * 0.06, -0.31, 0.01), (0.022, 0.022, 0.02), 2), EYE)
        p = Vector((sx * 0.04, -0.30, -0.02))
        mb.add(nh.tube([p, p + Vector((sx * 0.06, -0.18, 0.0)), p + Vector((sx * 0.16, -0.36, 0.02))],
                       [0.012, 0.008, 0.0], sides=5), LIMB)
    return kit.finish_swim(mb, NAME, roughness=0.4)


if __name__ == "__main__":
    nh.run(build, NAME, **kit.SWIM_VIEWS)
