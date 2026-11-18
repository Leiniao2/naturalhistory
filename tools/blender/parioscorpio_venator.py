"""
Procedural Parioscorpio venator (Early Silurian scorpion from the Waukesha biota of
Wisconsin, about 2.5 cm long, about 437 million years old) for map colonies (Swim style:
it lived in shallow water at the shore).

One of the oldest known scorpions: a short, squarish carapace with a pair of large,
bulging compound eyes near the front, big grasping pedipalp pincers, raptorial front
legs, a broad seven-segmented mesosoma and a slim tail curled over the back ending in a
large venom bulb with a curved sting. Glossy black-brown with an amber tail. Built with
nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/parioscorpio_venator.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ParioscorpioVenator.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="ParioscorpioVenator",
    y_front=-0.52, y_pro=-0.28, pro_wf=0.13, pro_wb=0.16, pro_round=0.15, pro_h=0.055,
    pre_len=0.46, pre_w=[0.17, 0.185, 0.19, 0.19, 0.18, 0.16, 0.12], pre_h=0.065,
    post_len=0.58, post_w=[0.075, 0.07, 0.066, 0.064, 0.064], post_round=0.95,
    curl=170, curl_start=0.0, telson="sting", telson_len=0.16, telson_w=0.085,
    eye="kidney", eye_x=0.45, eye_y=0.22, eye_size=1.3, chelicera="small", pedipalp=0.36,
    legs=[L(0.30, 0.34, -35, 2, 0.03, 0.020), L(0.50, 0.33, -5, 0, 0, 0.020),
          L(0.70, 0.35, 15, 0, 0, 0.021), L(0.90, 0.37, 35, 0, 0, 0.022)],
    shell=(0.16, 0.11, 0.07), shell_dark=(0.06, 0.04, 0.03), rim=(0.62, 0.42, 0.18),
    under=(0.50, 0.36, 0.20), leg=(0.48, 0.32, 0.14), leg_dark=(0.22, 0.14, 0.07),
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
