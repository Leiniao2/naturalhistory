"""
Procedural South African abalone or perlemoen (Haliotis midae) for the map, Fixed style.

A large adult (up to about 20 cm) clinging to a low rock crusted with pink coralline
algae: a thick, heavy, broadly oval ear-shaped shell whose outside is rugose - crossed
by prominent wavy radial ridges that break up into knobs where they meet the growth
undulations, crinkling the margin - brick-red to reddish brown, mottled darker and
patched with coralline crust, the small spire eroded pale. The spiral keel along the
left side carries a long row of sealed holes ending in six to eight open tremata. Under
the shell the grey-brown foot grips the rock, and a broad, cream-grey, frilly epipodium
spills well out past the rim with its banded tentacles - the "skirt" that makes a living
perlemoen look ruffled (see nh_abalone.py).
Faces -Y, pivot at the base of the rock (z = 0).

Usage:
  blender --background --python tools/blender/haliotis_midae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PerlemoenAbalone.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_abalone as ab  # noqa: E402

SHELL = ((0.52, 0.22, 0.14), (0.44, 0.24, 0.16), (0.58, 0.30, 0.18))   # brick red / red-brown
SHELL_DARK = (0.28, 0.13, 0.09)
SPIRE = (0.78, 0.66, 0.58)
FOOT = (0.30, 0.27, 0.22)            # grey-brown foot
EPIPODIUM = (0.62, 0.60, 0.52)       # cream-grey frilly skirt
TENTACLE = (0.70, 0.68, 0.60)
TENTACLE_TIP = (0.86, 0.84, 0.76)


def build():
    return ab.build(
        "PerlemoenAbalone", seed=9, length=1.0, width=0.76, height=0.24, ear=0.45,
        apex=(-0.34, 0.66), spin=0.34, row_angle=-0.30, holes_open=7, holes_closed=8,
        hole_size=0.032, keel=0.035, radial_ridges=15, ridge_amp=0.030, ridge_wave=1.3, bumps=0.6,
        growth_amp=0.008, rough=0.008, encrust=0.3,
        shell=SHELL, shell_dark=SHELL_DARK, spire=SPIRE, foot=FOOT, epipodium=EPIPODIUM,
        tentacle=TENTACLE, tentacle_tip=TENTACLE_TIP, stripes=0.5, frills=30, tentacles=50,
        tentacle_len=0.085, foot_height=0.10)


if __name__ == "__main__":
    nh.run(build, "PerlemoenAbalone", ground=(0.25, 0.32, 0.30),
           views=((35, 30), (0, 88), (-90, 8)))
