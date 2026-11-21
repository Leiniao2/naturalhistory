"""
Procedural Eusarcana obesa (Late Silurian sea scorpion, about 10-15 cm long, from Bertie
Group waterlimes of New York and Ontario) for map colonies (Swim style).

The most scorpion-like of the eurypterids: a small, rounded head shield with eyes near
the front, a very broad, bulging preabdomen ("obesa"), a short, narrow postabdomen held
curled up over the back and a curved, sting-like telson, like a scorpion's. The first
two pairs of legs are long and armed with long spines for trapping prey; the last pair
are small swimming paddles. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the
body centre.

Usage:
  blender --background --python tools/blender/eusarcana_obesa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EusarcanaObesa.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="EusarcanaObesa",
    y_front=-0.66, y_pro=-0.44, pro_wf=0.12, pro_wb=0.15, pro_round=0.45, pro_h=0.050,
    pre_len=0.52, pre_w=[0.20, 0.25, 0.28, 0.28, 0.25, 0.19, 0.12], pre_h=0.075,
    post_len=0.40, post_w=[0.065, 0.060, 0.056, 0.053, 0.050], post_round=1.0,
    curl=150, curl_start=0.05, telson="sting", telson_len=0.18, telson_w=0.05,
    eye="kidney", eye_x=0.50, eye_y=0.22, eye_size=0.85, chelicera="small",
    legs=[L(0.12, 0.42, -60, 3, 0.10, 0.020), L(0.30, 0.46, -42, 3, 0.10, 0.021),
          L(0.52, 0.22, 0, 1, 0.03, 0.018), L(0.72, 0.24, 20, 1, 0.03, 0.019),
          L(0.90, 0.17, 10, 0, 0.0, 0.026, paddle=0.20)],
    shell=(0.36, 0.26, 0.18), shell_dark=(0.18, 0.12, 0.08), rim=(0.66, 0.54, 0.40), pattern="bands",
    leg=(0.48, 0.36, 0.24), leg_dark=(0.26, 0.18, 0.11), spine=(0.88, 0.78, 0.60),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
