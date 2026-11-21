"""
Procedural Elrathia kingii (middle Cambrian ptychopariid trilobite of the Wheeler Shale, Utah).

Small, broadly oval trilobite: wide semicircular cephalon with short genal points, a
small tapering glabella and small crescent eyes, thirteen short thoracic segments with
rounded pleural tips, and a tiny semicircular pygidium. Dark grey-brown shell.
Built with nh_ord_trilobite.py. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Elrathia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="Elrathia",
    length=1.5, segments=13, ceph_frac=0.33, pyg_frac=0.10,
    ceph_w=0.56, thorax_w=0.55, thorax_w_back=0.30, pyg_w=0.22,
    ceph_p=2.0, ceph_q=2.0, pyg_p=1.8, pyg_q=1.6,
    dome=0.07, axis_frac=0.28, axis_h=0.06, pyg_axis=0.7, pyg_ribs=2,
    glab_w=0.26, glab_front=0.7, glab_len=0.6, glab_h=0.08, glab_furrows=2,
    eye_size=0.7, eye_x=0.5, eye_y=0.5,
    genal_spine=0.12, genal_spread=0.1, border=0.16, antenna=0.22, rows_seg=3,
    shell=(0.30, 0.27, 0.25), shell_light=(0.50, 0.45, 0.40),
    axis=(0.24, 0.21, 0.19), groove=(0.12, 0.10, 0.09), under=(0.40, 0.34, 0.28),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
