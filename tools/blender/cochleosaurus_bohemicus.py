"""
Procedural Cochleosaurus bohemicus (Late Carboniferous of Nýřany, Czech Republic, an edopoid temnospondyl about 1.2-2 m long) for map colonies (Ground style).

A crocodile-like temnospondyl: a long, flattish, triangular skull ending in a pair of short,
backward-pointing bony tabular horns at the back corners, small teeth, a robust trunk on short
sturdy legs and a moderately long tail; dark brown-grey with lighter flanks and a pale belly.
Built with nh_car_tetrapod (+ nh_b2_carboniferous_tetra for the horns).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/cochleosaurus_bohemicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Cochleosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_carboniferous_tetra as ct  # noqa: E402

SPEC = tp.Spec(
    name="Cochleosaurus",
    head_len=0.32, head_w=0.095, head_h=0.03, snout=0.3,
    neck_len=0.06, neck_r=0.05,
    trunk_len=0.48, trunk_r=0.085, trunk_h=0.7,
    tail_len=0.5, tail_r=0.05, tail_fin=1.3, tail_curve=0.1,
    leg_r=0.022, front=(0.06, 0.055), hind=(0.07, 0.06), foot=0.045, toes=5,
    back=(0.24, 0.20, 0.16), flank=(0.52, 0.46, 0.36), belly=(0.76, 0.72, 0.60),
    pattern="blotches", pattern_col=(0.16, 0.14, 0.11), pattern_scale=1.4,
    head_col=(0.24, 0.22, 0.18), eye_r=0.014, eye_at=0.62, eye_up=0.8, teeth=14, tooth_len=0.006,
    voxel=0.007, max_tris=7000,
)

FUSED = [ct.tabular_horns(0.12, 0.02, at=0.9, out=0.88, up=0.4, spread=0.38)]
PAINT = [ct.far_colour((0.42, 0.37, 0.30), dist=1.2, s_range=(0.0, 0.2))]

if __name__ == "__main__":
    ct.run(SPEC, fused=FUSED, paint=PAINT)
