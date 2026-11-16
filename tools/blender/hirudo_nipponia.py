"""
Procedural Asian medicinal leech (Hirudo nipponia) for map colonies (Swim style).

A freshwater bloodsucker of East Asian rice fields, ponds and marshes, a few
centimetres long: a flattened, tapering body with a narrow head end (oral sucker
with jaws underneath, five pairs of eye spots in an arc on top), widest behind
the middle and ending in a round caudal sucker. Olive-green back with five
longitudinal stripes - a thin orange median line, a pair of broad yellow-orange
paramedian stripes broken by black spots on every segment and a pair of paler
yellowish lateral stripes - yellowish margins and a greenish-yellow belly; the
fine annuli show as darker grooves. Built with nh_leech.py. The body is left
straight: on the map the shader (MapFeatureFlap.cginc, ApplyUndulate) swims it
with a travelling wave.

Usage:
  blender --background --python tools/blender/hirudo_nipponia.py -- [--render out.png]

Output: Assets/Resources/Models/Species/AsianMedicinalLeech.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 1.8 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_leech as lc  # noqa: E402

OLIVE = (0.17, 0.22, 0.09)
OLIVE_HEAD = (0.12, 0.15, 0.07)
ORANGE = (0.82, 0.52, 0.16)
YELLOW = (0.80, 0.66, 0.22)
BLACK = (0.03, 0.03, 0.02)
BELLY = (0.55, 0.55, 0.24)
MARGIN = (0.72, 0.62, 0.22)

SPEC = lc.Spec(
    name="AsianMedicinalLeech",
    half_width=0.135,
    top=0.42,
    belly=0.22,
    dome=2.4,
    annuli=30,
    sides_top=24,
    sides_belly=6,
    caudal=0.95,
    eye_pairs=5,
    eye_size=0.008,
    back=OLIVE,
    back_head=OLIVE_HEAD,
    belly_col=BELLY,
    margin_col=MARGIN,
    margin_width=0.10,
    stripes=[
        ((0.0, 0.07), ORANGE, 0.85),
        ((0.40, 0.11), ORANGE, 0.95),
        ((0.76, 0.07), YELLOW, 0.75),
    ],
    spots=[
        ((0.40, 0.09), BLACK, 2, 1, 0.7),
    ],
    belly_spots=[
        ((0.75, 0.12), (0.20, 0.22, 0.10), 2, 0.6),
    ],
)


if __name__ == "__main__":
    nh.run(lambda: lc.build(SPEC), "AsianMedicinalLeech", background=(0.10, 0.13, 0.09),
           views=((35, 30), (0, 90), (-90, 8), (20, -35)))
