"""
Procedural Ianthasaurus hardestiorum (Late Carboniferous of Garnett, Kansas, a small edaphosaurid synapsid about 70 cm long) for map colonies (Ground style).

A small, lizard-like sail-backed synapsid: a small, short head, a low-slung body on sprawling
legs and a long tail, carrying a tall dorsal sail of elongated neural spines, each studded with
short knobby crossbars; the sail web is a translucent-looking reddish ochre between dark spines,
the body brown.
Built with nh_car_tetrapod (+ nh_b2_carboniferous_tetra for the sail).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ianthasaurus_hardestiorum.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Ianthasaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_carboniferous_tetra as ct  # noqa: E402

SPEC = tp.Spec(
    name="Ianthasaurus",
    head_len=0.11, head_w=0.038, head_h=0.03, snout=0.45,
    neck_len=0.05, neck_r=0.03,
    trunk_len=0.38, trunk_r=0.05, trunk_h=0.95,
    tail_len=0.62, tail_r=0.03, tail_fin=1.1, tail_curve=0.14,
    leg_r=0.012, front=(0.06, 0.06), hind=(0.065, 0.065), foot=0.04, toes=5,
    back=(0.30, 0.21, 0.13), flank=(0.44, 0.32, 0.20), belly=(0.76, 0.64, 0.46),
    pattern="spots", pattern_col=(0.20, 0.13, 0.08), pattern_scale=1.0,
    head_col=(0.34, 0.24, 0.15), eye_r=0.011, eye_at=0.55, eye_up=0.45, teeth=5, tooth_len=0.004,
    voxel=0.005, max_tris=5000,
)

SPEC.extra.append(ct.dorsal_sail(-0.05, 1.0, 0.22, n=20, spine_r=0.0042,
                                 spine_col=(0.16, 0.10, 0.06), sail_col=(0.80, 0.40, 0.17),
                                 edge_col=(0.62, 0.26, 0.12), crossbars=4, bar_col=(0.20, 0.12, 0.07)))

if __name__ == "__main__":
    ct.run(SPEC)
