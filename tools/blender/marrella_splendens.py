"""
Procedural low-poly Marrella splendens (Burgess Shale marrellomorph arthropod).

Small, slender segmented trunk (26 segments) with a fringe of feathery legs and
gill branches down each side, a tiny button telson; a small wedge-shaped head
shield from which two pairs of long spines sweep back over the body (the outer
pair curving out and back, the inner pair arching up and back); a pair of long,
thin first antennae and a pair of stout, bristled swimming antennae. Pale
silvery-lilac body with darker spines (fossils show traces of iridescence).
Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Marrella.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.78, 0.74, 0.82)
BODY_DARK = (0.52, 0.48, 0.62)
BELLY = (0.90, 0.86, 0.86)
SPINE = (0.46, 0.30, 0.52)
SPINE_TIP = (0.80, 0.62, 0.80)
LEG = (0.84, 0.70, 0.70)
GILL = (0.86, 0.52, 0.56)
HEAD = (0.64, 0.56, 0.72)
EYE = (0.08, 0.06, 0.08)

Y0, Y1, SEG = -0.30, 0.55, 26


def width(t):
    return 0.07 * (1 - 0.75 * t ** 1.4)


def build():
    mb = nh.MeshBuilder()
    mb.add(ec.segmented_trunk(Y0, Y1, SEG, width, flat=0.55, sides=8),
           ec.banded(BODY, BODY_DARK, BELLY, Y0, (Y1 - Y0) / SEG, amount=0.5))
    # head shield: a small wedge
    mb.add(nh.uv_ellipsoid((0, Y0 - 0.06, 0.015), (0.075, 0.1, 0.04), segments=12, rings=7), HEAD)
    # legs + gill filaments
    for i in range(SEG):
        t = (i + 0.5) / SEG
        y = Y0 + (Y1 - Y0) * t
        w = width(t)
        ln = 0.06 + 0.05 * (1 - t)
        for s in (-1, 1):
            root = Vector((s * w * 0.8, y, -0.01))
            foot = root + Vector((s * ln * 0.8, -0.01, -ln * 0.6))
            mb.add(ec.jointed_leg([root, root.lerp(foot, 0.5) + Vector((s * 0.01, 0, 0.01)), foot],
                                  0.008, 0.003, sides=4), LEG, smooth=False)
            g = ec.paddle(ln * 1.05, 0.012, n=8, thickness=0.004)
            nh.transform(g, nh.Matrix.Rotation(math.radians(-15), 4, "Y") @
                         nh.Matrix.Rotation(math.radians(-25), 4, "Z"))
            ec.mirror(g, s)
            nh.transform(g, nh.Matrix.Translation((s * w * 0.7, y, 0.0)))
            mb.add(g, GILL, smooth=False)

    def spine_col(base, d, length):
        def c(co, n):
            t = max(0.0, min(1.0, (co - base).dot(d) / length))
            return nh.lerp(SPINE, SPINE_TIP, nh.smoothstep(0.6, 1.0, t))
        return c

    hy = Y0 - 0.04
    for s in (-1, 1):
        # outer spines: out sideways then sweeping back past the trunk's middle
        base = Vector((s * 0.06, hy, 0.02))
        pts = [base, base + Vector((s * 0.12, 0.06, 0.0)), base + Vector((s * 0.2, 0.25, -0.02)),
               base + Vector((s * 0.2, 0.48, -0.03)), base + Vector((s * 0.16, 0.66, -0.03))]
        mb.add(nh.tube(pts, [0.018, 0.015, 0.011, 0.007, 0.0], sides=6),
               spine_col(base, Vector((0, 1, 0)), 0.66))
        # inner spines: up and back in an arch over the body
        base = Vector((s * 0.03, hy + 0.02, 0.04))
        pts = [base, base + Vector((s * 0.05, 0.08, 0.1)), base + Vector((s * 0.09, 0.3, 0.16)),
               base + Vector((s * 0.1, 0.55, 0.12)), base + Vector((s * 0.09, 0.75, 0.06))]
        mb.add(nh.tube(pts, [0.016, 0.013, 0.01, 0.006, 0.0], sides=6),
               spine_col(base, Vector((0, 1, 0)), 0.75))
        # long thin first antennae
        a0 = Vector((s * 0.02, Y0 - 0.15, 0.0))
        mb.add(nh.tube([a0, a0 + Vector((s * 0.05, -0.15, 0.01)), a0 + Vector((s * 0.14, -0.3, -0.01)),
                        a0 + Vector((s * 0.26, -0.38, -0.03))], [0.008, 0.006, 0.004, 0.0], sides=4), LEG)
        # stout swimming antennae with bristles
        b0 = Vector((s * 0.05, Y0 - 0.1, -0.01))
        b1 = b0 + Vector((s * 0.16, -0.02, -0.01))
        b2 = b1 + Vector((s * 0.1, 0.1, -0.01))
        mb.add(nh.tube([b0, b1, b2], [0.014, 0.011, 0.006], sides=5), LEG)
        for k in range(6):
            p = b1.lerp(b2, k / 5) if k else b0.lerp(b1, 0.6)
            mb.add(ec.spike(p, p + Vector((s * 0.02, 0.05, 0)), r=0.004, sides=3), GILL, smooth=False)
        mb.add(nh.ellipsoid((s * 0.04, Y0 - 0.14, 0.02), (0.012, 0.012, 0.01), subdivisions=1), EYE)
    obj = mb.to_object("Marrella", roughness=0.35)
    return ec.centre(obj)


if __name__ == "__main__":
    ec.export(build, "Marrella")
