"""
Procedural Megalograptus ohioensis (Late Ordovician, Katian, megalograptid eurypterid
from southwestern Ohio, about 50-80 cm long) for map colonies (Swim style).

Megalograptid plan (nh_ord_eurypterid.py): a rounded, slightly trapezoidal prosoma with
small eyes; long, robust front legs (appendages II-IV) bristling with pairs of very long
spines; a short appendage V; swimming paddles; seven broad and five narrow abdominal
segments; and a spine-like telson flanked by the pair of serrated cercal blades that
distinguish Megalograptus. Mottled brown cuticle (colour conjectural).

Usage:
  blender --background --python tools/blender/megalograptus_ohioensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/MegalograptusOhioensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_model as nh  # noqa: E402
import nh_ord_eurypterid as eu  # noqa: E402

SPEC = eu.Spec(
    name="MegalograptusOhioensis",
    pro_w=0.20, pro_front=0.72, pro_corner=0.35,
    legs=(0.50, 0.60, 0.62), leg_spines=5, spine_len=0.15, leg_v=0.28, paddle=0.15,
    cercal=0.30, telson_len=0.40,
    pattern=0.6,
)

if __name__ == "__main__":
    nh.run(lambda: eu.build(SPEC), SPEC.name, **eu.VIEWS)
