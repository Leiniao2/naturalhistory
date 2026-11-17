"""
Procedural Odobenocetops peruvianus (Late Miocene - Pliocene of the Pisco
Formation, Peru) for map colonies: a small toothed whale related to narwhals
that converged on the walrus.

About 3-4 m long, with a short, blunt, beakless head, a muscular upper lip for
sucking molluscs from the sea floor, forward-facing eyes on top of the head,
and two tusks that point backwards along the body - in males the right one is
much longer than the left. Grey-brown with a paler belly.
Built with nh_neo_whale.py. Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/odobenocetops_peruvianus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/OdobenocetopsPeruvianus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_whale as q  # noqa: E402

SPEC = q.Spec(
    name="OdobenocetopsPeruvianus",
    length=1.6, radius=0.25, head_blunt=0.6, head_frac=0.16, jaw_open=0.0,
    flipper=0.24, fluke=0.50, dorsal=0.0, eye_fwd=1.0,
    tusks=[dict(s=0.30, y=0.05, z=0.55, len=0.80, r=0.04, dir=(0.2, 0.6, -1), bend=(0, 0.3, 1.0)),
           dict(s=-0.30, y=0.05, z=0.55, len=0.22, r=0.035, dir=(-0.2, 0.6, -1), bend=(0, 0.2, 0.4))],
    back=(0.40, 0.36, 0.32), belly=(0.72, 0.68, 0.62),
)

if __name__ == "__main__":
    q.main(SPEC)
