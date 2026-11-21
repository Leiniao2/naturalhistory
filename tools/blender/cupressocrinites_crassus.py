"""
Procedural Cupressocrinites crassus (Middle Devonian crinoid, Eifel, Germany) for the map
(Fixed style).

A stalked sea lily about 30 cm tall whose crown looks like a cypress cone (hence the name):
a long, round stem of short columnals rising from a root-like holdfast, a small, low cup of
a few large plates, and only five very broad, thick, undivided arms of stout block-like
brachial plates. Closed, the arms fit together edge to edge into a tight, pointed cone; the
fine pinnules folded inside were spread to filter food from the water. Built after
nh_ord_echino.crinoid. Purplish grey with a paler crown (colour conjectural).

Usage:
  blender --background --python tools/blender/cupressocrinites_crassus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cupressocrinites.fbx (pivot on the sea floor, z = 0)
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_ord_echino as ec  # noqa: E402

STEM = (0.50, 0.42, 0.46)
DARK = (0.30, 0.24, 0.28)
CUP = (0.62, 0.50, 0.52)
ARM = (0.80, 0.70, 0.62)
ARM_DARK = (0.56, 0.44, 0.40)

STEM_H, STEM_R = 1.0, 0.045
CROWN_H, CROWN_R = 0.62, 0.20


def crown_radius(v):
    """Radius of the closed crown cone at height fraction v (0 = cup rim, 1 = tip)."""
    return CROWN_R * (0.75 + 0.9 * v) * (1.0 - v) ** 0.8 + 0.004


def build():
    mb = nh.MeshBuilder()
    ec.mud_patch(mb, 0.4, ((0.36, 0.34, 0.30), (0.52, 0.48, 0.42)))
    for k in range(5):
        a = k / 5 * math.tau + 0.3
        mb.add(nh.tube([(0, 0, 0.03), (math.cos(a) * 0.12, math.sin(a) * 0.12, 0.02),
                        (math.cos(a + 0.3) * 0.24, math.sin(a + 0.3) * 0.24, 0.01)], [0.035, 0.02, 0.0], sides=5), DARK)
    n = 16
    pts = [Vector((0.06 * math.sin(t * 2.0) * t, 0.0, 0.02 + STEM_H * t)) for t in [i / n for i in range(n + 1)]]
    mb.add(nh.tube(pts, [STEM_R * (1.1 - 0.15 * i / n) for i in range(n + 1)], sides=10),
           ec._columnal_color(STEM, DARK))
    top = pts[-1]
    # low cup
    mb.add(nh.tube([top, top + Vector((0, 0, 0.05)), top + Vector((0, 0, 0.1))],
                   [STEM_R * 1.2, CROWN_R * 0.65, CROWN_R * 0.78], sides=10), CUP, smooth=False)
    base = top + Vector((0, 0, 0.09))
    # five broad, thick arms meeting in a cypress-cone crown
    m = 24
    for k in range(5):
        a = k / 5 * math.tau + math.pi / 2
        d = Vector((math.cos(a), math.sin(a), 0.0))
        apts, radii = [], []
        for i in range(m + 1):
            v = i / m
            r = crown_radius(v)
            apts.append(base + d * r * 0.78 + Vector((0, 0, CROWN_H * v)))
            radii.append(r * 0.62 if i < m else 0.0)

        def col(co, nrm, base=base):
            h = (co.z - base.z) / CROWN_H
            band = 0.5 + 0.5 * math.cos(h * math.tau * 9)
            c = nh.lerp(ARM, ARM_DARK, 0.85 * nh.smoothstep(0.6, 0.95, band))
            return nh.lerp(ARM_DARK, c, nh.smoothstep(-0.2, 0.5, nrm.dot(Vector((co.x - base.x, co.y - base.y, 0)).normalized()) if (co.x - base.x) ** 2 + (co.y - base.y) ** 2 > 1e-8 else 1.0))
        mb.add(nh.tube(apts, radii, sides=10, scale_xy=(1.0, 0.42)), col)
    # inner core so no gaps show between the arms
    core = [base + Vector((0, 0, CROWN_H * i / m)) for i in range(m + 1)]
    mb.add(nh.tube(core, [crown_radius(i / m) * 0.6 if i < m else 0.0 for i in range(m + 1)], sides=10), ARM_DARK)
    return ec._finish(mb, "Cupressocrinites")


if __name__ == "__main__":
    nh.run(build, "Cupressocrinites", **ec.VIEWS)
