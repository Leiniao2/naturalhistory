"""
Procedural Pterygotus anglicus (Late Silurian to Early Devonian pterygotid sea scorpion of
Britain, about 1.6 m long) for map colonies (Swim style).

The classic giant sea scorpion: a small, subquadrate prosoma with big compound eyes on
its front corners, a pair of enormous forward-reaching chelicerae with long, strongly
toothed pincers, slender walking legs and broad swimming paddles, a long flattened
opisthosoma of seven broad and five narrower segments, and a large, flat, oval telson
with a median keel used as a rudder. Olive-brown, banded. Built with
nh_sil_eurypterid.py.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/pterygotus_anglicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PterygotusAnglicus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="PterygotusAnglicus",
    y_front=-0.78, y_pro=-0.50, pro_wf=0.16, pro_wb=0.19, pro_round=0.25, pro_h=0.05,
    pre_len=0.76, pre_w=[0.20, 0.235, 0.255, 0.26, 0.245, 0.22, 0.18], pre_h=0.06,
    post_len=0.42, post_w=[0.12, 0.105, 0.095, 0.088, 0.084], telson="paddle", telson_len=0.42, telson_w=0.15,
    eye="marginal", eye_x=0.82, eye_y=0.10, eye_size=1.15, chelicera="giant", claw_len=0.56,
    legs=[L(0.15, 0.20, -45, 0, 0, 0.017), L(0.35, 0.23, -25, 0, 0, 0.018),
          L(0.55, 0.25, 0, 0, 0, 0.019), L(0.72, 0.27, 20, 0, 0, 0.020),
          L(0.90, 0.24, 5, 0, 0.0, 0.034, paddle=0.40)],
    shell=(0.34, 0.30, 0.16), shell_dark=(0.17, 0.15, 0.08), rim=(0.66, 0.58, 0.36), pattern="bands",
    under=(0.62, 0.56, 0.40), leg=(0.46, 0.38, 0.22), leg_dark=(0.26, 0.21, 0.12), spine=(0.90, 0.82, 0.58),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
