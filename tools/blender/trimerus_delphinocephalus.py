"""
Procedural Trimerus delphinocephalus (a large homalonotid trilobite, up to about 25 cm
long, from mid-Silurian seas of North America and England) for map colonies.

A big, smooth, burrowing trilobite: a triangular head drawn out at the front into a
blunt, upturned snout (the "dolphin head" of its name), a low, faint, trapezoid glabella,
small eyes, a broad thorax of thirteen segments with a wide axis and low, rounded
pleurae, and a long, triangular tail shield ending in a point. Built with
nh_sil_trilobite.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/trimerus_delphinocephalus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TrimerusDelphinocephalus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_trilobite as tr  # noqa: E402

SPEC = tr.Spec(
    name="TrimerusDelphinocephalus",
    length=1.7, segments=13, ceph_frac=0.27, pyg_frac=0.27, W=0.44, thorax_w=0.43, thorax_w_back=0.34, pyg_w=0.32,
    ceph_p=1.4, ceph_q=1.3, pyg_p=1.1, pyg_q=1.0, dome=0.10, glab_front=0.12, glab_back=0.18, glab_h=0.035,
    glab_len=0.70, glab_furrows=0, axis_w=0.22, axis_h=0.04, eye="small", eye_x=0.24, eye_y=0.45, eye_size=0.7,
    pyg_rings=10, pyg_ribs=6, pyg_spine=0.06, antenna=0.10,
    shell=(0.50, 0.44, 0.34), shell_light=(0.72, 0.66, 0.54), axis=(0.44, 0.38, 0.29), groove=(0.24, 0.20, 0.15),
)

if __name__ == "__main__":
    nh.run(lambda: tr.build(SPEC), SPEC.name, **tr.VIEWS)
