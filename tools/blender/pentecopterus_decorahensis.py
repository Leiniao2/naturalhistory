"""
Procedural Pentecopterus decorahensis (Middle Ordovician, Darriwilian, about 467 million
years ago, megalograptid eurypterid from the Winneshiek Shale of Iowa; up to about
1.7 m long, the largest Ordovician eurypterid) for map colonies (Swim style).

Megalograptid plan (nh_ord_eurypterid.py): a broad, rather polygonal prosoma (the name
recalls the Greek penteconter warship), large crescent eyes; long front legs armed
with long spines (fewer and longer towards the tips); broad paddles; a long abdomen
tapering into a narrow postabdomen and a long spiky telson, without cercal blades in
the model. Dark reddish-brown with paler segment margins (colour conjectural).

Usage:
  blender --background --python tools/blender/pentecopterus_decorahensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PentecopterusDecorahensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_eurypterid as eu  # noqa: E402

SPEC = eu.Spec(
    name="PentecopterusDecorahensis",
    y_front=-0.80, y_pro=-0.44, y_pre=0.34, y_post=0.80, telson_len=0.36,
    pro_w=0.235, pro_front=0.80, pro_corner=0.12, eye_x=0.15, eye_y=0.25,
    pre_w=(0.24, 0.27, 0.28, 0.27, 0.25, 0.21, 0.16),
    post_w=(0.11, 0.095, 0.085, 0.075, 0.068),
    legs=(0.48, 0.58, 0.64), leg_spines=4, spine_len=0.19, leg_v=0.30, paddle=0.18,
    cercal=0.0, telson_w=0.035,
    shell=(0.42, 0.17, 0.11), shell_dark=(0.24, 0.09, 0.06), rim=(0.76, 0.50, 0.32),
    leg=(0.55, 0.26, 0.15), leg_dark=(0.34, 0.14, 0.08), spine=(0.90, 0.74, 0.52),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
