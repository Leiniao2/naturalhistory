"""
Procedural Terataspis grandis for the map: the giant lichid trilobite of the Middle
Devonian (Eifelian, about 390 million years ago) Onondaga Limestone of New York and
Ontario, one of the largest trilobites known at up to about 60 cm long.

A broad, flattish lichid: a semicircular cephalon with a big, lobed glabella, long
genal spines, a thorax of about ten segments each ending in a backward-curving pleural
spine with a short spine on its axial ring, and a large, wide pygidium fringed with
paired marginal spines. The whole dorsal shell was covered in tubercles and small
spines.

Built with nh_dev_spiny.py (nh_ord_trilobite shell) plus tubercles and axial spines.
Colours are unknown: warm brown with paler tubercles. Faces -Y, pivot at the body
centre (Swim style).

Usage:
  blender --background --python tools/blender/terataspis_grandis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Terataspis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dev_spiny as sp  # noqa: E402

SHELL = (0.42, 0.27, 0.15)
LIGHT = (0.66, 0.48, 0.30)
TUBER = (0.62, 0.44, 0.27)

SPEC = sp.tri.Spec(
    name="Terataspis",
    length=1.3, segments=10, ceph_frac=0.30, pyg_frac=0.26,
    ceph_w=0.52, thorax_w=0.48, thorax_w_back=0.40, pyg_w=0.44,
    ceph_p=1.8, ceph_q=2.2, pyg_p=1.6, pyg_q=1.8,
    dome=0.07, axis_frac=0.30, axis_h=0.07, pyg_axis=0.55, pyg_ribs=3,
    glab_w=0.36, glab_front=1.35, glab_len=0.95, glab_h=0.12, glab_furrows=2,
    eye_size=0.8, eye_x=0.58, eye_y=0.35, eye_h=0.04,
    genal_spine=0.55, genal_spread=0.30, genal_r=0.035,
    pleural_spine=0.22, pleural_grow=0.05, pleural_back=0.62, pleural_r=0.022,
    pyg_spines=[(0.40, 0.40, 0.30), (0.78, 0.34, 0.80), (0.12, 0.30, 0.08)],
    border=0.10, rows_seg=4,
    shell=SHELL, shell_light=LIGHT, axis=(0.36, 0.22, 0.12),
    groove=(0.15, 0.09, 0.05), under=(0.34, 0.24, 0.15),
)


def extras(mb, body):
    sp.tubercles(mb, body, 260, 0.011, TUBER, seed=7)
    sp.axial_spines(mb, body, 0.07, 0.015, LIGHT, lean=0.25)
    # a pair of spines on the occipital ring and on the glabellar lobes
    for sx in (-1, 1):
        for (fx, fy, L) in ((0.10, body.y_ceph - 0.05, 0.12), (0.16, body.y_ceph - 0.20, 0.08)):
            z = body.height(sx * fx, fy)
            mb.add(sp.tri.spine((sx * fx, fy, z - 0.01), (sx * (fx + 0.03), fy + 0.06, z + L), 0.018, flat=1.0),
                   LIGHT)


if __name__ == "__main__":
    nh.run(lambda: sp.build(SPEC, extras), SPEC.name, **sp.VIEWS)
