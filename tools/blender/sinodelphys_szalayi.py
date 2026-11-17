"""
Procedural Sinodelphys szalayi (Liaoning, Early Cretaceous, ~125 Ma) for map colonies. Built with nh_pal_quad.py.

One of the earliest metatherians, the line of the marsupials: a mouse-sized tree-climber,
about 15 cm long with its tail, known from a skeleton with traces of fur. Drawn like a small
opossum: a long pointed snout with a pink nose, rounded dark ears, grasping feet and a long,
thin, scantily furred tail curled at the tip. Coat: grey with darker back and a pale face and
belly (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/sinodelphys_szalayi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Sinodelphys.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402

SPEC = q.Spec(
    name="Sinodelphys",
    length=0.42, shoulder=0.3, hip=0.34, width=0.09, depth=0.1, arch=0.03,
    fore_r=0.03, hind_r=0.042, shin=0.6, foot="paw", foot_r=0.03, toes=5, hock=0.3, stride=0.06,
    neck_len=0.08, neck_angle=25, neck_r=0.065,
    head_len=0.19, head_w=0.38, head_h=0.36, snout=0.95, snout_r=(0.24, 0.07), snout_tilt=14, jaw=0.85, jaw_r=0.12,
    ear=0.22, ear_shape="round", eye=0.085, eye_pos=(0.3, -0.3, 0.13), nose_col=(0.82, 0.55, 0.55),
    tail_len=0.85, tail_r=0.032, tail_angle=10, tail_curl=-110,
    coat=(0.52, 0.50, 0.47), back=(0.32, 0.30, 0.28), pale=(0.88, 0.85, 0.78), pale_amt=0.9,
    muzzle_col=(0.86, 0.82, 0.76), dark_legs=0.5,
    voxel=0.0085, max_tris=10000, ground=(0.30, 0.36, 0.22),
)


if __name__ == "__main__":
    q.main(SPEC)
