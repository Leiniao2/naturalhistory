"""
Procedural Andiva ivantsovi (Ediacaran proarticulate, White Sea, Russia, ~555 Ma) for map
colonies (Swim style). A flat oval body, longer than wide, with a broad smooth shield-like
zone at the front (a few much-enlarged first isomers sweeping round the front margin),
then rows of narrow transverse isomers that alternate (half offset) either side of a midline
groove and fan round the rounded rear. Built with nh_dickinsonid.py. Warm grey-tan with
paler crests and a paler front shield.

Usage:
  blender --background --python tools/blender/andiva_ivantsovi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Andiva.fbx
Pivot at the body centre, faces -Y (front).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dickinsonid as dk  # noqa: E402

SPEC = dk.Spec(
    name="Andiva",
    half_length=0.8,
    half_width=0.5,
    width_skew=0.0,
    front_round=2.4,
    back_round=1.9,
    widest=-0.15,
    isomers=22,
    rows_per=3,
    cols=8,
    grow=0.6,
    head=2,
    head_scale=4.5,
    mid_front=0.62,
    mid_back=0.86,
    fan=1.1,
    sweep=0.10,
    bow=0.06,
    height=0.07,
    thickness=0.03,
    relief=0.40,
    groove=0.6,
    groove_fade_front=0.7,
    seed=23,
    crest=(0.82, 0.74, 0.60),
    body=(0.64, 0.56, 0.44),
    furrow=(0.34, 0.28, 0.20),
    midline=(0.28, 0.22, 0.15),
    front_tint=(0.90, 0.84, 0.70),
    back_tint=(0.56, 0.48, 0.36),
)


def build():
    return dk.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "Andiva", background=(0.05, 0.14, 0.18), views=((0, 89), (30, 35), (-90, 10)))
