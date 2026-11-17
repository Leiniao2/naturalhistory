"""
Procedural Devonobius delta for the map: a centipede from the Middle Devonian (Givetian,
about 386 million years ago) of Gilboa, New York - one of the oldest centipedes known
and the only member of its own order, Devonobiomorpha, related to today's stone-dwelling
scolopendromorphs and earth centipedes. It was about a centimetre long.

A flattened head with long many-jointed antennae and a pair of venom claws (forcipules)
folded under the head - the centipede's poison fangs, already present - followed by a
flat trunk of alternating long and short tergites, each segment carrying a pair of legs,
and a last pair of longer, trailing legs. A small predator in the leaf litter of the
first forests.

Built with nh_dev_arthro pieces. Colours are unknown: amber-orange tergites with darker
margins, paler legs.

Usage:
  blender --background --python tools/blender/devonobius_delta.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Devonobius.fbx (Ground: pivot on the ground,
facing -Y).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_dev_arthro as ar  # noqa: E402

NAME = "Devonobius"

BODY = (0.62, 0.36, 0.12)
DARK = (0.22, 0.11, 0.04)
RIM = (0.36, 0.18, 0.07)
LEG = (0.78, 0.60, 0.36)
FANG = (0.18, 0.08, 0.04)

BASE = 0.045
SEGS = 15


def build():
    mb = nh.MeshBuilder()
    L = 1.4
    y0 = -L / 2 + 0.08
    dy = (L - 0.16) / (SEGS + 1)
    # head
    head = Vector((0, y0, BASE + 0.025))
    ar.plate(mb, head, (0.060, 0.060, 0.022), ar.glossy(nh.lerp(BODY, DARK, 0.3)), 12, 6)
    for s in (-1, 1):
        pts = [head + Vector((s * (0.03 + 0.03 * k * 0.5), -0.05 - 0.05 * k, 0.01 + 0.012 * k - 0.002 * k * k))
               for k in range(7)]
        ar.jointed(mb, pts, [0.009 - 0.001 * k for k in range(7)], ar.glossy(LEG), None, sides=4)
        f = head + Vector((s * 0.03, -0.02, -0.02))
        mb.add(nh.tube([f, f + Vector((s * 0.03, -0.04, 0.0)), f + Vector((-s * 0.005, -0.07, 0.0))],
                       [0.011, 0.008, 0.0], sides=5), FANG)
    for i in range(SEGS):
        y = y0 + dy * (i + 1)
        long_seg = i % 2 == 0
        w = 0.07 if i < SEGS - 2 else 0.07 - 0.015 * (i - SEGS + 3)

        def col(co, n, y=y):
            c = ar.glossy(BODY)(co, n)
            return nh.lerp(c, RIM, 0.7 * nh.smoothstep(0.55, 0.95, abs(co.y - y) / (dy * 0.55)))
        ar.plate(mb, (0, y, BASE + 0.02), (w * (1.0 if long_seg else 0.92), dy * 0.58, 0.020), col, 12, 6)
        last = i == SEGS - 1
        for s in (-1, 1):
            if last:
                ar.jointed(mb, [Vector((s * 0.05, y, BASE + 0.01)), Vector((s * 0.10, y + 0.08, BASE + 0.03)),
                                Vector((s * 0.12, y + 0.20, 0.01))], [0.010, 0.008, 0.004], ar.glossy(LEG), None, 4)
            else:
                swing = 0.03 * math.sin(i * 1.3 + (0 if s > 0 else math.pi))
                ar.leg(mb, s, (0.05, y, BASE + 0.01), 0.03 + swing, 0.15, BASE + 0.05, 0.009, ar.glossy(LEG))
    return ar.finish_ground(mb, NAME, BASE + 0.01)


if __name__ == "__main__":
    nh.run(build, NAME, **ar.GROUND_VIEWS)
