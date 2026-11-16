"""
Procedural Yorgia waggoneri (Ediacaran proarticulate) for map colonies (Swim style).

A broad dickinsoniid from the White Sea coast of Russia, up to about 25 cm long: a flat,
thin, soft-edged body about as wide as it is long and lopsided. A short, wide "head" zone
at the front is formed by a few enlarged first isomers that sweep round the broad front
margin; behind it a midline groove, set off to one side and gently bent, divides the body
into a wider and a narrower half, each crossed by alternating (half-offset) isomers that
fan back round the rounded rear. Ochre-brown with a paler head zone and darker furrows
(colours are a reconstruction choice). Built with nh_dickinsonid.py.

Usage:
  blender --background --python tools/blender/yorgia_waggoneri.py -- [--render out.png]

Output: Assets/Resources/Models/Species/Yorgia.fbx
Pivot at the body centre, faces -Y (front), back up (+Z). About 1.3 units across.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dickinsonid as dk  # noqa: E402

SPEC = dk.Spec(
    name="Yorgia",
    half_length=0.64,
    half_width=0.62,          # roughly as wide as long
    width_skew=0.22,          # right half wider than the left
    front_round=2.7,          # broad, blunt head end
    back_round=2.2,
    front_taper=0.0,
    widest=-0.10,             # widest in front of the middle
    isomers=26,
    rows_per=3,
    cols=8,
    grow=1.2,
    head=3,
    head_scale=2.8,
    mid_front=0.90,
    mid_back=0.80,
    mid_offset=0.16,
    mid_bend=0.10,
    fan=1.1,
    sweep=0.07,
    bow=0.05,
    height=0.06,
    thickness=0.03,
    relief=0.38,
    groove_fade_front=0.60,   # no midline groove across the head zone
    seed=19,
    crest=(0.86, 0.64, 0.45),
    body=(0.72, 0.49, 0.32),
    furrow=(0.40, 0.24, 0.14),
    midline=(0.33, 0.19, 0.12),
    front_tint=(0.90, 0.72, 0.56),
    back_tint=(0.62, 0.42, 0.26),
)


def build():
    return dk.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "Yorgia", background=(0.05, 0.14, 0.18), views=((0, 89), (30, 35), (-90, 10)))
