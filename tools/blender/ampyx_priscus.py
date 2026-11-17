"""
Procedural Ampyx priscus (Early Ordovician raphiophorid trilobite of the Fezouata Shale,
Morocco) for map colonies (Swim style).

A small blind trilobite: a triangular cephalon whose glabella swells forward into a
long, slightly upturned frontal spine; very long genal spines sweeping back well past
the tail; a short thorax of five (to six) segments; a broad, short triangular
pygidium. Fezouata specimens are found in single-file lines, apparently migrating in
queues, keeping in touch with each other's spines. Pale tan shell (colour conjectural).
Built with nh_ord_trilobite.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/ampyx_priscus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AmpyxPriscus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="AmpyxPriscus",
    length=0.95, segments=5, ceph_frac=0.45, pyg_frac=0.25,
    ceph_w=0.46, thorax_w=0.44, thorax_w_back=0.40, pyg_w=0.40,
    ceph_p=1.2, ceph_q=1.1, pyg_p=1.3, pyg_q=1.2,
    dome=0.05, axis_frac=0.26, axis_h=0.05, pyg_axis=0.7, pyg_ribs=3,
    glab_w=0.20, glab_front=1.9, glab_len=0.95, glab_h=0.10,
    eye_size=0.0, genal_spine=1.25, genal_spread=0.06, genal_r=0.03,
    frontal_spine=0.85, frontal_rise=0.10, border=0.05, antenna=0.0, rows_seg=5,
    shell=(0.66, 0.52, 0.34), shell_light=(0.84, 0.72, 0.52),
    axis=(0.56, 0.42, 0.26), groove=(0.30, 0.21, 0.13), under=(0.55, 0.44, 0.30),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
