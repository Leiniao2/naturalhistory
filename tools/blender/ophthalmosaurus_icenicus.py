"""
Procedural Ophthalmosaurus icenicus (Middle-Late Jurassic ophthalmosaurid ichthyosaur)
for the map (Swim style).

A compact, deep, teardrop-shaped, dolphin-like body about 4-6 m long, built for fast
cruising and deep diving: a slender, almost toothless-looking rostrum, ENORMOUS eyes
(among the largest relative to body size of any vertebrate) each ringed by the bony
plates of a sclerotic ring set in a raised orbit, a fleshy triangular dorsal fin,
large forefins and much smaller hindfins, and a strong, nearly symmetrical lunate tail
with a sharp tail bend.

Built with the shared ichthyosaur recipe (nh_ichthyosaur.py): lofted body, flipper,
dorsal and fluke slabs fused into one seamless surface (nh_model.MeshBuilder.fuse),
then repainted with countershading (dark slate back, grey flanks, pale belly) and
faint mottling. The colours are speculative but follow the dark, countershaded
pigmentation preserved in some Jurassic ichthyosaur fossils. Crisp eyes, sclerotic
plates and nostrils on top.

Usage:
  blender --background --python tools/blender/ophthalmosaurus_icenicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ophthalmosaurus.fbx
Pivot at the body centre, faces -Y, dorsal fin up (+Z). About 2 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ichthyosaur as ich  # noqa: E402

SPEC = ich.IchthyosaurSpec(
    name="Ophthalmosaurus",
    voxel=0.015, max_tris=20000,
    snout_len=0.26, snout_r=0.046, snout_tip_r=0.006,
    eye_r=0.072, head_h=0.115, head_w=0.088,
    body_h=0.200, belly_k=1.10, body_w=0.160, y_max=-0.28, rear_k=0.62,
    y_ped=0.60, ped_h=0.030, ped_w=0.020,
    tail_bend=22.0, y_bend=0.48,
    fore=(-0.44, 0.36, 0.14), fore_shape=0.40, fore_droop=30.0, fore_sweep=38.0,
    hind=(0.10, 0.13, 0.07), hind_shape=0.30, hind_droop=34.0, hind_sweep=42.0,
    dorsal=(0.02, 0.17, 0.30), dorsal_rake=0.65,
    fluke_up=0.32, fluke_down=0.34, fluke_sweep=0.26, fluke_chord=0.08, fluke_lunate=0.14,
    back=(0.13, 0.14, 0.17), flank=(0.36, 0.38, 0.41), belly=(0.86, 0.85, 0.80),
    fin=(0.10, 0.11, 0.13), mottle=(0.22, 0.23, 0.26), mottle_k=0.30,
    shade_line=-0.20, ring=(0.78, 0.72, 0.56), ring_plates=14,
)


def build():
    return ich.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "Ophthalmosaurus", background=(0.05, 0.18, 0.24),
           views=((35, 25), (-90, 4), (90, 4), (30, 62), (180, -40)))
