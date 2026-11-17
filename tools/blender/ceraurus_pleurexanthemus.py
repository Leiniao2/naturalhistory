"""
Procedural Ceraurus pleurexanthemus (Middle-Late Ordovician cheirurid trilobite of New
York and Ontario, famous from the Walcott-Rust Quarry where its legs are preserved) for
map colonies (Swim style).

A cheirurid: a strongly vaulted glabella that widens forward, cut by three pairs of
lateral furrows; small eyes; long genal spines curving back; eleven thoracic segments
whose pleurae end in short, backward-curving spine tips; and a small pygidium bearing a
pair of long spines. Warm brown shell with paler tubercles (colour conjectural).
Built with nh_ord_trilobite.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/ceraurus_pleurexanthemus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/CeraurusPleurexanthemus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="CeraurusPleurexanthemus",
    length=1.4, segments=11, ceph_frac=0.30, pyg_frac=0.10,
    ceph_w=0.50, thorax_w=0.44, thorax_w_back=0.34, pyg_w=0.26,
    ceph_p=1.8, ceph_q=2.2, pyg_p=1.6, pyg_q=1.6,
    dome=0.08, axis_frac=0.34, axis_h=0.08, pyg_axis=0.7, pyg_ribs=2,
    glab_w=0.30, glab_front=1.45, glab_len=0.92, glab_h=0.13, glab_furrows=3,
    eye_size=0.6, eye_x=0.62, eye_y=0.5, eye_h=0.03,
    genal_spine=0.45, genal_spread=0.25, genal_r=0.035,
    pleural_spine=0.10, pleural_grow=0.05, pleural_back=0.75, pleural_r=0.02,
    pyg_spines=[(0.65, 0.55, 0.12)], border=0.1, rows_seg=3,
    shell=(0.52, 0.32, 0.18), shell_light=(0.74, 0.54, 0.34),
    axis=(0.70, 0.48, 0.28), groove=(0.20, 0.11, 0.06), under=(0.44, 0.30, 0.20),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
