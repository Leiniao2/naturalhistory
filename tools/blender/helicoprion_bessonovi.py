"""
Procedural Helicoprion bessonovi (Early Permian eugeneodont, ~5-6 m) for map colonies, swimming.

The "buzz-saw" fish, a cartilaginous relative of ratfishes: a long, shark-like body with a
pointed snout, a tall triangular dorsal fin, broad pectoral fins and a big crescent tail,
and its famous tooth-whorl - a coiled spiral of well over a hundred serrated teeth set in
the middle of the lower jaw, new teeth added at the tip of the coil while the old ones
rolled inward. Here the visible outer turn of the whorl fills the front of the lower jaw,
its teeth sticking up from the jaw line. Dark slate-grey above, pale below.
Uses the loft/fuse helpers of nh_per_tetra. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/helicoprion_bessonovi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Helicoprion.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402
from mathutils import Vector as V, noise  # noqa: E402

NAME = "Helicoprion"
BACK = (0.20, 0.23, 0.26)
FLANK = (0.36, 0.40, 0.44)
BELLY = (0.84, 0.84, 0.80)
FIN = (0.18, 0.20, 0.23)
TOOTH = (0.92, 0.88, 0.76)
WHORL = (0.70, 0.64, 0.54)

BODY = [  # y, z, half width, half height
    (-0.92, -0.01, 0.0, 0.0),
    (-0.88, -0.01, 0.040, 0.040),
    (-0.78, -0.005, 0.085, 0.085),
    (-0.60, 0.0, 0.130, 0.135),
    (-0.35, 0.0, 0.150, 0.160),
    (-0.05, 0.0, 0.140, 0.150),
    (0.25, 0.0, 0.100, 0.110),
    (0.50, 0.0, 0.055, 0.065),
    (0.68, 0.0, 0.030, 0.040),
    (0.78, 0.0, 0.022, 0.032),
]
JAW = [(-0.52, -0.10, 0.10, 0.05), (-0.64, -0.15, 0.075, 0.038), (-0.76, -0.175, 0.045, 0.03),
       (-0.82, -0.18, 0.02, 0.018), (-0.835, -0.18, 0.0, 0.0)]  # lower jaw, mouth slightly open


def paint(co, n):
    c = nh.lerp(BELLY, FLANK, nh.smoothstep(-0.55, -0.05, n.z))
    c = nh.lerp(c, BACK, nh.smoothstep(0.05, 0.7, n.z))
    k = 1.0 + 0.06 * noise.noise(co * 18.0)
    return tuple(min(1.0, x * k) for x in c)


def fins(b):
    # dorsal
    b.add(pt.membrane([(0, -0.30, 0.13), (0, -0.02, 0.48), (0, 0.02, 0.46), (0, 0.10, 0.13)], 0.03), FIN)
    # tail: crescent lobes
    b.add(pt.membrane([(0, 0.70, 0.02), (0, 1.02, 0.42), (0, 1.06, 0.40), (0, 0.86, 0.0), (0, 1.02, -0.30),
                       (0, 0.98, -0.31), (0, 0.70, -0.04)], 0.03), FIN)
    for sx in (1, -1):
        # pectoral
        b.add(pt.membrane([(sx * 0.12, -0.50, -0.09), (sx * 0.48, -0.26, -0.22), (sx * 0.46, -0.20, -0.22),
                           (sx * 0.12, -0.32, -0.10)], 0.025), FIN)
        # pelvic
        b.add(pt.membrane([(sx * 0.06, 0.24, -0.08), (sx * 0.20, 0.38, -0.14), (sx * 0.19, 0.42, -0.14),
                           (sx * 0.05, 0.36, -0.07)], 0.018), FIN)


def whorl(mb):
    """Outer turn of the tooth spiral standing in the front of the lower jaw (midline, YZ plane)."""
    c = V((0.0, -0.74, -0.165))
    n = 26
    for i in range(n):
        t = i / (n - 1)
        a = math.radians(200 - 250 * t)       # from behind/below, over the top, down to the front
        r = 0.030 + 0.035 * t                  # spiral grows toward the front
        p = c + V((0, -math.cos(a) * r, math.sin(a) * r))
        out = V((0, -math.cos(a), math.sin(a)))
        h = 0.016 + 0.020 * t
        mb.add(pt.cone(p - out * 0.004, p + out * h, 0.007 + 0.003 * t, sides=5), TOOTH, smooth=False)
    mb.add(pt.oriented(c, (0.016, 0.05, 0.05)), WHORL)


def build():
    b = nh.MeshBuilder()
    b.add(pt.loft(pt.densify(BODY, 4), sides=24, power=2.0), FLANK)
    b.add(pt.loft(pt.densify(JAW, 3), sides=16, power=2.0), FLANK)
    fins(b)
    fused = b.fuse(voxel=0.012, smooth=4, smooth_factor=0.5)
    fused = pt.decimate(fused, 6000)
    mb = nh.MeshBuilder()
    mb.add(fused, paint)
    whorl(mb)
    for sx in (1, -1):
        e = V((sx * 0.072, -0.74, 0.035))
        mb.add(nh.ellipsoid(e, (0.016, 0.018, 0.016), subdivisions=2), (0.06, 0.06, 0.06))
        for k in range(5):  # gill slits
            y = -0.60 + 0.035 * k
            mb.add(pt.oriented((sx * 0.128, y, -0.02), (0.006, 0.006, 0.055)), (0.10, 0.11, 0.13))
    obj = mb.to_object(NAME, roughness=0.5)
    corners = [V(c) for c in obj.bound_box]
    centre = sum(corners, V()) / 8
    for v in obj.data.vertices:
        v.co -= centre
    return obj


if __name__ == "__main__":
    nh.run(build, NAME, background=(0.04, 0.10, 0.13), views=((35, 15), (-90, 4), (-60, 5)))
