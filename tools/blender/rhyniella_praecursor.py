"""
Procedural Rhyniella praecursor for the map: a springtail (Collembola) from the Early
Devonian (Pragian, about 410 million years ago) Rhynie chert of Scotland - one of the
oldest hexapods known; only about 1-2 mm long.

A soft, elongate six-legged body: a head with short four-jointed antennae and small eye
patches, three thoracic and six abdominal segments, three pairs of short legs and,
folded under the abdomen, the springtail's jumping fork (furcula), held by a catch and
snapped down to fling the animal into the air. It lived in the damp litter and mats
around the hot springs, probably eating fungi, algae and decaying plant matter.

Built with nh_dev_arthro pieces. Colours are unknown: grey-violet with paler segment
margins, like many living springtails.

Usage:
  blender --background --python tools/blender/rhyniella_praecursor.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Rhyniella.fbx (Ground: pivot on the ground,
facing -Y).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_dev_arthro as ar  # noqa: E402

NAME = "Rhyniella"

BODY = (0.38, 0.32, 0.44)
PALE = (0.62, 0.58, 0.66)
DARK = (0.10, 0.08, 0.12)
LEG = (0.56, 0.52, 0.60)

BASE = 0.12


def build():
    mb = nh.MeshBuilder()
    head = Vector((0, -0.46, BASE + 0.08))
    mb.add(nh.uv_ellipsoid(head, (0.10, 0.11, 0.08), 12, 8), ar.glossy(BODY, gloss=0.2))
    for s in (-1, 1):
        mb.add(nh.uv_ellipsoid(head + Vector((s * 0.07, -0.03, 0.03)), (0.025, 0.03, 0.02), 6, 4), DARK)
        root = head + Vector((s * 0.04, -0.09, 0.03))
        pts = [root, root + Vector((s * 0.04, -0.09, 0.06)), root + Vector((s * 0.08, -0.17, 0.08)),
               root + Vector((s * 0.12, -0.24, 0.07)), root + Vector((s * 0.15, -0.30, 0.05))]
        ar.jointed(mb, pts, [0.020, 0.017, 0.015, 0.012, 0.006], ar.glossy(BODY), PALE, sides=5)
    # thorax (3) and abdomen (6) segments
    ys = [-0.33, -0.23, -0.13, -0.03, 0.06, 0.15, 0.23, 0.30, 0.36]
    for i, y in enumerate(ys):
        r = 0.095 if i < 6 else 0.095 - 0.012 * (i - 5)

        def col(co, n, y=y):
            c = ar.glossy(BODY, gloss=0.2)(co, n)
            return nh.lerp(c, PALE, 0.5 * nh.smoothstep(0.03, 0.05, abs(co.y - y)))
        mb.add(nh.uv_ellipsoid((0, y, BASE + 0.07), (r, 0.058, r * 0.85), 12, 6), col)
    for s in (-1, 1):
        for hy, reach in ((-0.33, -0.08), (-0.23, 0.0), (-0.13, 0.08)):
            ar.leg(mb, s, (0.06, hy, BASE + 0.02), reach, 0.20, BASE + 0.06, 0.018, ar.glossy(LEG), PALE)
    # furcula folded forward under the abdomen
    base = Vector((0, 0.30, BASE + 0.01))
    for s in (-1, 1):
        mb.add(nh.tube([base, base + Vector((s * 0.02, -0.12, -0.03)), base + Vector((s * 0.03, -0.24, -0.04))],
                       [0.014, 0.010, 0.0], sides=5), PALE)
    return ar.finish_ground(mb, NAME, BASE + 0.02)


if __name__ == "__main__":
    nh.run(build, NAME, **ar.GROUND_VIEWS)
