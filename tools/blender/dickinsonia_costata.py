"""
Procedural Dickinsonia costata (Ediacaran proarticulate) for map colonies (Swim style).

The classic Dickinsonia of the Ediacara Hills (South Australia) and the White Sea: a flat,
thin, oval quilt lying on the microbial mat, usually a few centimetres to about 20 cm long.
A narrow midline groove runs almost its whole length and the body either side is divided
into many fine transverse tube-like isomers - about 36 a side here - that run straight out
to the soft margin in the middle of the body and fan round the curve of the margin at both
ends. The isomers of the two sides alternate (offset by half a unit) rather than pairing
up, and they are smallest at the slightly narrower front end and widen toward the back.
Soft pinkish tan with darker grooves and midline and a paler lip (colours are a
reconstruction choice). Built with nh_dickinsonid.py.

Usage:
  blender --background --python tools/blender/dickinsonia_costata.py -- [--render out.png]

Output: Assets/Resources/Models/Species/DickinsoniaCostata.fbx
Pivot at the body centre, faces -Y (front), back up (+Z). About 1.6 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_dickinsonid as dk  # noqa: E402

SPEC = dk.Spec(
    name="DickinsoniaCostata",
    half_length=0.80,
    half_width=0.56,          # length / width about 1.45
    front_round=2.0,
    back_round=2.3,           # fuller, rounder back end
    front_taper=0.10,
    widest=0.12,
    isomers=36,
    rows_per=3,
    cols=8,
    grow=1.6,
    mid_front=0.90,
    mid_back=0.86,
    bow=0.05,
    height=0.06,
    thickness=0.03,
    relief=0.45,
    seed=3,
    crest=(0.88, 0.68, 0.56),
    body=(0.76, 0.54, 0.41),
    furrow=(0.44, 0.27, 0.19),
    midline=(0.36, 0.21, 0.15),
    front_tint=(0.88, 0.62, 0.55),   # pinker toward the front
    back_tint=(0.66, 0.46, 0.30),    # more ochre toward the back
)


def build():
    return dk.build(SPEC)


if __name__ == "__main__":
    nh.run(build, "DickinsoniaCostata", background=(0.05, 0.14, 0.18), views=((0, 89), (30, 35), (-90, 10)))
