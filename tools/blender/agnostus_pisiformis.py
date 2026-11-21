"""
Procedural Agnostus pisiformis (late Cambrian agnostid, under 1 cm).

Tiny blind isopygous arthropod: a rounded cephalon and a pygidium of almost the same
size and shape, with only two thoracic segments between them; a pear-shaped glabella and
a matching pygidial axis, a narrow rim round both shields. Slightly arched; pale
honey-brown. Built with nh_ord_trilobite.py. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Agnostus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="Agnostus",
    length=1.4, segments=2, ceph_frac=0.43, pyg_frac=0.43,
    ceph_w=0.46, thorax_w=0.44, thorax_w_back=0.44, pyg_w=0.46,
    ceph_p=2.0, ceph_q=2.0, pyg_p=2.0, pyg_q=2.0,
    dome=0.16, axis_frac=0.28, axis_h=0.06, pyg_axis=0.75, pyg_ribs=2,
    glab_w=0.22, glab_front=1.2, glab_len=0.75, glab_h=0.08, glab_furrows=1,
    eye_size=0.0, border=0.14, antenna=0.12, legs=True, rows_seg=5,
    shell=(0.70, 0.52, 0.30), shell_light=(0.86, 0.70, 0.46),
    axis=(0.58, 0.40, 0.22), groove=(0.30, 0.20, 0.10), under=(0.60, 0.46, 0.30),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
