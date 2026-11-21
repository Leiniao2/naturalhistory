"""
Procedural Brontoscorpio anglicus (a giant Late Silurian scorpion from Shropshire,
England, estimated at about 90 cm long from one huge pincer finger) for map colonies
(Swim style: like other early scorpions it probably still lived in water).

A heavy, dark scorpion: broad, low carapace with a central eye tubercle, massive,
swollen pedipalp pincers, four pairs of stout walking legs, a broad seven-segment
preabdomen and a thick five-segment tail curled up over the back ending in a big bulb
and curved sting. Built with nh_sil_eurypterid.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/brontoscorpio_anglicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BrontoscorpioAnglicus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402
import nh_sil_extra as sx  # noqa: E402
from mathutils import Vector  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="BrontoscorpioAnglicus",
    y_front=-0.55, y_pro=-0.28, pro_wf=0.14, pro_wb=0.19, pro_round=0.10, pro_h=0.055,
    pre_len=0.52, pre_w=[0.19, 0.205, 0.21, 0.21, 0.20, 0.18, 0.13], pre_h=0.065,
    post_len=0.58, post_w=[0.085, 0.082, 0.080, 0.078, 0.078], post_round=0.95,
    curl=160, curl_start=0.0, telson="sting", telson_len=0.18, telson_w=0.085,
    eye="tubercle", eye_y=0.40, eye_size=1.3, chelicera="small", pedipalp=0.42,
    legs=[L(0.30, 0.32, -25, 1, 0.02, 0.026), L(0.50, 0.35, -5, 1, 0.02, 0.027),
          L(0.70, 0.38, 15, 1, 0.02, 0.028), L(0.90, 0.40, 35, 1, 0.02, 0.029)],
    shell=(0.20, 0.15, 0.10), shell_dark=(0.09, 0.07, 0.05), rim=(0.42, 0.32, 0.20),
    under=(0.46, 0.36, 0.24), leg=(0.32, 0.24, 0.15), leg_dark=(0.16, 0.12, 0.08), tubercles=0.35,
)



def extras(mb):
    # swollen, heavy pincer palms (the genus is known from one huge pincer)
    P = SPEC.pedipalp
    for k in (1, -1):
        base = Vector((k * 0.06, SPEC.y_front + 0.05, -0.01))
        j2 = base + Vector((k * P * 0.40, -P * 0.65, 0.03))
        mb.add(nh.uv_ellipsoid(tuple(j2 + Vector((0, -P * 0.12, 0))), (0.065, 0.11, 0.05), 12, 8),
               lambda co, n: nh.lerp(SPEC.shell, SPEC.rim, 0.35 * max(0.0, n.z)))


if __name__ == "__main__":
    nh.run(lambda: sx.with_extras(lambda: eu.build(SPEC), extras), SPEC.name, **eu.VIEWS)
