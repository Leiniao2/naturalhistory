"""
Procedural Offacolus kingi (mid-Silurian chelicerate from the Herefordshire
Lagerstaette, England, about 5 mm long) for map colonies (Swim style).

A tiny early relative of horseshoe crabs and sea scorpions: a broad, horseshoe-shaped
head shield, almost as wide as long, with a small median eye mound; under it a ring of
short legs splaying out beyond the margin; a short, tapering opisthosoma of a few broad
segments and three narrow ones, ending in a slender spine-like telson. Pale orange-
brown. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/offacolus_kingi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OffacolusKingi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="OffacolusKingi",
    y_front=-0.62, y_pro=-0.12, pro_wf=0.32, pro_wb=0.34, pro_round=0.95, pro_h=0.09,
    pre_len=0.36, pre_w=[0.28, 0.25, 0.21, 0.17, 0.13], pre_h=0.06,
    post_len=0.20, post_w=[0.07, 0.06, 0.05], post_round=0.8,
    telson="spike", telson_len=0.45, telson_w=0.025,
    eye="tubercle", eye_y=0.35, eye_size=0.9, chelicera="small",
    legs=[L(0.20, 0.30, -60, 2, 0.03, 0.016), L(0.36, 0.33, -40, 2, 0.03, 0.017),
          L(0.52, 0.35, -15, 2, 0.03, 0.018), L(0.68, 0.36, 10, 2, 0.03, 0.018),
          L(0.84, 0.34, 35, 2, 0.03, 0.018)],
    shell=(0.62, 0.40, 0.20), shell_dark=(0.38, 0.22, 0.10), rim=(0.82, 0.64, 0.40),
    under=(0.78, 0.62, 0.42), leg=(0.70, 0.50, 0.30), leg_dark=(0.50, 0.32, 0.18),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
