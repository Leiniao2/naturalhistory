"""
Procedural Isotelus rex (Late Ordovician asaphid, the largest complete trilobite known, ~72 cm)
for map colonies.

Modelled on the Manitoba holotype: an elongate-ovoid, smooth dorsal shield whose
greatest width (just in front of the genal angles) is under 60% of its length,
rounded genal angles without spines (as in the large adults found so far), a
long rounded cephalon and pygidium, a fairly tall vault and raised eye lobes -
it may have lain partly buried in the sediment with only its eyes showing.
Dark reddish-brown (colour is conjectural). Built with nh_isotelus.py.
Faces -Y, pivot at the body centre (Swim style, like Redlichia).

Usage:
  blender --background --python tools/blender/isotelus_rex.py -- [--render out.png]

Output: Assets/Resources/Models/Species/IsotelusRex.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_isotelus as iso  # noqa: E402

SPEC = iso.Spec(
    name="IsotelusRex",
    ceph_frac=0.36, pyg_frac=0.34,
    ceph_w=0.45, thorax_w=0.43, thorax_w_back=0.41, pyg_w=0.42,
    ceph_p=2.3, ceph_q=1.8, pyg_p=2.3, pyg_q=1.8,
    dome=0.14, axis_h=0.055, eye_h=0.06, eye_size=1.1, genal_spine=0.0,
    shell=(0.42, 0.24, 0.14), shell_light=(0.64, 0.42, 0.26),
    axis=(0.32, 0.17, 0.10), groove=(0.17, 0.09, 0.05), under=(0.34, 0.22, 0.14),
)


if __name__ == "__main__":
    nh.run(lambda: iso.build(SPEC), "IsotelusRex", views=((30, 40), (0, 85), (-90, 12)))
