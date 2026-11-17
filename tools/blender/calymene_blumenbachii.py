"""
Procedural Calymene blumenbachii (the "Dudley Bug", a mid-Silurian (Wenlock) trilobite
from the Wenlock Limestone of Dudley, England, about 6 cm long) for map colonies.

A semicircular cephalon without genal spines and a tall, bell-shaped glabella cut
into three pairs of rounded side lobes; small eyes on the cheeks; thirteen thoracic
segments with a strongly raised axis; a small rounded pygidium with six axial rings.
Grey-brown. Built with nh_sil_trilobite.py.
Faces -Y, pivot at the body centre (Swim style, like the other trilobites).

Usage:
  blender --background --python tools/blender/calymene_blumenbachii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CalymeneBlumenbachii.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_trilobite as tr  # noqa: E402

SPEC = tr.Spec(
    name="CalymeneBlumenbachii",
    segments=13, ceph_frac=0.30, pyg_frac=0.17, W=0.50, thorax_w=0.46, thorax_w_back=0.34, pyg_w=0.30,
    dome=0.10, glab_front=0.09, glab_back=0.19, glab_h=0.11, glab_len=0.88, glab_furrows=3, axis_w=0.17, axis_h=0.08,
    eye="small", eye_x=0.30, eye_y=0.45, eye_size=0.8, pyg_rings=6, pyg_ribs=5,
    shell=(0.46, 0.42, 0.36), shell_light=(0.66, 0.62, 0.54), axis=(0.38, 0.34, 0.28), groove=(0.16, 0.14, 0.11),
)

if __name__ == "__main__":
    nh.run(lambda: tr.build(SPEC), SPEC.name, **tr.VIEWS)
