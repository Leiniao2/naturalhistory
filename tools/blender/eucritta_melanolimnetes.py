"""
Procedural Eucritta melanolimnetes (Early Carboniferous of East Kirkton, Scotland, a small baphetoid stem tetrapod about 25-30 cm long, the "creature from the black lagoon") for map colonies (Ground style).

A small, slender stem tetrapod mixing fish-like and amphibian features: a short, blunt head
with very large eyes set far forward (its huge keyhole-shaped orbits), a small body, thin
sprawling legs and a long tapering tail; dark grey-green and mottled with a paler belly.
Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/eucritta_melanolimnetes.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Eucritta.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_carboniferous_tetra as ct  # noqa: E402

SPEC = tp.Spec(
    name="Eucritta",
    head_len=0.16, head_w=0.06, head_h=0.03, snout=0.5,
    neck_len=0.03, neck_r=0.04,
    trunk_len=0.33, trunk_r=0.048, trunk_h=0.85,
    tail_len=0.55, tail_r=0.03, tail_fin=1.5, tail_curve=0.14,
    leg_r=0.011, front=(0.07, 0.07), hind=(0.08, 0.075), foot=0.04, toes=5,
    back=(0.22, 0.26, 0.20), flank=(0.36, 0.40, 0.31), belly=(0.70, 0.70, 0.55),
    pattern="blotches", pattern_col=(0.08, 0.10, 0.07), pattern_scale=0.6,
    head_col=(0.20, 0.23, 0.18), iris=(0.80, 0.70, 0.25), eye_r=0.024, eye_at=0.36, eye_up=0.55, teeth=6,
    tooth_len=0.005, voxel=0.005, max_tris=3800,
)

if __name__ == "__main__":
    ct.run(SPEC)
