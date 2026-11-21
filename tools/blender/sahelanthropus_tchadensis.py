"""
Procedural Sahelanthropus tchadensis (Late Miocene of Chad, about 7 million
years ago) for map colonies: one of the oldest known members of the human
lineage.

A chimpanzee-sized ape with a small brain, a flat face for its age, a huge
brow ridge and small canines; it probably walked upright at least some of the
time while still climbing well. Shown standing, a little stooped, with long
arms, dark hair and grey-brown skin. Built with nh_neo_hominin.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/sahelanthropus_tchadensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SahelanthropusTchadensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_hominin as q  # noqa: E402

SPEC = q.Spec(
    name="SahelanthropusTchadensis",
    stature=1.15, leg=0.40, arm=0.50, shoulder=0.16, hip=0.12, chest=0.12, belly=1.08,
    head=0.085, muzzle=0.55, brow=1.0, stoop=18, toe_splay=0.6, fur=1.0,
    hair=(0.27, 0.20, 0.14), skin=(0.45, 0.36, 0.29), shag=0.008, bulk=1.1,
)

if __name__ == "__main__":
    q.main(SPEC)
