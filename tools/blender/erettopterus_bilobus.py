"""
Procedural Erettopterus bilobus (Early Silurian pterygotid sea scorpion from Lesmahagow,
Scotland, about 70 cm long) for map colonies (Swim style).

A lighter, more streamlined relative of Pterygotus: small prosoma with large marginal
eyes, long but slender chelicerae with small curved teeth, broad swimming paddles, a
smooth tapering opisthosoma and the genus' hallmark, a wide, flat telson split at its tip
into two rounded lobes (a tail fin for fast swimming). Pale sandy grey with dark spots.
Built with nh_sil_eurypterid.py; the bilobed telson is added via nh_sil_extra.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/erettopterus_bilobus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ErettopterusBilobus.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402
import nh_sil_extra as ex  # noqa: E402

L = eu.LegSpec
SPEC = eu.Spec(
    name="ErettopterusBilobus",
    y_front=-0.80, y_pro=-0.54, pro_wf=0.14, pro_wb=0.17, pro_round=0.30, pro_h=0.045,
    pre_len=0.72, pre_w=[0.18, 0.20, 0.21, 0.205, 0.19, 0.165, 0.135], pre_h=0.05,
    post_len=0.40, post_w=[0.10, 0.088, 0.078, 0.07, 0.066], telson="none",
    eye="marginal", eye_x=0.84, eye_y=0.12, eye_size=1.2, chelicera="giant", claw_len=0.30,
    legs=[L(0.15, 0.18, -45, 0, 0, 0.015), L(0.35, 0.20, -25, 0, 0, 0.016),
          L(0.55, 0.22, 0, 0, 0, 0.017), L(0.72, 0.24, 20, 0, 0, 0.018),
          L(0.90, 0.26, 5, 0, 0.0, 0.036, paddle=0.44)],
    shell=(0.58, 0.54, 0.44), shell_dark=(0.30, 0.27, 0.21), rim=(0.80, 0.76, 0.64), pattern="spots",
    under=(0.78, 0.74, 0.64), leg=(0.56, 0.50, 0.40), leg_dark=(0.34, 0.30, 0.23),
)


def telson(mb):
    b = eu.Body(SPEC)
    y0 = b.y_post - 0.02
    half = [(0.04, 0.0), (0.075, 0.06), (0.11, 0.14), (0.13, 0.22), (0.125, 0.29), (0.10, 0.34),
            (0.07, 0.355), (0.045, 0.33), (0.02, 0.27), (0.0, 0.24)]
    outline = [(x, y0 + y, 0.0) for x, y in half] + [(-x, y0 + y, 0.0) for x, y in reversed(half[:-1])]
    s = SPEC
    mb.add(nh.flat_panel(outline, thickness=0.016),
           lambda co, n: (nh.lerp(s.shell, s.rim, 0.7 * nh.smoothstep(0.06, 0.12, math.hypot(co.x, (co.y - y0 - 0.2) * 0.6)))
                          if n.z > -0.3 else s.under), smooth=False)
    mb.add(nh.tube([(0, y0, 0.006), (0, y0 + 0.12, 0.008), (0, y0 + 0.22, 0.004)], [0.014, 0.010, 0.0],
                   sides=6, scale_xy=(1.0, 0.5)), s.shell_dark)


if __name__ == "__main__":
    nh.run(lambda: ex.with_extras(lambda: eu.build(SPEC), telson), SPEC.name, **eu.VIEWS)
