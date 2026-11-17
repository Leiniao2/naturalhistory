"""
Procedural Flexicalymene meeki (Late Ordovician calymenid trilobite, one of the most
common fossils of the Cincinnati region) for map colonies (Swim style).

A strongly convex, spineless trilobite: a rounded cephalon with a bell-shaped glabella
bearing three pairs of rounded lateral lobes, small eyes, rounded genal angles; a
strongly trilobed thorax of thirteen segments; and a small semicircular pygidium with
a ringed axis. Often found rolled up into a ball. Grey-brown shell (colour conjectural).
Built with nh_ord_trilobite.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/flexicalymene_meeki.py -- [--render out.png]

Output: Assets/Resources/Models/Species/FlexicalymeneMeeki.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402

SPEC = tri.Spec(
    name="FlexicalymeneMeeki",
    length=1.6, segments=13, ceph_frac=0.30, pyg_frac=0.17,
    ceph_w=0.50, thorax_w=0.50, thorax_w_back=0.40, pyg_w=0.36,
    ceph_p=2.0, ceph_q=2.2, pyg_p=2.0, pyg_q=1.8,
    dome=0.13, axis_frac=0.36, axis_h=0.09, pyg_axis=0.85, pyg_ribs=5,
    glab_w=0.36, glab_front=0.7, glab_len=0.8, glab_h=0.12, glab_furrows=3,
    eye_size=0.6, eye_x=0.62, eye_y=0.5, eye_h=0.03,
    genal_spine=0.0, border=0.12, rows_seg=3,
    shell=(0.38, 0.35, 0.31), shell_light=(0.56, 0.52, 0.46),
    axis=(0.62, 0.57, 0.50), groove=(0.16, 0.14, 0.12), under=(0.40, 0.36, 0.32),
)

if __name__ == "__main__":
    nh.run(lambda: tri.build(SPEC), SPEC.name, **tri.VIEWS)
