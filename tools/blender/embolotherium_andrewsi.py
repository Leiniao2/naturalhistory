"""
Procedural Embolotherium andrewsi (Mongolia, late Eocene, ~40-35 Ma) for map colonies. Built with nh_pal_quad.py.

A huge brontothere about 2.5 m at the shoulder. Instead of a forked horn its nasal
bones rose into one tall, broad, upturned bony shield above the snout, like a
battering ram, in front of a long skull; a hump over the shoulders, a barrel body
and pillar legs on broad feet. Skin: slate grey-brown, nearly hairless (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/embolotherium_andrewsi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EmbolotheriumAndrewsi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import math  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_pal_quad as q  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

SHIELD = (0.36, 0.32, 0.29)

SPEC = q.Spec(
    name="EmbolotheriumAndrewsi",
    length=1.05, shoulder=0.98, hip=0.80, width=0.27, depth=0.30, hump=0.11, belly=1.08,
    fore_r=0.09, hind_r=0.105, shin=0.82, foot="pad", foot_r=0.085, hock=0.0, stride=0.08,
    neck_len=0.22, neck_angle=6, neck_r=0.18,
    head_len=0.46, head_w=0.34, head_h=0.30, snout=0.9, snout_r=(0.25, 0.19), snout_tilt=6, head_tilt=8,
    jaw=0.85, jaw_r=0.19, ear=0.15, ear_angle=30, eye=0.045, eye_pos=(0.3, -0.2, 0.06),
    tail_len=0.3, tail_r=0.04, tail_angle=-72, tail_tuft=0.03,
    coat=(0.50, 0.45, 0.40), back=(0.38, 0.34, 0.30), pale=(0.64, 0.59, 0.52), pale_amt=0.55, skin=0.7, fur=0.3,
    voxel=0.016, max_tris=15000, ground=(0.52, 0.48, 0.34),
)


def shield(b, L):
    """The nasal shield: a broad, tall plate rising from the snout and leaning forward, with a
    thickened, slightly notched rim, plus a ridge joining it to the face."""
    k = L.s.head_len
    rot = Matrix.Rotation(math.radians(25 - L.s.head_tilt), 3, "X")
    for (x, y, z, rx, ry, rz) in ((0, -0.98, 0.42, 0.42, 0.11, 0.42),       # the plate, leaning forward
                                  (0, -0.92, 0.12, 0.30, 0.22, 0.24),       # its thick base on the nasals
                                  (0.25, -1.14, 0.74, 0.17, 0.11, 0.13),    # rounded upper corners
                                  (-0.25, -1.14, 0.74, 0.17, 0.11, 0.13)):
        b.add(nh.ellipsoid(L.h(x, y, z), (rx * k, ry * k, rz * k), subdivisions=3, rotation=rot), SHIELD)


if __name__ == "__main__":
    q.main(SPEC, extra=shield)
