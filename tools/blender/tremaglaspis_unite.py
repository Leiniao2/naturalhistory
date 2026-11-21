"""
Procedural Tremaglaspis unite (Early Ordovician aglaspidid arthropod, Wales and Morocco)
for map colonies (Swim style).

An aglaspidid, a group of extinct arthropods that look like a cross between a trilobite
and a horseshoe crab: a few centimetres long, with a smooth, semicircular head shield
bearing small eyes and long genal spines, a trunk of eleven smooth segments whose side
lobes end in backward-pointing spines, and a long, slender tail spine. Walking legs
under the head and body. It crawled over the sea floor, probably scavenging. Smooth,
glossy dark brown with paler margins. Built on nh_ord_trilobite.py's shell (no
trilobation: a low axis and no glabella). Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/tremaglaspis_unite.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TremaglaspisUnite.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402

import nh_model as nh  # noqa: E402
import nh_ord_trilobite as tri  # noqa: E402
import nh_dev_spiny as sp  # noqa: E402

SPEC = tri.Spec(
    name="TremaglaspisUnite",
    length=1.3, segments=11, ceph_frac=0.30, pyg_frac=0.06,
    ceph_w=0.46, thorax_w=0.46, thorax_w_back=0.14, pyg_w=0.10,
    ceph_p=2.0, ceph_q=2.0,
    dome=0.10, axis_frac=0.40, axis_h=0.03, pyg_ribs=0,
    glab_w=0.2, glab_h=0.0, glab_furrows=0,
    eye_size=0.55, eye_x=0.32, eye_y=0.55, eye_h=0.03,
    genal_spine=0.30, genal_spread=0.10, genal_r=0.035,
    pleural_spine=0.07, pleural_back=0.85, pleural_r=0.02,
    border=0.05, rows_seg=3, antenna=0.0,
    shell=(0.34, 0.24, 0.16), shell_light=(0.60, 0.46, 0.32),
    axis=(0.30, 0.21, 0.14), groove=(0.16, 0.11, 0.07), under=(0.46, 0.36, 0.26),
    leg=(0.56, 0.42, 0.30),
)


def extras(mb, body):
    # long, slender tail spine
    y0 = body.y_back - 0.04
    z = 0.0
    mb.add(nh.tube([Vector((0, y0, z)), Vector((0, y0 + 0.30, z + 0.02)), Vector((0, y0 + 0.62, z + 0.05))],
                   [0.035, 0.022, 0.0], sides=7), SPEC.shell)


if __name__ == "__main__":
    nh.run(lambda: sp.build(SPEC, extras), SPEC.name, **tri.VIEWS)
