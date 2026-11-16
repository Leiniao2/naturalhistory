"""
Procedural red imported fire ant worker (Solenopsis invicta) walking, for map colonies.

A small, glossy myrmicine worker: a reddish-brown (copper) head, slightly notched
behind, with small eyes and toothed mandibles; 10-segmented elbowed antennae ending
in a distinct 2-segmented club; a smoothly humped reddish-brown mesosoma without
spines; a two-segmented waist (petiole and postpetiole nodes); and a darker
brown-black gaster with faint tergite bands and a protruding sting. Six reddish
legs, knees above the body line. Built with tools/blender/nh_ant.py.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/solenopsis_invicta.py -- [--render out.png]

Output: Assets/Resources/Models/Species/FireAnt.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_ant  # noqa: E402

COPPER = (0.52, 0.19, 0.06)
GASTER = (0.17, 0.095, 0.055)
LEG = (0.50, 0.21, 0.08)

PARAMS = dict(
    head_w=0.120, head_l=0.120, head_h=0.080, head_heart=0.35,
    eye_r=0.022,
    scape=0.17, funiculus=0.24, fun_segs=9, club_segs=2, club_scale=1.75,
    waist="two", pet_h=0.050, post_w=0.048,
    gaster_l=0.21, gaster_w=0.140, gaster_h=0.120,
    sting=True,
    head_col=COPPER, meso_col=COPPER, waist_col=COPPER, gaster_col=GASTER,
    leg_col=LEG, antenna_col=COPPER, mandible_col=(0.30, 0.10, 0.04),
    gloss=0.55,
)

if __name__ == "__main__":
    nh_ant.run(PARAMS, "FireAnt")
