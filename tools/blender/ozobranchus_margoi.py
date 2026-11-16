"""
Procedural sea-turtle leech (Ozobranchus margoi) for map colonies (Swim style).

A tiny marine leech, about 1 cm long, that spends its whole life on sea turtles,
clinging to the soft skin of the neck, flippers and tail (and around the eyes and
mouth) and feeding on their blood. A short, rounded body in two parts: a narrow
neck-like front (trachelosome) with a small oral sucker and tiny eye spots,
and a wider hind body (urosome) carrying seven pairs of finger-like gill tufts
along its sides, each tuft split into a few short digits, ending in a large round
caudal sucker it holds on with. Pale greyish-cream with a faint darker median line
and pinkish, blood-filled gills. Built with nh_leech.py. The body is left
straight: on the map the shader (MapFeatureFlap.cginc, ApplyUndulate) swims it
with a travelling wave.

Usage:
  blender --background --python tools/blender/ozobranchus_margoi.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TurtleLeech.fbx
Pivot at the body centre, faces -Y, back up (+Z). About 1.8 units long (incl. gills ~0.9 wide).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_leech as lc  # noqa: E402

BODY = (0.74, 0.70, 0.60)        # pale greyish-cream
BODY_HEAD = (0.66, 0.60, 0.52)
LINE = (0.46, 0.40, 0.34)
BELLY = (0.82, 0.78, 0.68)
GILL = (0.84, 0.50, 0.50)        # pinkish, blood-filled
SUCKER = (0.70, 0.64, 0.56)

SPEC = lc.Spec(
    name="TurtleLeech",
    half_width=0.20,
    top=0.62,
    belly=0.38,
    dome=2.1,
    profile=[(0.0, 0.22), (0.04, 0.34), (0.10, 0.36), (0.24, 0.38), (0.32, 0.50),
             (0.42, 0.82), (0.60, 1.00), (0.78, 0.96), (0.90, 0.70), (1.0, 0.45)],
    annuli=22,
    groove=0.965,
    sides_top=16,
    sides_belly=6,
    oral=0.65,
    caudal=1.10,
    caudal_offset=0.55,
    eye_pairs=1,
    eye_size=0.012,
    gills=7,
    gill_span=(0.40, 0.86),
    gill_fingers=3,
    gill_length=1.05,
    gill_radius=0.022,
    back=BODY,
    back_head=BODY_HEAD,
    belly_col=BELLY,
    groove_dark=0.88,
    mottle=0.10,
    stripes=[
        ((0.0, 0.10), LINE, 0.5),
    ],
    sucker_col=SUCKER,
    gill_col=GILL,
)


if __name__ == "__main__":
    nh.run(lambda: lc.build(SPEC), "TurtleLeech", background=(0.06, 0.14, 0.20),
           views=((35, 30), (0, 90), (-90, 8), (20, -35)))
