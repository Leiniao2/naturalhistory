"""
Procedural Palaeophis colossaeus (Mali and Niger, Trans-Saharan Seaway, early-middle Eocene)
for map colonies: a giant sea snake (Palaeophiidae), perhaps 8 m long or more,
one of the longest snakes known.

A long, muscular, laterally compressed body flattening toward the tail into a
paddle for swimming, with a fairly small head. It hunted fish and other prey in
warm, shallow coastal seas. Olive-grey with darker bands and a pale belly (unknown).
Built with nh_pal_snake.py, then squeezed sideways and centred.
Faces -Y, pivot at the body centre (swimmer).

Usage:
  blender --background --python tools/blender/palaeophis_colossaeus.py -- [--render out.png]

Output: Assets/Resources/Models/Species/PalaeophisColossaeus.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_pal_snake as sn  # noqa: E402
from mathutils import Vector  # noqa: E402

SPEC = sn.Spec(
    name="PalaeophisColossaeus",
    length=2.4, girth=0.085, head_len=0.12, head_w=0.06, neck=0.55, tail=0.2,
    base=(0.38, 0.40, 0.33), saddle=(0.16, 0.18, 0.16), belly=(0.80, 0.78, 0.66),
    saddles=26, saddle_w=0.4, side_spots=0.3, head_col=(0.28, 0.30, 0.25),
)


def build():
    obj = sn.build(SPEC)
    vs = obj.data.vertices
    L = SPEC.length
    for v in vs:
        # squeeze sideways (deep, narrow swimming body), more toward the paddle tail
        t = (v.co.y + L / 2) / L
        sq = 0.75 - 0.3 * nh.smoothstep(0.7, 1.0, t)
        if t > 0.08:
            v.co.x *= sq
            v.co.z *= 1.0 + 0.5 * nh.smoothstep(0.75, 1.0, t)
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
    c = (lo + hi) / 2
    for v in vs:
        v.co -= c
    obj.data.update()
    return obj


if __name__ == "__main__":
    nh.run(build, SPEC.name, background=(0.05, 0.22, 0.32), views=((35, 25), (-90, 5), (0, 80)))
