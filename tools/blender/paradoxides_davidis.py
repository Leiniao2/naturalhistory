"""
Procedural Paradoxides davidis (middle Cambrian giant paradoxidid trilobite, up to ~37 cm).

Long, flat, spiny trilobite: broad cephalon with a large glabella that widens forward,
long crescent eyes and long genal spines sweeping back past mid-body; about twenty
thoracic segments whose pleurae end in backswept spines lengthening towards the rear;
a tiny plate-like pygidium. Reddish brown shell with a paler axis.
Built with nh_ord_trilobite.py. Faces -Y, pivot at the body centre (Swim).

Output: Assets/Resources/Models/Species/Paradoxides.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="Paradoxides",
    length=1.9, segments=19, ceph_frac=0.26, pyg_frac=0.05,
    ceph_w=0.50, thorax_w=0.46, thorax_w_back=0.20, pyg_w=0.10,
    ceph_p=2.2, ceph_q=1.8, pyg_p=1.5, pyg_q=1.5,
    dome=0.05, axis_frac=0.28, axis_h=0.06, pyg_axis=0.6, pyg_ribs=1,
    glab_w=0.26, glab_front=1.8, glab_len=0.92, glab_h=0.10, glab_furrows=3,
    eye_size=1.1, eye_x=0.55, eye_y=0.45,
    genal_spine=0.75, genal_spread=0.05, genal_r=0.035,
    pleural_spine=0.16, pleural_grow=0.06, pleural_back=0.75,
    border=0.08, antenna=0.30, rows_seg=3, rows_ceph=16,
    shell=(0.46, 0.27, 0.18), shell_light=(0.66, 0.46, 0.32),
    axis=(0.58, 0.38, 0.24), groove=(0.22, 0.12, 0.08), under=(0.45, 0.32, 0.22),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
