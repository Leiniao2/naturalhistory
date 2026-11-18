"""
Procedural Carcinosoma newlini (Late Silurian carcinosomatid sea scorpion from the
Přídolí of Indiana, about 90 cm long) for map colonies (Swim style).

A broad, flat, almost round preabdomen behind a small, wide prosoma with kidney-shaped
eyes; a narrow, cylindrical postabdomen held arched up behind it, ending in a long,
slightly flattened spike-like telson; and robust, forward-reaching walking legs armed
with long curved spines (two per joint), used as a cage to trap prey. Dark red-brown
with pale spots. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/carcinosoma_newlini.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CarcinosomaNewlini.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="CarcinosomaNewlini",
    y_front=-0.66, y_pro=-0.42, pro_wf=0.17, pro_wb=0.21, pro_round=0.5, pro_h=0.055,
    pre_len=0.60, pre_w=[0.26, 0.31, 0.33, 0.33, 0.30, 0.24, 0.16], pre_h=0.065,
    post_len=0.55, post_w=[0.075, 0.068, 0.062, 0.058, 0.055], post_round=1.0,
    curl=45, curl_start=0.2, telson="spike", telson_len=0.36, telson_w=0.04,
    eye="kidney", eye_x=0.55, eye_y=0.32, eye_size=1.0, chelicera="small",
    legs=[L(0.10, 0.36, -65, 2, 0.07, 0.024), L(0.28, 0.42, -50, 2, 0.08, 0.025),
          L(0.48, 0.44, -30, 2, 0.08, 0.026), L(0.70, 0.30, 15, 1, 0.04, 0.022),
          L(0.90, 0.22, 10, 0, 0.0, 0.030, paddle=0.28)],
    shell=(0.40, 0.18, 0.12), shell_dark=(0.20, 0.08, 0.05), rim=(0.70, 0.46, 0.32), pattern="spots",
    leg=(0.50, 0.26, 0.16), leg_dark=(0.28, 0.12, 0.07), spine=(0.90, 0.72, 0.52),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
