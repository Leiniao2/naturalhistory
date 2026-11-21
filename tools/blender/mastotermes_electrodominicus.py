"""
Procedural Mastotermes electrodominicus (Miocene amber of the Dominican
Republic) for map colonies: an extinct giant termite preserved in amber.

A worker of the most primitive living termite family, whose only surviving
member is Australia's giant northern termite: a soft, pale, cockroach-like
body broadly joined to a long, banded abdomen, a big rounded orange-brown head
with strong biting mandibles and straight, bead-like antennae, no eyes to
speak of. Built with nh_ant.py (termites are not ants, but share the worker
layout). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/mastotermes_electrodominicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MastotermesElectrodominicus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_ant  # noqa: E402

HEAD = (0.66, 0.40, 0.16)
BODY = (0.88, 0.80, 0.64)
BAND = (0.70, 0.60, 0.44)
LEG = (0.86, 0.78, 0.60)

PARAMS = dict(
    head_w=0.125, head_l=0.135, head_h=0.085, head_heart=0.0, head_pitch=6.0,
    eye_r=0.006, eye_y=-0.10,
    mandible=1.25, mandible_teeth=3,
    scape=0.05, funiculus=0.30, fun_segs=14, club_segs=0, ant_r=0.010,
    scape_dir=(0.6, -0.7, 0.35), fun_dir=(0.45, -0.85, 0.05), fun_dir2=(0.55, -0.75, -0.25),
    meso_len=0.30, meso_h=0.115, meso_w=1.3, groove=0.04, legs=0.85,
    meso_profile=((0.0, 0.60), (0.15, 0.95), (0.33, 0.80), (0.5, 0.90), (0.66, 0.80), (0.82, 0.92), (1.0, 0.70)),
    waist="hidden",
    gaster_l=0.30, gaster_w=0.15, gaster_h=0.10, gaster_tilt=2.0, gaster_bands=7,
    sting=False,
    head_col=HEAD, meso_col=BODY, waist_col=BODY, gaster_col=BODY, band_col=BAND,
    leg_col=LEG, antenna_col=(0.70, 0.50, 0.28), mandible_col=(0.30, 0.15, 0.06),
    gloss=0.35,
)

if __name__ == "__main__":
    nh_ant.run(PARAMS, "MastotermesElectrodominicus")
