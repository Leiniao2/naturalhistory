"""
Procedural low-poly Metaspriggina walcotti (Burgess Shale early vertebrate).

A small, slim, finless, laterally flattened fish-like chordate: a blunt head
with a pair of large, bulging camera eyes set forward on top and a small
nostril pit between them; a row of gill bars behind the head; zig-zag
(chevron) blocks of muscle along the flanks; the body tapering to a low tail
fin fold. Silvery olive back, pale belly, darker chevrons.
Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Metaspriggina.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector  # noqa: E402

BACK = (0.48, 0.52, 0.40)
BELLY = (0.88, 0.86, 0.78)
CHEVRON = (0.30, 0.32, 0.24)
GILL = (0.70, 0.36, 0.34)
EYE = (0.04, 0.04, 0.05)
EYE_RIM = (0.82, 0.80, 0.66)
FIN = (0.66, 0.68, 0.56)


def radius(t):
    return 0.075 * math.sin(math.pi * min(1.0, 0.18 + t * 0.9)) ** 0.7 + 0.004


def build():
    mb = nh.MeshBuilder()
    n = 30
    pts, radii = [], []
    for i in range(n + 1):
        t = i / n
        y = -0.5 + t
        pts.append((0.025 * math.sin(t * 5.0) * t, y, 0.0))
        radii.append(radius(t))
    radii[0], radii[-1] = 0.035, 0.0

    def col(co, nrm):
        t = co.y + 0.5
        c = nh.lerp(BELLY, BACK, nh.smoothstep(-0.03, 0.04, co.z))
        if 0.22 < t < 0.98:
            # chevrons: V pointing forward, period ~0.04
            ph = (co.y + abs(co.z) * 0.8) / 0.042
            band = nh.smoothstep(0.75, 1.0, 0.5 + 0.5 * math.cos(ph * math.tau))
            c = nh.lerp(c, CHEVRON, 0.6 * band)
        if 0.1 < t < 0.2 and co.z < 0.02:
            ph = co.y / 0.016
            c = nh.lerp(c, GILL, 0.7 * nh.smoothstep(0.6, 1.0, 0.5 + 0.5 * math.cos(ph * math.tau)))
        return c

    mb.add(nh.tube(pts, radii, sides=12, scale_xy=(0.55, 1.0)), col)
    # low fin fold on the rear back and belly, tail fin
    for sgn in (1, -1):
        outline = []
        for i in range(9):
            t = 0.55 + 0.45 * i / 8
            outline.append((0.0, -0.5 + t, sgn * (radius(t) + 0.025 * nh.smoothstep(0.55, 0.9, t))))
        for i in range(8, -1, -1):
            t = 0.55 + 0.45 * i / 8
            outline.append((0.0, -0.5 + t, sgn * radius(t) * 0.5))
        fin = nh.flat_panel([(z, y, 0) for (_, y, z) in outline], thickness=0.006)
        nh.transform(fin, nh.Matrix.Rotation(math.radians(-90), 4, "Y"))
        mb.add(fin, FIN, smooth=False)
    for s in (-1, 1):
        p = Vector((s * 0.03, -0.43, 0.035))
        mb.add(nh.ellipsoid(p, (0.024, 0.026, 0.022), subdivisions=2), EYE_RIM)
        mb.add(nh.ellipsoid(p + Vector((s * 0.008, -0.004, 0.004)), (0.018, 0.02, 0.018), subdivisions=2), EYE)
    mb.add(nh.ellipsoid((0, -0.48, 0.03), (0.008, 0.008, 0.006), subdivisions=1), EYE)
    return ec.centre(mb.to_object("Metaspriggina", roughness=0.35))


if __name__ == "__main__":
    ec.export(build, "Metaspriggina")
