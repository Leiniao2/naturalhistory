"""
Procedural Yilingia spiciformis (late Ediacaran, Yangtze Gorges, China, ~550 Ma): a long,
narrow, segmented, trilobed animal. A raised central axis runs down the back; each of its
roughly fifty body units carries a pair of flat lateral lobes drawn out into backward-pointing
spiky tips ("spiciformis"); a blunt, rounded head unit at the front and a tapering tail.
Olive-brown with darker segment boundaries and paler lobe tips. Swim style (a mobile seafloor
crawler): pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/yilingia_spiciformis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Yilingia.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_edicam as ec  # noqa: E402
from mathutils import Vector, Matrix  # noqa: E402

AXIS = (0.50, 0.44, 0.28)
AXIS_DARK = (0.30, 0.25, 0.15)
LOBE = (0.62, 0.54, 0.36)
TIP = (0.86, 0.78, 0.58)
BELLY = (0.74, 0.68, 0.54)
Y0, Y1, SEG = -0.95, 0.95, 40


def wiggle(y):
    return 0.06 * math.sin(y * 3.2)


def width(t):
    return 0.05 * (1 - 0.5 * max(0.0, t - 0.7) / 0.3) if t > 0.7 else 0.05


def build():
    mb = nh.MeshBuilder()
    trunk = ec.segmented_trunk(Y0, Y1, SEG, width, flat=0.7, sides=8, tip=0.01, pinch=0.8)
    for v in trunk.verts:
        v.co.x += wiggle(v.co.y)
    mb.add(trunk, ec.banded(AXIS, AXIS_DARK, BELLY, Y0, (Y1 - Y0) / SEG, amount=0.7))
    head = nh.uv_ellipsoid((wiggle(Y0 - 0.04), Y0 - 0.04, 0), (0.1, 0.07, 0.035), segments=14, rings=7)
    mb.add(head, lambda co, n: nh.lerp(BELLY, LOBE, nh.smoothstep(-0.5, 0.2, n.z)))
    seg = (Y1 - Y0) / SEG
    for i in range(SEG):
        t = i / (SEG - 1)
        y = Y0 + (i + 0.3) * seg
        ln = 0.1 * (1 - 0.6 * max(0.0, t - 0.6) / 0.4)
        for s in (-1, 1):
            lobe = nh.flat_panel([(0, -seg * 0.45, 0), (ln * 0.6, -seg * 0.35, 0), (ln, seg * 0.9, 0),
                                  (ln * 0.5, seg * 0.35, 0), (0, seg * 0.45, 0)], thickness=0.012)
            nh.transform(lobe, Matrix.Rotation(math.radians(-6), 4, "Y"))
            ec.mirror(lobe, s)
            nh.transform(lobe, Matrix.Translation((wiggle(y) + s * 0.035, y, -0.005)))
            mb.add(lobe, lambda co, n, y=y: nh.lerp(LOBE, TIP, nh.smoothstep(0.06, 0.13, abs(co.x - wiggle(y)))),
                   smooth=False)
    return ec.centre(mb.to_object("Yilingia", roughness=0.6))


if __name__ == "__main__":
    ec.export(build, "Yilingia")
