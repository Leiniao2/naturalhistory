"""
Procedural Lasanius problematicus (an anaspid, a small jawless fish about 8 cm long from
the Silurian of Lesmahagow, Scotland) for map colonies.

A slender, almost naked jawless fish: no body scales except a crest of hooked scutes
along the back and a row of slender rod-like plates over the gill region; small eyes, a
terminal mouth, long gill row, a low fin fold along each side of the belly and a large
hypocercal tail (the body axis turns down into the lower lobe). Smooth, pale olive skin
with muscle bands. Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/lasanius_problematicus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/LasaniusProblematicus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mathutils import Vector  # noqa: E402
import nh_model as nh  # noqa: E402
import nh_early_fish as ef  # noqa: E402
import nh_sil_extra as sx  # noqa: E402
import nh_sil_fish as sf  # noqa: E402

SPEC = sf.Spec(
    name="LasaniusProblematicus",
    rows=[(-0.82, 0.010, 0.012, 0.012, 0.0), (-0.77, 0.040, 0.05, 0.045, 0.0), (-0.64, 0.060, 0.085, 0.075, 0.0),
          (-0.40, 0.062, 0.095, 0.080, 0.0), (-0.10, 0.056, 0.09, 0.075, -0.005), (0.20, 0.044, 0.07, 0.06, -0.02),
          (0.42, 0.030, 0.045, 0.040, -0.045), (0.62, 0.018, 0.026, 0.024, -0.09), (0.82, 0.004, 0.006, 0.006, -0.17)],
    power=2.0, skin="smooth", head_back=-0.62, myomeres=20,
    tail="hypo", tail_y0=0.40, tail_main=0.24, tail_minor=0.06,
    scutes=(-0.30, 0.36, 10, 0.035), folds=(-0.20, 0.30, 0.04),
    gills=(-0.60, -0.40, 8, -0.2, 0.010),
    eye_y=-0.71, eye_a=0.25, eye_r=0.026, mouth=(-0.82, -0.78, 0.0),
    back=(0.32, 0.34, 0.24), flank=(0.58, 0.58, 0.44), belly=(0.86, 0.84, 0.72), blotch=(0.24, 0.25, 0.18),
    blotch_amount=0.25, fin=(0.46, 0.46, 0.36), fin_edge=(0.72, 0.72, 0.60), ray=(0.30, 0.30, 0.22),
)

ROD = (0.78, 0.74, 0.58)


def extras(mb):
    # the "branchial" rods: slender bony bars slanting down over the gill region
    prof = ef.Profile(SPEC.rows, power=SPEC.power)
    for s in (1, -1):
        for i in range(7):
            y = -0.58 + i * 0.03
            a = prof.point(y, 0.6, 0.004)
            b = prof.point(y + 0.05, -0.9, 0.004)
            a.x *= s
            b.x *= s
            mb.add(nh.tube([a, b], [0.005, 0.003], sides=4), ROD)


if __name__ == "__main__":
    nh.run(lambda: sx.with_extras(lambda: sf.build(SPEC), extras), SPEC.name, **sf.PREVIEW)
