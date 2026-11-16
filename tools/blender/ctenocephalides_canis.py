"""
Procedural dog flea (Ctenocephalides canis), an adult standing ready to jump, for map colonies.

A tiny wingless insect flattened from side to side (nh_flea.py): dark brown and glossy,
with shingled body plates each carrying a row of backward bristles, and huge hind legs.
Like the cat flea it has both combs (a genal comb of eight dark spines along the lower
margin of the head and a pronotal comb of about sixteen along the hind margin of the
pronotum), but the head is shorter and higher, with a strongly curved, domed forehead,
and the first spine of the genal comb is only about half as long as the second - the
features that tell the two apart. Small dark eye, clubbed antenna folded back behind
it, piercing mouthparts below.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/ctenocephalides_canis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DogFlea.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_flea as flea  # noqa: E402

SPEC = flea.Spec(
    name="DogFlea",
    head_len=0.20, head_h=0.17, head_w=0.072, frons=2.4, tip=0.48, eye_r=0.018,
    genal=(0.036, 0.074, 0.073, 0.070, 0.066, 0.062, 0.058, 0.053), pronotal=8, pronotal_len=0.058,
    body_color=(0.27, 0.16, 0.085), dark_color=(0.11, 0.065, 0.035),
    leg_color=(0.38, 0.25, 0.13), mouth_color=(0.44, 0.30, 0.16),
    seta_color=(0.08, 0.05, 0.03), comb_color=(0.04, 0.025, 0.015),
)


if __name__ == "__main__":
    flea.run(SPEC)
