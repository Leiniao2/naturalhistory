"""
Procedural Protosuchus richardsoni (Early Jurassic protosuchid crocodylomorph, Arizona) for map colonies.

An early land-living crocodile relative about 1 m long: a short, broad, triangular head with
sharp teeth and an enlarged fang in the lower jaw, a body carried on long, upright legs,
and two neat rows of square bony armour plates down the back and tail. It hunted small
animals on dry land rather than in water. Painted dusty brown with darker crossbands and a
pale belly (colour unknown). Built with nh_car_tetrapod. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/protosuchus_richardsoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Protosuchus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_jurassic_small as sm  # noqa: E402

SPEC = tp.Spec(
    name="Protosuchus",
    head_len=0.17, head_w=0.065, head_h=0.035, snout=0.3,
    neck_len=0.06, neck_r=0.04,
    trunk_len=0.36, trunk_r=0.065, trunk_h=0.8,
    tail_len=0.6, tail_r=0.04, tail_fin=1.15, tail_curve=0.1,
    leg_r=0.016, front=(0.085, 0.1), hind=(0.1, 0.11), foot=0.04, toes=4,
    back=(0.36, 0.28, 0.18), flank=(0.54, 0.44, 0.30), belly=(0.84, 0.78, 0.62),
    pattern="bands", pattern_col=(0.24, 0.18, 0.11), pattern_scale=1.0,
    iris=(0.85, 0.65, 0.15), eye_r=0.012, eye_at=0.68, eye_up=0.75, teeth=7, tooth_len=0.008,
    voxel=0.0055, max_tris=7000,
    extra=[sm.scutes((0.30, 0.23, 0.15), 0.25, 1.0, 0.026, 0.013, rows=(-0.3, 0.3))],
)

if __name__ == "__main__":
    tp.run(SPEC)
