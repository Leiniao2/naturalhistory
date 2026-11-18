"""
Procedural Pachycrocuta brevirostris (giant short-faced hyena, Pliocene to
Middle Pleistocene of Africa and Eurasia) for map colonies.

The largest hyena known, about lion-sized (up to ~110 kg): the hyena plan of
high, massive shoulders over a steeply sloping back and short hind legs, a thick
neck with a bristly mane, a short, very broad and deep bone-crushing muzzle,
round ears and a short bushy tail. Coat sandy grey-brown with dark spots on the
flanks and legs (spotted like the living spotted hyena, its closest relative).
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/pachycrocuta_brevirostris.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PachycrocutaBrevirostris.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="PachycrocutaBrevirostris",
    leg_f=0.58, leg_h=0.40, length=0.78, girth=(0.20, 0.24), belly=1.05,
    leg_r=(0.078, 0.068), leg_taper=0.62, foot="paw", foot_r=1.05, stride=0.12,
    neck_len=0.26, neck_angle=24, neck_r=(0.19, 0.14),
    head_len=0.29, head_r=(0.14, 0.13), snout_r=(0.07, 0.07), head_pitch=24, jaw=1.2, cranium=1.1,
    ears="round", ear_size=0.10, mane=0.06,
    tail_len=0.28, tail_r=0.04, tail_tuft=0.05, tail_droop=0.9,
    coat=(0.62, 0.54, 0.40), dark=(0.36, 0.30, 0.22), pale=(0.78, 0.72, 0.60),
    mane_col=(0.25, 0.20, 0.15),
    pattern=q.combine(q.spots((0.24, 0.18, 0.12), freq=11.0, size=0.26, amount=0.85),
                      q.face((0.30, 0.25, 0.19), t0=0.8, amount=0.6)),
    shag=0.006, voxel=0.016,
)

if __name__ == "__main__":
    q.main(SPEC)
