"""
Procedural Neanderthal (Homo neanderthalensis, Middle-Late Pleistocene of
Europe and western Asia) for map colonies.

A stocky, barrel-chested human with short forearms and shins (a cold-adapted
build), a long, low skull with a large brain, a strong double-arched brow
ridge, a big projecting nose and midface and no chin. Shown walking, with
reddish-brown head hair, light skin and a hide wrap round the waist.
Built with nh_neo_hominin.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/homo_neanderthalensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/HomoNeanderthalensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_hominin as q  # noqa: E402

SPEC = q.Spec(
    name="HomoNeanderthalensis",
    stature=1.65, leg=0.46, arm=0.42, shoulder=0.16, hip=0.125, chest=0.12, belly=1.1, bulk=1.3,
    head=0.078, muzzle=0.35, brow=0.8, stoop=3, toe_splay=0.0, fur=0.0,
    hair=(0.40, 0.22, 0.12), skin=(0.80, 0.62, 0.50), wrap=(0.42, 0.30, 0.18), shag=0.004, voxel=0.014,
)

if __name__ == "__main__":
    q.main(SPEC)
