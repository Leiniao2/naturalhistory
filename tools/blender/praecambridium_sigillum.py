"""
Procedural Praecambridium sigillum (Ediacaran proarticulate) for map colonies (Swim style).

A minute, shield-shaped animal from South Australia, under 1 cm long, once mistaken for a
trilobite larva: a large, smooth, semicircular head shield followed by a few broad, chevron-
like segments that grow wider toward the back and alternate either side of the midline.
Grey-brown with a paler shield. Faces -Y, pivot at the body centre.

Output: Assets/Resources/Models/Species/Praecambridium.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dickinsonid as dk  # noqa: E402

SPEC = dk.Spec(
    name="Praecambridium",
    half_length=0.78,
    half_width=0.62,
    front_round=2.2,
    back_round=1.6,
    widest=-0.25,
    isomers=7,
    rows_per=5,
    cols=9,
    grow=0.3,
    head=1,
    head_scale=2.6,
    mid_front=0.5,
    mid_back=0.92,
    fan=1.0,
    bow=0.1,
    sweep=0.06,
    height=0.1,
    thickness=0.035,
    relief=0.4,
    groove=0.45,
    groove_fade_front=0.7,
    isomer_tone=0.06,
    seed=5,
    crest=(0.80, 0.74, 0.64),
    body=(0.64, 0.56, 0.46),
    furrow=(0.32, 0.26, 0.20),
    midline=(0.40, 0.33, 0.26),
    front_tint=(0.88, 0.84, 0.74),
    margin=(0.50, 0.43, 0.35),
)


def build():
    return dk.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "Praecambridium", background=(0.05, 0.14, 0.18), views=((0, 89), (30, 35), (-90, 10)))
