"""
Procedural Rhyniognatha hirsti for the map: one of the oldest insects known, from the
Early Devonian Rhynie chert of Scotland, about 410 million years ago.

Only its tiny head and jaws are preserved: strong, triangular mandibles hinged at two
points (dicondylic), the kind of jaws of the later winged insects, which suggests the
insect lineage was already well established. The rest of the body is reconstructed here
as a generic primitive insect: a slender, tapering body with three thoracic and ten
abdominal segments, six walking legs, long antennae and a pair of long tail cerci.

Built with nh_dev_arthro. Colours are unknown: a dark bronze body with paler segment
edges and reddish jaws.

Usage:
  blender --background --python tools/blender/rhyniognatha_hirsti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Rhyniognatha.fbx (Ground: pivot on the ground,
facing -Y).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_dev_arthro as ar  # noqa: E402

NAME = "Rhyniognatha"

BODY = (0.30, 0.25, 0.16)
PALE = (0.66, 0.58, 0.40)
DARK = (0.06, 0.05, 0.04)
JAW = (0.55, 0.24, 0.10)
JAW_TIP = (0.20, 0.08, 0.04)
LEG = (0.50, 0.42, 0.28)

BASE = 0.10


def build():
    mb = nh.MeshBuilder()
    head = Vector((0, -0.42, BASE + 0.07))
    mb.add(nh.uv_ellipsoid(head, (0.095, 0.085, 0.070), 12, 8), ar.glossy(BODY, gloss=0.3))
    for s in (-1, 1):
        # compound eyes
        mb.add(nh.uv_ellipsoid(head + Vector((s * 0.075, -0.01, 0.030)), (0.030, 0.040, 0.030), 8, 5),
               ar.glossy(DARK, gloss=0.6))
        # long antennae
        root = head + Vector((s * 0.035, -0.075, 0.04))
        pts = [root, root + Vector((s * 0.05, -0.10, 0.07)), root + Vector((s * 0.12, -0.20, 0.09)),
               root + Vector((s * 0.20, -0.30, 0.08)), root + Vector((s * 0.27, -0.38, 0.05))]
        ar.jointed(mb, pts, [0.012, 0.010, 0.008, 0.006, 0.003], ar.glossy(BODY), PALE, sides=5)
        # big triangular mandibles meeting in front of the head
        b = head + Vector((s * 0.050, -0.070, -0.035))
        mb.add(nh.tube([b, b + Vector((s * 0.010, -0.045, -0.005)), head + Vector((s * 0.008, -0.150, -0.040))],
                       [0.038, 0.026, 0.0], sides=6, scale_xy=(1.0, 0.55)),
               lambda co, n, b=b: nh.lerp(JAW, JAW_TIP, nh.smoothstep(0.03, 0.08, (co - b).length)))
        # short maxillary palps
        p = head + Vector((s * 0.06, -0.05, -0.05))
        ar.jointed(mb, [p, p + Vector((s * 0.04, -0.05, -0.02)), p + Vector((s * 0.05, -0.09, -0.05))],
                   [0.010, 0.008, 0.005], ar.glossy(LEG), sides=5)
    # thorax (3) and abdomen (10) segments, tapering
    ys = [-0.32, -0.23, -0.14]
    ys += [-0.06 + i * 0.058 for i in range(10)]
    for i, y in enumerate(ys):
        r = 0.090 if i < 3 else 0.088 * (1.0 - 0.07 * (i - 3))

        def col(co, n, y=y):
            c = ar.glossy(BODY, gloss=0.3)(co, n)
            return nh.lerp(c, PALE, 0.5 * nh.smoothstep(0.022, 0.034, abs(co.y - y)))
        ry = 0.058 if i < 3 else 0.045
        mb.add(nh.uv_ellipsoid((0, y, BASE + 0.06 - 0.002 * max(0, i - 3)), (r, ry, r * 0.65), 12, 6), col)
    for s in (-1, 1):
        for hy, reach, splay in ((-0.32, -0.10, 0.24), (-0.23, 0.02, 0.27), (-0.14, 0.14, 0.27)):
            ar.leg(mb, s, (0.07, hy, BASE + 0.03), reach, splay, BASE + 0.08, 0.016, ar.glossy(LEG), PALE)
        # a pair of long cerci at the tail
        t = Vector((s * 0.015, ys[-1] + 0.02, BASE + 0.06))
        ar.jointed(mb, [t, t + Vector((s * 0.05, 0.12, 0.02)), t + Vector((s * 0.11, 0.26, 0.03)),
                        t + Vector((s * 0.16, 0.38, 0.02))], [0.010, 0.008, 0.005, 0.002], ar.glossy(BODY), PALE,
                   sides=5)
    return ar.finish_ground(mb, NAME, BASE + 0.03)


if __name__ == "__main__":
    nh.run(build, NAME, **ar.GROUND_VIEWS)
