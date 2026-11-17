"""
Procedural Mixosaurus cornalianus (Middle Triassic mixosaurid ichthyosaur, ~1 m) for the
map (Swim style).

A small, common ichthyosaur of the Anisian-Ladinian seas of Monte San Giorgio (about 242
million years ago), and one of the first known with a tall, triangular dorsal fin, as
soft-tissue outlines show. A slim body, a long, narrow, toothed snout, big eyes, front
flippers clearly larger than the hind ones, and a tail with a distinct downward bend
carrying a lower lobe and a smaller, fleshy upper lobe, half-way between the eel-like
early ichthyosaurs and the tuna-shaped later ones. Built with the shared ichthyosaur
recipe (nh_ichthyosaur.py). Countershaded blue-grey (speculative).
Pivot at the body centre, faces -Y.

Usage:
  blender --background --python tools/blender/mixosaurus_cornalianus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Mixosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ichthyosaur as ich  # noqa: E402

SPEC = ich.IchthyosaurSpec(
    name="Mixosaurus",
    voxel=0.013, max_tris=12000,
    snout_len=0.30, snout_r=0.032, snout_tip_r=0.006,
    eye_r=0.050, head_h=0.085, head_w=0.068,
    body_h=0.150, belly_k=1.05, body_w=0.125, y_max=-0.22, rear_k=0.62,
    y_ped=0.66, ped_h=0.030, ped_w=0.020,
    tail_bend=16.0, y_bend=0.52,
    fore=(-0.40, 0.26, 0.11), fore_shape=0.35, fore_droop=32.0, fore_sweep=40.0,
    hind=(0.12, 0.15, 0.07), hind_shape=0.28, hind_droop=36.0, hind_sweep=45.0,
    dorsal=(0.02, 0.19, 0.30), dorsal_rake=0.45,
    fluke_up=0.12, fluke_down=0.26, fluke_sweep=0.22, fluke_chord=0.10, fluke_lunate=0.06,
    back=(0.16, 0.20, 0.26), flank=(0.40, 0.46, 0.52), belly=(0.88, 0.88, 0.84),
    fin=(0.12, 0.15, 0.20), mottle=(0.26, 0.30, 0.36), mottle_k=0.35,
    shade_line=-0.10, ring=(0.75, 0.70, 0.55), ring_plates=13,
)


def build():
    return ich.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "Mixosaurus", background=(0.05, 0.18, 0.24), views=((35, 25), (-90, 4), (30, 62)))
