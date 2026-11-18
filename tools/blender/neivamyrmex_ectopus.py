"""
Procedural Neivamyrmex ectopus worker (a New World army ant known from Miocene
Dominican amber, about 20-16 million years ago, the first fossil army ant
described) walking, for map colonies.

An ecitonine army ant worker: a long, parallel-sided head with only tiny
vestigial eyes (army ants hunt blind, by scent), strong curved mandibles,
short elbowed antennae with 12 segments and no club; a slim mesosoma without
spines; a two-segmented waist (petiole and postpetiole); a smooth oval gaster
with a sting. Uniform glossy reddish-brown, darker on the head and mandibles.
Built with tools/blender/nh_ant.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/neivamyrmex_ectopus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/NeivamyrmexEctopus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_ant  # noqa: E402

BODY = (0.40, 0.17, 0.07)
HEAD = (0.30, 0.12, 0.05)
LEG = (0.46, 0.22, 0.10)

PARAMS = dict(
    head_w=0.100, head_l=0.150, head_h=0.075, head_heart=0.15,
    eye_r=0.007, eye_y=-0.30,
    mandible=1.45, mandible_teeth=3,
    scape=0.13, funiculus=0.18, fun_segs=10, club_segs=0, ant_r=0.011,
    meso_len=0.34, meso_h=0.11, meso_w=0.85, groove=0.15,
    waist="two", pet_h=0.048, pet_w=0.040, post_w=0.050,
    gaster_l=0.19, gaster_w=0.115, gaster_h=0.100,
    sting=True,
    head_col=HEAD, meso_col=BODY, waist_col=BODY, gaster_col=BODY,
    leg_col=LEG, antenna_col=LEG, mandible_col=(0.22, 0.08, 0.03),
    gloss=0.6,
)

if __name__ == "__main__":
    nh_ant.run(PARAMS, "NeivamyrmexEctopus")
