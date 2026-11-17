"""
Procedural Mixopterus kiaeri (Late Silurian mixopterid sea scorpion from Ringerike,
Norway, about 75 cm long) for map colonies (Swim style).

A subquadrate prosoma with kidney-shaped eyes; the first two pairs of walking legs
are long, raptorial and armed with long paired spines, forming a catching basket;
the hind legs are shorter, with swimming paddles behind them. The narrow postabdomen
and its curved spike-like telson are carried arched up over the back, scorpion-like.
Brown with dark mottling. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/mixopterus_kiaeri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MixopterusKiaeri.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="MixopterusKiaeri",
    y_front=-0.70, y_pro=-0.42, pro_wf=0.15, pro_wb=0.17, pro_round=0.3, pro_h=0.055,
    pre_len=0.55, pre_w=[0.18, 0.20, 0.205, 0.20, 0.18, 0.15, 0.12], pre_h=0.06,
    post_len=0.45, post_w=[0.07, 0.062, 0.056, 0.052, 0.05], post_round=0.9,
    curl=110, curl_start=0.1, telson="spike", telson_len=0.30, telson_w=0.03,
    eye="kidney", eye_x=0.55, eye_y=0.30, eye_size=1.0, chelicera="small",
    legs=[L(0.12, 0.46, -60, 3, 0.09, 0.022), L(0.30, 0.48, -40, 3, 0.09, 0.023),
          L(0.52, 0.24, 0, 1, 0.03, 0.019), L(0.72, 0.26, 20, 1, 0.03, 0.020),
          L(0.90, 0.20, 10, 0, 0.0, 0.028, paddle=0.26)],
    shell=(0.46, 0.30, 0.16), shell_dark=(0.22, 0.13, 0.07), rim=(0.72, 0.56, 0.36), pattern="spots",
    leg=(0.52, 0.34, 0.18), leg_dark=(0.30, 0.18, 0.09),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
