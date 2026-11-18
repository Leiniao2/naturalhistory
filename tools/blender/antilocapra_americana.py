"""
Procedural pronghorn (Antilocapra americana, living, western North America) for
map colonies: the fastest land animal of the Americas, the sole survivor of the
Antilocapridae.

A slender, deer-sized runner about 1.4 m long: long thin legs with small black
hooves, a compact deep-chested body, a medium neck and a long head with very
large eyes set high and the black, forked, backward-hooked horn sheaths of the
male. Coat tan-cinnamon above with a white belly and flanks, two white bands
across the throat, white cheeks, a black face patch and a big white rump patch
around the short tail. Built with nh_neo_quad.py. Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/antilocapra_americana.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AntilocapraAmericana.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402,F401
import nh_model as nh  # noqa: E402,F401
import nh_neo_quad as q  # noqa: E402

WHITE = (0.94, 0.92, 0.88)


def markings(co, n, c, s):
    L = q.Layout(s)
    # white lower flanks / belly
    if L.ys - 0.05 < co.y < L.yh + 0.05 and co.z < L.axis_z(co.y) - s.girth[1] * 0.2 and co.z > s.leg_f * 0.92:
        c = nh.lerp(c, WHITE, 0.95)
    # big white rump patch
    if co.y > L.yh + s.girth[0] * 0.25 and co.z > s.leg_h * 0.95 and n.y > 0.1:
        c = nh.lerp(c, WHITE, 0.95 * nh.smoothstep(0.1, 0.4, n.y))
    # two white throat bands across the neck
    t = (Vector(co) - L.neck0).dot(L.neck_dir) / max(s.neck_len, 1e-3)
    if n.z < 0.0 and 0.0 < t < 1.05:
        for b0 in (0.35, 0.75):
            if abs(t - b0) < 0.09:
                c = nh.lerp(c, WHITE, 0.9 * (1 - nh.smoothstep(0.1, 0.5, n.z)))
    # white cheeks, black face stripe down the nose
    d = Vector(co) - L.hb
    tt = d.dot(L.F) / s.head_len
    side = abs(co.x)
    if 0.1 < tt < 1.1:
        if 0.45 < tt < 0.95 and side < s.snout_r[0] * 0.6 and n.z > 0.35:
            c = nh.lerp(c, (0.08, 0.06, 0.05), 0.85)
        elif n.z < 0.2 and 0.2 < tt < 0.6:
            c = nh.lerp(c, WHITE, 0.8)
    return c


HORN = (0.06, 0.05, 0.05)


def horns(mb, L, surf):
    """Black forked horn sheaths: upright, tips hooked back, a short forward prong half way up."""
    for sx in (-1, 1):
        o = Vector(L.h(0.24, sx * 0.14, 0.15))
        p, nrm = surf.near(o)
        root = p - nrm * 0.01
        mb.add(q.bent_tube(root, (sx * 0.12, 0.05, 1), 0.21, 0.03, bend=(0, 1.4, -0.3), tip_r=0.005, flat=0.7), HORN)
        mb.add(q.bent_tube(root + Vector((sx * 0.008, -0.012, 0.075)), (sx * 0.1, -1, 0.7), 0.06, 0.016,
                           tip_r=0.003), HORN)


SPEC = q.Spec(
    name="AntilocapraAmericana",
    leg_f=0.70, leg_h=0.74, length=0.70, girth=(0.17, 0.21),
    leg_r=(0.045, 0.055), leg_taper=0.45, foot="hoof", foot_r=0.8, stride=0.15,
    neck_len=0.42, neck_angle=48, neck_r=(0.11, 0.07),
    head_len=0.36, head_r=(0.075, 0.09), snout_r=(0.04, 0.05), head_pitch=55, eye_t=0.30, eye_u=0.45,
    ears="point", ear_size=0.10,
    tail_len=0.08, tail_r=0.03, tail_droop=0.6,
    coat=(0.72, 0.50, 0.28), dark=(0.55, 0.36, 0.20), pale=(0.82, 0.64, 0.42), hoof_col=(0.05, 0.05, 0.05),
    pattern=markings, extra_details=horns, shag=0.003, voxel=0.014,
)

if __name__ == "__main__":
    q.main(SPEC)
