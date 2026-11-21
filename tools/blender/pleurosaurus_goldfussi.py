"""
Procedural Pleurosaurus goldfussi (Late Jurassic marine rhynchocephalian, Solnhofen, Germany)
for map colonies (Swim style).

A sea-going relative of the living tuatara, about 60 cm long, that took to the water and became
almost eel-like: a long, narrow, pointed head with the nostrils set far back, a very long,
slender body, tiny paddle-like limbs held back against the flanks, and an extremely long,
flattened tail making up most of its length, used for swimming by undulation. Painted dark
grey-green above with a pale belly (colour unknown). Built with nh_car_tetrapod (swim pose).
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/pleurosaurus_goldfussi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Pleurosaurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402

SPEC = tp.Spec(
    name="Pleurosaurus",
    head_len=0.12, head_w=0.026, head_h=0.018, snout=0.25,
    neck_len=0.05, neck_r=0.022,
    trunk_len=0.42, trunk_r=0.032, trunk_h=0.8,
    tail_len=0.85, tail_r=0.024, tail_fin=1.9, tail_curve=0.18,
    leg_r=0.008, front=(0.025, 0.025), hind=(0.03, 0.03), foot=0.022, toes=5,
    swim=True,
    back=(0.20, 0.25, 0.22), flank=(0.36, 0.42, 0.36), belly=(0.86, 0.84, 0.74),
    pattern="spots", pattern_col=(0.12, 0.15, 0.12), pattern_scale=0.8, lateral_line=True,
    iris=(0.80, 0.66, 0.25), eye_r=0.007, eye_at=0.6, eye_up=0.55, teeth=6, tooth_len=0.004,
    voxel=0.004, max_tris=6000,
)

if __name__ == "__main__":
    tp.run(SPEC)
