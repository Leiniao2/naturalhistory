"""
Procedural Acutiramus macrophthalmus (Late Silurian pterygotid sea scorpion of the
Bertie Group, New York and Ontario, over 2 m long) for map colonies (Swim style).

Pterygotid body plan: a small, subquadrate prosoma with big compound eyes on its
front corners (macrophthalmus = "large eye"), a pair of huge forward-reaching
chelicerae whose long pincer rami carry rows of inclined, acute denticles, slender
unspined walking legs and broad swimming paddles; a long opisthosoma of seven broad
and five narrower segments ending in a flat, spear-shaped telson used as a rudder.
Dark reddish-brown. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/acutiramus_macrophthalmus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AcutiramusMacrophthalmus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="AcutiramusMacrophthalmus",
    y_front=-0.80, y_pro=-0.48, pro_wf=0.17, pro_wb=0.20, pro_round=0.22, pro_h=0.055,
    pre_len=0.74, pre_w=[0.21, 0.235, 0.25, 0.25, 0.235, 0.21, 0.17], pre_h=0.065,
    post_len=0.44, post_w=[0.11, 0.095, 0.085, 0.078, 0.074], telson="paddle", telson_len=0.36, telson_w=0.105,
    eye="marginal", eye_x=0.80, eye_y=0.12, eye_size=1.25, chelicera="giant", claw_len=0.40,
    legs=[L(0.15, 0.22, -45, 0, 0, 0.018), L(0.35, 0.25, -25, 0, 0, 0.019),
          L(0.55, 0.27, 0, 0, 0, 0.020), L(0.72, 0.29, 20, 0, 0, 0.021),
          L(0.90, 0.25, 5, 0, 0.0, 0.032, paddle=0.34)],
    shell=(0.42, 0.17, 0.10), shell_dark=(0.24, 0.09, 0.06), rim=(0.70, 0.42, 0.25),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
