"""
Procedural Megacerops coloradensis (North America, late Eocene, ~38-34 Ma) for map colonies. Built with nh_pal_quad.py.

A brontothere ("thunder beast"), a rhino-like relative of horses about 2.5 m
at the shoulder, with a hump over the shoulders and a blunt, forked bony horn on
the end of its nose, larger in males, probably used in shoving contests. Columnar
legs on broad feet. Skin: grey-brown, nearly hairless (unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/megacerops_coloradensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MegaceropsColoradensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402,F401

SPEC = q.Spec(
    name="MegaceropsColoradensis",
    length=1.0, shoulder=0.96, hip=0.80, width=0.25, depth=0.28, hump=0.09, belly=1.05,
    fore_r=0.085, hind_r=0.1, shin=0.8, foot="pad", foot_r=0.08, hock=0.0, stride=0.08,
    neck_len=0.22, neck_angle=8, neck_r=0.17,
    head_len=0.42, head_w=0.36, head_h=0.32, snout=0.85, snout_r=(0.26, 0.2), snout_tilt=8, head_tilt=10,
    jaw=0.85, jaw_r=0.2, ear=0.17, ear_angle=28, eye=0.05, eye_pos=(0.32, -0.22, 0.08),
    tail_len=0.32, tail_r=0.04, tail_angle=-70, tail_tuft=0.03,
    horns=[Horn(base=(0.1, -0.8, 0.1), direction=(0.6, -0.45, 1), length=0.36, radius=0.13, tip=0.9, flat=0.7, fuse=True,
                color=(0.40, 0.35, 0.30))],
    coat=(0.47, 0.41, 0.35), back=(0.37, 0.32, 0.27), pale=(0.58, 0.52, 0.45), pale_amt=0.6, skin=0.6, fur=0.3,
    voxel=0.016, max_tris=14000, ground=(0.50, 0.48, 0.32),
)


if __name__ == "__main__":
    q.main(SPEC)
