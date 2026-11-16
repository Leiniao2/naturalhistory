"""
Procedural Dickinsonia menneri (Ediacaran proarticulate) for map colonies (Swim style).

A small, broad Dickinsonia from the White Sea coast of Russia, usually only a few
centimetres long: a nearly round, flat, soft-edged body with comparatively few, broad
isomers (14 a side here) either side of a short midline groove. The isomers of the two
sides alternate by half a unit; they are narrowest at the front, broaden markedly toward
the back and fan out round the full, rounded margin, so each one reads as a fat, raised
pad. Warmer ochre-tan with darker furrows (colours are a reconstruction choice).
Built with nh_dickinsonid.py.

Usage:
  blender --background --python tools/blender/dickinsonia_menneri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DickinsoniaMenneri.fbx
Pivot at the body centre, faces -Y (front), back up (+Z). About 1.5 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dickinsonid as dk  # noqa: E402

SPEC = dk.Spec(
    name="DickinsoniaMenneri",
    half_length=0.74,
    half_width=0.64,          # length / width about 1.15
    front_round=2.1,
    back_round=2.4,
    front_taper=0.08,
    widest=0.10,
    isomers=14,
    rows_per=4,
    cols=9,
    grow=1.8,
    mid_front=0.80,
    mid_back=0.72,
    fan=1.1,
    bow=0.06,
    height=0.075,
    thickness=0.032,
    relief=0.55,
    groove_width=0.05,
    isomer_tone=0.09,
    seed=11,
    crest=(0.88, 0.67, 0.48),
    body=(0.74, 0.52, 0.34),
    furrow=(0.42, 0.26, 0.16),
    midline=(0.34, 0.20, 0.13),
    front_tint=(0.86, 0.62, 0.50),
    back_tint=(0.64, 0.44, 0.27),
)


def build():
    return dk.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "DickinsoniaMenneri", background=(0.05, 0.14, 0.18), views=((0, 89), (30, 35), (-90, 10)))
