"""
Procedural Selenopeltis buchii (Ordovician odontopleurid trilobite of Bohemia and the
Moroccan Anti-Atlas) for map colonies (Swim style).

A wide, flat, spiny odontopleurid: a short, broad cephalon with a narrow raised
glabella and small eyes on low stalks, long genal spines, nine thoracic segments each
drawn out into a very long, slender pleural spine sweeping back and outward (longer
towards the back), and a tiny pygidium with a fringe of spines. With its spines it is
about as wide as it is long. Dark brown shell (colour conjectural).
Built with nh_ord_trilobite.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/selenopeltis_buchii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SelenopeltisBuchii.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="SelenopeltisBuchii",
    length=1.1, segments=9, ceph_frac=0.30, pyg_frac=0.10,
    ceph_w=0.42, thorax_w=0.36, thorax_w_back=0.26, pyg_w=0.20,
    ceph_p=1.6, ceph_q=2.4, pyg_p=1.5, pyg_q=1.5,
    dome=0.05, axis_frac=0.36, axis_h=0.07, pyg_axis=0.6, pyg_ribs=1,
    glab_w=0.30, glab_front=0.85, glab_len=0.9, glab_h=0.08, glab_furrows=2,
    eye_size=0.7, eye_x=0.6, eye_y=0.4, eye_stalk=0.06,
    genal_spine=0.75, genal_spread=0.55, genal_r=0.03,
    pleural_spine=0.55, pleural_grow=0.12, pleural_back=0.72, pleural_r=0.018,
    pyg_spines=[(0.3, 0.35, 0.15), (0.7, 0.30, 0.45)], border=0.1, rows_seg=4,
    shell=(0.36, 0.24, 0.15), shell_light=(0.56, 0.40, 0.26),
    axis=(0.30, 0.19, 0.11), groove=(0.14, 0.09, 0.05), under=(0.32, 0.23, 0.16),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
