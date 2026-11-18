"""
Procedural Parabarrandia crassa (Middle Ordovician asaphid trilobite of Bohemia and Iberia) for
map colonies (Swim style).

A streamlined, torpedo-shaped open-water trilobite: a long, narrow, smooth (effaced) and
strongly vaulted shield, with a bullet-shaped cephalon, very large eyes spread over the cheeks,
no spines, eight narrow thoracic segments and a long tapering pygidium. Built for swimming
rather than crawling. Pale, countershaded grey (colour conjectural). Built with
nh_ord_trilobite.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/parabarrandia_crassa.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ParabarrandiaCrassa.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="ParabarrandiaCrassa",
    length=1.8, segments=8, ceph_frac=0.36, pyg_frac=0.30,
    ceph_w=0.30, thorax_w=0.29, thorax_w_back=0.24, pyg_w=0.23,
    ceph_p=1.7, ceph_q=1.4, pyg_p=1.4, pyg_q=1.2,
    dome=0.15, axis_frac=0.42, axis_h=0.03, pyg_axis=0.85, pyg_ribs=0,
    glab_w=0.45, glab_front=1.15, glab_len=0.9, glab_h=0.04,
    eye_size=1.7, eye_x=0.72, eye_y=0.45, eye_h=0.05,
    border=0.05, antenna=0.16, legs=True,
    shell=(0.46, 0.48, 0.50), shell_light=(0.76, 0.77, 0.74),
    axis=(0.38, 0.40, 0.42), groove=(0.22, 0.23, 0.25), under=(0.80, 0.78, 0.72),
    eye=(0.08, 0.10, 0.12),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
