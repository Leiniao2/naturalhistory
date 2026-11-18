"""
Procedural Sarcoprion edax (Late Permian eugeneodont, ~3 m) for map colonies, swimming.

The "flesh-saw" of the Late Permian seas of East Greenland, a relative of Helicoprion: a
sleek, torpedo-shaped cartilaginous fish with a long, pointed snout and, at the front of the
lower jaw, a tall tooth-whorl - a curved, saw-like blade of big, laterally compressed,
triangular teeth that worked against the upper jaw to slice prey. Tall triangular dorsal
fin, long sickle-shaped pectorals and a deep crescent tail made it a fast open-water hunter.
Dark blue-grey above with a silvery belly.
Built on helicoprion_bessonovi.py (its loft / fin helpers) with a slimmer, more streamlined
body, larger fins and a taller, more blade-like whorl. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/sarcoprion_edax.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sarcoprion.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_per_tetra as pt  # noqa: E402
import helicoprion_bessonovi as h  # noqa: E402
from mathutils import Vector as V  # noqa: E402

h.NAME = "Sarcoprion"
h.BACK = (0.14, 0.19, 0.28)
h.FLANK = (0.40, 0.47, 0.55)
h.BELLY = (0.88, 0.89, 0.88)
h.FIN = (0.12, 0.16, 0.24)
h.BODY = [
    (-1.00, -0.02, 0.0, 0.0),
    (-0.95, -0.015, 0.030, 0.030),
    (-0.82, -0.005, 0.075, 0.075),
    (-0.60, 0.0, 0.110, 0.120),
    (-0.35, 0.0, 0.125, 0.140),
    (-0.05, 0.0, 0.110, 0.125),
    (0.25, 0.0, 0.075, 0.085),
    (0.50, 0.0, 0.040, 0.050),
    (0.68, 0.0, 0.022, 0.032),
    (0.78, 0.0, 0.018, 0.028),
]
h.JAW = [(-0.52, -0.09, 0.08, 0.045), (-0.66, -0.13, 0.06, 0.034), (-0.80, -0.15, 0.035, 0.026),
         (-0.86, -0.155, 0.015, 0.016), (-0.875, -0.155, 0.0, 0.0)]


def fins(b):
    b.add(pt.membrane([(0, -0.30, 0.11), (0, -0.06, 0.52), (0, -0.01, 0.50), (0, 0.10, 0.11)], 0.03), h.FIN)
    b.add(pt.membrane([(0, 0.70, 0.02), (0, 1.06, 0.48), (0, 1.10, 0.46), (0, 0.88, 0.0), (0, 1.06, -0.36),
                       (0, 1.02, -0.37), (0, 0.70, -0.04)], 0.03), h.FIN)
    for sx in (1, -1):
        b.add(pt.membrane([(sx * 0.10, -0.50, -0.08), (sx * 0.56, -0.18, -0.24), (sx * 0.53, -0.13, -0.24),
                           (sx * 0.10, -0.33, -0.09)], 0.025), h.FIN)
        b.add(pt.membrane([(sx * 0.05, 0.24, -0.07), (sx * 0.18, 0.38, -0.12), (sx * 0.17, 0.42, -0.12),
                           (sx * 0.04, 0.36, -0.06)], 0.018), h.FIN)


def whorl(mb):
    """A tall, blade-like arc of big triangular teeth at the front of the lower jaw."""
    c = V((0.0, -0.84, -0.115))
    n = 11
    for i in range(n):
        t = i / (n - 1)
        a = math.radians(150 - 150 * t)
        r = 0.045 + 0.025 * t
        p = c + V((0, -math.cos(a) * r, math.sin(a) * r * 1.3))
        out = V((0, -math.cos(a), math.sin(a))).normalized()
        hgt = 0.055 + 0.04 * math.sin(math.pi * t)
        mb.add(pt.cone(p - out * 0.004, p + out * hgt, 0.017, sides=4), h.TOOTH, smooth=False)
    mb.add(pt.oriented(c + V((0, -0.01, 0.0)), (0.014, 0.045, 0.04)), h.WHORL)


h.fins = fins
h.whorl = whorl

if __name__ == "__main__":
    nh.run(h.build, h.NAME, background=(0.04, 0.10, 0.13), views=((35, 15), (-90, 4), (-60, 5)))
