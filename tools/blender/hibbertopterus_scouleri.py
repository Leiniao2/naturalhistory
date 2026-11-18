"""
Procedural Hibbertopterus scouleri (Early Carboniferous of Scotland, a giant sweep-feeding
eurypterid about 1.6-1.8 m long and one of the heaviest arthropods ever) for map colonies
(Ground style: a trackway shows it walked over land).

A broad, heavy sea scorpion: a huge, rounded, shovel-like head shield with small kidney eyes
set near its middle, a very wide, segmented, oval body, a short tail ending in a stubby
lanceolate spike, two front pairs of legs fringed with long raking spines for combing small
animals out of the mud, and two stout rear walking legs. Dark grey-brown cuticle studded
with pale scale-like tubercles. Built with nh_sil_eurypterid. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/hibbertopterus_scouleri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Hibbertopterus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="Hibbertopterus",
    mode="ground", leg_lift=0.06,
    y_front=-0.62, y_pro=-0.20, pro_wf=0.26, pro_wb=0.33, pro_round=0.55, pro_h=0.08,
    pre_len=0.52, pre_w=[0.35, 0.37, 0.36, 0.33, 0.28, 0.22, 0.16], pre_h=0.08,
    post_len=0.22, post_w=[0.12, 0.10, 0.085], post_round=0.6,
    telson="spike", telson_len=0.18, telson_w=0.05,
    eye="kidney", eye_x=0.28, eye_y=0.42, eye_size=0.9, chelicera="small", tubercles=0.45,
    legs=[L(0.10, 0.34, -60, 4, 0.07, 0.022), L(0.30, 0.42, -35, 4, 0.08, 0.026),
          L(0.55, 0.42, -5, 1, 0.03, 0.03), L(0.80, 0.50, 25, 1, 0.03, 0.034), L(0.98, 0.56, 50, 1, 0.03, 0.038)],
    shell=(0.28, 0.25, 0.21), shell_dark=(0.14, 0.12, 0.10), rim=(0.58, 0.52, 0.42),
    under=(0.46, 0.40, 0.32), leg=(0.32, 0.27, 0.21), leg_dark=(0.20, 0.17, 0.13), spine=(0.70, 0.62, 0.48),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.GROUND_VIEWS)
