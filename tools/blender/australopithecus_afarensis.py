"""
Procedural Australopithecus afarensis (Pliocene, 3.9-2.9 million years ago, East
Africa) for map colonies, the species of "Lucy" and the Laetoli footprints.

A small, fully bipedal hominin about 1.1-1.5 m tall: short legs, fairly long
arms, a broad, funnel-shaped trunk, a small-brained head with a forward-
jutting face and a low brow, and human-like feet without a grasping toe.
Shown covered in brown hair with bare face, hands and feet (hair cover is a
reconstruction choice). Built with nh_neo_hominin.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/australopithecus_afarensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AustralopithecusAfarensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_hominin as q  # noqa: E402

SPEC = q.Spec(
    name="AustralopithecusAfarensis",
    stature=1.25, leg=0.44, arm=0.46, shoulder=0.15, hip=0.13, chest=0.11, belly=1.12,
    head=0.088, muzzle=0.7, brow=0.5, stoop=8, toe_splay=0.0, fur=1.0,
    hair=(0.30, 0.21, 0.14), skin=(0.42, 0.31, 0.24), shag=0.006,
)

if __name__ == "__main__":
    q.main(SPEC)
