"""
Procedural Vendia sokolovi (Ediacaran proarticulate) for map colonies (Swim style).

A tiny, flat, oval animal from the White Sea, about 1 cm long, built from only a handful of
large, sickle-shaped isomers that alternate left and right of an off-centre midline, the first
one enlarged and wrapping round the front. Its lopsided, glide-symmetric quilting is the
proarticulate hallmark. Rusty orange with darker furrows. Faces -Y, pivot at the body centre.

Output: Assets/Resources/Models/Species/Vendia.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dickinsonid as dk  # noqa: E402

SPEC = dk.Spec(
    name="Vendia",
    half_length=0.8,
    half_width=0.52,
    width_skew=0.08,
    front_round=2.4,
    back_round=1.7,
    widest=-0.15,
    isomers=7,
    rows_per=5,
    cols=9,
    grow=0.4,
    head=0,
    head_scale=1.0,
    mid_front=0.85,
    mid_back=0.9,
    mid_offset=0.1,
    mid_bend=0.0,
    fan=1.3,
    bow=0.08,
    sweep=0.0,
    height=0.09,
    thickness=0.035,
    relief=0.6,
    groove=0.5,
    groove_fade_front=0.3,
    isomer_tone=0.1,
    seed=7,
    crest=(0.92, 0.62, 0.40),
    body=(0.80, 0.48, 0.28),
    furrow=(0.40, 0.20, 0.12),
    midline=(0.34, 0.17, 0.10),
    front_tint=(0.94, 0.70, 0.50),
    margin=(0.60, 0.34, 0.20),
)


def build():
    return dk.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "Vendia", background=(0.05, 0.14, 0.18), views=((0, 89), (30, 35), (-90, 10)))
