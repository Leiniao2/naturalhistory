"""
Procedural Triadobatrachus massinoti (Early Triassic, ~250 Ma, Madagascar), the earliest known
proto-frog, for map colonies (Ground style).

About 10 cm long and halfway to a frog: the broad, flat, round-snouted frog head with big eyes,
but a longer body than any frog (14 vertebrae against a frog's 9 or fewer), a short stub of a
tail still present, and hind legs only a little longer than the forelegs. It could not leap: it
crawled and swam, kicking with both hind legs together. Colours unknown: olive-brown above with
darker blotches, pale below.
Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/triadobatrachus_massinoti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Triadobatrachus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Triadobatrachus",
    head_len=0.22, head_w=0.12, head_h=0.045, snout=0.5,
    neck_len=0.01, neck_r=0.09,
    trunk_len=0.38, trunk_r=0.095, trunk_h=0.65,
    tail_len=0.07, tail_r=0.035, tail_fin=1.0, tail_curve=0.0,
    leg_r=0.02, front=(0.085, 0.08), hind=(0.11, 0.10), foot=0.06, toes=5,
    back=(0.30, 0.30, 0.16), flank=(0.42, 0.40, 0.24), belly=(0.84, 0.80, 0.62),
    pattern="blotches", pattern_col=(0.12, 0.11, 0.05), pattern_scale=1.8,
    head_col=(0.32, 0.31, 0.17), iris=(0.82, 0.62, 0.20), eye_r=0.03, eye_at=0.5, eye_up=0.85, teeth=0,
    voxel=0.006, max_tris=5000,
)

if __name__ == "__main__":
    tp.run(SPEC)
