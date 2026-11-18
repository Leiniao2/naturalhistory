"""
Procedural Bumastoides milleri (Late Ordovician illaenid trilobite of eastern North America)
for map colonies (Swim style).

A smooth, rounded "bumastid" trilobite that lived dug into the sea floor: a near-oval shield
whose head and tail shields are almost featureless, very strongly vaulted, with the furrows
effaced so the three lobes barely show, ten short thoracic segments, a big semicircular
pygidium and small eyes set far back on the head. Its fore part is dusted with sediment where
it sat in its burrow. Built with nh_ord_trilobite.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/bumastoides_milleri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/BumastoidesMilleri.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="BumastoidesMilleri",
    length=1.4, segments=10, ceph_frac=0.38, pyg_frac=0.36,
    ceph_w=0.50, thorax_w=0.52, thorax_w_back=0.50, pyg_w=0.50,
    ceph_p=2.0, ceph_q=2.0, pyg_p=2.2, pyg_q=2.0,
    dome=0.24, axis_frac=0.45, axis_h=0.015, pyg_axis=0.2, pyg_ribs=0,
    glab_w=0.40, glab_front=1.0, glab_len=0.7, glab_h=0.015,
    eye_size=0.8, eye_x=0.72, eye_y=0.22, eye_h=0.03,
    border=0.03, antenna=0.12, legs=False,
    shell=(0.52, 0.40, 0.28), shell_light=(0.74, 0.62, 0.46),
    axis=(0.48, 0.36, 0.25), groove=(0.34, 0.25, 0.17), under=(0.42, 0.34, 0.26),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
