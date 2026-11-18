"""
Procedural Orthacanthus compressus (Late Carboniferous coal-swamp lakes and rivers of North
America, a large freshwater xenacanth shark up to about 3 m long) for map colonies (Swim style).

An eel-like shark: a broad, flat head with small eyes and a mouth full of two-pronged teeth,
a long, low, ribbon-like dorsal fin running from mid-back right into the tapering, pointed
tail, paddle-shaped pectoral fins and, its trademark, a long serrated spine sticking up and
back from the back of the skull. Olive-brown above, pale below. Built with nh_car_fish.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/orthacanthus_compressus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Orthacanthus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_car_fish as cf  # noqa: E402
from mathutils import Vector  # noqa: E402

SPINE = (0.84, 0.78, 0.62)


def head_spine(sp, tree):
    """The long occipital spine with a row of small barbs along its underside."""
    a, b, c = Vector((0, -0.40, 0.045)), Vector((0, -0.30, 0.085)), Vector((0, -0.18, 0.115))
    out = [(nh.tube([a, b, c], [0.010, 0.007, 0.0], sides=6), SPINE)]
    for k in range(6):
        t = 0.15 + 0.13 * k
        p = (a.lerp(b, t * 2) if t < 0.5 else b.lerp(c, (t - 0.5) * 2))
        out.append((nh.tube([p, p + Vector((0, -0.012, -0.012))], [0.003, 0.0], sides=3), SPINE))
    return out


SPEC = cf.Spec(
    name="Orthacanthus",
    mid=[(-0.6, 0.0), (0.6, 0.0)],
    height=[(-0.6, 0.0), (-0.59, 0.025), (-0.52, 0.045), (-0.35, 0.06), (-0.05, 0.058), (0.25, 0.04),
            (0.48, 0.018), (0.6, 0.002)],
    width=[(-0.6, 0.0), (-0.59, 0.035), (-0.52, 0.06), (-0.35, 0.062), (-0.05, 0.05), (0.25, 0.03),
           (0.48, 0.012), (0.6, 0.002)],
    fins=[
        # long ribbon dorsal running into the tail
        ("mid", [(-0.12, 0.05), (-0.08, 0.085), (0.30, 0.075), (0.55, 0.03), (0.60, 0.005), (0.40, 0.02),
                 (0.0, 0.05)]),
        # ventral tail lobe and paired anal fins
        ("mid", [(0.36, -0.02), (0.42, -0.06), (0.58, -0.02), (0.60, -0.004)]),
        ("mid", [(0.22, -0.035), (0.26, -0.07), (0.32, -0.035)]),
        ("pair", (0.05, -0.36, -0.04), [(0, 0, 0), (0.0, 0.07, 0.0), (0.12, 0.13, -0.03), (0.13, 0.07, -0.03)]),
        ("pair", (0.03, 0.08, -0.04), [(0, 0, 0), (0.0, 0.08, 0.0), (0.07, 0.11, -0.03), (0.07, 0.04, -0.03)]),
    ],
    fin_th=0.012,
    back=(0.30, 0.29, 0.20), flank=(0.46, 0.44, 0.32), belly=(0.84, 0.80, 0.68),
    fin_col=(0.26, 0.25, 0.17), pattern="mottle", pattern_col=(0.18, 0.17, 0.11), pattern_scale=0.8,
    eye=(-0.53, 0.022, 0.014), iris=(0.75, 0.68, 0.30), gills=6, gill_y=-0.45,
    teeth=7, tooth_len=0.012, mouth_y=(-0.595, -0.53), mouth_z=-0.018,
    voxel=0.0055, max_tris=7000,
    extra=[head_spine],
)

if __name__ == "__main__":
    cf.run(SPEC)
