"""
Procedural Isotelus maximus (Late Ordovician asaphid trilobite, Ohio's state fossil) for map colonies.

A big, smooth "effaced" trilobite: broad semicircular cephalon and pygidium of
about equal size with only faint traces of the glabella and pygidial axis, a
short thorax of eight grooved segments with a raised axial lobe, crescent eyes
on low lobes, and - unlike adult I. gigas and I. rex - genal spines sweeping
back alongside the thorax. Broadest outline of the three Isotelus species.
Warm ochre-brown (colour is conjectural). Built with nh_isotelus.py.
Faces -Y, pivot at the body centre (Swim style, like Redlichia).

Usage:
  blender --background --python tools/blender/isotelus_maximus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/IsotelusMaximus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_isotelus as iso  # noqa: E402

SPEC = iso.Spec(
    name="IsotelusMaximus",
    ceph_w=0.52, thorax_w=0.48, thorax_w_back=0.46, pyg_w=0.47,
    ceph_p=2.0, ceph_q=2.0, pyg_p=2.0, pyg_q=2.0,
    dome=0.11, eye_h=0.04, genal_spine=0.36,
    shell=(0.55, 0.37, 0.19), shell_light=(0.76, 0.57, 0.33),
    axis=(0.42, 0.26, 0.13), groove=(0.22, 0.13, 0.06),
)


if __name__ == "__main__":
    nh.run(lambda: iso.build(SPEC), "IsotelusMaximus", views=((30, 40), (0, 85), (-90, 12)))
