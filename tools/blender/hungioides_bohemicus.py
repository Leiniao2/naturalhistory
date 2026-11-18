"""
Procedural Hungioides bohemicus (Middle Ordovician dikelokephalid trilobite of peri-Gondwanan
Europe; giant specimens from the roofing slates of Arouca, Portugal) for map colonies (Swim style).

One of the largest trilobites: a broad, flat, oval shield 40-50 cm long or more. A wide
semicircular cephalon with a long glabella expanding forward, crescent eyes and short genal
spines; eight broad thoracic segments with blunt, backswept pleural tips; and a big, wide,
flattened pygidium carrying a pair of short posterolateral spines. Dull slate-grey brown
(colour conjectural). Built with nh_ord_trilobite.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/hungioides_bohemicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HungioidesBohemicus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="HungioidesBohemicus",
    length=1.7, segments=8, ceph_frac=0.30, pyg_frac=0.34,
    ceph_w=0.62, thorax_w=0.62, thorax_w_back=0.56, pyg_w=0.58,
    ceph_p=2.4, ceph_q=1.6, pyg_p=1.8, pyg_q=1.5,
    dome=0.07, axis_frac=0.26, axis_h=0.05, pyg_axis=0.7, pyg_ribs=6,
    glab_w=0.24, glab_front=1.35, glab_len=0.85, glab_h=0.06, glab_furrows=2,
    eye_size=1.1, eye_x=0.5, eye_y=0.45, eye_h=0.03,
    genal_spine=0.22, genal_spread=0.10, genal_r=0.04,
    pleural_spine=0.10, pleural_grow=0.10, pleural_back=0.75, pleural_r=0.03,
    pyg_spines=[(0.92, 0.26, 0.10)], border=0.10, antenna=0.22,
    shell=(0.42, 0.38, 0.33), shell_light=(0.62, 0.57, 0.49),
    axis=(0.34, 0.30, 0.26), groove=(0.18, 0.16, 0.14), under=(0.36, 0.32, 0.28),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
