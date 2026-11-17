"""
Procedural Proscorpius osborni (Late Silurian scorpion from the Bertie Group of New
York, about 4 cm long) for map colonies (Swim style; it may have lived in water).

Scorpion body plan: a squarish carapace with a median eye tubercle and tiny lateral
eye clusters, a pair of stout pedipalps ending in pincers, four pairs of walking legs,
a seven-segmented mesosoma and a narrow five-segmented metasoma curled up over the
back ending in a bulbous telson with a curved sting. Dark glossy brown. Built with
nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/proscorpius_osborni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProscorpiusOsborni.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="ProscorpiusOsborni",
    y_front=-0.55, y_pro=-0.30, pro_wf=0.12, pro_wb=0.16, pro_round=0.08, pro_h=0.05,
    pre_len=0.50, pre_w=[0.165, 0.175, 0.18, 0.18, 0.175, 0.16, 0.12], pre_h=0.06,
    post_len=0.62, post_w=[0.07, 0.066, 0.063, 0.060, 0.060], post_round=0.95,
    curl=165, curl_start=0.0, telson="sting", telson_len=0.14, telson_w=0.06,
    eye="tubercle", eye_y=0.35, eye_size=1.1, chelicera="small", pedipalp=0.30,
    legs=[L(0.30, 0.30, -25, 0, 0, 0.020), L(0.50, 0.33, -5, 0, 0, 0.021),
          L(0.70, 0.36, 15, 0, 0, 0.022), L(0.90, 0.38, 35, 0, 0, 0.023)],
    shell=(0.30, 0.20, 0.11), shell_dark=(0.14, 0.09, 0.05), rim=(0.52, 0.38, 0.22),
    under=(0.55, 0.42, 0.26), leg=(0.42, 0.30, 0.16), leg_dark=(0.26, 0.17, 0.09),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
