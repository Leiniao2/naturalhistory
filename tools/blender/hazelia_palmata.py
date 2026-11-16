"""
Procedural Hazelia palmata (Middle Cambrian demosponge, Burgess Shale, British Columbia) for the
map: a broad, flattened cup like a cupped hand ("palmata"), its margin divided into irregular
finger-like lobes, rising from a small basal attachment on a little patch of dark mud.

Hazelia has a thin wall of tightly packed monaxon spicules in mainly radial, anastomosing
tracts with a fine spicule net in the skin; in H. palmata the radial tracts project a couple
of millimetres beyond the margin. Here the tracts are low pale ribs running up the wall,
bristling with short spicules, and fringing the lobed margin with fine needles. Specimens
reach about 15 cm. Warm tan with paler tracts and a dark inside; the living colour is unknown.
See nh_hazelia.py for the shared builder. Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/hazelia_palmata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HazeliaPalmata.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_hazelia as nhz  # noqa: E402

SPEC = nhz.HazeliaSpec(
    seed=4,
    # (radius, height): narrow attachment widening into a broad, flattened fan-cup
    profile=[(0.04, 0.0), (0.13, 0.10), (0.36, 0.38), (0.62, 0.74), (0.80, 1.08)],
    sx=1.0, sy=0.17, curl=0.16,
    segs=64, rows=15, inner_rows=5, wall=0.045, inner_bottom=0.3,
    lobes=5, lobe_depth=0.26, lobe_sharp=0.55, lobe_flare=0.06,
    lobe_across=True, rough=0.02,
    wobble=0.11,
    tracts=17, tract_relief=0.018, tract_wander=0.3,
    needles=(3, (0.05, 0.10)),
    bristles=(140, (0.03, 0.06)),
    holdfast=(0.09, 0.035),
    mud=(0.35, 0.65),
    body=(0.78, 0.64, 0.44),
    shade=(0.55, 0.43, 0.29),
    tract=(0.93, 0.85, 0.68),
    rim=(0.90, 0.82, 0.64),
    inside=(0.28, 0.20, 0.13),
)


def build():
    return nhz.build(SPEC, "HazeliaPalmata")


if __name__ == "__main__":
    nh.run(build, "HazeliaPalmata", ground=(0.40, 0.38, 0.34), views=((15, 20), (80, 20), (10, 70)))
