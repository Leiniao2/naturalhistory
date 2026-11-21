"""
Procedural Campylocephalus permianus (Late Permian hibbertopterid eurypterid, ~1.4 m) for map colonies.

The last known sea scorpion, from the Late Permian of Russia: a heavy, broad hibbertopterid
with a large, rounded head shield bearing small kidney-shaped eyes, a wide, rounded body
narrowing to a short tail with a spike, and front legs fringed with combs of spines that
raked small animals out of the mud. Dark reddish-brown armour with pale tubercles.
Built with nh_sil_eurypterid. Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/campylocephalus_permianus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Campylocephalus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="Campylocephalus",
    mode="swim",
    y_front=-0.64, y_pro=-0.18, pro_wf=0.28, pro_wb=0.34, pro_round=0.6, pro_h=0.09,
    pre_len=0.50, pre_w=[0.36, 0.38, 0.37, 0.34, 0.29, 0.23, 0.17], pre_h=0.08,
    post_len=0.20, post_w=[0.13, 0.11, 0.09], post_round=0.6,
    telson="spike", telson_len=0.16, telson_w=0.05,
    eye="kidney", eye_x=0.32, eye_y=0.40, eye_size=0.8, chelicera="small", tubercles=0.6,
    legs=[L(0.10, 0.36, -60, 5, 0.08, 0.022), L(0.30, 0.44, -35, 5, 0.09, 0.026),
          L(0.55, 0.40, -5, 1, 0.03, 0.03), L(0.80, 0.46, 25, 1, 0.03, 0.034), L(0.98, 0.52, 50, 1, 0.03, 0.038)],
    shell=(0.36, 0.19, 0.12), shell_dark=(0.18, 0.09, 0.06), rim=(0.66, 0.46, 0.30),
    under=(0.56, 0.40, 0.28), leg=(0.40, 0.24, 0.15), leg_dark=(0.24, 0.13, 0.08), spine=(0.78, 0.64, 0.46),
    pattern="spots",
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
