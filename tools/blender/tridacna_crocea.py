"""
Procedural crocus clam or boring clam (Tridacna crocea) for the map, Fixed style.

The smallest giant clam, about 15 cm long, which bores into coral heads and sits
embedded in the rock right up to its rim: a lump of reef rock, crusted with pink
coralline algae and turf with a few small coral knobs, holding a short, triangular
shell with low, close-set scaly ribs, of which only the scalloped margin shows. Filling
the gape and spreading over the rim is the brilliant mantle - electric blue and purple,
streaked with darker lines and an orange-gold band along its wavy edge, fringed with
small eye spots, with the exhalant siphon raised near one end and the slit of the
inhalant aperture in the middle (see nh_tridacna.py). Pivot at the base of the rock
(z = 0).

Usage:
  blender --background --python tools/blender/tridacna_crocea.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CrocusClam.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_tridacna as tc  # noqa: E402

SHELL = (0.84, 0.78, 0.66)          # greyish white tinged yellow
SHELL_DARK = (0.60, 0.54, 0.44)
FOULING = (0.42, 0.40, 0.30)
MANTLE = (0.22, 0.20, 0.82)         # electric blue-violet
MANTLE2 = (0.48, 0.18, 0.72)        # purple
STREAKS = (0.08, 0.06, 0.38)
EDGE = (0.95, 0.55, 0.12)           # orange-gold rim
EYES = (0.40, 0.90, 0.95)


def build():
    return tc.build(
        "CrocusClam", seed=21, length=1.2, height=0.70, inflation=0.26, spread=1.75,
        centre=(0.0, 0.40), tri=0.5, ribs=7, rib_amp=0.035, rib_sharp=0.8, scallop=0.07,
        scale_rows=3, scale_len=0.05, scale_from=0.72,
        gape=0.15, lip=0.03, n_theta=56, n_u=10,
        shell=SHELL, shell_dark=SHELL_DARK, fouling=FOULING, foul=0.4,
        mantle=MANTLE, mantle2=MANTLE2, pattern="streaks", pattern_col=STREAKS, pattern_scale=3.5,
        pattern_amt=0.6, edge_col=EDGE, edge_width=0.16, eye_col=EYES, eyes=36,
        over=0.10, droop=0.03, bulge=0.10, ruffle=0.03, mantle_frac=0.66, n_w=14, mantle_smooth=0.75,
        seat="rock", embed=0.93, rock_size=1.3, rock_round=2.4)


if __name__ == "__main__":
    nh.run(build, "CrocusClam", ground=(0.70, 0.66, 0.54), views=((35, 30), (10, 70), (-90, 10)))
