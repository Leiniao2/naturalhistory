"""
Procedural Waeringoscorpio hefteri for the map: a small aquatic scorpion from the Early
Devonian (Emsian, about 400 million years ago) Hunsrück Slate of Germany, about 3-4 cm
long.

A typical early scorpion (pincered pedipalps, four pairs of walking legs, a broad
seven-segmented mesosoma and a narrow, curled five-segmented tail ending in a sting),
remarkable for the rows of slender, filament-like lobes that stick out sideways from
the underside of its abdomen - interpreted as external gills, showing that it lived and
breathed under water.

Built with nh_sil_eurypterid.py (the scorpion setup of proscorpius_osborni.py) plus the
gill filaments. Colours are unknown: very dark brown-black with paler joints and pale,
pinkish gill tufts. Faces -Y, pivot at the body centre (Swim style).

Usage:
  blender --background --python tools/blender/waeringoscorpio_hefteri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Waeringoscorpio.fbx
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
from mathutils import Vector  # noqa: E402
import nh_sil_eurypterid as eu  # noqa: E402

GILL = (0.80, 0.56, 0.52)
GILL_TIP = (0.88, 0.76, 0.72)

L = eu.LegSpec
SPEC = eu.Spec(
    name="Waeringoscorpio",
    y_front=-0.55, y_pro=-0.30, pro_wf=0.12, pro_wb=0.16, pro_round=0.08, pro_h=0.05,
    pre_len=0.52, pre_w=[0.165, 0.178, 0.185, 0.185, 0.178, 0.16, 0.12], pre_h=0.055,
    post_len=0.60, post_w=[0.068, 0.064, 0.061, 0.058, 0.058], post_round=0.95,
    curl=150, curl_start=0.0, telson="sting", telson_len=0.14, telson_w=0.055,
    eye="tubercle", eye_y=0.35, eye_size=1.0, chelicera="small", pedipalp=0.32,
    legs=[L(0.30, 0.30, -25, 0, 0, 0.019), L(0.50, 0.33, -5, 0, 0, 0.020),
          L(0.70, 0.36, 15, 0, 0, 0.021), L(0.90, 0.38, 35, 0, 0, 0.022)],
    shell=(0.18, 0.14, 0.11), shell_dark=(0.07, 0.055, 0.05), rim=(0.32, 0.26, 0.22),
    under=(0.36, 0.30, 0.26), leg=(0.22, 0.18, 0.15), leg_dark=(0.10, 0.08, 0.07),
)

_eyes = eu.eyes


def eyes_and_gills(mb, b):
    _eyes(mb, b)
    s = b.s
    n = len(s.pre_w)
    seg = s.pre_len / n
    for i in range(1, n - 1):
        y = s.y_pro + seg * (i + 0.45)
        w = s.pre_w[i]
        for sx in (-1, 1):
            for k in range(4):
                yy = y - seg * 0.30 + seg * 0.2 * k
                base = Vector((sx * w * 0.85, yy, -0.025))
                L_ = 0.19 + 0.04 * math.sin(i * 1.3 + k)
                d = Vector((sx * 1.0, 0.20 + 0.15 * k, -0.10)).normalized()
                mid = base + d * L_ * 0.55 + Vector((0, 0, -0.01))
                tip = base + d * L_ + Vector((0, 0.02, 0.005))
                mb.add(nh.tube([base, mid, tip], [0.013, 0.009, 0.0], sides=5),
                       lambda co, nn, b0=base: nh.lerp(GILL, GILL_TIP, min(1.0, (co - b0).length / 0.12)))


eu.eyes = eyes_and_gills

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
