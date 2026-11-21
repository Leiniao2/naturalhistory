"""
Procedural Ichthyosaurus communis (Early Jurassic ichthyosaur, England) for the map (Swim style).

The classic "fish-lizard" first found by Mary Anning at Lyme Regis: a sleek, dolphin-shaped
marine reptile about 2 m long with a long, narrow, toothy snout, large eyes ringed by
bony sclerotic plates, broad front flippers (wider than in most ichthyosaurs, with extra
rows of finger bones), small hind flippers, a fleshy triangular dorsal fin and a crescent
tail fin. It gave birth to live young at sea. Painted with dark, countershaded colours
(dark grey-brown back, pale belly), as preserved pigment suggests for Jurassic ichthyosaurs.
Built with nh_ichthyosaur. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/ichthyosaurus_communis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ichthyosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ichthyosaur as ich  # noqa: E402

SPEC = ich.IchthyosaurSpec(
    name="Ichthyosaurus",
    voxel=0.014, max_tris=16000,
    snout_len=0.34, snout_r=0.034, snout_tip_r=0.006,
    eye_r=0.05, head_h=0.09, head_w=0.072,
    body_h=0.165, belly_k=1.05, body_w=0.135, y_max=-0.24, rear_k=0.6,
    y_ped=0.62, ped_h=0.028, ped_w=0.02,
    tail_bend=20.0, y_bend=0.5,
    fore=(-0.42, 0.32, 0.16), fore_shape=0.55, fore_droop=30.0, fore_sweep=36.0,
    hind=(0.12, 0.14, 0.07), hind_shape=0.35, hind_droop=34.0, hind_sweep=42.0,
    dorsal=(0.0, 0.15, 0.28), dorsal_rake=0.6,
    fluke_up=0.3, fluke_down=0.32, fluke_sweep=0.26, fluke_chord=0.09, fluke_lunate=0.13,
    back=(0.20, 0.17, 0.14), flank=(0.42, 0.38, 0.33), belly=(0.88, 0.85, 0.78),
    fin=(0.15, 0.13, 0.11), mottle=(0.28, 0.24, 0.20), mottle_k=0.3,
    shade_line=-0.15, ring=(0.80, 0.74, 0.58), ring_plates=14,
)

if __name__ == "__main__":
    nh.run(lambda: ich.build(SPEC), "Ichthyosaurus", background=(0.05, 0.18, 0.24),
           views=((35, 25), (-90, 4), (30, 62)))
