"""
Procedural Whitmania leech (Whitmania pigra) for map colonies (Swim style).

The big, broad, flat leech of East Asian rice fields, ponds and lakes, up to
10-12 cm long. Not a bloodsucker: its jaws are weak and it swallows snails,
worms and insect larvae whole. A wide, thick, almost parallel-sided body that
narrows sharply to a small head (five pairs of eye spots) and to a small caudal
sucker; the annuli are crowded and fine. Dark olive-green to brown back with
fine dark longitudinal lines and rows of small dark spots, narrow yellowish
margins and a pale yellow belly with faint dark lines. Built with nh_leech.py.
The body is left straight: on the map the shader (MapFeatureFlap.cginc,
ApplyUndulate) swims it with a travelling wave.

Usage:
  blender --background --python tools/blender/whitmania_pigra.py -- [--render out.png]

Output: Assets/Resources/Models/Species/WhitmaniaLeech.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 1.8 units long.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_leech as lc  # noqa: E402

BACK = (0.19, 0.20, 0.10)        # dark olive-brown
BACK_HEAD = (0.13, 0.12, 0.07)
LINE = (0.05, 0.05, 0.03)
PALE_LINE = (0.36, 0.33, 0.13)
MARGIN = (0.74, 0.62, 0.24)      # yellowish margin
BELLY = (0.80, 0.70, 0.36)       # pale yellow
BELLY_LINE = (0.42, 0.36, 0.18)

SPEC = lc.Spec(
    name="WhitmaniaLeech",
    half_width=0.30,
    top=0.30,
    belly=0.14,
    dome=2.8,
    profile=[(0.0, 0.12), (0.04, 0.26), (0.10, 0.42), (0.22, 0.72), (0.40, 0.92),
             (0.65, 1.00), (0.82, 0.92), (0.93, 0.60), (1.0, 0.30)],
    annuli=28,
    groove=0.98,
    sides_top=26,
    sides_belly=6,
    oral=0.5,
    caudal=0.40,
    caudal_offset=0.7,
    eye_pairs=5,
    eye_size=0.010,
    back=BACK,
    back_head=BACK_HEAD,
    belly_col=BELLY,
    margin_col=MARGIN,
    margin_width=0.09,
    groove_dark=0.86,
    stripes=[
        ((0.0, 0.035), LINE, 0.9),
        ((0.15, 0.07), PALE_LINE, 0.6),
        ((0.30, 0.035), LINE, 0.8),
        ((0.50, 0.035), LINE, 0.8),
        ((0.68, 0.035), LINE, 0.7),
    ],
    spots=[
        ((0.30, 0.06), LINE, 2, 0, 0.6),
        ((0.58, 0.05), LINE, 2, 1, 0.5),
    ],
    belly_spots=[
        ((0.45, 0.06), BELLY_LINE, 1, 3.0),
    ],
    sucker_col=(0.52, 0.45, 0.22),
)


if __name__ == "__main__":
    nh.run(lambda: lc.build(SPEC), "WhitmaniaLeech", background=(0.10, 0.13, 0.09),
           views=((35, 30), (0, 90), (-90, 8), (20, -35)))
