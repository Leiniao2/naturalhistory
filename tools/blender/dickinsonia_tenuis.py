"""
Procedural Dickinsonia tenuis (Ediacaran proarticulate) for map colonies (Swim style).

A slender Dickinsonia from the Ediacara Member of South Australia: the same flat, thin,
soft-edged quilt as D. costata but markedly more elongated and narrow, with nearly
parallel sides and very numerous, very fine transverse isomers (about 52 a side here)
crowding either side of a long midline groove. The isomers of the two sides alternate,
run almost straight across along the body, fan round the two rounded ends and are finest
at the front. Pale pinkish tan with darker furrows (colours are a reconstruction choice).
Built with nh_dickinsonid.py.

Usage:
  blender --background --python tools/blender/dickinsonia_tenuis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DickinsoniaTenuis.fbx
Pivot at the body centre, faces -Y (front), back up (+Z). About 1.64 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dickinsonid as dk  # noqa: E402

SPEC = dk.Spec(
    name="DickinsoniaTenuis",
    half_length=0.82,
    half_width=0.34,          # length / width about 2.4
    front_round=2.2,
    back_round=2.6,
    front_taper=0.06,
    widest=0.05,
    isomers=52,
    rows_per=2,
    cols=6,
    grow=1.0,
    mid_front=0.92,
    mid_back=0.90,
    fan=1.15,
    bow=0.03,
    height=0.045,
    thickness=0.025,
    relief=0.40,
    groove_width=0.06,
    seed=7,
    crest=(0.90, 0.72, 0.60),
    body=(0.78, 0.58, 0.46),
    furrow=(0.48, 0.31, 0.23),
    midline=(0.38, 0.23, 0.17),
    front_tint=(0.90, 0.66, 0.60),
    back_tint=(0.72, 0.52, 0.38),
)


def build():
    return dk.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "DickinsoniaTenuis", background=(0.05, 0.14, 0.18), views=((0, 89), (30, 35), (-90, 10)))
