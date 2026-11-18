"""
Procedural Physornis fortis (Patagonia, Argentina, Oligocene, ~29-25 Ma) for map colonies:
one of the largest Paleogene terror birds (Phorusrhacidae), about 2 m tall.

A heavily built, flightless predator: a massive, deep, hooked beak on a thick neck,
a bulky body with tiny wings and strong legs with three forward toes, sturdier
and slower than the later, lankier Kelenken. Shown grey-brown with a darker back
and pale, barred-looking belly (a reconstruction choice). Built with nh_neo_bigbird.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/physornis_fortis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PhysornisFortis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_bigbird as q  # noqa: E402

SPEC = q.Spec(
    name="PhysornisFortis",
    hip=0.95, body=(0.27, 0.44, 0.31), body_tilt=12, leg_r=0.068,
    neck=((0, -0.32, 0.20), (0, -0.40, 0.50), (0, -0.50, 0.74)), neck_r=(0.15, 0.115, 0.10),
    head_r=0.15, beak_len=0.48, beak_h=0.32, hook=1.0, wing=0.2, tail=0.18,
    feather=(0.36, 0.33, 0.28), dark=(0.20, 0.18, 0.15), pale=(0.72, 0.68, 0.58),
    head_col=(0.30, 0.27, 0.23), beak_col=(0.55, 0.50, 0.40), leg_col=(0.46, 0.42, 0.32), stride=0.28,
)

if __name__ == "__main__":
    q.main(SPEC)
