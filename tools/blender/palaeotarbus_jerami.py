"""
Procedural Palaeotarbus jerami (Late Silurian trigonotarbid arachnid from Ludford Lane,
Shropshire, England, one of the oldest land animals known, a few mm long) for map
colonies (Ground style).

Trigonotarbids were spider-like arachnids without silk glands or venom: a
subtriangular carapace with a median eye tubercle, small chelicerae and leg-like
pedipalps, four pairs of long walking legs and a rounded, flattened opisthosoma
armoured with tergites split into median and lateral plates. Dark brown. Built with
nh_sil_eurypterid.py. Faces -Y, pivot on the ground (feet at z = 0).

Usage:
  blender --background --python tools/blender/palaeotarbus_jerami.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PalaeotarbusJerami.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="PalaeotarbusJerami",
    mode="ground", leg_lift=0.10,
    y_front=-0.50, y_pro=-0.15, pro_wf=0.06, pro_wb=0.20, pro_round=0.25, pro_h=0.06,
    pre_len=0.62, pre_w=[0.24, 0.27, 0.28, 0.27, 0.24, 0.19, 0.12, 0.05], pre_h=0.07,
    post_len=0.0, post_w=[], telson="none", telson_len=0.0,
    eye="tubercle", eye_y=0.30, eye_size=1.0, chelicera="small", body_dark_line=True, tubercles=0.35,
    legs=[L(0.10, 0.25, -60, 0, 0, 0.018), L(0.30, 0.50, -40, 0, 0, 0.022), L(0.50, 0.55, -15, 0, 0, 0.022),
          L(0.70, 0.55, 15, 0, 0, 0.022), L(0.90, 0.62, 45, 0, 0, 0.023)],
    shell=(0.30, 0.22, 0.14), shell_dark=(0.14, 0.10, 0.06), rim=(0.48, 0.38, 0.26),
    under=(0.42, 0.34, 0.24), leg=(0.38, 0.28, 0.17), leg_dark=(0.24, 0.17, 0.10),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.GROUND_VIEWS)
