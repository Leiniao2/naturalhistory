"""
Procedural Ardipithecus ramidus (Early Pliocene, about 4.4 million years ago,
Middle Awash, Ethiopia) for map colonies, after the "Ardi" skeleton.

A chimp-sized early hominin that walked upright on the ground but still
climbed well: long arms, a small head with a projecting muzzle, a small brain
and a grasping, splayed big toe. Shown walking, covered in dark hair with bare
face, hands and feet. Built with nh_neo_hominin.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/ardipithecus_ramidus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ArdipithecusRamidus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_hominin as q  # noqa: E402

SPEC = q.Spec(
    name="ArdipithecusRamidus",
    stature=1.20, leg=0.42, arm=0.50, shoulder=0.15, hip=0.11, chest=0.10,
    head=0.085, muzzle=0.85, brow=0.6, stoop=14, toe_splay=1.0, fur=1.0,
    hair=(0.12, 0.09, 0.07), skin=(0.36, 0.27, 0.21), shag=0.006,
)

if __name__ == "__main__":
    q.main(SPEC)
