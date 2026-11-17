"""
Procedural Encrinurus punctatus (mid-Silurian "strawberry-headed" trilobite from the
Wenlock Limestone of England and Gotland, about 5 cm long) for map colonies.

A cephalon and club-shaped glabella covered in coarse tubercles, small eyes raised on
short stalks, short genal spines, twelve thoracic segments with blunt pleural tips and
a long triangular pygidium whose axis carries many more rings than the pleural fields
have ribs. Reddish-tan. Built with nh_sil_trilobite.py.
Faces -Y, pivot at the body centre (Swim style, like the other trilobites).

Usage:
  blender --background --python tools/blender/encrinurus_punctatus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EncrinurusPunctatus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_trilobite as tr  # noqa: E402

SPEC = tr.Spec(
    name="EncrinurusPunctatus",
    segments=12, ceph_frac=0.30, pyg_frac=0.30, W=0.46, thorax_w=0.42, thorax_w_back=0.34, pyg_w=0.34,
    ceph_p=2.2, ceph_q=1.8, pyg_p=1.3, pyg_q=1.1, dome=0.10, glab_front=0.17, glab_back=0.12, glab_h=0.10,
    glab_len=0.95, glab_furrows=2, axis_w=0.14, axis_h=0.06, eye="stalk", eye_x=0.27, eye_y=0.40, eye_size=1.0,
    genal_spine=0.12, pleural_tips=0.02, pyg_rings=16, pyg_ribs=6, tubercles=70,
    shell=(0.58, 0.38, 0.24), shell_light=(0.80, 0.62, 0.44), axis=(0.50, 0.30, 0.18), groove=(0.22, 0.13, 0.08),
)

if __name__ == "__main__":
    nh.run(lambda: tr.build(SPEC), SPEC.name, **tr.VIEWS)
