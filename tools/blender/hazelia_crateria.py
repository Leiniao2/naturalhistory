"""
Procedural Hazelia crateria (Middle Cambrian demosponge, Burgess Shale, British Columbia; named
by Rigby in 1986) for the map: a wide, round, crater-like bowl on a short narrow base, its thin
wall built of radial spicule tracts, on a little patch of dark mud.

Like the other Hazelia species it has a thin wall of tightly packed monaxon spicules in mainly
radial, anastomosing tracts and a small basal attachment; this one is a broad cup ("crateria",
crater- or bowl-shaped). Unlike the flattened, lobed H. palmata the bowl is round and open,
with a gently wavy, slightly in-turned margin and only a short fringe of tract spicules. Pale
greyish cream with faint paler tracts and a dark bowl interior; the living colour is unknown.
See nh_hazelia.py for the shared builder. Fixed style: pivot at the base (z = 0).

Usage:
  blender --background --python tools/blender/hazelia_crateria.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HazeliaCrateria.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_hazelia as nhz  # noqa: E402

SPEC = nhz.HazeliaSpec(
    seed=11,
    # (radius, height): short stalk, then a wide, shallow bowl whose rim turns slightly inward
    profile=[(0.05, 0.0), (0.09, 0.07), (0.30, 0.20), (0.56, 0.38), (0.72, 0.58), (0.74, 0.70), (0.70, 0.76)],
    sx=1.0, sy=0.92, curl=0.0,
    segs=64, rows=16, inner_rows=7, wall=0.05, inner_bottom=0.07,
    lobes=7, lobe_depth=0.05, lobe_sharp=0.8, lobe_flare=0.0,
    wobble=0.08, rough=0.015, pores=(5.0, 0.55),
    tracts=21, tract_relief=0.022, tract_wander=0.35,
    needles=(3, (0.04, 0.07)),
    bristles=(110, (0.025, 0.04)),
    holdfast=(0.10, 0.035),
    mud=(0.6, 0.95),
    body=(0.62, 0.58, 0.48),
    shade=(0.42, 0.39, 0.32),
    tract=(0.92, 0.90, 0.82),
    rim=(0.88, 0.85, 0.76),
    inside=(0.24, 0.20, 0.16),
)


def build():
    return nhz.build(SPEC, "HazeliaCrateria")


if __name__ == "__main__":
    nh.run(build, "HazeliaCrateria", ground=(0.40, 0.38, 0.34), views=((15, 20), (80, 45), (10, 75)))
