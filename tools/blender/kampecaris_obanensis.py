"""
Procedural Kampecaris obanensis (mid-Silurian millipede-like myriapod from the island of
Kerrera near Oban, Scotland, about 425 million years old, one of the oldest land animals
known) for map colonies (Ground style).

A small, slender, cylindrical body of about a dozen rounded, ring-like segments (no wide
side flanges like Arthropleura), each with a pair of short legs on each side, a small
head with short antennae. Dark brown with paler segment margins. Built with
nh_arthropleura.py (tergites with very narrow paranota). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/kampecaris_obanensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/KampecarisObanensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_arthropleura as ap  # noqa: E402

SPEC = ap.Spec(
    name="KampecarisObanensis",
    segments=12,
    length=1.5,
    half_width=0.10,
    dome=0.075,
    axial=0.85,
    paranota_droop=0.02,
    lobe_sweep=0.3,
    clearance=0.04,
    cols=12,
    rows=4,
    leg_sides=4,
    leg_reach=0.06,
    antenna=0.16,
    bend=0.10,
    axis_col=(0.38, 0.25, 0.14),
    para_col=(0.46, 0.32, 0.18),
    edge_col=(0.58, 0.45, 0.30),
    groove_col=(0.10, 0.06, 0.04),
    leg_col=(0.46, 0.34, 0.20),
    leg_tip_col=(0.28, 0.19, 0.11),
)


if __name__ == "__main__":
    nh.run(lambda: ap.build(SPEC), SPEC.name, ground=(0.24, 0.22, 0.14), views=((35, 30), (0, 75), (-90, 10)))
