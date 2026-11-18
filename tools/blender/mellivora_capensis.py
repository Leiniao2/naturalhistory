"""
Procedural honey badger / ratel (Mellivora capensis, living, Africa to India)
for map colonies.

A stocky, low, broad-bodied mustelid about 70-80 cm long: short, powerful legs,
long curved claws on the front feet for digging, a small broad head with tiny
ears and small eyes and a short tail. The famous colouring: jet-black legs,
belly, face and tail, and a broad silvery-white to grey mantle from the crown
over the back to the tail root. Its thick, loose skin lets it twist round and
bite back when seized. Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/mellivora_capensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MellivoraCapensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

def mantle(co, n, c, s):
    """Silver-grey cape from the crown over the back to the tail root; black face, legs, belly and tail."""
    L = q.Layout(s)
    body_line = L.axis_z(L.ys) - s.girth[1] * 0.05
    head_line = L.h(s.eye_t)[2] + s.head_r[1] * 0.35       # just above the eyes
    y_head = L.h(s.eye_t)[1]
    t = nh.smoothstep(y_head, L.ys, co.y)
    line = head_line + (body_line - head_line) * t
    if co.y > L.ys:
        line = L.axis_z(co.y) - s.girth[1] * 0.05
    k = nh.smoothstep(line - 0.02, line + 0.03, co.z)
    if co.y < y_head - s.head_len * 0.1:                  # muzzle black
        k = 0.0
    if co.y > L.yh + s.girth[0] * 0.9:                    # tail black beyond the root
        k *= nh.smoothstep(L.yh + s.girth[0] * 1.3, L.yh + s.girth[0] * 0.9, co.y)
    black = (0.05, 0.05, 0.05)
    silver = (0.82, 0.81, 0.76)
    return nh.lerp(black, silver, k)


SPEC = q.Spec(
    name="MellivoraCapensis",
    leg_f=0.24, leg_h=0.25, length=0.80, girth=(0.21, 0.20), belly=1.0,
    leg_r=(0.068, 0.068), leg_taper=0.72, foot="plantigrade", foot_r=1.2, stride=0.10,
    neck_len=0.16, neck_angle=12, neck_r=(0.17, 0.14),
    head_len=0.30, head_r=(0.12, 0.10), snout_r=(0.055, 0.05), head_pitch=18, eye_t=0.45,
    ears="none",
    tail_len=0.30, tail_r=0.05, tail_droop=0.35,
    coat=(0.06, 0.06, 0.06), dark=(0.04, 0.04, 0.04), pale=(0.08, 0.08, 0.08), countershade=0.0,
    pattern=mantle, shag=0.006, voxel=0.015,
)

if __name__ == "__main__":
    q.main(SPEC)
