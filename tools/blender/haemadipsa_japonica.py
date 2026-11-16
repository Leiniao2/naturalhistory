"""
Procedural Japanese mountain leech (Haemadipsa japonica) for map colonies (Ground style).

A land leech of damp mountain forests in Japan, 2-3 cm long when resting. It waits
on the forest floor and low vegetation, senses the warmth, breath and footsteps of
deer, wild boar and people, and loops toward them to suck blood. A slender,
nearly round-bodied leech that tapers to a narrow head with five pairs of eye
spots in an arc, and ends in a small caudal sucker barely wider than the body.
Reddish tan-brown back with three dark longitudinal stripes (a median one and a
pair along the flanks), a narrow pale line along each side and a paler yellowish-
brown belly. Built with nh_leech.py. The body is left straight: on the map the
Slither gait (MapFeatureFlap.cginc, ApplyUndulate) bends it as it crawls.

Usage:
  blender --background --python tools/blender/haemadipsa_japonica.py -- [--render out.png]

Output: Assets/Resources/Models/Species/JapaneseLandLeech.fbx
Faces -Y, pivot on the ground (belly and caudal sucker at z = 0). About 1.8 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_leech as lc  # noqa: E402

TAN = (0.64, 0.36, 0.17)        # reddish tan-brown
TAN_HEAD = (0.44, 0.22, 0.11)
STRIPE = (0.16, 0.08, 0.05)
PALE = (0.78, 0.60, 0.34)
BELLY = (0.68, 0.50, 0.30)

SPEC = lc.Spec(
    name="JapaneseLandLeech",
    half_width=0.085,
    top=0.80,
    belly=0.45,
    dome=2.0,
    profile=[(0.0, 0.20), (0.04, 0.38), (0.12, 0.52), (0.30, 0.80), (0.55, 0.96),
             (0.75, 1.00), (0.90, 0.88), (0.97, 0.70), (1.0, 0.55)],
    annuli=34,
    groove=0.965,
    sides_top=20,
    sides_belly=6,
    oral=0.65,
    caudal=1.1,
    caudal_offset=0.65,
    eye_pairs=5,
    eye_size=0.0075,
    ground=True,
    back=TAN,
    back_head=TAN_HEAD,
    belly_col=BELLY,
    margin_col=PALE,
    margin_width=0.10,
    groove_dark=0.90,
    mottle=0.14,
    stripes=[
        ((0.0, 0.09), STRIPE, 0.95),
        ((0.55, 0.10), STRIPE, 0.9),
    ],
    sucker_col=(0.46, 0.28, 0.15),
)


if __name__ == "__main__":
    nh.run(lambda: lc.build(SPEC), "JapaneseLandLeech", ground=(0.30, 0.25, 0.15),
           views=((35, 30), (0, 90), (-90, 8), (150, 35)))
