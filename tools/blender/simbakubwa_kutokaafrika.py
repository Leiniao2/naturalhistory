"""
Procedural Simbakubwa kutokaafrika (Early Miocene of Kenya, about 22 million
years ago) for map colonies: one of the largest hyaenodont predators, bigger
than a polar bear (perhaps 1,000-1,500 kg).

A heavy, low-slung creodont-style hunter: a long, deep body on short, thick,
semi-plantigrade legs with broad clawed paws, a thick neck and a huge, long,
narrow-snouted skull with a high sagittal crest and long slicing teeth
(Simbakubwa means 'big lion' in Swahili, but it was no cat), small rounded
ears and a long, heavy tail. Dark grey-brown with a paler belly.
Built with nh_pal_quad.py (like Hyaenodon). Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/simbakubwa_kutokaafrika.py -- [--render out.png]

Output: Assets/Resources/Models/Species/SimbakubwaKutokaafrika.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402,F401
import nh_pal_quad as q  # noqa: E402
from nh_pal_quad import Horn  # noqa: E402

SPEC = q.Spec(
    name="SimbakubwaKutokaafrika",
    length=0.86, shoulder=0.72, hip=0.66, width=0.17, depth=0.21, belly=1.05,
    fore_r=0.068, hind_r=0.074, shin=0.6, foot="paw", foot_r=0.058, toes=5, hock=0.3, stride=0.09,
    neck_len=0.24, neck_angle=20, neck_r=0.12,
    head_len=0.35, head_w=0.33, head_h=0.35, snout=0.95, snout_r=(0.27, 0.17), snout_tilt=8, jaw=0.95, jaw_r=0.19,
    ear=0.16, ear_shape="round", eye=0.055, eye_pos=(0.3, -0.25, 0.14), nose_col=(0.06, 0.05, 0.05),
    tail_len=0.70, tail_r=0.06, tail_angle=-35, tail_curl=15,
    horns=[Horn(base=(0.13, -1.12, -0.12), direction=(0.08, -0.15, -1), length=0.24, radius=0.034,
                color=(0.9, 0.86, 0.75))],
    coat=(0.52, 0.42, 0.31), back=(0.30, 0.23, 0.17), pale=(0.74, 0.66, 0.54), pale_amt=0.7, dark_legs=0.5,
    stripes=7, stripe_col=(0.22, 0.17, 0.13), stripe_amt=0.35,
    voxel=0.013, max_tris=16000, ground=(0.50, 0.48, 0.32),
)


if __name__ == "__main__":
    q.main(SPEC)
