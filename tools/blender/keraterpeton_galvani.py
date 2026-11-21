"""
Procedural Keraterpeton galvani (Late Carboniferous of Jarrow, Ireland, a nectridean lepospondyl about 30 cm long) for map colonies (Swim style).

A small newt-like aquatic lepospondyl: a flattened head with a pair of short, backward-pointing
tabular horns at the rear corners of the skull (a small-horned forerunner of Diplocaulus'
boomerang head), a small body, short limbs folded back and a long, laterally flattened tail
longer than the body, fringed with little spiny scales; greenish brown with a paler belly.
Built with nh_car_tetrapod (+ nh_b2_carboniferous_tetra for the horns).
Faces -Y, pivot at the body centre.

Usage:
  blender --background --python tools/blender/keraterpeton_galvani.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Keraterpeton.fbx
"""

from mathutils import Vector

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_car_tetrapod as tp  # noqa: E402
import nh_b2_carboniferous_tetra as ct  # noqa: E402
import nh_model as nh  # noqa: E402

SPEC = tp.Spec(
    name="Keraterpeton",
    head_len=0.15, head_w=0.07, head_h=0.022, snout=0.55,
    neck_len=0.02, neck_r=0.045,
    trunk_len=0.32, trunk_r=0.05, trunk_h=0.8,
    tail_len=0.62, tail_r=0.03, tail_fin=1.3, tail_curve=0.08,
    leg_r=0.01, front=(0.04, 0.035), hind=(0.045, 0.04), foot=0.025, toes=4, swim=True,
    back=(0.26, 0.27, 0.13), flank=(0.40, 0.38, 0.20), belly=(0.76, 0.72, 0.50),
    pattern="blotches", pattern_col=(0.17, 0.18, 0.08), pattern_scale=0.9,
    head_col=(0.28, 0.28, 0.14), eye_r=0.012, eye_at=0.42, eye_up=0.85, teeth=0,
    voxel=0.005, max_tris=3800,
)

FIN = dict(start=0.0, end=0.98, peak=0.3)
FUSED = [ct.tabular_horns(0.11, 0.013, at=0.9, out=0.92, up=0.0, spread=0.9),
         ct.tail_fin(0.05, below=0.9, **FIN)]
PAINT = [ct.far_colour((0.22, 0.22, 0.11), dist=1.25, s_range=(0.0, 0.2))]


def tail_spines(sp, spine):
    """Little spiny scales along the top and bottom edges of the tail fin, pointing back."""
    out = []
    col = (0.18, 0.17, 0.09)
    n = 18
    for i in range(n):
        u = 0.06 + 0.84 * i / (n - 1)
        s = spine.s_trunk + sp.tail_len * u
        p = spine.at(s)
        h = ct.fin_height(0.05, u, **FIN)
        L = 0.014 * (1.0 - 0.5 * i / n)
        r = 0.0032 * (1 - 0.4 * i / n)
        for sz, depth in ((1, h), (-1, h * 0.9)):
            b = p + Vector((0, 0, sz * (depth - 0.004)))
            out.append((nh.tube([b, b + Vector((0, L * 0.9, sz * L * 0.45))], [r, 0.0], sides=4), col))
    return out


SPEC.extra.append(tail_spines)

if __name__ == "__main__":
    ct.run(SPEC, fused=FUSED, paint=PAINT)
