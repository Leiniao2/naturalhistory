"""
Procedural giant clam (Tridacna gigas) for the map, Fixed style.

The largest living bivalve, an adult about a metre long lying hinge-down on a sandy
reef flat among coral rubble: two enormous, heavy, chalky grey-white valves fouled
green-brown toward the base, each folded into four or five huge rounded ribs with
smooth backs (no fluted scales), whose crests lobe out into big rounded scallops so
the wide gape between the valves zig-zags from end to end. Out of it bulges the fleshy
mantle: golden brown and olive, the colour of the zooxanthellae it farms, scattered
with iridescent blue-green spots and edged with a row of small eye spots, with a
raised exhalant siphon near one end and the slit of the inhalant aperture in the
middle (see nh_tridacna.py). Pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/tridacna_gigas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/GiantClam.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tridacna as tc  # noqa: E402

SHELL = (0.80, 0.78, 0.72)          # chalky grey-white
SHELL_DARK = (0.56, 0.54, 0.48)
FOULING = (0.38, 0.40, 0.26)
MANTLE = (0.52, 0.42, 0.16)         # golden brown
MANTLE2 = (0.34, 0.36, 0.16)        # olive
SPOTS = (0.18, 0.70, 0.66)          # iridescent blue-green
EDGE = (0.22, 0.50, 0.46)
EYES = (0.30, 0.85, 0.80)


def build():
    return tc.build(
        "GiantClam", seed=4, length=1.6, height=0.95, inflation=0.44, spread=1.80,
        centre=(0.0, 0.38), ribs=5, rib_amp=0.075, rib_sharp=0.75, scallop=0.12,
        gape=0.22, lip=0.06, n_theta=84, n_u=20,
        shell=SHELL, shell_dark=SHELL_DARK, fouling=FOULING, foul=0.55,
        mantle=MANTLE, mantle2=MANTLE2, pattern="spots", pattern_col=SPOTS, pattern_scale=9.0,
        pattern_amt=0.8, edge_col=EDGE, edge_width=0.12, eye_col=EYES, eyes=70,
        over=0.03, droop=0.02, bulge=0.08, ruffle=0.015, mantle_frac=0.62, n_w=22, mantle_smooth=0.0, seat="rubble")


if __name__ == "__main__":
    nh.run(build, "GiantClam", ground=(0.78, 0.72, 0.56), views=((35, 30), (10, 70), (-90, 10)))
