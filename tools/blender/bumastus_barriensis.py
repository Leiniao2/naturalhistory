"""
Procedural Bumastus barriensis (a smooth, rounded illaenid trilobite, about 8-10 cm long,
from the Wenlock Limestone of Dudley and the Silurian reefs of England) for map
colonies.

The "smooth trilobite": its shell is so effaced that the head and tail shields are
almost featureless, highly vaulted domes, with no visible glabella or tail rings; big
crescent eyes far back on the head; a short thorax of ten segments with a very wide
axis; a large, rounded, smooth tail shield as big as the head. It lived nestled in the
reef, head and tail curled for protection. Built with nh_sil_trilobite.py.
Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/bumastus_barriensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BumastusBarriensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_trilobite as tr  # noqa: E402

SPEC = tr.Spec(
    name="BumastusBarriensis",
    length=1.5, segments=10, ceph_frac=0.38, pyg_frac=0.36, W=0.50, thorax_w=0.50, thorax_w_back=0.48, pyg_w=0.48,
    ceph_p=2.4, ceph_q=2.0, pyg_p=2.2, pyg_q=1.8, dome=0.18, glab_front=0.16, glab_back=0.16, glab_h=0.0,
    glab_len=0.5, glab_furrows=0, axis_w=0.27, axis_h=0.05, eye="small", eye_x=0.33, eye_y=0.30, eye_size=1.5,
    pyg_rings=0, pyg_ribs=0, antenna=0.10,
    shell=(0.62, 0.50, 0.36), shell_light=(0.82, 0.72, 0.56), axis=(0.56, 0.44, 0.31), groove=(0.30, 0.22, 0.14),
)

if __name__ == "__main__":
    nh.run(lambda: tr.build(SPEC), SPEC.name, **tr.VIEWS)
