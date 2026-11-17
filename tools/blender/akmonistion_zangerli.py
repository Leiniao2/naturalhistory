"""
Procedural Akmonistion zangerli (Early Carboniferous of Bearsden, Scotland, a stethacanthid
shark about 60-70 cm long) for map colonies (Swim style).

A stocky shark with a blunt snout, big eyes and a nearly symmetrical crescent tail, carrying
its trademark: a tall dorsal spine topped by a flat, anvil-shaped "brush" whose upper surface,
like the top of the head, bristles with enlarged tooth-like denticles. Dark grey-brown above,
pale below. Built with nh_car_fish. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/akmonistion_zangerli.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Akmonistion.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

DENTICLE = (0.80, 0.78, 0.70)
BRUSH = (0.18, 0.17, 0.17)


def brush(sp):
    parts = [nh.tube([(0, -0.12, 0.08), (0, -0.13, 0.2), (0, -0.12, 0.27)], [0.028, 0.024, 0.03], sides=10)]
    # anvil: flat-topped block wider fore-aft than the spine, overhanging forward
    parts.append(nh.uv_ellipsoid((0, -0.14, 0.30), (0.035, 0.10, 0.045), 16, 10,
                                 deform=lambda v: 1.0 - 0.25 * max(0.0, v.z) ** 4))
    return parts


def denticles(sp, tree):
    out = []
    for i in range(7):
        for j in range(3):
            y = -0.22 + i * 0.025
            x = (j - 1) * 0.018
            loc, nrm, _i, _d = tree.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
            if loc is not None and loc.z > 0.25:
                out.append((nh.tube([loc - nrm * 0.002, loc + Vector((0, -0.006, 0.016))], [0.006, 0.0], sides=4),
                            DENTICLE))
    for i in range(4):
        for j in range(2):
            y = -0.50 + i * 0.03
            x = (j - 0.5) * 0.03
            loc, nrm, _i, _d = tree.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
            if loc is not None:
                out.append((nh.tube([loc - nrm * 0.002, loc + nrm * 0.012], [0.005, 0.0], sides=4), DENTICLE))
    return out


SPEC = cf.Spec(
    name="Akmonistion",
    mid=[(-0.6, -0.01), (0.25, 0.0), (0.6, 0.05)],
    height=[(-0.6, 0.0), (-0.585, 0.04), (-0.5, 0.085), (-0.25, 0.115), (0.05, 0.095), (0.3, 0.045),
            (0.45, 0.03), (0.6, 0.006)],
    width=[(-0.6, 0.0), (-0.585, 0.035), (-0.5, 0.075), (-0.25, 0.095), (0.05, 0.075), (0.3, 0.035),
           (0.45, 0.022), (0.6, 0.004)],
    fins=[
        ("mid", [(0.40, 0.03), (0.55, 0.22), (0.62, 0.22), (0.57, 0.05), (0.62, -0.15), (0.56, -0.16), (0.40, -0.01)]),
        ("mid", [(0.20, 0.05), (0.27, 0.12), (0.31, 0.12), (0.32, 0.04)]),
        ("pair", (0.07, -0.30, -0.06), [(0, 0, 0), (0.0, 0.08, 0.0), (0.16, 0.12, -0.07), (0.17, 0.07, -0.08)]),
        ("pair", (0.04, 0.12, -0.06), [(0, 0, 0), (0.0, 0.07, 0.0), (0.07, 0.09, -0.04), (0.06, 0.03, -0.04)]),
    ],
    fused_extra=[brush],
    back=(0.22, 0.21, 0.21), flank=(0.36, 0.35, 0.34), belly=(0.84, 0.82, 0.76),
    fin_col=(0.20, 0.19, 0.19), pattern="none",
    eye=(-0.48, 0.03, 0.026), iris=(0.55, 0.55, 0.35), gills=5, gill_y=-0.37,
    extra=[denticles],
)

if __name__ == "__main__":
    cf.run(SPEC)
