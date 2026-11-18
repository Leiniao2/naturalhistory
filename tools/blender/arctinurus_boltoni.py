"""
Procedural Arctinurus boltoni (mid-Silurian lichid trilobite from the Rochester Shale of
New York, up to about 18 cm long) for map colonies (Swim style).

One of the largest, broadest Silurian trilobites: a very wide, flat, heavily tuberculate
exoskeleton; a cephalon with a large, swollen, lobed glabella, small eyes and short genal
spines; eleven thoracic segments whose pleurae end in broad, flat, backward-curving
spines; and a big pygidium fringed with three pairs of broad, flattened marginal spines.
Warm red-brown with pale tubercles. Built with nh_sil_trilobite.py (+ pygidial spines via
nh_sil_extra). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/arctinurus_boltoni.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArctinurusBoltoni.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_sil_trilobite as tr  # noqa: E402
import nh_sil_extra as ex  # noqa: E402

SPEC = tr.Spec(
    name="ArctinurusBoltoni",
    length=1.2, segments=11, ceph_frac=0.28, pyg_frac=0.25, W=0.62, thorax_w=0.62, thorax_w_back=0.54, pyg_w=0.50,
    ceph_p=2.0, ceph_q=2.2, pyg_p=1.6, pyg_q=1.3, dome=0.06, glab_front=0.22, glab_back=0.15, glab_h=0.11,
    glab_len=0.95, glab_furrows=2, axis_w=0.15, axis_h=0.06, eye="small", eye_x=0.36, eye_y=0.45, eye_size=0.9,
    genal_spine=0.16, pleural_tips=0.22, pyg_rings=4, pyg_ribs=3, tubercles=140, antenna=0.12,
    shell=(0.54, 0.30, 0.18), shell_light=(0.82, 0.62, 0.44), axis=(0.46, 0.24, 0.14), groove=(0.20, 0.10, 0.06),
    under=(0.44, 0.28, 0.18), leg=(0.58, 0.40, 0.26),
)


def pyg_spines(mb):
    s = SPEC
    yb = s.length / 2
    yp = yb - s.length * s.pyg_frac
    for t, L, out in ((0.25, 0.20, 0.55), (0.55, 0.22, 0.35), (0.85, 0.20, 0.12)):
        y = yp + (yb - yp) * t
        w = s.pyg_w * max(0.0, 1.0 - t ** s.pyg_p) ** (1.0 / s.pyg_q)
        for sx in (-1, 1):
            b0 = Vector((sx * (w * 0.85), y - 0.03, 0.0))
            tip = b0 + Vector((sx * L * out, L, -0.01))
            mb.add(nh.tube([b0, b0.lerp(tip, 0.5) + Vector((sx * 0.01, 0, 0)), tip], [0.05, 0.03, 0.0],
                           sides=6, scale_xy=(1.0, 0.35)), s.shell)


if __name__ == "__main__":
    nh.run(lambda: ex.with_extras(lambda: tr.build(SPEC), pyg_spines), SPEC.name, **tr.VIEWS)
