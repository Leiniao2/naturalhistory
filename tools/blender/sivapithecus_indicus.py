"""
Procedural Sivapithecus indicus (Middle-Late Miocene of the Siwaliks, India and
Pakistan) for map colonies: a great ape close to the ancestry of the orangutan.

A chimp-sized ape shown moving on all fours: long arms raise the shoulders over
the shorter hind legs, the hands resting on curled fingers; a short neck, a
concave, orangutan-like face with a projecting muzzle, small ears and no tail.
Long reddish-brown hair (an orangutan-like reconstruction choice).
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/sivapithecus_indicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SivapithecusIndicus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="SivapithecusIndicus",
    leg_f=0.55, leg_h=0.38, length=0.42, girth=(0.17, 0.19),
    leg_r=(0.05, 0.06), leg_taper=0.7, foot="knuckle", stride=0.10,
    neck_len=0.10, neck_angle=30, neck_r=(0.12, 0.10),
    head_len=0.22, head_r=(0.10, 0.11), snout_r=(0.075, 0.07), head_pitch=5, cranium=1.1, eye_t=0.45, eye_u=0.35,
    ears="round", ear_size=0.04,
    tail_len=0.0,
    coat=(0.52, 0.27, 0.12), dark=(0.36, 0.18, 0.08), pale=(0.64, 0.38, 0.20),
    pattern=q.face((0.42, 0.30, 0.24), 0.55),
    shag=0.012, voxel=0.012, max_tris=9000,
)

if __name__ == "__main__":
    q.main(SPEC)
