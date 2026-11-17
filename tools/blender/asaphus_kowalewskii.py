"""
Procedural Asaphus kowalewskii (Middle Ordovician asaphid trilobite from the St Petersburg
region, Russia) for map colonies (Swim style).

An asaphid with a broad semicircular cephalon and pygidium of similar size, eight
thoracic segments, a smooth, partly effaced glabella and short rounded genal angles -
and its famous compound eyes perched on top of very long, slender stalks rising
straight up from the cheeks, letting it watch while buried in the sediment.
Grey-brown shell (colour conjectural). Built with nh_ord_trilobite.py.
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/asaphus_kowalewskii.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AsaphusKowalewskii.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="AsaphusKowalewskii",
    length=1.5, segments=8, ceph_frac=0.34, pyg_frac=0.32,
    ceph_w=0.52, thorax_w=0.50, thorax_w_back=0.46, pyg_w=0.47,
    ceph_p=2.2, ceph_q=1.9, pyg_p=2.0, pyg_q=1.9,
    dome=0.10, axis_frac=0.32, axis_h=0.05, pyg_axis=0.75, pyg_ribs=0,
    glab_w=0.26, glab_front=1.25, glab_len=0.8, glab_h=0.05,
    eye_size=1.1, eye_x=0.52, eye_y=0.45, eye_h=0.02, eye_stalk=0.62,
    genal_spine=0.08, genal_spread=0.0, border=0.08,
    shell=(0.40, 0.33, 0.26), shell_light=(0.62, 0.54, 0.43),
    axis=(0.33, 0.26, 0.20), groove=(0.17, 0.13, 0.10), under=(0.36, 0.30, 0.24),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, background=(0.05, 0.18, 0.22),
           views=((30, 30), (0, 85), (-90, 8)))
