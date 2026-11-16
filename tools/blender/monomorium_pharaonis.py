"""
Procedural pharaoh ant worker (Monomorium pharaonis) walking, for map colonies.

A tiny (about 2 mm) pale yellowish to light-brown myrmicine worker, finely
sculptured and rather matte: a long, nearly parallel-sided head with small eyes,
12-segmented elbowed antennae ending in a 3-segmented club, a slender mesosoma
with a deep metanotal groove, a two-segmented waist (petiole and postpetiole
nodes), and a smooth gaster that darkens to brown toward the tip, with a small
sting. Six slim pale legs. Built with tools/blender/nh_ant.py.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/monomorium_pharaonis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PharaohAnt.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_ant  # noqa: E402

YELLOW = (0.80, 0.55, 0.22)
BODY = (0.74, 0.47, 0.18)
GASTER = (0.76, 0.50, 0.20)
TIP = (0.26, 0.13, 0.05)
LEG = (0.86, 0.64, 0.32)

PARAMS = dict(
    head_w=0.095, head_l=0.135, head_h=0.072, head_heart=0.15,
    eye_r=0.017, eye_y=-0.05, mandible=0.85,
    scape=0.18, funiculus=0.25, fun_segs=11, club_segs=3, club_scale=1.85, ant_r=0.009,
    meso_len=0.36, meso_h=0.105, meso_w=0.85, groove=0.45,
    waist="two", pet_h=0.044, pet_w=0.030, post_w=0.040,
    gaster_l=0.18, gaster_w=0.120, gaster_h=0.105,
    sting=True,
    legs=1.0, leg_r=0.011,
    head_col=YELLOW, meso_col=BODY, waist_col=BODY, gaster_col=GASTER, gaster_tip=TIP, tip_start=0.38, gaster_bands=3,
    band_col=(0.68, 0.44, 0.17),
    leg_col=LEG, antenna_col=LEG, mandible_col=(0.55, 0.32, 0.10),
    gloss=0.25,
)

if __name__ == "__main__":
    nh_ant.run(PARAMS, "PharaohAnt")
