"""
Procedural Japanese abalone (Haliotis discus, including the northern subspecies
H. d. hannai) for the map, Fixed style.

An adult clinging to a low rock crusted with pink coralline algae: an oval, fairly
convex ear-shaped shell about 15-20 cm long, its outside smooth apart from fine growth
lines and low, broad spiral undulations - brownish green, mottled with olive and
darker bands, eroded pinkish at the small posterior spire and spotted with coralline
crust. A raised keel spirals out from the spire along the left side carrying a row of
sealed holes that ends in four or five open respiratory holes (tremata) with raised
rims. Under the shell the dark, almost black muscular foot grips the rock, and the
dark olive epipodium frills out past the shell rim with slender tentacles; two
cephalic tentacles reach forward from under the anterior margin (see nh_abalone.py).
Faces -Y, pivot at the base of the rock (z = 0).

Usage:
  blender --background --python tools/blender/haliotis_discus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/JapaneseAbalone.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_abalone as ab  # noqa: E402

SHELL = ((0.36, 0.34, 0.20), (0.42, 0.33, 0.20), (0.30, 0.36, 0.22))   # brownish green, mottled
SHELL_DARK = (0.20, 0.20, 0.12)
SPIRE = (0.66, 0.50, 0.46)
FOOT = (0.07, 0.07, 0.06)            # very dark foot
EPIPODIUM = (0.12, 0.13, 0.09)
TENTACLE = (0.22, 0.24, 0.17)
TENTACLE_TIP = (0.42, 0.44, 0.34)


def build():
    return ab.build(
        "JapaneseAbalone", seed=5, length=1.0, width=0.70, height=0.19, ear=0.55,
        apex=(-0.30, 0.64), spin=0.30, row_angle=-0.25, holes_open=5, holes_closed=7,
        hole_size=0.034, keel=0.025, radial_ridges=9, ridge_amp=0.006, ridge_wave=0.6, bumps=0.0,
        growth_amp=0.004, rough=0.004, encrust=0.2,
        shell=SHELL, shell_dark=SHELL_DARK, spire=SPIRE, foot=FOOT, epipodium=EPIPODIUM,
        tentacle=TENTACLE, tentacle_tip=TENTACLE_TIP, stripes=0.0, frills=24, tentacles=40,
        tentacle_len=0.07, foot_height=0.085)


if __name__ == "__main__":
    nh.run(build, "JapaneseAbalone", ground=(0.25, 0.32, 0.30),
           views=((35, 30), (0, 88), (-90, 8)))
