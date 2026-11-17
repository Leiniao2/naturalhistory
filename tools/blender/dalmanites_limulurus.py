"""
Procedural Dalmanites limulurus (mid-Silurian phacopid trilobite from the Rochester Shale
of New York, about 6 cm long) for map colonies.

A broad cephalon with long backswept genal spines, a forward-widening glabella and big,
tall schizochroal eyes made of separate lenses; eleven thoracic segments with pointed
pleural tips; a triangular pygidium with many ribs ending in a long tail spine (mucro).
Dark brown. Built with nh_sil_trilobite.py.
Faces -Y, pivot at the body centre (Swim style, like the other trilobites).

Usage:
  blender --background --python tools/blender/dalmanites_limulurus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DalmanitesLimulurus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_sil_trilobite as tr  # noqa: E402

SPEC = tr.Spec(
    name="DalmanitesLimulurus",
    segments=11, ceph_frac=0.28, pyg_frac=0.30, W=0.48, thorax_w=0.44, thorax_w_back=0.36, pyg_w=0.35,
    ceph_p=1.8, ceph_q=1.5, pyg_p=1.2, pyg_q=1.0, dome=0.08, glab_front=0.17, glab_back=0.10, glab_h=0.07,
    glab_len=0.9, glab_furrows=3, axis_w=0.13, axis_h=0.05, eye="schizo", eye_x=0.26, eye_y=0.45, eye_size=1.1,
    genal_spine=0.40, pleural_tips=0.04, pyg_rings=10, pyg_ribs=7, pyg_spine=0.35,
    shell=(0.36, 0.26, 0.17), shell_light=(0.58, 0.45, 0.32), axis=(0.30, 0.21, 0.13), groove=(0.13, 0.09, 0.06),
)

if __name__ == "__main__":
    nh.run(lambda: tr.build(SPEC), SPEC.name, **tr.VIEWS)
