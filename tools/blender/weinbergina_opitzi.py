"""
Procedural Weinbergina opitzi (Early Devonian, Hunsrueck Slate, Germany) for map colonies
(Swim style, a seabed crawler like the other horseshoe-crab relatives).

A horseshoe-crab-like synziphosurine about 10 cm long: a broad, semicircular, smoothly
vaulted head shield with small eye tubercles, a wide abdomen of ten free segments narrowing
into a short tail and a long spike-like telson. Pyritised Hunsrueck fossils show its walking
legs, which reach out beyond the head shield. Olive-brown with paler rims. Built with
nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/weinbergina_opitzi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Weinbergina.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402
import nh_sil_extra as ex  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="Weinbergina",
    y_front=-0.70, y_pro=-0.18, pro_wf=0.46, pro_wb=0.50, pro_round=1.0, pro_h=0.11,
    pre_len=0.50, pre_w=[0.38, 0.36, 0.33, 0.30, 0.26, 0.22, 0.18], pre_h=0.06,
    post_len=0.18, post_w=[0.10, 0.08, 0.065], post_round=0.7,
    telson="spike", telson_len=0.48, telson_w=0.026,
    eye="tubercle", eye_y=0.32, eye_size=0.8, chelicera="small",
    legs=[L(0.30, 0.42, -55, 1, 0.025, 0.016), L(0.45, 0.46, -35, 1, 0.025, 0.017),
          L(0.60, 0.48, -12, 1, 0.025, 0.017), L(0.75, 0.48, 12, 1, 0.025, 0.018),
          L(0.90, 0.46, 35, 2, 0.025, 0.018)],
    shell=(0.44, 0.38, 0.22), shell_dark=(0.26, 0.21, 0.12), rim=(0.74, 0.66, 0.44),
    under=(0.66, 0.58, 0.42), leg=(0.58, 0.48, 0.30), leg_dark=(0.36, 0.28, 0.16),
)


def extras(mb):
    """Small paired lateral eye bumps on the head shield."""
    b = eu.Body(SPEC)
    for sx in (1, -1):
        y = SPEC.y_front + b.L * 0.45
        x = sx * b.pro_w(y) * 0.62
        mb.add(nh.ellipsoid((x, y, b.pro_height(x, y) + 0.004), (0.018, 0.03, 0.010), 2), (0.20, 0.16, 0.10))


if __name__ == "__main__":
    nh.run(lambda: ex.with_extras(lambda: eu.build(SPEC), extras), SPEC.name, **eu.VIEWS)
