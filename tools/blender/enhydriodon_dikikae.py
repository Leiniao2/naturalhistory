"""
Procedural Enhydriodon dikikae (Early Pliocene of Ethiopia, about 3.5 million
years ago) for map colonies: a giant otter about the size of a lion (perhaps
200 kg), the largest otter known.

A heavy, wolverine-to-bear-like otter: a long, thick body on short, strong
legs with broad webbed paws, a short thick neck, a broad, blunt, flat-topped
head with small ears and a powerful, deep muzzle with big crushing cheek
teeth, and a long, thick, tapering tail. Dense dark chocolate-brown fur with a
paler cream throat. Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/enhydriodon_dikikae.py -- [--render out.png]

Output: Assets/Resources/Models/Species/EnhydriodonDikikae.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

def throat(co, n, c, s):
    L = q.Layout(s)
    if co.y < L.ys + 0.02 and n.z < -0.2 and co.z > s.leg_f * 0.8:
        return nh.lerp(c, (0.80, 0.72, 0.58), 0.7 * nh.smoothstep(-0.2, -0.6, n.z))
    return c


SPEC = q.Spec(
    name="EnhydriodonDikikae",
    leg_f=0.30, leg_h=0.30, length=1.00, girth=(0.21, 0.23), belly=1.0,
    leg_r=(0.075, 0.08), leg_taper=0.7, foot="plantigrade", foot_r=1.25, stride=0.11,
    neck_len=0.22, neck_angle=12, neck_r=(0.19, 0.16),
    head_len=0.34, head_r=(0.15, 0.12), snout_r=(0.085, 0.06), head_pitch=8, jaw=1.15, cranium=1.05,
    eye_t=0.45, eye_u=0.45,
    ears="round", ear_size=0.05,
    tail_len=0.75, tail_r=0.085, tail_droop=0.30,
    coat=(0.34, 0.24, 0.16), dark=(0.18, 0.12, 0.08), pale=(0.62, 0.52, 0.40),
    pattern=throat, shag=0.004, voxel=0.017,
)

if __name__ == "__main__":
    q.main(SPEC)
