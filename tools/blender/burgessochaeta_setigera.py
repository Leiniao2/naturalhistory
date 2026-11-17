"""
Procedural low-poly Burgessochaeta setigera (Burgess Shale polychaete worm).

A slim bristle worm of about two dozen segments in a gentle wave; each segment
carries a pair of fleshy parapodia with two fan-shaped bundles of long, fine
chaetae (bristles) splaying sideways; a small rounded head lobe with a pair of
long, thin tentacles curving forward. Ochre-pink body, pale golden bristles.
Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Burgessochaeta.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

BODY = (0.82, 0.54, 0.42)
BODY_DARK = (0.60, 0.36, 0.28)
BELLY = (0.92, 0.74, 0.62)
PARA = (0.86, 0.60, 0.48)
CHAETA = (0.96, 0.86, 0.58)

Y0, Y1, SEG = -0.5, 0.55, 24


def wave_x(y):
    return 0.06 * math.sin(y * 5.5)


def build():
    mb = nh.MeshBuilder()
    pts, radii = [], []
    n = SEG * 2
    for i in range(n + 1):
        y = Y0 + (Y1 - Y0) * i / n
        t = i / n
        pts.append((wave_x(y), y, 0.0))
        radii.append(0.04 * (1 - 0.6 * t ** 2) * (0.85 if i % 2 == 0 else 1.0))
    radii[-1] = 0.0
    mb.add(nh.tube(pts, radii, sides=8, scale_xy=(1.0, 0.75)),
           ec.banded(BODY, BODY_DARK, BELLY, Y0, (Y1 - Y0) / SEG, amount=0.6))
    mb.add(nh.uv_ellipsoid((wave_x(Y0), Y0 - 0.03, 0.0), (0.035, 0.04, 0.03), segments=10, rings=6), BODY)
    for i in range(SEG):
        t = (i + 0.5) / SEG
        y = Y0 + (Y1 - Y0) * t
        r = 0.04 * (1 - 0.6 * t ** 2)
        x0 = wave_x(y)
        dx = 0.33 * math.cos(y * 5.5)  # body direction (slope of the wave)
        for s in (-1, 1):
            root = Vector((x0 + s * r * 0.8, y, 0.0))
            tip = root + Vector((s * 0.04, -s * 0.04 * dx * 0, 0.0))
            mb.add(nh.tube([root, tip], [0.016, 0.01], sides=5), PARA)
            for k in range(5):
                for lvl in (-1, 1):
                    a = math.radians(-35 + 17.5 * k)
                    d = Vector((s * math.cos(a), math.sin(a) * 0.6, lvl * 0.25)).normalized()
                    mb.add(nh.tube([tip, tip + d * (0.09 * (1 - 0.4 * t))], [0.0035, 0.0], sides=3, cap_start=False),
                           CHAETA, smooth=False)
    for s in (-1, 1):
        b = Vector((wave_x(Y0) + s * 0.015, Y0 - 0.06, 0.01))
        mb.add(nh.tube([b, b + Vector((s * 0.04, -0.1, 0.02)), b + Vector((s * 0.1, -0.2, 0.0)),
                        b + Vector((s * 0.12, -0.28, -0.02))], [0.008, 0.006, 0.004, 0.0], sides=4), BODY)
    return ec.centre(mb.to_object("Burgessochaeta", roughness=0.45))


if __name__ == "__main__":
    ec.export(build, "Burgessochaeta")
