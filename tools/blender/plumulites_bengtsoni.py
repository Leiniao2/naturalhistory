"""
Procedural Plumulites bengtsoni Vinther, Van Roy & Briggs, 2008 (Early Ordovician machaeridian
from the Fezouata Shale of Morocco) for map colonies (Swim style).

Machaeridians were armoured annelid worms, relatives of today's scaleworms. Plumulites was a
slender worm a few centimetres long whose back was covered from end to end by rows of
overlapping, ridged calcite plates, like a coat of mail or a stack of roof tiles, two columns on
each side meeting along the midline. Beneath the armour each segment carried a pair of fleshy
parapodia with bundles of bristles (chaetae) sticking out at the sides, and the head had a pair
of small jaws. Pale grey-white plates with growth ridges over a pinkish body (colours
conjectural). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/plumulites_bengtsoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PlumulitesBengtsoni.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Matrix, Vector  # noqa: E402
import nh_model as nh  # noqa: E402

BODY = (0.78, 0.56, 0.52)
BODY_DARK = (0.56, 0.36, 0.34)
PLATE = (0.86, 0.85, 0.80)
PLATE_DARK = (0.56, 0.55, 0.52)
CHAETA = (0.92, 0.84, 0.62)
JAW = (0.20, 0.14, 0.10)

LENGTH = 1.8
SEGS = 22
R = 0.075


def axis(t):
    """Body axis: y from front (-) to back (+), a gentle S-curve sideways."""
    y = -LENGTH / 2 + LENGTH * t
    return Vector((0.08 * math.sin(t * math.pi * 1.6), y, 0.0))


def width(t):
    return R * (0.55 + 0.45 * math.sin(math.pi * min(1.0, 0.15 + t * 0.95)) ** 0.6)


def build():
    mb = nh.MeshBuilder()
    n = 40
    pts = [axis(i / n) for i in range(n + 1)]
    radii = [width(i / n) for i in range(n + 1)]
    radii[0] *= 0.6
    radii[-1] = 0.01
    mb.add(nh.tube(pts, radii, sides=12, scale_xy=(1.0, 0.65)),
           lambda co, nn: nh.lerp(BODY, BODY_DARK, 0.5 + 0.5 * math.cos((co.y + LENGTH / 2) / LENGTH * SEGS * math.tau)))

    for i in range(SEGS):
        t = (i + 0.5) / SEGS
        p = axis(t)
        d = (axis(min(1.0, t + 0.01)) - axis(max(0.0, t - 0.01))).normalized()
        side = Vector((-d.y, d.x, 0)).normalized()      # points to +x for d = +y... sign below
        w = width(t)
        # two columns of plates per side: inner (near midline, higher) and outer (on the flank)
        for sx in (-1, 1):
            for col, (off, up, tilt, size) in enumerate(((0.32, 0.62, 18, 1.0), (0.85, 0.28, 48, 0.9))):
                c = p + side * (-sx) * w * off + Vector((0, 0, w * up))
                rx, ry, rz = w * 0.55 * size, LENGTH / SEGS * 0.95, w * 0.10
                bm = nh.ellipsoid((0, 0, 0), (rx, ry, rz), subdivisions=2,
                                  deform=lambda v: 1.0 + 0.10 * v.y)
                rot = Matrix.Rotation(math.radians(-sx * tilt), 4, "Y") @ Matrix.Rotation(math.radians(-14), 4, "X")
                yaw = Matrix.Rotation(math.atan2(d.x, d.y) * -1.0, 4, "Z")
                nh.transform(bm, Matrix.Translation(c) @ yaw @ rot)
                cc = c.copy()
                mb.add(bm, lambda co, nn, cc=cc, ry=ry: nh.lerp(PLATE, PLATE_DARK,
                       0.55 * nh.smoothstep(0.5, 1.0, math.cos(((co - cc).y / ry) * 9.0) * 0.5 + 0.5)
                       + 0.35 * nh.smoothstep(0.3, 1.0, (co - cc).y / ry)), smooth=False)
        # parapodia with chaetae bundles sticking out under the armour
        for sx in (-1, 1):
            base = p + side * (-sx) * w * 0.9 + Vector((0, 0, -w * 0.15))
            out = (side * (-sx) + Vector((0, 0, -0.15))).normalized()
            mb.add(nh.tube([base, base + out * w * 0.45], [w * 0.22, w * 0.12], sides=5), BODY)
            for k in range(3):
                a = (k - 1) * 0.35
                dd = (out + d * a + Vector((0, 0, 0.1 * k - 0.1))).normalized()
                tip = base + out * w * 0.4 + dd * w * 1.1
                mb.add(nh.tube([base + out * w * 0.4, tip], [w * 0.03, 0.0], sides=3), CHAETA, smooth=False)

    # head with a pair of small dark jaws
    h = axis(0.0)
    for sx in (-1, 1):
        mb.add(nh.tube([h + Vector((sx * 0.015, 0.02, -0.01)), h + Vector((sx * 0.025, -0.03, -0.012)),
                        h + Vector((sx * 0.008, -0.05, -0.012))], [0.012, 0.009, 0.0], sides=5), JAW)
    obj = mb.to_object("PlumulitesBengtsoni", roughness=0.45)
    vs = obj.data.vertices
    c = Vector(((min(v.co.x for v in vs) + max(v.co.x for v in vs)) / 2,
                (min(v.co.y for v in vs) + max(v.co.y for v in vs)) / 2,
                (min(v.co.z for v in vs) + max(v.co.z for v in vs)) / 2))
    for v in vs:
        v.co -= c
    return obj


if __name__ == "__main__":
    nh.run(build, "PlumulitesBengtsoni", background=(0.05, 0.18, 0.22), views=((30, 40), (0, 85), (-90, 12)))
