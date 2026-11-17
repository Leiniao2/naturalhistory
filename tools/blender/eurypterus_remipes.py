"""
Procedural Eurypterus remipes (Late Silurian sea scorpion, the New York state fossil,
usually 10-20 cm long) for map colonies (Swim style).

A subquadrate prosoma with kidney-shaped compound eyes set in from the margins, small
chelicerae, three pairs of short spiny walking legs plus a longer fourth pair, and a
pair of broad swimming paddles; twelve opisthosomal segments (seven broad, five narrow
cylindrical) and a long, slender, spike-like telson. Olive-brown with paler tergite
margins. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/eurypterus_remipes.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EurypterusRemipes.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="EurypterusRemipes",
    y_front=-0.70, y_pro=-0.42, pro_wf=0.15, pro_wb=0.165, pro_round=0.35, pro_h=0.055,
    pre_len=0.62, pre_w=[0.17, 0.19, 0.20, 0.20, 0.185, 0.16, 0.13], pre_h=0.055,
    post_len=0.42, post_w=[0.085, 0.075, 0.068, 0.062, 0.058], telson="spike", telson_len=0.42, telson_w=0.028,
    eye="kidney", eye_x=0.50, eye_y=0.36, eye_size=1.0, chelicera="small",
    legs=[L(0.12, 0.16, -50, 2, 0.03, 0.018), L(0.30, 0.19, -30, 2, 0.035, 0.019),
          L(0.50, 0.22, -5, 2, 0.035, 0.020), L(0.70, 0.27, 20, 1, 0.025, 0.021),
          L(0.88, 0.18, 10, 0, 0.0, 0.028, paddle=0.30)],
    shell=(0.40, 0.33, 0.18), shell_dark=(0.22, 0.18, 0.10), rim=(0.66, 0.56, 0.36),
    under=(0.64, 0.56, 0.40), leg=(0.48, 0.38, 0.22), leg_dark=(0.30, 0.24, 0.13), spine=(0.80, 0.70, 0.50),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
