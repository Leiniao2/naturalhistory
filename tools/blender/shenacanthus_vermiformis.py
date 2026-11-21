"""
Procedural Shenacanthus vermiformis (an early cartilaginous fish, a few centimetres long,
from the early Silurian, about 436 million years ago, of Chongqing, China, described in
2022) for map colonies.

A slender, shark-like little fish with a surprise: a box of large bony plates round its
shoulders and chest, like a placoderm's, ahead of a long body clad in tiny shark-like
scales. Small eyes near a short rounded snout, gill slits behind the head, fin spines in
front of the paired and dorsal fins and an upturned (heterocercal) tail.
Built with nh_sil_fish.py. Faces -Y, pivot at the body centre (Swim).

Usage:
  blender --background --python tools/blender/shenacanthus_vermiformis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/ShenacanthusVermiformis.fbx
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
    name="ShenacanthusVermiformis",
    rows=[(-0.84, 0.015, 0.015, 0.012, 0.0), (-0.79, 0.055, 0.050, 0.04, 0.0), (-0.66, 0.085, 0.080, 0.065, 0.0),
          (-0.46, 0.095, 0.095, 0.075, 0.005), (-0.20, 0.080, 0.085, 0.065, 0.01), (0.10, 0.060, 0.065, 0.05, 0.02),
          (0.36, 0.040, 0.045, 0.035, 0.04), (0.60, 0.022, 0.025, 0.020, 0.08), (0.84, 0.004, 0.005, 0.004, 0.14)],
    power=2.4, skin="shagreen", head_back=-0.62,
    tail="hetero", tail_y0=0.48, tail_main=0.20, tail_minor=0.06,
    median=[(-0.08, 0.06, 0.08, 1, 0.8), (0.24, 0.36, 0.06, 1, 0.8), (0.30, 0.40, 0.04, -1, 0.7)],
    paired=[(-0.40, -0.30, -0.6, 0.10, 1.0, 0.3, 0.8), (0.12, 0.18, -1.0, 0.05, 0.7, 0.5, 0.9)],
    spines=[(-0.42, -0.7, (0.06, 0.07, -0.05), 0.008)],
    gills=(-0.60, -0.50, 5, -0.1, 0.012),
    eye_y=-0.73, eye_a=0.45, eye_r=0.022, eye_look=(0.85, -0.35, 0.3), mouth=(-0.83, -0.74, 0.4),
    back=(0.24, 0.26, 0.28), flank=(0.46, 0.48, 0.50), belly=(0.84, 0.84, 0.80), blotch=(0.16, 0.17, 0.19),
    blotch_amount=0.2, fin=(0.34, 0.36, 0.38), fin_edge=(0.62, 0.64, 0.66), ray=(0.20, 0.21, 0.22),
)

BONE = (0.52, 0.48, 0.40)
SUTURE = (0.14, 0.12, 0.10)


def extras(mb):
    prof = ef.Profile(SPEC.rows, power=SPEC.power)
    # shoulder box: bony plates wrapping the flanks and belly just behind the gills
    y0, y1 = -0.48, -0.26

    def col(co, n):
        import math
        k = (co.y - y0) / (y1 - y0)
        phi = math.atan2(co.z - prof.CZ(co.y), abs(co.x))
        if abs(k - 0.55) < 0.05 or min(abs(phi - a) for a in (-1.2, -0.3, 0.5, 1.3)) < 0.07 \
                or k < 0.06 or k > 0.94:
            return SUTURE
        return nh.lerp(BONE, (0.80, 0.76, 0.66), 0.5 * nh.smoothstep(0.0, -1.0, phi))
    mb.add(ef.loft(prof, y0, y1, 8, 22, grow=0.007, cap0=False, cap1=False), col)
    # dorsal fin spines
    for y, h in ((-0.10, 0.10), (0.22, 0.08)):
        b = Vector((0.0, y, prof.top(y) - 0.004))
        ef.spine(mb, b, b + Vector((0.0, 0.05, h)), 0.008, (0.70, 0.66, 0.58), (0.30, 0.28, 0.24))


if __name__ == "__main__":
    nh.run(lambda: sx.with_extras(lambda: sf.build(SPEC), extras), SPEC.name, **sf.PREVIEW)
