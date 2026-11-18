"""
Procedural Iniopteryx rushlaui (Late Carboniferous of Indiana and Kansas, an iniopterygian,
a small ratfish relative about 45 cm long) for map colonies (Swim style).

A short, deep-headed fish with huge eyes and a blunt snout, a body tapering to a thin tail
ending in a small paddle, and enormous wing-like pectoral fins set high on the shoulders,
their leading edges armed with rows of hooked denticles; it may have used them to burst out
of the water and glide like a flying fish. Dark brown above with pale fin edges.
Built with nh_car_fish. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/iniopteryx_rushlaui.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Iniopteryx.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

HOOK = (0.88, 0.84, 0.70)
ROOT = Vector((0.07, -0.30, 0.07))
TIP = Vector((0.50, -0.12, 0.20))


def hooks(sp, tree):
    """Hooked denticles along the leading edge of each pectoral wing."""
    out = []
    for sx in (-1, 1):
        for k in range(7):
            p = ROOT.lerp(TIP, 0.15 + 0.12 * k)
            p = Vector((sx * p.x, p.y - 0.01, p.z + 0.01))
            out.append((nh.tube([p, p + Vector((sx * 0.004, -0.018, 0.012)), p + Vector((sx * 0.006, -0.012, 0.022))],
                                [0.005, 0.003, 0.0], sides=4), HOOK))
    return out


SPEC = cf.Spec(
    name="Iniopteryx",
    mid=[(-0.6, 0.0), (0.0, 0.0), (0.6, 0.0)],
    height=[(-0.6, 0.0), (-0.595, 0.04), (-0.57, 0.10), (-0.48, 0.14), (-0.30, 0.14), (-0.05, 0.085), (0.2, 0.04),
            (0.45, 0.014), (0.6, 0.004)],
    width=[(-0.6, 0.0), (-0.595, 0.035), (-0.57, 0.08), (-0.48, 0.11), (-0.30, 0.11), (-0.05, 0.06), (0.2, 0.028),
           (0.45, 0.01), (0.6, 0.003)],
    fins=[
        ("mid", [(0.40, 0.012), (0.50, 0.05), (0.60, 0.012), (0.60, -0.012), (0.50, -0.05), (0.40, -0.012)]),
        ("mid", [(0.05, 0.07), (0.10, 0.11), (0.22, 0.05)]),
        # huge pectoral wings high on the shoulder, swept back and up
        ("pair", tuple(ROOT), [(0, 0, 0), (TIP.x - ROOT.x, TIP.y - ROOT.y, TIP.z - ROOT.z), (0.40, 0.30, 0.10),
                               (0.20, 0.30, 0.03), (0.0, 0.14, 0.0)], 0.014),
        ("pair", (0.04, 0.02, -0.06), [(0, 0, 0), (0.0, 0.07, 0.0), (0.07, 0.10, -0.04), (0.06, 0.03, -0.04)]),
    ],
    back=(0.30, 0.23, 0.17), flank=(0.48, 0.38, 0.30), belly=(0.80, 0.74, 0.64),
    fin_col=(0.30, 0.24, 0.19), pattern="spots", pattern_col=(0.12, 0.09, 0.07), pattern_scale=0.8,
    eye=(-0.46, 0.04, 0.05), iris=(0.70, 0.75, 0.55), gills=0,
    extra=[hooks],
)

if __name__ == "__main__":
    cf.run(SPEC)
