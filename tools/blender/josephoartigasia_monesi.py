"""
Procedural Josephoartigasia monesi (Pliocene to earliest Pleistocene of Uruguay)
for map colonies: the largest rodent ever found, about 3 m long and perhaps
480-1,000 kg, a giant relative of the living pacarana.

A bull-sized rodent: a massive barrel body on short, thick legs with blunt
clawed feet, almost no neck, an enormous deep, blunt-snouted head (the skull
alone about 53 cm long) with small eyes and ears and huge, forward-pointing
orange-enamelled incisors, and a short tail. Coarse brown fur with faint paler
stripes along the flanks, like a pacarana. Built with nh_neo_quad.py.
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/josephoartigasia_monesi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/JosephoartigasiaMonesi.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

def flank_stripes(co, n, c, s):
    L = q.Layout(s)
    if co.y < L.ys or co.y > L.yh + 0.1 or abs(n.x) < 0.45 or co.z < s.leg_f * 1.1:
        return c
    band = 0.5 + 0.5 * __import__("math").sin(co.z * 34.0)
    return nh.lerp(c, (0.70, 0.60, 0.45), 0.45 * nh.smoothstep(0.8, 0.95, band))


SPEC = q.Spec(
    name="JosephoartigasiaMonesi",
    leg_f=0.28, leg_h=0.30, length=0.95, girth=(0.32, 0.34), belly=1.12,
    hump=0.12, hump_y=0.15,
    leg_r=(0.085, 0.095), leg_taper=0.75, foot="paw", foot_r=1.25, stride=0.08,
    neck_len=0.12, neck_angle=10, neck_r=(0.27, 0.23),
    head_len=0.50, head_r=(0.20, 0.20), snout_r=(0.11, 0.115), head_pitch=25, jaw=1.1, cranium=1.05,
    eye_t=0.42, eye_u=0.45,
    ears="round", ear_size=0.07,
    tail_len=0.15, tail_r=0.05, tail_droop=0.9,
    tusks=[dict(t=1.02, s=sx * 0.045, u=-0.10, dir=(0, -0.7, -1), len=0.17, r=0.032, tip=0.022, bend=(0, 0.5, 0),
                flat=0.55, color=(0.85, 0.48, 0.15)) for sx in (-1, 1)],
    coat=(0.40, 0.30, 0.20), dark=(0.25, 0.18, 0.12), pale=(0.60, 0.50, 0.38),
    pattern=flank_stripes, shag=0.008, voxel=0.02,
)

if __name__ == "__main__":
    q.main(SPEC)
