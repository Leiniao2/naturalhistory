"""
Procedural Argentine ant worker (Linepithema humile) walking, for map colonies.

A small, slender dolichoderine worker in a fairly uniform light-to-mid brown with
a slightly darker gaster and a soft sheen: an elongate oval head with modest eyes,
long 12-segmented elbowed antennae without a club (the scapes reach past the back
of the head), a low mesosoma with a clear metanotal groove and a rounded
propodeum, a one-segmented waist (a thin upright petiole scale), and a smooth oval
gaster with no sting. Six long, slim legs. Built with tools/blender/nh_ant.py.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/linepithema_humile.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArgentineAnt.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_ant  # noqa: E402

BROWN = (0.42, 0.26, 0.13)
GASTER = (0.32, 0.19, 0.09)
LEG = (0.48, 0.32, 0.17)

PARAMS = dict(
    head_w=0.095, head_l=0.125, head_h=0.070, head_heart=0.10,
    eye_r=0.026, eye_y=-0.10, mandible=0.85, mandible_teeth=5,
    scape=0.22, funiculus=0.30, fun_segs=11, club_segs=0, ant_r=0.009,
    meso_len=0.38, meso_h=0.105, meso_w=0.90, groove=0.32,
    meso_profile=((0.0, 0.50), (0.12, 0.90), (0.28, 1.00), (0.46, 0.84), (0.60, 0.72),
                  (0.72, 0.80), (0.86, 0.80), (1.0, 0.45)),
    waist="scale", pet_h=0.048, pet_w=0.030,
    gaster_l=0.19, gaster_w=0.115, gaster_h=0.100, gaster_tilt=4.0,
    sting=False,
    legs=1.08, leg_r=0.011,
    head_col=BROWN, meso_col=BROWN, waist_col=BROWN, gaster_col=GASTER,
    leg_col=LEG, antenna_col=LEG, mandible_col=(0.30, 0.18, 0.09),
    gloss=0.40,
)

if __name__ == "__main__":
    nh_ant.run(PARAMS, "ArgentineAnt")
