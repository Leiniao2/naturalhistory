"""
Procedural Onychopterella augusti (Late Ordovician eurypterid of the Soom Shale, South
Africa, known from exceptionally preserved soft parts) for map colonies (Swim style).

A slender, smooth sea scorpion about 15 cm long: a rounded-square prosoma with small
kidney-shaped eyes near the middle, three pairs of short, spiny front legs for grasping
prey, a long, plain walking leg (V), and a pair of large swimming paddles (VI) that end
in a claw-like spine (the "claw-wing" of its name); a narrow, tapering body of seven
preabdominal and five postabdominal segments and a long, spike-like telson. Dark olive-
brown. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/onychopterella_augusti.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OnychopterellaAugusti.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec

SPEC = eu.Spec(
    name="OnychopterellaAugusti",
    y_front=-0.74, y_pro=-0.48, pro_wf=0.12, pro_wb=0.13, pro_round=0.30, pro_h=0.045,
    pre_len=0.64, pre_w=[0.135, 0.15, 0.155, 0.15, 0.14, 0.12, 0.10], pre_h=0.05,
    post_len=0.46, post_w=[0.07, 0.062, 0.056, 0.050, 0.046], telson="spike", telson_len=0.50, telson_w=0.024,
    eye="kidney", eye_x=0.45, eye_y=0.42, eye_size=0.7, chelicera="small",
    legs=[L(0.15, 0.20, -55, 3, 0.05, 0.016), L(0.32, 0.24, -35, 3, 0.05, 0.017),
          L(0.50, 0.26, -12, 3, 0.05, 0.018), L(0.70, 0.36, 25, 0, 0.0, 0.018),
          L(0.88, 0.22, 12, 0, 0.0, 0.026, paddle=0.36)],
    shell=(0.30, 0.28, 0.17), shell_dark=(0.16, 0.15, 0.09), rim=(0.56, 0.52, 0.34),
    under=(0.58, 0.54, 0.38), leg=(0.40, 0.36, 0.22), leg_dark=(0.24, 0.21, 0.12), spine=(0.76, 0.70, 0.50),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
