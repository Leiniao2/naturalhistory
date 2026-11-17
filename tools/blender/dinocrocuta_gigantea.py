"""
Procedural Dinocrocuta gigantea (Late Miocene of Eurasia and Africa) for map
colonies: a giant bone-cracking "hyena", a percrocutid rather than a true
hyena, about the size of a lion.

Hyena-like build with long front legs and a back that slopes down to shorter
hind legs, a thick neck and a massive, broad head with a short, deep muzzle
and huge jaws; rounded ears, a short bushy tail. Sandy coat with dark spots
(a hyena-like reconstruction choice). Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/dinocrocuta_gigantea.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DinocrocutaGigantea.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="DinocrocutaGigantea",
    leg_f=0.70, leg_h=0.54, length=0.72, girth=(0.18, 0.22),
    leg_r=(0.065, 0.06), leg_taper=0.6, foot="paw", stride=0.12,
    neck_len=0.28, neck_angle=25, neck_r=(0.17, 0.13),
    head_len=0.36, head_r=(0.12, 0.12), snout_r=(0.07, 0.075), head_pitch=25,
    ears="round", ear_size=0.09, mane=0.04,
    tail_len=0.32, tail_r=0.04, tail_tuft=0.06, tail_droop=0.8,
    coat=(0.66, 0.56, 0.40), dark=(0.42, 0.34, 0.24), pale=(0.82, 0.76, 0.64),
    mane_col=(0.30, 0.24, 0.17),
    pattern=q.spots((0.22, 0.17, 0.12), freq=12, size=0.26, amount=0.8, zmin=0.08),
    shag=0.006, voxel=0.016,
)

if __name__ == "__main__":
    q.main(SPEC)
