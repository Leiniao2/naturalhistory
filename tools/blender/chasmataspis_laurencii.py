"""
Procedural Chasmataspis laurencii (Middle Ordovician chasmataspidid, Tennessee, the oldest
known member of its group) for map colonies (Swim style).

A small horseshoe-crab-like chelicerate a few centimetres long: a broad, semicircular
head shield with small eyes on top; behind it a short, wide "buckler" of three fused
segments, then a narrow, tapering tail of nine ring-like segments ending in a short spine.
Walking legs with a few spines splay out under the head shield. Sandy brown with a darker
buckler. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/chasmataspis_laurencii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ChasmataspisLaurencii.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec

SPEC = eu.Spec(
    name="ChasmataspisLaurencii",
    y_front=-0.72, y_pro=-0.22, pro_wf=0.36, pro_wb=0.36, pro_round=1.0, pro_h=0.07,
    pre_len=0.30, pre_w=[0.33, 0.31, 0.26], pre_h=0.06,
    post_len=0.62, post_w=[0.13, 0.115, 0.10, 0.09, 0.08, 0.07, 0.062, 0.055, 0.048],
    post_round=0.7, telson="spike", telson_len=0.20, telson_w=0.024,
    eye="tubercle", eye_y=0.35, eye_size=0.9, chelicera="small",
    legs=[L(0.20, 0.20, -50, 1, 0.03, 0.020), L(0.38, 0.24, -25, 1, 0.03, 0.021),
          L(0.56, 0.26, 0, 1, 0.03, 0.022), L(0.72, 0.27, 25, 1, 0.03, 0.022),
          L(0.86, 0.24, 45, 0, 0.0, 0.024)],
    shell=(0.52, 0.40, 0.24), shell_dark=(0.32, 0.22, 0.12), rim=(0.74, 0.62, 0.42),
    under=(0.66, 0.56, 0.40), leg=(0.56, 0.44, 0.28), leg_dark=(0.36, 0.26, 0.15), spine=(0.80, 0.70, 0.50),
    tubercles=0.3,
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
