"""
Procedural Titanoboa cerrejonensis (middle-late Paleocene, ~60-58 Ma, Cerrejon
Formation, Colombia) for map colonies. Built with nh_pal_snake.py.

The largest snake known, a boid related to boas and anacondas, about 13 m long and
over 1 tonne, with a body nearly 1 m thick at its widest. It lived in hot tropical
swamp-forest rivers and probably ate fish such as giant lungfish, and crocodile
relatives. Pattern: olive with dark boa-like saddles and side blotches and a pale
belly (colour unknown).
Faces -Y, pivot on the ground.

Usage:
  blender --background --python tools/blender/titanoboa_cerrejonensis.py -- [--render out.png]

Output: Assets/Resources/Models/Species/TitanoboaCerrejonensis.fbx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nh_pal_snake as sn  # noqa: E402

SPEC = sn.Spec(
    name="TitanoboaCerrejonensis",
    length=2.4, girth=0.095, head_len=0.15, head_w=0.085, neck=0.5, tail=0.14,
    base=(0.36, 0.36, 0.20), saddle=(0.13, 0.12, 0.08), belly=(0.78, 0.74, 0.55),
    saddles=20, saddle_w=0.42, side_spots=0.7, head_col=(0.26, 0.25, 0.15),
)

if __name__ == "__main__":
    sn.main(SPEC)
