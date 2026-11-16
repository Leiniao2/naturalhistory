"""
Procedural cat flea (Ctenocephalides felis), an adult standing ready to jump, for map colonies.

A tiny wingless insect flattened from side to side (nh_flea.py): dark reddish-brown,
glossy, with shingled body plates each carrying a row of backward bristles, and huge
hind legs. Cat fleas have both combs: a genal comb of eight dark spines along the lower
margin of the head (the first about as long as the second) and a pronotal comb of about
sixteen spines along the hind margin of the pronotum. The head is long and low, about
twice as long as high, with a long, gently sloping forehead running down to a narrow, rounded
front; small dark eye, clubbed antenna folded back behind it, piercing mouthparts below.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/ctenocephalides_felis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CatFlea.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_flea as flea  # noqa: E402

SPEC = flea.Spec(
    name="CatFlea",
    head_len=0.27, head_h=0.135, head_w=0.070, frons=1.6, tip=0.42, eye_r=0.017,
    genal=(0.074, 0.076, 0.074, 0.071, 0.068, 0.064, 0.060, 0.055), pronotal=8, pronotal_len=0.060,
    body_color=(0.42, 0.15, 0.07), dark_color=(0.15, 0.045, 0.022),
    leg_color=(0.46, 0.20, 0.09), mouth_color=(0.50, 0.26, 0.12),
    seta_color=(0.10, 0.04, 0.02), comb_color=(0.05, 0.022, 0.012),
)


if __name__ == "__main__":
    flea.run(SPEC)
