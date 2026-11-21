"""
Procedural Dendrerpeton acadianum (Late Carboniferous of Joggins, Nova Scotia, a temnospondyl amphibian about 1 m long, found inside fossil tree stumps) for map colonies (Ground style).

A salamander / small-crocodile-like temnospondyl: a broad, flat, parabolic skull with big eyes
set well back and a dark otic notch at each rear corner of the skull, a stout trunk, sturdy
sprawling legs and a medium tail; brown-olive with darker blotches and a pale belly.
Built with nh_car_tetrapod (+ nh_b2_carboniferous_tetra for the skull table and otic notch).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/dendrerpeton_acadianum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Dendrerpeton.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_carboniferous_tetra as ct  # noqa: E402

SPEC = tp.Spec(
    name="Dendrerpeton",
    head_len=0.19, head_w=0.1, head_h=0.03, snout=0.68,
    neck_len=0.035, neck_r=0.058,
    trunk_len=0.42, trunk_r=0.075, trunk_h=0.72,
    tail_len=0.42, tail_r=0.045, tail_fin=1.25, tail_curve=0.1,
    leg_r=0.02, front=(0.075, 0.07), hind=(0.085, 0.075), foot=0.045, toes=5,
    back=(0.30, 0.26, 0.14), flank=(0.46, 0.40, 0.22), belly=(0.84, 0.78, 0.58),
    pattern="blotches", pattern_col=(0.11, 0.09, 0.04), pattern_scale=0.8,
    head_col=(0.33, 0.29, 0.16), eye_r=0.02, eye_at=0.58, eye_up=0.75, teeth=8, tooth_len=0.006,
    voxel=0.006, max_tris=6000,
)

FUSED = []
PAINT = [ct.otic_notch(col=(0.08, 0.06, 0.03), at=0.9, width=0.26, out=0.72)]
SPEC.extra.append(ct.otic_disc(at=0.88, size=0.12, out=0.86, up=0.25))

if __name__ == "__main__":
    ct.run(SPEC, fused=FUSED, paint=PAINT)
