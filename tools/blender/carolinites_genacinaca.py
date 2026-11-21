"""
Procedural Carolinites genacinaca (Early-Middle Ordovician telephinid trilobite, found
round the world) for map colonies (Swim style).

An open-water trilobite: a small cephalon almost taken over by two huge, bulging,
kidney-shaped compound eyes that wrap round its sides and gave it near all-round vision; a
narrow, swollen glabella between them, short genal spines, a thorax of thirteen narrow,
slightly spined segments and a small pygidium. Pale, translucent grey-tan, darker eyes
with a lattice of lenses. Built with nh_ord_trilobite.py (+ nh_dev_spiny extras). Faces -Y,
pivot at the body centre.

Usage:
  blender --background --python tools/blender/carolinites_genacinaca.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CarolinitesGenacinaca.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402
import nh_dev_spiny as sp  # noqa: E402

SPEC = tri.Spec(
    name="CarolinitesGenacinaca",
    length=1.5, segments=13, ceph_frac=0.30, pyg_frac=0.12,
    ceph_w=0.46, thorax_w=0.44, thorax_w_back=0.26, pyg_w=0.22,
    ceph_p=2.0, ceph_q=2.0,
    dome=0.08, axis_frac=0.32, axis_h=0.08, pyg_ribs=3,
    glab_w=0.30, glab_front=1.35, glab_len=0.95, glab_h=0.15, glab_furrows=0,
    eye_size=0.0, genal_spine=0.22, genal_spread=0.25, genal_r=0.03,
    pleural_spine=0.06, pleural_back=0.75, pleural_r=0.018,
    border=0.06, rows_seg=3, antenna=0.16,
    shell=(0.62, 0.56, 0.46), shell_light=(0.82, 0.77, 0.66),
    axis=(0.54, 0.46, 0.36), groove=(0.26, 0.22, 0.17), under=(0.55, 0.50, 0.42),
)


def extras(mb, body):
    y_eye = body.y_ceph - 0.55 * (body.y_ceph - body.y_front)
    for sx in (-1, 1):
        x = sx * body.half_width(y_eye) * 0.72
        c = (x, y_eye, body.height(x, y_eye) + 0.01)

        def col(co, n, sx=sx):
            # hexagonal-ish lens lattice on a dark eye
            k = 0.5 + 0.25 * (math.sin(co.y * 140) + math.sin((co.z + co.x * sx) * 140))
            base = (0.10, 0.09, 0.08) if n.x * sx > -0.2 else (0.30, 0.27, 0.22)
            return nh.lerp(base, (0.34, 0.30, 0.22), 0.6 * nh.smoothstep(0.75, 1.0, k))
        mb.add(nh.uv_ellipsoid(c, (0.13, 0.20, 0.11), 20, 12), col)


if __name__ == "__main__":
    nh.run(lambda: sp.build(SPEC, extras), SPEC.name, **tri.VIEWS)
