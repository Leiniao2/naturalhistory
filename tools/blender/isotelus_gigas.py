"""
Procedural Isotelus gigas (Middle-Late Ordovician asaphid trilobite, type species of Isotelus)
for map colonies.

Smaller and flatter than I. maximus: a narrower outline (width a little over half
the length), a broadly subtriangular cephalon and pygidium with more angular
margins, angular genal corners but no genal spines (adults lose them), a low
vault with low-set eyes, and the usual smooth "effaced" shields around an
eight-segment thorax. Greyish tan (colour is conjectural). Built with nh_isotelus.py.
Faces -Y, pivot at the body centre (Swim style, like Redlichia).

Usage:
  blender --background --python tools/blender/isotelus_gigas.py -- [--render out.png]

Output: Assets/Resources/Models/Species/IsotelusGigas.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_isotelus as iso  # noqa: E402

SPEC = iso.Spec(
    name="IsotelusGigas",
    ceph_frac=0.35, pyg_frac=0.35,
    ceph_w=0.44, thorax_w=0.41, thorax_w_back=0.39, pyg_w=0.41,
    ceph_p=1.3, ceph_q=1.7, pyg_p=1.3, pyg_q=1.7,
    dome=0.075, axis_h=0.04, eye_h=0.025, eye_size=0.9, genal_angle=0.05,
    shell=(0.50, 0.44, 0.34), shell_light=(0.70, 0.64, 0.52),
    axis=(0.38, 0.33, 0.25), groove=(0.18, 0.15, 0.11), under=(0.40, 0.36, 0.29),
    leg=(0.52, 0.44, 0.32),
)


if __name__ == "__main__":
    nh.run(lambda: iso.build(SPEC), "IsotelusGigas", views=((30, 40), (0, 85), (-90, 12)))
