"""
Procedural oriental rat flea (Xenopsylla cheopis), an adult standing ready to jump, for
map colonies.

A tiny wingless insect flattened from side to side (nh_flea.py): pale amber-brown and
glossy, with shingled body plates each carrying a row of backward bristles, and huge hind
legs. Unlike the cat and dog fleas it has no combs at all - neither a genal comb under the
head nor a pronotal comb - so the head and thorax look smooth. The head is evenly rounded
in front, with a large dark eye, the stout ocular bristle in front of it and a clubbed
antenna folded back behind it; piercing mouthparts below.
Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/xenopsylla_cheopis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/RatFlea.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_flea as flea  # noqa: E402

SPEC = flea.Spec(
    name="RatFlea",
    head_len=0.21, head_h=0.16, head_w=0.070, frons=2.0, tip=0.45, eye_r=0.024,
    genal=(), pronotal=0,
    body_color=(0.74, 0.48, 0.21), dark_color=(0.42, 0.24, 0.09),
    leg_color=(0.80, 0.58, 0.30), mouth_color=(0.78, 0.56, 0.30),
    seta_color=(0.30, 0.16, 0.06), eye_color=(0.05, 0.03, 0.02),
)


if __name__ == "__main__":
    flea.run(SPEC)
