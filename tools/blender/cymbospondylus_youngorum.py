"""
Procedural Cymbospondylus youngorum (Middle Triassic giant ichthyosaur, ~17 m) for the
map (Swim style).

A colossal early ichthyosaur from the 246-million-year-old Fossil Hill Member of
Nevada, described in 2021: its skull alone was about 2 metres long, and it reached
whale size less than three million years after the first ichthyosaurs appeared. Unlike
later ichthyosaurs it was long and slender, almost eel-like, with a long tail lacking a
strong tail bend and only a low fin at its end, no tall dorsal fin, small flippers, and
a long, narrow snout full of conical teeth for seizing squid-like animals and fish.
Built with the shared ichthyosaur recipe (nh_ichthyosaur.py). Countershaded dark
brown-grey with mottling (speculative). Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/cymbospondylus_youngorum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cymbospondylus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ichthyosaur as ich  # noqa: E402

SPEC = ich.IchthyosaurSpec(
    name="Cymbospondylus",
    voxel=0.012, max_tris=16000,
    snout_len=0.24, snout_r=0.028, snout_tip_r=0.006,
    eye_r=0.030, head_h=0.065, head_w=0.055,
    body_h=0.095, belly_k=1.05, body_w=0.085, y_max=-0.35, rear_k=0.80,
    y_ped=0.80, ped_h=0.022, ped_w=0.016,
    tail_bend=5.0, y_bend=0.72,
    fore=(-0.50, 0.15, 0.07), fore_shape=0.25, fore_droop=32.0, fore_sweep=42.0,
    hind=(-0.05, 0.11, 0.055), hind_shape=0.22, hind_droop=36.0, hind_sweep=46.0,
    dorsal=None,
    fluke_up=0.07, fluke_down=0.11, fluke_sweep=0.15, fluke_chord=0.10, fluke_lunate=0.02,
    back=(0.20, 0.17, 0.14), flank=(0.44, 0.39, 0.33), belly=(0.86, 0.82, 0.74),
    fin=(0.15, 0.12, 0.10), mottle=(0.30, 0.25, 0.20), mottle_k=0.50,
    shade_line=-0.25, ring=(0.72, 0.66, 0.52), ring_plates=12,
)


def build():
    return ich.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "Cymbospondylus", background=(0.05, 0.18, 0.24), views=((35, 25), (-90, 4), (30, 62)))
