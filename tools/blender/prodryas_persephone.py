"""
Procedural Prodryas persephone (a brush-footed butterfly, late Eocene, Florissant lake beds,
Colorado) for map swarms. One of the best-preserved fossil butterflies, with a wingspan of about
5 cm and its wing pattern still visible: dark brown wings with a band of pale cream spots across
the forewing and white dots near its tip, a warm orange-brown flush on the hindwings and a dark
eyespot ringed in cream near the hindwing margin.
Mid-flap, wings open in a shallow V (reuses the slab-layer wing builder of monarch_butterfly.py).
Faces -Y, pivot at the body centre (Swarm).

Usage:
  blender --background --python tools/blender/prodryas_persephone.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProdryasPersephone.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import monarch_butterfly as mbf  # noqa: E402

BROWN = (0.16, 0.10, 0.06)
TAWNY = (0.62, 0.34, 0.12)
CREAM = (0.93, 0.86, 0.66)
WHITE = (0.96, 0.95, 0.92)
BLACK = (0.04, 0.03, 0.03)
BODY = (0.18, 0.12, 0.08)

FOREWING = [(0.030, -0.070), (0.110, -0.160), (0.230, -0.250), (0.360, -0.320), (0.470, -0.350),
            (0.530, -0.340), (0.555, -0.290), (0.545, -0.210), (0.510, -0.130), (0.460, -0.060),
            (0.400, -0.005), (0.320, 0.040), (0.220, 0.055), (0.120, 0.040), (0.050, 0.010)]
HINDWING = [(0.030, 0.000), (0.120, -0.030), (0.240, -0.020), (0.330, 0.030), (0.385, 0.100),
            (0.400, 0.170), (0.375, 0.240), (0.330, 0.290), (0.260, 0.330), (0.180, 0.345),
            (0.105, 0.320), (0.055, 0.250), (0.030, 0.130)]
T0, T1, T2, T3 = 0.004, 0.0055, 0.007, 0.0085


def fore():
    parts = [(mbf.slab(FOREWING, T0), BROWN)]
    # darker veins from the root
    root = (0.05, -0.02)
    for idx in (2, 3, 4, 6, 8, 10, 12):
        parts.append((mbf.ribbon(mbf.curve(root, FOREWING[idx], 0.03), 0.005, 0.003, T1),
                      tuple(c * 0.6 for c in BROWN)))
    # a slanting band of pale cream spots across the middle of the forewing
    for c, r in (((0.28, -0.20), 0.032), ((0.33, -0.15), 0.034), ((0.37, -0.095), 0.032),
                 ((0.40, -0.045), 0.026), ((0.25, -0.25), 0.024)):
        parts.append((mbf.disc(c, r, T2, sides=9), CREAM))
    for c, r in (((0.47, -0.30), 0.012), ((0.50, -0.27), 0.012), ((0.52, -0.235), 0.011)):
        parts.append((mbf.disc(c, r, T2), WHITE))
    return parts


def hind():
    parts = [(mbf.slab(HINDWING, T0), BROWN)]
    field = mbf.inset(HINDWING, (0.06, 0.08), 0.72)
    parts.append((mbf.slab(field, T1), lambda co, n: nh.lerp(TAWNY, BROWN, nh.smoothstep(0.1, 0.32, co.length))))
    # eyespot: black with a cream ring and a white pupil, near the outer margin
    c = (0.27, 0.235)
    parts.append((mbf.disc(c, 0.05, T2, sides=14), CREAM))
    parts.append((mbf.disc(c, 0.037, T3, sides=14), BLACK))
    parts.append((mbf.disc((c[0] - 0.008, c[1] - 0.008), 0.012, T3 + 0.0015, sides=8), WHITE))
    for p in ((0.36, 0.14), (0.35, 0.08)):
        parts.append((mbf.disc(p, 0.014, T2), CREAM))
    return parts


def build():
    mb = nh.MeshBuilder()
    mbf.BODY = BODY
    mbf.WHITE = (0.55, 0.45, 0.32)  # muted body dots
    mbf.EYE = (0.10, 0.08, 0.06)
    mbf.build_body(mb)
    for mirror in (False, True):
        mbf.place(fore(), mb, mirror, lift_deg=22, hinge=(0.025, -0.025, 0.020), sweep_deg=-4)
        mbf.place(hind(), mb, mirror, lift_deg=16, hinge=(0.025, 0.005, 0.010), sweep_deg=2)
    return mb.to_object("ProdryasPersephone", roughness=0.55)


if __name__ == "__main__":
    nh.run(build, "ProdryasPersephone", background=(0.30, 0.40, 0.30), views=((35, 30), (0, 75), (-90, 10)))
