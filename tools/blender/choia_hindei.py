"""
Procedural Choia hindei (Cambrian demosponge; Burgess Shale, House Range of Utah, and the
type material from Little Metis, Quebec) for the map: a large, broad, low disc with coarse
radial spicule tracts and a ring of stout coronal spicules.

C. hindei is told apart from C. carteri mainly by its larger disc (up to about 6 cm across)
and its coarser texture of thicker spicules. So compared with choia_carteri.py the disc here
is much broader relative to the spicule fringe (about 60% of the overall width), flatter and
more dome-like, with about 20 bold radial ribs in relief; the coronal spicules are fewer,
thicker, more irregular in length and shorter relative to the disc. It lies loose on the mud,
propped on the lower spicules. Warmer ochre-tan body (colour unknown; a plausible sponge
tone) with buff, glassy spicules. See nh_choia.py for the shared builder.
Fixed style: pivot on the ground (z = 0).

Usage:
  blender --background --python tools/blender/choia_hindei.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChoiaHindei.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_choia as nc  # noqa: E402

SPEC = nc.ChoiaSpec(
    seed=12,
    disc_r=0.62,
    disc_h=0.28,
    rim_t=0.08,
    cone_p=1.7,                    # broad, low dome
    lift=0.05,
    segments=80,
    ribs=20,                       # coarse spicule tracts
    rib_depth=0.016,
    osculum_r=0.06,
    upper=(22, (0.30, 0.46), (0.018, 0.023), (8.0, 30.0)),
    lower=(22, (0.32, 0.48), (0.019, 0.024), (None, None)),
    jitter=0.25,
    sag=0.04,
    body=(0.82, 0.64, 0.40),
    body_dark=(0.56, 0.40, 0.22),
    rib_col=(0.93, 0.80, 0.58),
    osculum=(0.26, 0.16, 0.09),
    spicule_base=(0.74, 0.62, 0.44),
    spicule_tip=(0.95, 0.91, 0.80),
)


def build():
    return nc.build(SPEC, "ChoiaHindei")


if __name__ == "__main__":
    nh.run(build, "ChoiaHindei", ground=(0.36, 0.34, 0.30), views=((20, 30), (70, 12), (10, 75)))
