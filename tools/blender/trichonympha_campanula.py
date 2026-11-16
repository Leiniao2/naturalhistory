"""
Procedural low-poly Trichonympha campanula for colony instancing: one of the
largest termite-gut flagellates (a few hundred micrometres long), named for its
bell shape.

A broad, campanulate cell: a short rostrum with a glassy cap at the front widens
quickly into a big rounded bell. Dense rows of long flagella spring from the
rostrum and the front half of the bell and trail backwards over it in a shaggy
sheath; the bare rear end is greyer and packed with angular brown wood
splinters engulfed from the termite's gut, and a faint nucleus shows through the
middle. Pale grey-blue, glassy colours (vertex colours, see nh_model).

Drift style: pivot at the body centre, faces -Y (rostrum first).

Usage:
  blender --background --python tools/blender/trichonympha_campanula.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TrichonymphaCampanula.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nh_model as nh  # noqa: E402
import nh_trichonympha as tr  # noqa: E402

SEED = 3
LENGTH = 1.8
# (t, radius): t = 0 rostrum tip, 1 rear end. Short rostrum, broad bell.
PROFILE = [
    (0.00, 0.000), (0.012, 0.055), (0.035, 0.080), (0.06, 0.070),   # rostral cap
    (0.10, 0.082), (0.17, 0.125), (0.26, 0.215), (0.36, 0.335),     # flaring shoulder of the bell
    (0.47, 0.430), (0.60, 0.475), (0.74, 0.470), (0.86, 0.420),
    (0.95, 0.290), (0.99, 0.130), (1.00, 0.000),                    # broad, blunt rear
]


def build():
    return tr.build(
        PROFILE, "TrichonymphaCampanula", SEED, length=LENGTH, flatten=0.92,
        nucleus_t=0.40, rostrum_t=0.10,
        flagella_args=dict(rows=34, per_row=9, t_range=(0.03, 0.5), length=(0.24, 0.30),
                           t_max=0.68, twist=0.4, lift=0.06, radius=0.0065),
        wood_args=dict(count=46, t_range=(0.66, 0.99), size=(0.05, 0.09)),
    )


if __name__ == "__main__":
    nh.run(build, "TrichonymphaCampanula", views=((35, 35), (-90, 10), (180, 60)))
