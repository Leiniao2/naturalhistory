"""
Procedural Slimonia acuminata (Silurian slimonid sea scorpion from Lesmahagow,
Scotland, up to about 1 m long) for map colonies (Swim style).

A long, rectangular prosoma, longer than wide, with small compound eyes on its front
corners; small chelicerae; slender spiny walking legs and swimming paddles; a long
tapering opisthosoma; and its hallmark, a long, flattened, blade-like telson with
finely serrated edges ending in a short point. Mottled grey-brown. Built with
nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/slimonia_acuminata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SlimoniaAcuminata.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="SlimoniaAcuminata",
    y_front=-0.85, y_pro=-0.45, pro_wf=0.14, pro_wb=0.16, pro_round=0.12, pro_h=0.05,
    pre_len=0.72, pre_w=[0.17, 0.19, 0.20, 0.20, 0.19, 0.17, 0.14], pre_h=0.055,
    post_len=0.42, post_w=[0.09, 0.08, 0.072, 0.066, 0.062], telson="blade", telson_len=0.50, telson_w=0.055,
    eye="marginal", eye_x=0.85, eye_y=0.06, eye_size=0.75, chelicera="small",
    legs=[L(0.12, 0.18, -45, 2, 0.03, 0.016), L(0.32, 0.22, -25, 2, 0.03, 0.017),
          L(0.52, 0.25, 0, 2, 0.03, 0.018), L(0.72, 0.27, 20, 1, 0.03, 0.019),
          L(0.90, 0.22, 5, 0, 0.0, 0.028, paddle=0.30)],
    shell=(0.40, 0.36, 0.30), shell_dark=(0.22, 0.20, 0.17), rim=(0.66, 0.60, 0.50), pattern="spots",
    under=(0.62, 0.58, 0.48), leg=(0.46, 0.40, 0.32), leg_dark=(0.28, 0.24, 0.19),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
