"""
Procedural Rugosodon eurasiaticus (Middle-Late Jurassic multituberculate, Liaoning, China) for map colonies.

A rat-sized early mammal about 17 cm long including the tail, from the multituberculates, the
"rodents of the Mesozoic": a short, blunt snout with chisel-like front incisors and
many-cusped grinding cheek teeth for an omnivorous diet, small round ears, whiskers, very
flexible ankles that could swivel for climbing and digging, and a long tail. Painted
grey-brown fur with a pale belly (colour unknown). Built with nh_car_tetrapod. Faces -Y,
pivot on the ground.

Usage:
  blender --background --python tools/blender/rugosodon_eurasiaticus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Rugosodon.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_jurassic_small as sm  # noqa: E402

SPEC = tp.Spec(
    name="Rugosodon",
    head_len=0.2, head_w=0.075, head_h=0.06, snout=0.4,
    neck_len=0.04, neck_r=0.07,
    trunk_len=0.38, trunk_r=0.1, trunk_h=0.9,
    tail_len=0.5, tail_r=0.022, tail_fin=1.0, tail_curve=0.12,
    leg_r=0.022, front=(0.065, 0.07), hind=(0.075, 0.08), foot=0.04, toes=5,
    back=(0.34, 0.31, 0.27), flank=(0.48, 0.44, 0.38), belly=(0.84, 0.80, 0.72),
    pattern="none", head_col=(0.36, 0.32, 0.28), iris=(0.04, 0.03, 0.03), eye_r=0.016, eye_at=0.5, eye_up=0.5,
    teeth=0, voxel=0.006, max_tris=6000,
    extra=[sm.ears(0.03, (0.40, 0.34, 0.30), at=0.92, inner=(0.75, 0.55, 0.50)), sm.incisors(0.025, 0.005, color=(0.92, 0.85, 0.70)),
           sm.whiskers(0.07)],
)

if __name__ == "__main__":
    tp.run(SPEC)
