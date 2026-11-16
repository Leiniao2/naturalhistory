"""
Procedural ghost ant worker (Tapinoma melanocephalum) walking, for map colonies.

A tiny dolichoderine worker in two tones: the head and mesosoma are dark brown,
while the antennae, legs and the gaster are pale, almost translucent milky white,
so on the ground the ant seems to be all legs and abdomen with no head. Oval head
with long 12-segmented elbowed antennae (no club), a short humped mesosoma, a
one-segmented waist reduced to a tiny scale hidden under the overhanging front of
the soft oval gaster, and no sting. Six slim pale legs.
Built with tools/blender/nh_ant.py.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/tapinoma_melanocephalum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GhostAnt.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_ant  # noqa: E402

DARK = (0.15, 0.08, 0.045)
PALE = (0.94, 0.88, 0.70)
PALE_TIP = (0.80, 0.74, 0.60)
LEG = (0.95, 0.90, 0.74)

PARAMS = dict(
    head_w=0.105, head_l=0.120, head_h=0.072, head_heart=0.12,
    eye_r=0.025, eye_y=-0.12, mandible=0.8,
    scape=0.21, funiculus=0.28, fun_segs=11, club_segs=0, ant_r=0.009,
    meso_len=0.32, meso_h=0.115, meso_w=0.90, groove=0.20,
    meso_profile=((0.0, 0.50), (0.12, 0.92), (0.28, 1.00), (0.48, 0.86), (0.62, 0.74),
                  (0.76, 0.72), (0.90, 0.60), (1.0, 0.40)),
    waist="hidden",
    gaster_l=0.21, gaster_w=0.140, gaster_h=0.120, gaster_tilt=2.0, gaster_bands=4,
    band_col=(0.80, 0.72, 0.54),
    sting=False,
    legs=1.0, leg_r=0.011,
    head_col=DARK, meso_col=DARK, waist_col=PALE, gaster_col=PALE, gaster_tip=PALE_TIP,
    leg_col=LEG, scape_col=LEG, antenna_col=LEG, mandible_col=(0.45, 0.32, 0.18),
    gloss=0.55,
)

if __name__ == "__main__":
    nh_ant.run(PARAMS, "GhostAnt")
