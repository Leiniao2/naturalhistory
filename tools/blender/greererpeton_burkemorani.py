"""
Procedural Greererpeton burkemorani (Early Carboniferous of West Virginia, a colosteid stem tetrapod about 1.5 m long) for map colonies (Swim style).

A long, eel-like aquatic tetrapod with about 40 trunk vertebrae: a flat, broad head with
lateral-line grooves, a very long low body, tiny limbs folded against the flanks and a deep,
finned swimming tail; olive-grey back, a pale lateral line and a yellowish belly.
Built with nh_car_tetrapod (+ nh_b2_carboniferous_tetra for head lateral-line grooves).
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/greererpeton_burkemorani.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Greererpeton.fbx
"""

import math

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_carboniferous_tetra as ct  # noqa: E402
import nh_model as nh  # noqa: E402

SPEC = tp.Spec(
    name="Greererpeton",
    head_len=0.17, head_w=0.065, head_h=0.024, snout=0.6,
    neck_len=0.03, neck_r=0.045,
    trunk_len=0.85, trunk_r=0.047, trunk_h=0.85,
    tail_len=0.5, tail_r=0.032, tail_fin=1.3, tail_curve=0.12,
    leg_r=0.009, front=(0.03, 0.025), hind=(0.035, 0.03), foot=0.02, toes=5, swim=True,
    back=(0.27, 0.29, 0.22), flank=(0.42, 0.43, 0.32), belly=(0.86, 0.76, 0.40),
    pattern="none", pattern_col=(0.18, 0.19, 0.14),
    head_col=(0.29, 0.30, 0.23), eye_r=0.011, eye_at=0.5, eye_up=0.85, teeth=10, tooth_len=0.005,
    lateral_line=True, voxel=0.006, max_tris=6500,
)


def head_grooves(base, sp, spine):
    """Dark lateral-line canal grooves on the skull roof (an arc from snout past each eye)."""
    def paint(co, n):
        c = base(co, n)
        s, p, _d = spine.nearest(co)
        if s < sp.head_len * 1.05:
            u = s / sp.head_len
            side = (co.x - p.x) / max(spine.rx(s), 1e-3)
            up = (co.z - p.z) / max(spine.rz(s), 1e-3)
            if up > 0.2:
                for target in (0.35 + 0.25 * u, 0.75):
                    if abs(abs(side) - target) < 0.04:
                        c = nh.lerp(c, (0.12, 0.12, 0.09), 0.8)
        # thin dark segment lines across the long body (vertebral myomeres hint)
        if spine.s_neck < s < spine.s_trunk and n.z > -0.2:
            ph = ((s - spine.s_neck) / (sp.trunk_len / 40)) % 1.0
            if ph < 0.12:
                c = tuple(x * 0.85 for x in c)
        return c
    return paint


if __name__ == "__main__":
    ct.run(SPEC, fused=[ct.tail_fin(0.1, below=0.8, start=0.0, end=0.98, peak=0.35)], paint=[head_grooves])
