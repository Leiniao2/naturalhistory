"""
Procedural Triarthrus eatoni (Late Ordovician olenid trilobite, New York; famous for the
pyritized specimens of Beecher's Trilobite Bed that keep their legs and antennae) for map
colonies (Swim style).

A small, flat, rather parallel-sided trilobite: a semicircular cephalon with a long,
parallel-sided glabella crossed by three pairs of furrows, tiny eyes, short genal angles;
a long thorax of fourteen narrow segments and a tiny pygidium. The long antennae and the
paired legs that peek out all round are what made it famous. Brassy gold, like the pyrite
the fossils are preserved in. Built with nh_ord_trilobite.py. Faces -Y, pivot at the
body centre.

Usage:
  blender --background --python tools/blender/triarthrus_eatoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TriarthrusEatoni.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402
import nh_dev_spiny as sp  # noqa: E402

SPEC = tri.Spec(
    name="TriarthrusEatoni",
    length=1.6, segments=14, ceph_frac=0.25, pyg_frac=0.07,
    ceph_w=0.44, thorax_w=0.43, thorax_w_back=0.30, pyg_w=0.16,
    ceph_p=2.2, ceph_q=2.0, pyg_p=2.0, pyg_q=2.0,
    dome=0.07, axis_frac=0.33, axis_h=0.07, pyg_axis=0.8, pyg_ribs=2,
    glab_w=0.34, glab_front=0.9, glab_len=0.88, glab_h=0.09, glab_furrows=3,
    eye_size=0.45, eye_x=0.6, eye_y=0.55, eye_h=0.02,
    genal_spine=0.06, genal_spread=0.05, border=0.10, rows_seg=3, antenna=0.0,
    shell=(0.62, 0.50, 0.24), shell_light=(0.86, 0.74, 0.42),
    axis=(0.74, 0.60, 0.30), groove=(0.28, 0.22, 0.10), under=(0.50, 0.40, 0.20),
    leg=(0.80, 0.66, 0.36),
)


def extras(mb, body):
    yf = body.y_front
    gold = (0.70, 0.56, 0.28)
    for sx in (-1, 1):
        # long, gently curving antennae, as in the pyritized fossils
        pts = [(sx * 0.07, yf + 0.06, -0.02), (sx * 0.12, yf - 0.12, -0.016), (sx * 0.22, yf - 0.34, -0.01),
               (sx * 0.36, yf - 0.52, -0.004), (sx * 0.52, yf - 0.62, 0.0)]
        mb.add(nh.tube(pts, [0.016, 0.013, 0.010, 0.007, 0.0], sides=5), gold)
        # extra leg tips under the cephalon and the pygidium
        for y in (body.y_front + 0.12, body.y_front + 0.25, body.y_back - 0.05):
            w = body.half_width(y)
            mb.add(nh.tube([(sx * (w - 0.08), y, -0.03), (sx * (w + 0.01), y + 0.01, -0.04),
                            (sx * (w + 0.06), y + 0.03, -0.055)], [0.013, 0.010, 0.0], sides=4), SPEC.leg)


if __name__ == "__main__":
    nh.run(lambda: sp.build(SPEC, extras), SPEC.name, **tri.VIEWS)
