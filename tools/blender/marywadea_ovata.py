"""
Procedural Marywadea ovata (Ediacaran proarticulate) for map colonies (Swim style).

An oval, flattened animal a few centimetres long from South Australia, a broader relative of
Spriggina: a smooth, crescent-shaped head shield at the front and a body of many fine,
offset segments either side of a midline that fan back round the rounded rear.
Fawn with a pale head shield and brown furrows. Faces -Y, pivot at the body centre.

Output: Assets/Resources/Models/Species/Marywadea.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dickinsonid as dk  # noqa: E402

SPEC = dk.Spec(
    name="Marywadea",
    half_length=0.82,
    half_width=0.5,
    front_round=2.6,
    back_round=1.9,
    widest=-0.1,
    isomers=30,
    rows_per=3,
    cols=8,
    grow=0.6,
    head=2,
    head_scale=4.5,
    mid_front=0.62,
    mid_back=0.86,
    fan=1.2,
    bow=0.08,
    sweep=0.1,
    height=0.08,
    thickness=0.03,
    relief=0.45,
    groove=0.35,
    groove_fade_front=0.45,
    isomer_tone=0.05,
    seed=9,
    crest=(0.88, 0.76, 0.58),
    body=(0.74, 0.60, 0.42),
    furrow=(0.40, 0.29, 0.18),
    midline=(0.50, 0.36, 0.22),
    front_tint=(0.94, 0.86, 0.70),
    margin=(0.58, 0.44, 0.30),
)


def build():
    return dk.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "Marywadea", background=(0.05, 0.14, 0.18), views=((0, 89), (30, 35), (-90, 10)))
