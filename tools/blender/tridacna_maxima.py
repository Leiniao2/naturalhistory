"""
Procedural small giant clam or elongate giant clam (Tridacna maxima) for the map,
Fixed style.

An adult about 20-30 cm long wedged into a reef crevice, its lower half sunk in a lump
of coral rock crusted with pink coralline algae: the shell is elongate and
asymmetric - the umbones sit well toward one end and the other end is drawn out - with
many close-set ribs, each crest set with rows of short upturned fluted scales near the
margin, whitish with a creamy-yellow tinge. The mantle is the showpiece: a brilliant
blue and green, patterned with wavy darker streaks and pale dots, its broad wavy margin
spreading out over the edge of the shell and fringed with a row of small eye spots,
with a raised exhalant siphon and the slit-like inhalant aperture (see nh_tridacna.py).
Pivot at the base of the rock (z = 0).

Usage:
  blender --background --python tools/blender/tridacna_maxima.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SmallGiantClam.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tridacna as tc  # noqa: E402

SHELL = (0.86, 0.82, 0.68)          # white, tinged creamy yellow
SHELL_DARK = (0.62, 0.58, 0.46)
FOULING = (0.45, 0.42, 0.30)
SCALES = (0.94, 0.90, 0.78)
MANTLE = (0.10, 0.42, 0.78)         # brilliant blue
MANTLE2 = (0.08, 0.55, 0.50)        # blue-green
STREAKS = (0.04, 0.16, 0.40)        # dark wavy streaks
EDGE = (0.25, 0.78, 0.62)           # bright green margin
EYES = (0.80, 0.92, 0.95)


def build():
    return tc.build(
        "SmallGiantClam", seed=8, length=1.5, height=0.62, inflation=0.26, spread=1.85,
        centre=(0.0, 0.42), asym=0.32, ribs=9, rib_amp=0.05, rib_sharp=0.8, scallop=0.06,
        scale_rows=5, scale_len=0.07, scale_from=0.5,
        gape=0.14, lip=0.03, n_theta=72, n_u=14,
        shell=SHELL, shell_dark=SHELL_DARK, fouling=FOULING, foul=0.3, scale_col=SCALES,
        mantle=MANTLE, mantle2=MANTLE2, pattern="streaks", pattern_col=STREAKS, pattern_scale=3.0,
        pattern_amt=0.7, edge_col=EDGE, edge_width=0.18, eye_col=EYES, eyes=48,
        over=0.13, droop=0.07, bulge=0.10, ruffle=0.03, mantle_frac=0.70, n_w=18, mantle_smooth=0.85,
        seat="rock", embed=0.32)


if __name__ == "__main__":
    nh.run(build, "SmallGiantClam", ground=(0.70, 0.66, 0.54), views=((35, 30), (10, 70), (-90, 10)))
