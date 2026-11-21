"""
Procedural Proconsul africanus (Early Miocene of East Africa) for map colonies:
an early ape, close to the split between apes and Old World monkeys.

A baboon-sized, tailless primate that walked on all fours along branches with
its palms flat, monkey-like in build but with an ape's skull, a short muzzle
and no tail. Dark brown fur with a bare grey face.
Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/proconsul_africanus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ProconsulAfricanus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

SPEC = q.Spec(
    name="ProconsulAfricanus",
    leg_f=0.40, leg_h=0.38, length=0.44, girth=(0.14, 0.16),
    leg_r=(0.045, 0.05), leg_taper=0.7, foot="plantigrade", stride=0.12,
    neck_len=0.10, neck_angle=30, neck_r=(0.10, 0.09),
    head_len=0.22, head_r=(0.10, 0.10), snout_r=(0.06, 0.055), head_pitch=8, cranium=1.15,
    eye_t=0.48, eye_u=0.35,
    ears="round", ear_size=0.035,
    tail_len=0.0,
    coat=(0.36, 0.25, 0.16), dark=(0.22, 0.15, 0.10), pale=(0.50, 0.38, 0.26),
    pattern=q.face((0.42, 0.38, 0.36), t0=0.5, amount=0.85),
    shag=0.010, voxel=0.011, max_tris=9000,
)

if __name__ == "__main__":
    q.main(SPEC)
